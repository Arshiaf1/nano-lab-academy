from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router

from .services import (
    assignment_public_view,
    confirm_section_completion,
    create_assignment_submission,
    generate_certification,
    list_my_certifications,
    create_quiz_attempt_submission,
    question_public_view,
    serialize_submission,
)
from .store import (
    get_assignment,
    get_learning_plan,
    get_lesson,
    get_quiz,
    get_section,
    list_assignment_submissions,
    mark_lesson_watched,
    mark_stage2_completed,
)


router = Router()


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


@router.post("/sections/{section_id}/confirm")
def confirm_section(section_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    section = get_section(section_id)
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    user_id = str(payload.get("user_id", "me"))
    completion, validation = confirm_section_completion(user_id=user_id, section=section)
    if completion is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Section requirements are not met: "
                f"missing_mandatory_lessons={validation['missing_mandatory_lessons']}, "
                f"missing_passed_quizzes={validation['missing_passed_quizzes']}, "
                f"missing_assignments_at_least_80={validation['missing_assignments_at_least_80']}"
            ),
        )

    return {
        "id": completion.id,
        "user_id": completion.user_id,
        "section_id": completion.section_id,
        "completed_at": completion.completed_at.isoformat(),
    }


@router.get("/certifications/my")
def my_certifications(user_id: str = "me") -> list[dict[str, Any]]:
    return list_my_certifications(user_id=user_id)


@router.post("/certifications/generate")
def create_certification(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    user_name = str(payload.get("name", user_id))
    plan_id = int(payload.get("plan_id", 1))

    plan = get_learning_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    certification, checks = generate_certification(user_id=user_id, user_name=user_name, plan=plan)
    if certification is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Certification requirements are not met: "
                f"all_sections_completed={checks['all_sections_completed']}, "
                f"stage2_completed={checks['stage2_completed']}"
            ),
        )

    return {
        "id": certification.id,
        "user_id": certification.user_id,
        "plan_id": certification.plan_id,
        "certificate_url": certification.certificate_url,
        "certificate_text": certification.certificate_text,
        "badge_awarded": "Certified",
        "created_at": certification.created_at.isoformat(),
    }


@router.post("/lessons/{lesson_id}/watch")
def watch_lesson(lesson_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    user_id = str(payload.get("user_id", "me"))
    mark_lesson_watched(user_id=user_id, lesson_id=lesson_id)
    return {"user_id": user_id, "lesson_id": lesson_id, "watched": True}


@router.post("/stage2/complete")
def complete_stage2(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    mark_stage2_completed(user_id)
    return {"user_id": user_id, "stage2_completed": True}
