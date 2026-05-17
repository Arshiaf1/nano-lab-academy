from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router

from .gamification import award_xp, check_and_award_badges, record_activity, update_streak
from .stage import enforce_stage1_access, record_exam_attempt
from .services import (
    assignment_public_view,
    create_assignment_submission,
    create_quiz_attempt_submission,
    question_public_view,
    serialize_submission,
)
from .store import get_assignment, get_quiz, list_assignment_submissions


router = Router()


@router.get("/quizzes/{quiz_id}")
def get_quiz_details(quiz_id: int, user_id: str = "me") -> dict[str, Any]:
    enforce_stage1_access(user_id, "/quizzes/{quiz_id}")
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
    enforce_stage1_access(user_id, "/quizzes/{quiz_id}/attempt")
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
    enforce_stage1_access(user_id, "/assignments/my")
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
def get_assignment_details(assignment_id: int, user_id: str = "me") -> dict[str, Any]:
    enforce_stage1_access(user_id, "/assignments/{assignment_id}")
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
    enforce_stage1_access(user_id, "/assignments/{assignment_id}/submit")
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
        "badge_ids": submission.badge_ids,
        "submission": serialize_submission(submission),
    }


@router.post("/lessons/{lesson_id}/progress")
def update_lesson_progress(lesson_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    enforce_stage1_access(user_id, "/lessons/{lesson_id}/progress")
    completed_raw = payload.get("completed", True)
    if not isinstance(completed_raw, bool):
        raise HTTPException(status_code=400, detail="completed must be a boolean")

    xp_awarded = 0
    if completed_raw:
        xp_awarded = 10
        award_xp(user_id, xp_awarded, "lesson_progress")

    current_streak = update_streak(user_id)
    record_activity(
        user_id,
        event_type="lesson_progress",
        source="lesson",
        score=100.0 if completed_raw else None,
        passed=completed_raw,
    )
    badge_ids = check_and_award_badges(user_id)

    return {
        "lesson_id": lesson_id,
        "user_id": user_id,
        "completed": completed_raw,
        "xp_awarded": xp_awarded,
        "current_streak": current_streak,
        "badge_ids": badge_ids,
    }


@router.post("/exams/{exam_id}/attempt")
def submit_exam_attempt(exam_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    enforce_stage1_access(user_id, "/exams/{exam_id}/attempt")
    if "score" not in payload:
        raise HTTPException(status_code=400, detail="score is required")

    try:
        score = float(payload["score"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="score must be a number") from exc

    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="score must be between 0 and 100")

    record_exam_attempt(user_id, exam_id, score)
    return {
        "user_id": user_id,
        "exam_id": exam_id,
        "score": score,
        "passed": score >= 80,
    }
