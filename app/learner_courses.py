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
from .store import get_assignment, get_lesson, get_quiz, list_assignment_submissions, log_notes_download


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


@router.get("/lessons/{lesson_id}/download-notes")
def download_lesson_notes(lesson_id: int, user_id: str = "") -> dict[str, Any]:
    if not user_id.strip():
        raise HTTPException(status_code=401, detail="Authentication required")

    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # TODO: Replace with S3 presigned URL generation when object storage is enabled.
    download_url = f"{lesson.notes_pdf_url}?user={user_id}"
    log_notes_download(lesson_id=lesson.id, user_id=user_id, notes_url=download_url)
    return {"lesson_id": lesson.id, "download_url": download_url}


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
