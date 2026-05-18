from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from itertools import count
from typing import Any, Literal


QuestionType = Literal["mc", "true_false", "short_answer"]
SubmissionKind = Literal["quiz", "assignment"]
SubmissionStatus = Literal["pending_review", "graded"]
PaymentStatus = Literal["initiated", "paid", "failed"]


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
class UserAccount:
    id: str
    plan_id: str | None = None
    plan_active_until: datetime | None = None
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Enrollment:
    id: int
    user_id: str
    stage1_locked: bool = True
    stage1_deadline: datetime | None = None
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Payment:
    id: int
    user_id: str
    amount: int
    currency: str
    payment_gateway_ref: str
    status: PaymentStatus
    plan_id: str | None = None
    for_stage_unlock: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    paid_at: datetime | None = None


quizzes: dict[int, Quiz] = {}
assignments: dict[int, Assignment] = {}
submissions: dict[int, Submission] = {}
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
users: dict[str, UserAccount] = {}
enrollments: dict[int, Enrollment] = {}
payments: dict[int, Payment] = {}

_submission_ids = count(1)
_enrollment_ids = count(1)
_payment_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def next_payment_id() -> int:
    return next(_payment_ids)


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


def get_or_create_user(user_id: str) -> UserAccount:
    if user_id not in users:
        users[user_id] = UserAccount(id=user_id)
    return users[user_id]


def get_latest_enrollment(user_id: str) -> Enrollment | None:
    user_enrollments = [enrollment for enrollment in enrollments.values() if enrollment.user_id == user_id]
    if not user_enrollments:
        return None
    return max(user_enrollments, key=lambda enrollment: enrollment.id)


def create_payment(
    *,
    user_id: str,
    amount: int,
    currency: str,
    plan_id: str | None,
    for_stage_unlock: bool,
) -> Payment:
    payment_id = next_payment_id()
    payment = Payment(
        id=payment_id,
        user_id=user_id,
        amount=amount,
        currency=currency,
        payment_gateway_ref=f"pay_{payment_id}",
        status="initiated",
        plan_id=plan_id,
        for_stage_unlock=for_stage_unlock,
    )
    payments[payment.id] = payment
    get_or_create_user(user_id)
    return payment


def get_payment(payment_id: int) -> Payment | None:
    return payments.get(payment_id)


def get_payment_by_ref(payment_gateway_ref: str) -> Payment | None:
    for payment in payments.values():
        if payment.payment_gateway_ref == payment_gateway_ref:
            return payment
    return None


def mark_payment_paid(payment: Payment) -> Payment:
    payment.status = "paid"
    payment.paid_at = utcnow()
    payment.updated_at = utcnow()
    payments[payment.id] = payment
    return payment


def activate_user_plan(user_id: str, plan_id: str) -> UserAccount:
    user = get_or_create_user(user_id)
    user.plan_id = plan_id
    user.plan_active_until = utcnow() + timedelta(days=30)
    user.updated_at = utcnow()
    users[user.id] = user
    return user


def unlock_stage1_for_user(user_id: str) -> Enrollment | None:
    enrollment = get_latest_enrollment(user_id)
    if enrollment is None:
        return None
    now = utcnow()
    base_deadline = enrollment.stage1_deadline if enrollment.stage1_deadline and enrollment.stage1_deadline > now else now
    enrollment.stage1_locked = False
    enrollment.stage1_deadline = base_deadline + timedelta(days=30)
    enrollment.updated_at = now
    enrollments[enrollment.id] = enrollment
    return enrollment


def list_all_payments() -> list[Payment]:
    return sorted(payments.values(), key=lambda payment: payment.created_at, reverse=True)


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

    if "me" not in users:
        users["me"] = UserAccount(id="me")

    if not enrollments:
        enrollment_id = next(_enrollment_ids)
        enrollments[enrollment_id] = Enrollment(
            id=enrollment_id,
            user_id="me",
            stage1_locked=True,
            stage1_deadline=utcnow() + timedelta(days=90),
        )


seed_data()
