from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any, Literal


QuestionType = Literal["mc", "true_false", "short_answer"]
SubmissionKind = Literal["quiz", "assignment"]
SubmissionStatus = Literal["pending_review", "graded"]
Stage2EnrollmentStatus = Literal["pending", "active", "rejected"]


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
class LabPartner:
    id: int
    name: str
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Stage2Task:
    id: int
    title: str
    description: str = ""
    plan_key: str = "default"
    is_active: bool = True
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Stage2Enrollment:
    id: int
    user_id: str
    lab_partner_id: int
    plan_key: str = "default"
    status: Stage2EnrollmentStatus = "pending"
    stage3_unlocked: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Stage2TaskEvaluation:
    id: int
    user_id: str
    task_id: int
    score: float
    comments: str = ""
    submitted_by: str = "admin"
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Stage2FinalRating:
    id: int
    user_id: str
    overall_score: float
    approved: bool
    comments: str = ""
    submitted_by: str = "admin"
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


quizzes: dict[int, Quiz] = {}
assignments: dict[int, Assignment] = {}
submissions: dict[int, Submission] = {}
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
lab_partners: dict[int, LabPartner] = {}
stage2_tasks: dict[int, Stage2Task] = {}
stage2_enrollments: dict[str, Stage2Enrollment] = {}
stage2_task_evaluations: dict[int, Stage2TaskEvaluation] = {}
stage2_final_ratings: dict[str, Stage2FinalRating] = {}

_submission_ids = count(1)
_lab_partner_ids = count(1)
_stage2_task_ids = count(1)
_stage2_enrollment_ids = count(1)
_stage2_task_evaluation_ids = count(1)
_stage2_final_rating_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def next_lab_partner_id() -> int:
    return next(_lab_partner_ids)


def next_stage2_task_id() -> int:
    return next(_stage2_task_ids)


def next_stage2_enrollment_id() -> int:
    return next(_stage2_enrollment_ids)


def next_stage2_task_evaluation_id() -> int:
    return next(_stage2_task_evaluation_ids)


def next_stage2_final_rating_id() -> int:
    return next(_stage2_final_rating_ids)


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


def get_lab_partner(lab_partner_id: int) -> LabPartner | None:
    return lab_partners.get(lab_partner_id)


def save_lab_partner(lab_partner: LabPartner) -> LabPartner:
    lab_partner.updated_at = utcnow()
    lab_partners[lab_partner.id] = lab_partner
    return lab_partner


def list_lab_partners(*, active_only: bool = False) -> list[LabPartner]:
    partners = list(lab_partners.values())
    if active_only:
        partners = [partner for partner in partners if partner.is_active]
    return sorted(partners, key=lambda partner: partner.id)


def get_stage2_task(task_id: int) -> Stage2Task | None:
    return stage2_tasks.get(task_id)


def save_stage2_task(task: Stage2Task) -> Stage2Task:
    task.updated_at = utcnow()
    stage2_tasks[task.id] = task
    return task


def list_stage2_tasks(*, plan_key: str | None = None, active_only: bool = True) -> list[Stage2Task]:
    tasks = list(stage2_tasks.values())
    if plan_key is not None:
        tasks = [task for task in tasks if task.plan_key == plan_key]
    if active_only:
        tasks = [task for task in tasks if task.is_active]
    return sorted(tasks, key=lambda task: task.id)


def get_stage2_enrollment(user_id: str) -> Stage2Enrollment | None:
    return stage2_enrollments.get(user_id)


def save_stage2_enrollment(enrollment: Stage2Enrollment) -> Stage2Enrollment:
    enrollment.updated_at = utcnow()
    stage2_enrollments[enrollment.user_id] = enrollment
    return enrollment


def get_stage2_task_evaluation(user_id: str, task_id: int) -> Stage2TaskEvaluation | None:
    for evaluation in stage2_task_evaluations.values():
        if evaluation.user_id == user_id and evaluation.task_id == task_id:
            return evaluation
    return None


def save_stage2_task_evaluation(evaluation: Stage2TaskEvaluation) -> Stage2TaskEvaluation:
    evaluation.updated_at = utcnow()
    stage2_task_evaluations[evaluation.id] = evaluation
    return evaluation


def list_stage2_task_evaluations(*, user_id: str | None = None, task_id: int | None = None) -> list[Stage2TaskEvaluation]:
    evaluations = list(stage2_task_evaluations.values())
    if user_id is not None:
        evaluations = [evaluation for evaluation in evaluations if evaluation.user_id == user_id]
    if task_id is not None:
        evaluations = [evaluation for evaluation in evaluations if evaluation.task_id == task_id]
    return sorted(evaluations, key=lambda evaluation: evaluation.created_at, reverse=True)


def get_stage2_final_rating(user_id: str) -> Stage2FinalRating | None:
    return stage2_final_ratings.get(user_id)


def save_stage2_final_rating(final_rating: Stage2FinalRating) -> Stage2FinalRating:
    final_rating.updated_at = utcnow()
    stage2_final_ratings[final_rating.user_id] = final_rating
    return final_rating


def list_stage2_final_ratings() -> list[Stage2FinalRating]:
    return sorted(stage2_final_ratings.values(), key=lambda final_rating: final_rating.created_at, reverse=True)


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


def seed_stage2_data() -> None:
    if lab_partners:
        return

    partner_1 = LabPartner(
        id=next_lab_partner_id(),
        name="Nano Research Hub",
        description="Applied nanotech projects and mentorship.",
        is_active=True,
    )
    partner_2 = LabPartner(
        id=next_lab_partner_id(),
        name="Quantum Bio Labs",
        description="Interdisciplinary lab with biology and data tracks.",
        is_active=True,
    )
    save_lab_partner(partner_1)
    save_lab_partner(partner_2)

    save_stage2_task(
        Stage2Task(
            id=next_stage2_task_id(),
            title="Environment Setup",
            description="Set up tools and submit proof of environment readiness.",
            plan_key="default",
            is_active=True,
        )
    )
    save_stage2_task(
        Stage2Task(
            id=next_stage2_task_id(),
            title="Mentored Experiment",
            description="Deliver one supervised experiment report.",
            plan_key="default",
            is_active=True,
        )
    )
    save_stage2_task(
        Stage2Task(
            id=next_stage2_task_id(),
            title="Research Summary",
            description="Present findings from mentor sessions.",
            plan_key="research",
            is_active=True,
        )
    )


seed_data()
seed_stage2_data()
