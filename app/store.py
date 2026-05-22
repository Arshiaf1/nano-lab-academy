from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any, Literal


QuestionType = Literal["mc", "true_false", "short_answer"]
SubmissionKind = Literal["quiz", "assignment"]
SubmissionStatus = Literal["pending_review", "graded"]
PlanTier = Literal["free", "pro"]


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
class CourseLesson:
    id: int
    title: str
    description: str
    video_url: str
    notes: str
    quiz_id: int | None = None
    assignment_id: int | None = None
    freemium_locked: bool = False
    xp_reward: int = 20


@dataclass(slots=True)
class CourseSection:
    id: int
    title: str
    description: str = ""
    children: list[CourseLesson] = field(default_factory=list)


@dataclass(slots=True)
class Course:
    id: int
    title: str
    description: str
    outline: list[CourseSection] = field(default_factory=list)


@dataclass(slots=True)
class Enrollment:
    id: int
    user_id: str
    course_id: int
    plan_tier: PlanTier
    enrolled_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


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
user_xp: dict[str, int] = {}
awarded_badges: dict[str, set[str]] = {}
courses: dict[int, Course] = {}
lessons: dict[int, CourseLesson] = {}
enrollments: dict[str, Enrollment] = {}
lesson_progress: dict[str, set[int]] = {}
user_streak: dict[str, int] = {}

stage1_deadline = datetime(2026, 5, 29, 18, 0, tzinfo=timezone.utc)

stage2_lab_partners = [
    {"id": "partner-1", "name": "Ava Chen", "skill": "Python automation", "availability": "Today"},
    {"id": "partner-2", "name": "Mateo Silva", "skill": "UI debugging", "availability": "Tomorrow"},
    {"id": "partner-3", "name": "Nadia Patel", "skill": "Data modeling", "availability": "This week"},
]

stage2_tasks = [
    {"id": "task-1", "title": "Pair on a learning workflow", "status": "open"},
    {"id": "task-2", "title": "Review a sample submission", "status": "in progress"},
    {"id": "task-3", "title": "Submit supervisor reflection", "status": "open"},
]

stage2_supervisor_ratings = [
    {"name": "Supervisor Ana", "rating": 4.8, "note": "Strong collaboration and consistent follow-through."},
    {"name": "Supervisor Ben", "rating": 4.5, "note": "Clear reasoning and good partner communication."},
]

stage3_jobs = [
    {"id": "job-1", "title": "Junior Lab Engineer", "location": "Remote", "type": "Full-time", "salary": "$78k-$92k"},
    {"id": "job-2", "title": "Learning Operations Associate", "location": "Hybrid", "type": "Contract", "salary": "$42/hr"},
    {"id": "job-3", "title": "Instructional Content Specialist", "location": "Remote", "type": "Part-time", "salary": "$58k-$66k"},
]

stage3_applications: list[dict[str, Any]] = []

_submission_ids = count(1)
_enrollment_ids = count(1)


def next_submission_id() -> int:
    return next(_submission_ids)


def next_enrollment_id() -> int:
    return next(_enrollment_ids)


def add_xp(user_id: str, amount: int) -> int:
    user_xp[user_id] = user_xp.get(user_id, 0) + amount
    return user_xp[user_id]


def get_quiz(quiz_id: int) -> Quiz | None:
    return quizzes.get(quiz_id)


def get_assignment(assignment_id: int) -> Assignment | None:
    return assignments.get(assignment_id)


def get_course(course_id: int) -> Course | None:
    return courses.get(course_id)


def get_lesson(lesson_id: int) -> CourseLesson | None:
    return lessons.get(lesson_id)


def get_my_enrollment(user_id: str = "me") -> Enrollment | None:
    return enrollments.get(user_id)


