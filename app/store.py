from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any, Literal


QuestionType = Literal["mc", "true_false", "short_answer"]
SubmissionKind = Literal["quiz", "assignment"]
SubmissionStatus = Literal["pending_review", "graded"]


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
class Lesson:
    id: int
    title: str
    notes_pdf_url: str


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


quizzes: dict[int, Quiz] = {}
assignments: dict[int, Assignment] = {}
submissions: dict[int, Submission] = {}
lessons: dict[int, Lesson] = {}
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
download_logs: list[dict[str, Any]] = []

_submission_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def add_xp(user_id: str, amount: int) -> int:
    user_xp[user_id] = user_xp.get(user_id, 0) + amount
    return user_xp[user_id]


def get_quiz(quiz_id: int) -> Quiz | None:
    return quizzes.get(quiz_id)


def get_assignment(assignment_id: int) -> Assignment | None:
    return assignments.get(assignment_id)


def get_submission(submission_id: int) -> Submission | None:
    return submissions.get(submission_id)


def get_lesson(lesson_id: int) -> Lesson | None:
    return lessons.get(lesson_id)


def log_notes_download(*, lesson_id: int, user_id: str, notes_url: str) -> None:
    download_logs.append(
        {
            "lesson_id": lesson_id,
            "user_id": user_id,
            "notes_url": notes_url,
            "downloaded_at": utcnow(),
        }
    )


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


def seed_data() -> None:
    if quizzes or assignments or lessons:
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

    lessons[1] = Lesson(
        id=1,
        title="Lesson 1: Nano Lab Orientation",
        notes_pdf_url="http://localhost:8000/static/notes/lesson-1.pdf",
    )


seed_data()
