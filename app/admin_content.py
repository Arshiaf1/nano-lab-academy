from __future__ import annotations

from typing import Any

from .auth import require_admin
from .framework import HTTPException, Router
from .framework import Request

from .services import finalize_grade, serialize_submission
from .store import evaluate_stage2, get_submission, list_pending_submissions


router = Router(prefix="/admin")


@router.get("/submissions/pending")
def get_pending_submissions(request: Request) -> list[dict[str, Any]]:
    require_admin(request)
    return [serialize_submission(submission) for submission in list_pending_submissions()]


@router.post("/submissions/{submission_id}/grade")
def grade_submission(submission_id: int, payload: dict[str, Any], request: Request) -> dict[str, Any]:
    require_admin(request)
    submission = get_submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    if "score" not in payload:
        raise HTTPException(status_code=400, detail="score is required")

    try:
        score = float(payload["score"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="score must be a number") from exc

    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="score must be between 0 and 100")

    graded_submission = finalize_grade(submission, score)
    return {
        "submission_id": graded_submission.id,
        "kind": graded_submission.kind,
        "score": graded_submission.score,
        "passed": graded_submission.passed,
        "xp_awarded": graded_submission.xp_awarded,
        "badge_ids": graded_submission.badge_ids,
        "submission": serialize_submission(graded_submission),
    }


@router.post("/stage2/evaluate")
def evaluate_stage2_enrollment(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    require_admin(request)
    user_id = str(payload.get("user_id", "me"))

    try:
        score = float(payload.get("score", 0))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="score must be a number") from exc

    approved = bool(payload.get("approved", score >= 80))
    evaluation = evaluate_stage2(
        user_id,
        score=score,
        approved=approved,
        evaluator=str(payload.get("evaluator", "admin")),
        comments=str(payload.get("comments", "")),
    )
    return {
        "evaluation": evaluation,
    }