def enroll_user(user_id: str = "me", plan_tier: PlanTier = "free", course_id: int = 1) -> Enrollment:
    enrollment = enrollments.get(user_id)
    if enrollment is None:
        enrollment = Enrollment(
            id=next_enrollment_id(),
            user_id=user_id,
            course_id=course_id,
            plan_tier=plan_tier,
        )
        enrollments[user_id] = enrollment
        return enrollment

    enrollment.plan_tier = plan_tier
    enrollment.course_id = course_id
    enrollment.updated_at = utcnow()
    return enrollment


def completed_lessons(user_id: str = "me") -> set[int]:
    return lesson_progress.setdefault(user_id, set())


def complete_lesson(user_id: str, lesson_id: int) -> dict[str, Any]:
    completed = completed_lessons(user_id)
    is_new_completion = lesson_id not in completed
    completed.add(lesson_id)

    if is_new_completion:
        add_xp(user_id, 20)
        user_streak[user_id] = user_streak.get(user_id, 0) + 1

    badge_ids: list[str] = []
    if user_streak.get(user_id, 0) >= 3 and "lesson_runner" not in awarded_badges.setdefault(user_id, set()):
        awarded_badges[user_id].add("lesson_runner")
        badge_ids.append("lesson_runner")

    return {
        "lesson_id": lesson_id,
        "completed": True,
        "is_new_completion": is_new_completion,
        "xp": user_xp.get(user_id, 0),
        "streak": user_streak.get(user_id, 0),
        "badge_ids": badge_ids,
    }


def stage1_state(user_id: str = "me") -> dict[str, Any]:
    locked = utcnow() >= stage1_deadline
    return {
        "stage1_deadline": stage1_deadline.isoformat(),
        "stage1_locked": locked,
        "remaining_seconds": max(0, int((stage1_deadline - utcnow()).total_seconds())),
        "user_id": user_id,
    }


def stage2_state() -> dict[str, Any]:
    return {
        "lab_partners": stage2_lab_partners,
        "tasks": stage2_tasks,
        "supervisor_ratings": stage2_supervisor_ratings,
    }


def stage3_state() -> dict[str, Any]:
    return {
        "jobs": stage3_jobs,
        "applications": stage3_applications,
    }


def submit_stage3_application(payload: dict[str, Any]) -> dict[str, Any]:
    application = {
        "id": len(stage3_applications) + 1,
        "job_id": payload.get("job_id"),
        "name": payload.get("name", ""),
        "email": payload.get("email", ""),
        "cover_letter": payload.get("cover_letter", ""),
        "submitted_at": utcnow().isoformat(),
    }
    stage3_applications.append(application)
    return application


def submit_stage2_partner_selection(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "partner_id": payload.get("partner_id"),
        "partner_name": next((partner["name"] for partner in stage2_lab_partners if partner["id"] == payload.get("partner_id")), None),
        "selected_at": utcnow().isoformat(),
    }


def lesson_is_locked(lesson: CourseLesson, enrollment: Enrollment | None) -> bool:
    return lesson.freemium_locked and (enrollment is None or enrollment.plan_tier == "free")


def course_lessons(course: Course) -> list[CourseLesson]:
    return [lesson for section in course.outline for lesson in section.children]


def course_progress(course: Course, user_id: str = "me") -> dict[str, Any]:
    all_lessons = course_lessons(course)
    completed = completed_lessons(user_id)
    completed_count = sum(1 for lesson in all_lessons if lesson.id in completed)
    total_count = len(all_lessons)
    percent = round((completed_count / total_count) * 100, 2) if total_count else 0.0

    stage_progress: list[dict[str, Any]] = []
    for index, section in enumerate(course.outline, start=1):
        section_total = len(section.children)
        section_completed = sum(1 for lesson in section.children if lesson.id in completed)
        stage_progress.append(
            {
                "id": section.id,
                "title": section.title,
                "order": index,
                "completed_lessons": section_completed,
                "total_lessons": section_total,
                "progress": round((section_completed / section_total) * 100, 2) if section_total else 0.0,
                "completed": section_total > 0 and section_completed == section_total,
            }
        )

    current_stage = next((stage for stage in stage_progress if stage["progress"] < 100), stage_progress[-1] if stage_progress else None)

    return {
        "course_id": course.id,
        "completed_lessons": completed_count,
        "total_lessons": total_count,
        "progress": percent,
        "current_stage": current_stage,
        "stages": stage_progress,
    }


