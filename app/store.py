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
    mandatory: bool = True


@dataclass(slots=True)
class Section:
    id: int
    plan_id: int
    title: str
    lesson_ids: list[int] = field(default_factory=list)
    quiz_ids: list[int] = field(default_factory=list)
    assignment_ids: list[int] = field(default_factory=list)


@dataclass(slots=True)
class LearningPlan:
    id: int
    name: str
    section_ids: list[int] = field(default_factory=list)


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
class SectionCompletion:
    id: int
    user_id: str
    section_id: int
    completed_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Certification:
    id: int
    user_id: str
    plan_id: int
    certificate_url: str
    certificate_text: str
    created_at: datetime = field(default_factory=utcnow)


quizzes: dict[int, Quiz] = {}
assignments: dict[int, Assignment] = {}
lessons: dict[int, Lesson] = {}
sections: dict[int, Section] = {}
learning_plans: dict[int, LearningPlan] = {}
submissions: dict[int, Submission] = {}
section_completions: dict[int, SectionCompletion] = {}
certifications: dict[int, Certification] = {}
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
user_watched_lessons: dict[str, set[int]] = {}
user_stage2_completed: set[str] = set()

_submission_ids = count(1)
_section_completion_ids = count(1)
_certification_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def next_section_completion_id() -> int:
    return next(_section_completion_ids)


def next_certification_id() -> int:
    return next(_certification_ids)


def add_xp(user_id: str, amount: int) -> int:
    user_xp[user_id] = user_xp.get(user_id, 0) + amount
    return user_xp[user_id]


def get_quiz(quiz_id: int) -> Quiz | None:
    return quizzes.get(quiz_id)


def get_assignment(assignment_id: int) -> Assignment | None:
    return assignments.get(assignment_id)


def get_lesson(lesson_id: int) -> Lesson | None:
    return lessons.get(lesson_id)


def get_section(section_id: int) -> Section | None:
    return sections.get(section_id)


def get_learning_plan(plan_id: int) -> LearningPlan | None:
    return learning_plans.get(plan_id)


def get_submission(submission_id: int) -> Submission | None:
    return submissions.get(submission_id)


def save_submission(submission: Submission) -> Submission:
    submissions[submission.id] = submission
    return submission


def save_section_completion(completion: SectionCompletion) -> SectionCompletion:
    section_completions[completion.id] = completion
    return completion


def get_section_completion_for_user(user_id: str, section_id: int) -> SectionCompletion | None:
    for completion in section_completions.values():
        if completion.user_id == user_id and completion.section_id == section_id:
            return completion
    return None


def list_section_completions(user_id: str | None = None) -> list[SectionCompletion]:
    items = list(section_completions.values())
    if user_id is not None:
        items = [completion for completion in items if completion.user_id == user_id]
    return sorted(items, key=lambda completion: completion.completed_at)


def save_certification(certification: Certification) -> Certification:
    certifications[certification.id] = certification
    return certification


def get_certification_for_user_plan(user_id: str, plan_id: int) -> Certification | None:
    for certification in certifications.values():
        if certification.user_id == user_id and certification.plan_id == plan_id:
            return certification
    return None


def list_certifications(user_id: str | None = None) -> list[Certification]:
    items = list(certifications.values())
    if user_id is not None:
        items = [certification for certification in items if certification.user_id == user_id]
    return sorted(items, key=lambda certification: certification.created_at, reverse=True)


def list_assignment_submissions(user_id: str | None = None) -> list[Submission]:
    items = [submission for submission in submissions.values() if submission.kind == "assignment"]
    if user_id is not None:
        items = [submission for submission in items if submission.user_id == user_id]
    return sorted(items, key=lambda submission: submission.created_at, reverse=True)


def list_submissions_for(user_id: str, kind: SubmissionKind, related_id: int) -> list[Submission]:
    items = [
        submission
        for submission in submissions.values()
        if submission.user_id == user_id and submission.kind == kind and submission.related_id == related_id
    ]
    return sorted(items, key=lambda submission: submission.created_at, reverse=True)


def list_pending_submissions() -> list[Submission]:
    return sorted(
        [submission for submission in submissions.values() if submission.status == "pending_review"],
        key=lambda submission: submission.created_at,
    )


def mark_lesson_watched(user_id: str, lesson_id: int) -> None:
    user_watched_lessons.setdefault(user_id, set()).add(lesson_id)


def watched_lessons(user_id: str) -> set[int]:
    return user_watched_lessons.get(user_id, set())


def mark_stage2_completed(user_id: str) -> None:
    user_stage2_completed.add(user_id)


def is_stage2_completed(user_id: str) -> bool:
    return user_id in user_stage2_completed


def seed_data() -> None:
    if quizzes or assignments or lessons or sections or learning_plans:
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

    lessons[1] = Lesson(id=1, title="Welcome to Nano Lab", mandatory=True)
    lessons[2] = Lesson(id=2, title="How grading works", mandatory=False)

    sections[1] = Section(
        id=1,
        plan_id=1,
        title="Foundations",
        lesson_ids=[1, 2],
        quiz_ids=[1],
        assignment_ids=[1],
    )

    learning_plans[1] = LearningPlan(
        id=1,
        name="Nano Lab Starter Plan",
        section_ids=[1],
    )


seed_data()
