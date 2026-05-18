from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router
from .services import (
    serialize_lab_partner,
    serialize_stage2_enrollment,
    serialize_stage2_final_rating,
    serialize_stage2_task,
    serialize_stage2_task_evaluation,
    unlock_stage3_if_qualified,
)
from .store import (
    Stage2Enrollment,
    Stage2FinalRating,
    Stage2TaskEvaluation,
    get_lab_partner,
    get_stage2_enrollment,
    get_stage2_final_rating,
    get_stage2_task,
    get_stage2_task_evaluation,
    list_lab_partners,
    list_stage2_task_evaluations,
    list_stage2_tasks,
    next_stage2_enrollment_id,
    next_stage2_final_rating_id,
    next_stage2_task_evaluation_id,
    save_stage2_enrollment,
    save_stage2_final_rating,
    save_stage2_task_evaluation,
)


router = Router(prefix="/stage2")


def _is_admin(payload: dict[str, Any]) -> bool:
    actor_role = str(payload.get("actor_role", "admin")).strip().lower()
    return actor_role == "admin"


@router.get("/lab-partners")
def get_stage2_lab_partners() -> list[dict[str, Any]]:
    return [serialize_lab_partner(partner) for partner in list_lab_partners(active_only=True)]


@router.post("/enroll")
def enroll_stage2(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    if "lab_partner_id" not in payload:
        raise HTTPException(status_code=400, detail="lab_partner_id is required")

    try:
        lab_partner_id = int(payload["lab_partner_id"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="lab_partner_id must be an integer") from exc

    lab_partner = get_lab_partner(lab_partner_id)
    if lab_partner is None:
        raise HTTPException(status_code=404, detail="Lab partner not found")
    if not lab_partner.is_active:
        raise HTTPException(status_code=400, detail="Lab partner is not active")

    enrollment = get_stage2_enrollment(user_id)
    if enrollment is None:
        enrollment = Stage2Enrollment(
            id=next_stage2_enrollment_id(),
            user_id=user_id,
            lab_partner_id=lab_partner_id,
            plan_key=str(payload.get("plan_key", "default")),
            status="pending",
            stage3_unlocked=False,
        )
    else:
        enrollment.lab_partner_id = lab_partner_id
        enrollment.plan_key = str(payload.get("plan_key", enrollment.plan_key))
        enrollment.status = "pending"

    # MVP behavior: auto-activate immediately.
    enrollment.status = "active"
    saved = save_stage2_enrollment(enrollment)
    return {"enrollment": serialize_stage2_enrollment(saved)}


@router.get("/my-status")
def my_stage2_status(user_id: str = "me") -> dict[str, Any]:
    enrollment = get_stage2_enrollment(user_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Stage 2 enrollment not found")

    tasks = list_stage2_tasks(plan_key=enrollment.plan_key, active_only=True)
    task_evaluations = list_stage2_task_evaluations(user_id=user_id)
    final_rating = get_stage2_final_rating(user_id)
    return {
        "enrollment": serialize_stage2_enrollment(enrollment),
        "stage2_tasks": [serialize_stage2_task(task) for task in tasks],
        "evaluations": {
            "task_evaluations": [serialize_stage2_task_evaluation(evaluation) for evaluation in task_evaluations],
            "final_rating": serialize_stage2_final_rating(final_rating) if final_rating else None,
        },
    }


@router.post("/tasks/{task_id}/submit")
def submit_stage2_task(task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_admin(payload):
        raise HTTPException(status_code=403, detail="Only admin can submit task evaluations")

    task = get_stage2_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Stage 2 task not found")

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
    return {"evaluation": serialize_stage2_task_evaluation(saved)}


@router.post("/final-rating")
def submit_final_stage2_rating(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_admin(payload):
        raise HTTPException(status_code=403, detail="Only admin can submit final rating")

    user_id = str(payload.get("user_id", "me"))
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

    saved_final_rating = save_stage2_final_rating(final_rating)
    stage3_unlocked = unlock_stage3_if_qualified(user_id) if approved and overall_score >= 80 else False
    return {
        "final_rating": serialize_stage2_final_rating(saved_final_rating),
        "stage3_unlocked": stage3_unlocked,
    }
