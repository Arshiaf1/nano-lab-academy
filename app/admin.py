from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router
from .services import (
    finalize_grade,
    serialize_lab_partner,
    serialize_stage2_enrollment,
    serialize_stage2_final_rating,
    serialize_stage2_task,
    serialize_stage2_task_evaluation,
    serialize_submission,
    unlock_stage3_if_qualified,
)
from .store import (
    LabPartner,
    Stage2FinalRating,
    Stage2Task,
    Stage2TaskEvaluation,
    get_submission,
    get_stage2_enrollment,
    get_stage2_final_rating,
    get_stage2_task,
    get_stage2_task_evaluation,
    list_lab_partners,
    list_pending_submissions,
    list_stage2_final_ratings,
    list_stage2_task_evaluations,
    list_stage2_tasks,
    next_lab_partner_id,
    next_stage2_final_rating_id,
    next_stage2_task_id,
    next_stage2_task_evaluation_id,
    save_lab_partner,
    save_stage2_final_rating,
    save_stage2_task,
    save_stage2_task_evaluation,
)


router = Router(prefix="/admin")


@router.get("/submissions/pending")
def get_pending_submissions() -> list[dict[str, Any]]:
    return [serialize_submission(submission) for submission in list_pending_submissions()]


@router.post("/submissions/{submission_id}/grade")
def grade_submission(submission_id: int, payload: dict[str, Any]) -> dict[str, Any]:
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


@router.get("/lab-partners")
def get_admin_lab_partners() -> list[dict[str, Any]]:
    return [serialize_lab_partner(partner) for partner in list_lab_partners(active_only=False)]


@router.post("/lab-partners")
def create_lab_partner(payload: dict[str, Any]) -> dict[str, Any]:
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    partner = LabPartner(
        id=next_lab_partner_id(),
        name=name,
        description=str(payload.get("description", "")),
        is_active=bool(payload.get("is_active", True)),
    )
    saved = save_lab_partner(partner)
    return {"lab_partner": serialize_lab_partner(saved)}


@router.post("/lab-partners/{lab_partner_id}/status")
def update_lab_partner_status(lab_partner_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    from .store import get_lab_partner

    partner = get_lab_partner(lab_partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Lab partner not found")

    if "is_active" not in payload or not isinstance(payload["is_active"], bool):
        raise HTTPException(status_code=400, detail="is_active must be a boolean")

    partner.is_active = payload["is_active"]
    saved = save_lab_partner(partner)
    return {"lab_partner": serialize_lab_partner(saved)}


@router.get("/stage2/tasks")
def get_stage2_tasks_admin(plan_key: str | None = None) -> list[dict[str, Any]]:
    active_only = False
    tasks = list_stage2_tasks(plan_key=plan_key, active_only=active_only)
    return [serialize_stage2_task(task) for task in tasks]


@router.post("/stage2/tasks")
def create_stage2_task(payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    task = Stage2Task(
        id=next_stage2_task_id(),
        title=title,
        description=str(payload.get("description", "")),
        plan_key=str(payload.get("plan_key", "default")),
        is_active=bool(payload.get("is_active", True)),
    )
    saved = save_stage2_task(task)
    return {"task": serialize_stage2_task(saved)}


@router.post("/stage2/tasks/{task_id}/status")
def update_stage2_task_status(task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    task = get_stage2_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if "is_active" not in payload or not isinstance(payload["is_active"], bool):
        raise HTTPException(status_code=400, detail="is_active must be a boolean")
    task.is_active = payload["is_active"]
    saved = save_stage2_task(task)
    return {"task": serialize_stage2_task(saved)}


@router.get("/stage2/evaluations")
def get_stage2_evaluations(user_id: str | None = None) -> dict[str, Any]:
    task_evaluations = list_stage2_task_evaluations(user_id=user_id)
    final_ratings = list_stage2_final_ratings()
    if user_id is not None:
        final_ratings = [final_rating for final_rating in final_ratings if final_rating.user_id == user_id]
    return {
        "task_evaluations": [serialize_stage2_task_evaluation(evaluation) for evaluation in task_evaluations],
        "final_ratings": [serialize_stage2_final_rating(final_rating) for final_rating in final_ratings],
    }


@router.post("/stage2/tasks/{task_id}/evaluate")
def evaluate_stage2_task(task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    task = get_stage2_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    user_id = str(payload.get("user_id", "me"))
    enrollment = get_stage2_enrollment(user_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Stage 2 enrollment not found")
    if task.plan_key != enrollment.plan_key:
        raise HTTPException(status_code=400, detail="Task does not belong to this user's plan")

    if "score" not in payload:
        raise HTTPException(status_code=400, detail="score is required")
    try:
        score = float(payload["score"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="score must be a number") from exc
    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="score must be between 0 and 100")

    comments = str(payload.get("comments", ""))
    submitted_by = str(payload.get("submitted_by", "admin"))
    evaluation = get_stage2_task_evaluation(user_id, task_id)
    if evaluation is None:
        evaluation = Stage2TaskEvaluation(
            id=next_stage2_task_evaluation_id(),
            user_id=user_id,
            task_id=task_id,
            score=score,
            comments=comments,
            submitted_by=submitted_by,
        )
    else:
        evaluation.score = score
        evaluation.comments = comments
        evaluation.submitted_by = submitted_by
    saved = save_stage2_task_evaluation(evaluation)
    return {
        "evaluation": serialize_stage2_task_evaluation(saved),
        "enrollment": serialize_stage2_enrollment(enrollment),
    }


@router.post("/stage2/final-rating")
def submit_stage2_final_rating_admin(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    enrollment = get_stage2_enrollment(user_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Stage 2 enrollment not found")

    if "overall_score" not in payload:
        raise HTTPException(status_code=400, detail="overall_score is required")
    if "approved" not in payload:
        raise HTTPException(status_code=400, detail="approved is required")

    try:
        overall_score = float(payload["overall_score"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="overall_score must be a number") from exc
    if overall_score < 0 or overall_score > 100:
        raise HTTPException(status_code=400, detail="overall_score must be between 0 and 100")

    approved = payload["approved"]
    if not isinstance(approved, bool):
        raise HTTPException(status_code=400, detail="approved must be a boolean")

    comments = str(payload.get("comments", ""))
    submitted_by = str(payload.get("submitted_by", "admin"))
    final_rating = get_stage2_final_rating(user_id)
    if final_rating is None:
        final_rating = Stage2FinalRating(
            id=next_stage2_final_rating_id(),
            user_id=user_id,
            overall_score=overall_score,
            approved=approved,
            comments=comments,
            submitted_by=submitted_by,
        )
    else:
        final_rating.overall_score = overall_score
        final_rating.approved = approved
        final_rating.comments = comments
        final_rating.submitted_by = submitted_by
    saved = save_stage2_final_rating(final_rating)
    stage3_unlocked = unlock_stage3_if_qualified(user_id) if approved and overall_score >= 80 else False
    return {
        "final_rating": serialize_stage2_final_rating(saved),
        "stage3_unlocked": stage3_unlocked,
        "enrollment": serialize_stage2_enrollment(enrollment),
    }
