from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .framework import HTTPException, Router
from .store import (
    JobApplication,
    JobListing,
    get_job_application,
    get_job_listing,
    get_user_badges,
    list_job_applications,
    list_job_listings,
    next_job_application_id,
    next_job_listing_id,
    save_job_application,
    save_job_listing,
    delete_job_listing,
)


router = Router()
ADMIN_APPLICATION_STATUSES = {"pending", "reviewing", "accepted", "rejected"}
JOB_TYPES = {"internship", "job"}


def _serialize_job(job_listing: JobListing) -> dict[str, Any]:
    data = asdict(job_listing)
    data["created_at"] = job_listing.created_at.isoformat()
    data["updated_at"] = job_listing.updated_at.isoformat()
    return data


def _serialize_application(application: JobApplication) -> dict[str, Any]:
    data = asdict(application)
    data["applied_at"] = application.applied_at.isoformat()
    data["updated_at"] = application.updated_at.isoformat()
    return data


def _normalize_badges(raw_badges: Any) -> list[str]:
    if raw_badges is None:
        return []
    if isinstance(raw_badges, str):
        values = [part.strip() for part in raw_badges.split(",")]
        return [badge for badge in values if badge]
    if isinstance(raw_badges, list):
        badges: list[str] = []
        for item in raw_badges:
            badge = str(item).strip()
            if badge:
                badges.append(badge)
        return badges
    raise HTTPException(status_code=400, detail="required_badges must be a list or comma-separated string")


def _require_job(job_id: int, *, active_only: bool = False) -> JobListing:
    job = get_job_listing(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if active_only and not job.is_active:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def _validate_job_type(job_type: str) -> str:
    normalized = job_type.strip().lower()
    if normalized not in JOB_TYPES:
        raise HTTPException(status_code=400, detail="type must be internship or job")
    return normalized


def _parse_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
    raise HTTPException(status_code=400, detail=f"{field_name} must be a boolean")


@router.get("/jobs")
def list_jobs(required_badges: str | None = None) -> list[dict[str, Any]]:
    filters = set(_normalize_badges(required_badges))
    jobs = list_job_listings(active_only=True)
    if filters:
        jobs = [job for job in jobs if filters.issubset(set(job.required_badges))]
    return [_serialize_job(job) for job in jobs]


@router.get("/jobs/{job_id}")
def job_details(job_id: int) -> dict[str, Any]:
    job = _require_job(job_id, active_only=True)
    return _serialize_job(job)


@router.post("/jobs/{job_id}/apply")
def apply_to_job(job_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    job = _require_job(job_id, active_only=True)
    user_id = str(payload.get("user_id", "me"))
    cover_letter = payload.get("cover_letter")

    missing_badges = [badge for badge in job.required_badges if badge not in get_user_badges(user_id)]
    if missing_badges:
        raise HTTPException(status_code=400, detail=f"Missing required badges: {', '.join(missing_badges)}")

    for existing in list_job_applications(user_id=user_id, job_id=job_id):
        if existing.user_id == user_id and existing.job_id == job_id:
            raise HTTPException(status_code=409, detail="You have already applied for this job")

    application = save_job_application(
        JobApplication(
            id=next_job_application_id(),
            user_id=user_id,
            job_id=job_id,
            cover_letter=None if cover_letter is None else str(cover_letter),
        )
    )
    return {"application_id": application.id, "status": application.status, "application": _serialize_application(application)}


@router.get("/applications/my")
def my_applications(user_id: str = "me") -> list[dict[str, Any]]:
    return [_serialize_application(application) for application in list_job_applications(user_id=user_id)]


@router.get("/admin/jobs")
def admin_list_jobs() -> list[dict[str, Any]]:
    return [_serialize_job(job) for job in list_job_listings(active_only=False)]


@router.post("/admin/jobs")
def admin_create_job(payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    if not description:
        raise HTTPException(status_code=400, detail="description is required")

    job = save_job_listing(
        JobListing(
            id=next_job_listing_id(),
            employer_id=str(payload.get("employer_id", "admin")),
            title=title,
            description=description,
            required_badges=_normalize_badges(payload.get("required_badges")),
            location=str(payload.get("location", "")).strip(),
            type=_validate_job_type(str(payload.get("type", "job"))),
            is_active=_parse_bool(payload.get("is_active", True), field_name="is_active"),
        )
    )
    return _serialize_job(job)


@router.get("/admin/jobs/{job_id}")
def admin_job_details(job_id: int) -> dict[str, Any]:
    return _serialize_job(_require_job(job_id))


@router.post("/admin/jobs/{job_id}")
def admin_update_job(job_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    job = _require_job(job_id)

    if "title" in payload:
        title = str(payload["title"]).strip()
        if not title:
            raise HTTPException(status_code=400, detail="title cannot be empty")
        job.title = title
    if "description" in payload:
        description = str(payload["description"]).strip()
        if not description:
            raise HTTPException(status_code=400, detail="description cannot be empty")
        job.description = description
    if "required_badges" in payload:
        job.required_badges = _normalize_badges(payload["required_badges"])
    if "location" in payload:
        job.location = str(payload["location"]).strip()
    if "type" in payload:
        job.type = _validate_job_type(str(payload["type"]))
    if "is_active" in payload:
        job.is_active = _parse_bool(payload["is_active"], field_name="is_active")

    return _serialize_job(save_job_listing(job))


@router.post("/admin/jobs/{job_id}/delete")
def admin_delete_job(job_id: int) -> dict[str, Any]:
    if not delete_job_listing(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"deleted": True}


@router.get("/admin/jobs/{job_id}/applications")
def admin_job_applications(job_id: int) -> list[dict[str, Any]]:
    _require_job(job_id)
    return [_serialize_application(application) for application in list_job_applications(job_id=job_id)]


@router.get("/admin/applications")
def admin_all_applications() -> list[dict[str, Any]]:
    return [_serialize_application(application) for application in list_job_applications()]


@router.post("/admin/applications/{application_id}/status")
def admin_update_application_status(application_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    application = get_job_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    status = str(payload.get("status", "")).strip().lower()
    if status not in ADMIN_APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail="status must be pending, reviewing, accepted, or rejected")

    application.status = status
    return _serialize_application(save_job_application(application))
