from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any, Literal


QuestionType = Literal["mc", "true_false", "short_answer"]
SubmissionKind = Literal["quiz", "assignment"]
SubmissionStatus = Literal["pending_review", "graded"]
JobType = Literal["internship", "job"]
ApplicationStatus = Literal["pending", "reviewing", "accepted", "rejected"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class QuizQuestion:
    id: int
    prompt: str
    question_type: QuestionType
    correct_answer: Any
    options: list[str] = field(default_factory=list)
    explanation: str = ""
    points: float = 1.0


@dataclass(slots=True)
class Quiz:
    id: int
    title: str
    description: str = ""
    pass_threshold: float = 70.0
    questions: list[QuizQuestion] = field(default_factory=list)


@dataclass(slots=True)
class Assignment:
    id: int
    title: str
    description: str
    instructions: str = ""
    pass_threshold: float = 70.0


@dataclass(slots=True)
class Submission:
    id: int
    kind: SubmissionKind
    user_id: str
    related_id: int
    status: SubmissionStatus
    score: float | None = None
    passed: bool | None = None
    xp_awarded: int = 0
    manual_review_required: bool = False
    payload: dict[str, Any] = field(default_factory=dict)
    badge_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class JobListing:
    id: int
    employer_id: str
    title: str
    description: str
    required_badges: list[str] = field(default_factory=list)
    location: str = ""
    type: JobType = "job"
    is_active: bool = True
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class JobApplication:
    id: int
    user_id: str
    job_id: int
    cover_letter: str | None
    status: ApplicationStatus = "pending"
    applied_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


quizzes: dict[int, Quiz] = {}
assignments: dict[int, Assignment] = {}
submissions: dict[int, Submission] = {}
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
job_listings: dict[int, JobListing] = {}
job_applications: dict[int, JobApplication] = {}

_submission_ids = count(1)
_job_listing_ids = count(1)
_job_application_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def next_job_listing_id() -> int:
    return next(_job_listing_ids)


def next_job_application_id() -> int:
    return next(_job_application_ids)


def add_xp(user_id: str, amount: int) -> int:
    user_xp[user_id] = user_xp.get(user_id, 0) + amount
    return user_xp[user_id]


def get_quiz(quiz_id: int) -> Quiz | None:
    return quizzes.get(quiz_id)


def get_assignment(assignment_id: int) -> Assignment | None:
    return assignments.get(assignment_id)


def get_submission(submission_id: int) -> Submission | None:
    return submissions.get(submission_id)


def save_submission(submission: Submission) -> Submission:
    submissions[submission.id] = submission
    return submission


def get_job_listing(job_id: int) -> JobListing | None:
    return job_listings.get(job_id)


def save_job_listing(job_listing: JobListing) -> JobListing:
    job_listing.updated_at = utcnow()
    job_listings[job_listing.id] = job_listing
    return job_listing


def delete_job_listing(job_id: int) -> bool:
    deleted = job_listings.pop(job_id, None)
    return deleted is not None


def list_job_listings(*, active_only: bool = False) -> list[JobListing]:
    items = list(job_listings.values())
    if active_only:
        items = [job_listing for job_listing in items if job_listing.is_active]
    return sorted(items, key=lambda job_listing: job_listing.created_at, reverse=True)


def get_job_application(application_id: int) -> JobApplication | None:
    return job_applications.get(application_id)


def save_job_application(application: JobApplication) -> JobApplication:
    application.updated_at = utcnow()
    job_applications[application.id] = application
    return application


def list_job_applications(
    *,
    user_id: str | None = None,
    job_id: int | None = None,
) -> list[JobApplication]:
    items = list(job_applications.values())
    if user_id is not None:
        items = [application for application in items if application.user_id == user_id]
    if job_id is not None:
        items = [application for application in items if application.job_id == job_id]
    return sorted(items, key=lambda application: application.applied_at, reverse=True)


def get_user_badges(user_id: str) -> set[str]:
    return awarded_badges.get(user_id, set())


def list_assignment_submissions(user_id: str | None = None) -> list[Submission]:
    items = [submission for submission in submissions.values() if submission.kind == "assignment"]
    if user_id is not None:
        items = [submission for submission in items if submission.user_id == user_id]
    return sorted(items, key=lambda submission: submission.created_at, reverse=True)


def list_pending_submissions() -> list[Submission]:
    return sorted(
        [submission for submission in submissions.values() if submission.status == "pending_review"],
        key=lambda submission: submission.created_at,
    )


def seed_data() -> None:
    if quizzes or assignments:
        return

    quizzes[1] = Quiz(
        id=1,
        title="Intro to Nano Lab",
        description="A starter quiz for the academy platform.",
        pass_threshold=70.0,
        questions=[
            QuizQuestion(
                id=101,
                prompt="Which component runs the learning workflow?",
                question_type="mc",
                correct_answer="router",
                options=["router", "worksheet", "table", "theme"],
            ),
            QuizQuestion(
                id=102,
                prompt="True or false: assignments can be graded later by an admin.",
                question_type="true_false",
                correct_answer=True,
                options=["true", "false"],
            ),
            QuizQuestion(
                id=103,
                prompt="Name the review step used for open-ended responses.",
                question_type="short_answer",
                correct_answer="manual review",
            ),
        ],
    )

    assignments[1] = Assignment(
        id=1,
        title="Project Brief",
        description="Submit a short project brief for the course.",
        instructions="Upload a file URL or paste your response as text.",
        pass_threshold=70.0,
    )


def seed_stage3_data() -> None:
    if job_listings:
        return

    save_job_listing(
        JobListing(
            id=next_job_listing_id(),
            employer_id="lab-alpha",
            title="Junior Lab Intern",
            description="Entry-level internship for QA lab tasks.",
            required_badges=["quiz_pass"],
            location="Tehran",
            type="internship",
            is_active=True,
        )
    )
    save_job_listing(
        JobListing(
            id=next_job_listing_id(),
            employer_id="lab-beta",
            title="Lab Operator",
            description="Operate and maintain lab workflows.",
            required_badges=["quiz_pass", "assignment_pass"],
            location="Karaj",
            type="job",
            is_active=True,
        )
    )


seed_data()
seed_stage3_data()
