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
    complete_lesson,
    enrollment_summary,
    enroll_user,
    gamification_status,
    get_assignment,
    get_lesson,
    get_quiz,
    lesson_summary,
    list_assignment_submissions,
)


router = Router()


@router.get("/enrollments/my")
def my_enrollment(user_id: str = "me") -> dict[str, Any]:
    return enrollment_summary(user_id)


@router.post("/enrollments/enroll")
def enroll(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    plan_tier = str(payload.get("plan_tier", "free"))
    if plan_tier not in {"free", "pro"}:
        raise HTTPException(status_code=400, detail="plan_tier must be free or pro")

    enroll_user(user_id=user_id, plan_tier=plan_tier)
    return enrollment_summary(user_id)


@router.get("/courses/tree")
def course_tree(user_id: str = "me") -> dict[str, Any]:
    return enrollment_summary(user_id)


@router.get("/gamification/status")
def my_gamification_status(user_id: str = "me") -> dict[str, Any]:
    return gamification_status(user_id)


@router.post("/lessons/{lesson_id}/complete")
def mark_lesson_complete(lesson_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    completion = complete_lesson(user_id, lesson_id)
    return {
        "completion": completion,
        "lesson": lesson_summary(lesson_id, user_id),
        "gamification": gamification_status(user_id),
    }


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