def gamification_status(user_id: str = "me") -> dict[str, Any]:
    badge_ids = sorted(awarded_badges.get(user_id, set()))
    return {
        "xp": user_xp.get(user_id, 0),
        "streak": user_streak.get(user_id, 0),
        "badges": badge_ids,
        "stage_progress": course_progress(courses[1], user_id) if 1 in courses else None,
    }


def enrollment_summary(user_id: str = "me") -> dict[str, Any]:
    enrollment = get_my_enrollment(user_id)
    course = get_course(enrollment.course_id) if enrollment else get_course(1)
    if course is None:
        return {"enrolled": False, "course": None, "plan_tier": None}

    return {
        "enrolled": enrollment is not None,
        "plan_tier": enrollment.plan_tier if enrollment else None,
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "progress": course_progress(course, user_id) if enrollment else None,
            "outline": [
                {
                    "id": section.id,
                    "title": section.title,
                    "description": section.description,
                    "children": [
                        {
                            "id": lesson.id,
                            "title": lesson.title,
                            "description": lesson.description,
                            "locked": lesson_is_locked(lesson, enrollment),
                            "quiz_id": lesson.quiz_id,
                            "assignment_id": lesson.assignment_id,
                        }
                        for lesson in section.children
                    ],
                }
                for section in course.outline
            ],
        },
    }


def lesson_summary(lesson_id: int, user_id: str = "me") -> dict[str, Any] | None:
    lesson = get_lesson(lesson_id)
    if lesson is None:
        return None

    enrollment = get_my_enrollment(user_id)
    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "video_url": lesson.video_url,
        "notes": lesson.notes,
        "quiz_id": lesson.quiz_id,
        "assignment_id": lesson.assignment_id,
        "locked": lesson_is_locked(lesson, enrollment),
        "completed": lesson.id in completed_lessons(user_id),
        "xp_reward": lesson.xp_reward,
    }


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


def seed_data() -> None:
    if quizzes or assignments or courses:
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

    lessons[101] = CourseLesson(
        id=101,
        title="Welcome to Nano Lab",
        description="Start here to understand the learning flow.",
        video_url="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        notes="Welcome notes: use the course outline to move through the stages.",
        quiz_id=1,
        xp_reward=20,
    )
    lessons[102] = CourseLesson(
        id=102,
        title="Workspace Tour",
        description="Learn where lessons, quizzes, and assignments live.",
        video_url="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        notes="Workspace notes: the API and UI share the same in-memory data.",
        assignment_id=1,
        xp_reward=20,
    )
    lessons[201] = CourseLesson(
        id=201,
        title="Build Your First Lesson",
        description="This lesson is locked for free enrollments.",
        video_url="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        notes="Build notes: upgrade to unlock the next stage.",
        freemium_locked=True,
        xp_reward=30,
    )
    lessons[202] = CourseLesson(
        id=202,
        title="Capstone Review",
        description="Wrap up with a final review and reflection.",
        video_url="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        notes="Review notes: revisit the quiz if you need more XP.",
        freemium_locked=True,
        xp_reward=30,
    )

    courses[1] = Course(
        id=1,
        title="Nano Lab Academy",
        description="A compact freemium course track with lessons, quizzes, and assignments.",
        outline=[
            CourseSection(
                id=1,
                title="Stage 1. Foundations",
                description="Get oriented and complete the starter content.",
                children=[lessons[101], lessons[102]],
            ),
            CourseSection(
                id=2,
                title="Stage 2. Build",
                description="Apply the core flow with a more advanced lesson.",
                children=[lessons[201]],
            ),
            CourseSection(
                id=3,
                title="Stage 3. Launch",
                description="Finish the track with a final capstone review.",
                children=[lessons[202]],
            ),
        ],
    )


seed_data()
