from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router

from .services import (
    assignment_public_view,
    create_assignment_submission,
    create_quiz_attempt_submission,
    question_public_view,
    serialize_submission,
)
from .store import (
    application_summary,
    certification_status,
    confirm_section,
    complete_lesson,
    create_payment_checkout,
    enrollment_summary,
    enroll_user,
    enroll_stage2,
    gamification_status,
    get_assignment,
    get_registered_learner,
    get_lesson,
    get_quiz,
    jobs_summary,
    lesson_summary,
    list_assignment_submissions,
    current_payments,
    finalize_payment_webhook,
    register_learner,
    stage1_completion_state,
    stage2_state,
    stage2_enrollment_state,
    stage3_state,
    stage1_state,
    submit_stage2_task,
    submit_stage2_partner_selection,
    submit_stage3_application,
    stage3_unlock_state,
    stage1_completion_state,
    certification_summary,
)


router = Router()


def _canonical_user_id(payload: dict[str, Any] | None = None, user_id: str | None = None) -> str:
    if user_id:
        return str(user_id)
    if payload and payload.get("user_id"):
        return str(payload["user_id"])
    return "me"


@router.post("/auth/register")
def register(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id") or payload.get("email") or payload.get("full_name") or "learner")
    profile = register_learner(
        user_id=user_id,
        email=str(payload.get("email", "")),
        full_name=str(payload.get("full_name", "")),
        plan_tier=str(payload.get("plan_tier", "basics")),
    )
    return {
        "user": profile,
        "registered": True,
        "enrollment": enrollment_summary(user_id),
    }


@router.get("/courses/available")
def available_courses() -> dict[str, Any]:
    return {
        "courses": [
            {
                "id": 1,
                "title": "Nano Lab Academy",
                "description": "A compact freemium course track with lessons, quizzes, and assignments.",
            }
        ]
    }


@router.get("/enrollments/my")
def my_enrollment(user_id: str = "me") -> dict[str, Any]:
    return enrollment_summary(user_id)


@router.get("/courses/my")
def my_courses(user_id: str = "me") -> dict[str, Any]:
    return enrollment_summary(user_id)


@router.post("/enrollments/enroll")
def enroll(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    plan_tier_raw = str(payload.get("plan_tier", "basics"))
    try:
        plan_tier = str(register_learner(user_id=user_id, plan_tier=plan_tier_raw)["plan_tier"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="plan_tier must be basics, pro, or ultra") from exc

    enroll_user(user_id=user_id, plan_tier=plan_tier)
    return enrollment_summary(user_id)


@router.get("/courses/tree")
def course_tree(user_id: str = "me") -> dict[str, Any]:
    return enrollment_summary(user_id)


@router.get("/gamification/status")
def my_gamification_status(user_id: str = "me") -> dict[str, Any]:
    status = gamification_status(user_id)
    status.update(stage1_state(user_id))
    return status


@router.get("/stage/status")
def stage_status(user_id: str = "me") -> dict[str, Any]:
    stage1 = stage1_state(user_id)
    stage2 = stage2_enrollment_state(user_id)
    return {
        "user_id": user_id,
        "stage1": stage1,
        "stage2": stage2,
        "stage3_unlocked": stage2["stage3_unlocked"],
    }


@router.post("/stage/check-stage1")
def check_stage1(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    return {
        **stage1_state(user_id),
        "user_id": user_id,
        "stage2_unlocked": stage1_completion_state(user_id)["stage2_unlocked"],
    }


@router.post("/stage/check-stage2")
def check_stage2(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    status = stage2_enrollment_state(user_id)
    return {
        "user_id": user_id,
        **status,
    }


@router.post("/lessons/{lesson_id}/complete")
def mark_lesson_complete(lesson_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    completion = complete_lesson(user_id, lesson_id)
    return {
        "completion": completion,
        "lesson": lesson_summary(lesson_id, user_id),
        "gamification": gamification_status(user_id),
    }


@router.post("/lessons/{lesson_id}/progress")
def mark_lesson_progress(lesson_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return mark_lesson_complete(lesson_id, payload)


@router.post("/download-notes")
def download_notes(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        lesson_id = int(payload.get("lesson_id"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="lesson_id is required") from exc

    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {
        "lesson_id": lesson.id,
        "filename": f"lesson-{lesson.id}-notes.txt",
        "content": lesson.notes,
    }


@router.get("/lessons/{lesson_id}/download-notes")
def download_notes_get(lesson_id: int, user_id: str = "me") -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {
        "lesson_id": lesson.id,
        "filename": f"lesson-{lesson.id}-notes.txt",
        "content": lesson.notes,
        "user_id": user_id,
    }


@router.post("/sections/{section_id}/confirm")
def confirm_course_section(section_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    course = enrollment_summary(user_id).get("course")
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    section = next((item for item in course["outline"] if item["id"] == section_id), None)
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    if not section["completed"]:
        raise HTTPException(status_code=400, detail="Complete the section lessons before confirming")

    return confirm_section(user_id, section_id)


@router.get("/stage2/lab-partners")
def stage2_lab_partners() -> dict[str, Any]:
    return stage2_state()


@router.get("/stage2/my-status")
def stage2_my_status(user_id: str = "me") -> dict[str, Any]:
    return {
        "user_id": user_id,
        **stage2_enrollment_state(user_id),
    }


@router.post("/stage2/enroll")
def stage2_enroll(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    enrollment = enroll_stage2(user_id, str(payload.get("lab_partner_id") or payload.get("partner_id") or ""))
    return {
        "enrollment": enrollment,
        "status": stage2_enrollment_state(user_id),
    }


@router.post("/stage2/tasks/{task_id}/submit")
def stage2_submit_task(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    submission = submit_stage2_task(user_id, task_id, payload)
    return {
        "submission": submission,
        "status": stage2_enrollment_state(user_id),
    }


@router.get("/stage-2/data")
def stage_two_data() -> dict[str, Any]:
    return stage2_state()


@router.post("/stage-2/select-partner")
def stage_two_select_partner(payload: dict[str, Any]) -> dict[str, Any]:
    return submit_stage2_partner_selection(payload)


@router.get("/stage-3/data")
def stage_three_data() -> dict[str, Any]:
    return stage3_state()


@router.post("/stage-3/apply")
def stage_three_apply(payload: dict[str, Any]) -> dict[str, Any]:
    application = submit_stage3_application(payload)
    return {
        "application": application,
        "applications": stage3_state()["applications"],
    }


@router.get("/jobs")
def jobs(user_id: str = "me") -> dict[str, Any]:
    return jobs_summary(user_id)


@router.get("/jobs/{job_id}")
def job_details(job_id: str, user_id: str = "me") -> dict[str, Any]:
    job = next((item for item in jobs_summary(user_id)["jobs"] if str(item["id"]) == str(job_id)), None)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/jobs/{job_id}/apply")
def apply_for_job(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    if not stage3_unlock_state(user_id):
        raise HTTPException(status_code=403, detail="Stage 3 is locked until the Stage 2 evaluation is approved")

    application = submit_stage3_application({**payload, "job_id": job_id, "user_id": user_id})
    return {
        "application": application,
        "applications": application_summary(user_id),
        "stage3_unlocked": True,
    }


@router.get("/applications/my")
def my_applications(user_id: str = "me") -> list[dict[str, Any]]:
    return application_summary(user_id)


@router.post("/payments/create-checkout")
def create_checkout(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = _canonical_user_id(payload)
    checkout_type = str(payload.get("type", "stage_unlock"))
    amount = float(payload.get("amount", 29))
    plan_tier = str(payload.get("plan_tier", "pro"))
    payment = create_payment_checkout(user_id=user_id, checkout_type=checkout_type, amount=amount, plan_tier=plan_tier)
    return {
        "payment": payment,
        "payments": current_payments(user_id),
    }


@router.post("/payments/webhook")
def payment_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    reference = str(payload.get("reference") or payload.get("checkout_id") or payload.get("payment_reference") or "").strip()
    if not reference:
        raise HTTPException(status_code=400, detail="reference is required")

    payment = finalize_payment_webhook(reference=reference, status=str(payload.get("status", "succeeded")), metadata={k: v for k, v in payload.items() if k not in {"reference", "checkout_id", "payment_reference", "status"}})
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    user_id = str(payment["user_id"])
    return {
        "payment": payment,
        "enrollment": enrollment_summary(user_id),
        "stage1": stage1_state(user_id),
    }


@router.get("/certifications/my")
def my_certifications(user_id: str = "me") -> list[dict[str, Any]]:
    return certification_status(user_id)


@router.get("/quizzes/{quiz_id}")
def get_quiz_details(quiz_id: int) -> dict[str, Any]:
    quiz = get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "pass_threshold": quiz.pass_threshold,
        "questions": [question_public_view(question) for question in quiz.questions],
    }


@router.post("/quizzes/{quiz_id}/attempt")
def submit_quiz_attempt(quiz_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    quiz = get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    user_id = str(payload.get("user_id", "me"))
    answers = payload.get("answers") or []
    if not isinstance(answers, list):
        raise HTTPException(status_code=400, detail="answers must be a list")

    normalized_answers: list[dict[str, Any]] = []
    for answer in answers:
        if not isinstance(answer, dict) or "question_id" not in answer or "answer" not in answer:
            raise HTTPException(status_code=400, detail="Each answer must contain question_id and answer")
        normalized_answers.append({"question_id": answer["question_id"], "answer": answer["answer"]})

    submission = create_quiz_attempt_submission(
        quiz=quiz,
        user_id=user_id,
        answers=normalized_answers,
    )

    return {
        "submission_id": submission.id,
        "score": submission.score,
        "passed": submission.passed,
        "manual_review_required": submission.manual_review_required,
        "xp_awarded": submission.xp_awarded,
        "badge_ids": submission.badge_ids,
        "submission": serialize_submission(submission),
    }


@router.get("/assignments/my")
def my_assignments(user_id: str = "me") -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for submission in list_assignment_submissions(user_id=user_id):
        assignment = get_assignment(submission.related_id)
        results.append(
            {
                "submission_id": submission.id,
                "assignment_id": submission.related_id,
                "assignment_title": assignment.title if assignment else None,
                "score": submission.score,
                "passed": submission.passed,
                "status": submission.status,
                "xp_awarded": submission.xp_awarded,
                "submitted_at": submission.created_at.isoformat(),
            }
        )
    return results


@router.get("/assignments/{assignment_id}")
def get_assignment_details(assignment_id: int) -> dict[str, Any]:
    assignment = get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment_public_view(assignment)


@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(assignment_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    assignment = get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")

    user_id = str(payload.get("user_id", "me"))
    file_url = payload.get("file_url")
    text_answer = payload.get("text_answer")
    if not file_url and not text_answer:
        raise HTTPException(status_code=400, detail="Provide file_url or text_answer")

    submission = create_assignment_submission(
        assignment=assignment,
        user_id=user_id,
        file_url=file_url,
        text_answer=text_answer,
    )

    return {
        "submission_id": submission.id,
        "score": submission.score,
        "passed": submission.passed,
        "xp_awarded": submission.xp_awarded,
        "submission": serialize_submission(submission),
    }
