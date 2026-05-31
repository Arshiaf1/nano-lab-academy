"""SQLAlchemy models for Nano Lab Academy."""

from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer,
    JSON, String, Float, Date, func
)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type that uses CHAR(32) for SQLite."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value)).replace('-', '')
        return str(value).replace('-', '')

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


class UserRole(str, Enum):
    """User role enumeration."""
    LEARNER = "learner"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    EMPLOYER = "employer"


class PlanType(str, Enum):
    """Plan type enumeration."""
    BASICS = "basics"
    PRO = "pro"
    ULTRA = "ultra"


class QuestionType(str, Enum):
    """Question type enumeration."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class Stage2Status(str, Enum):
    """Stage 2 enrollment status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class JobType(str, Enum):
    """Job type enumeration."""
    INTERNSHIP = "internship"
    JOB = "job"


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    INITIATED = "initiated"
    PAID = "paid"
    FAILED = "failed"


# ============================================================================
# Core Models
# ============================================================================

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.LEARNER, nullable=False)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=True)
    plan_active_until = Column(DateTime, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    plan = relationship("Plan", back_populates="users")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    lesson_progress = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="user", cascade="all, delete-orphan")
    exam_attempts = relationship("ExamAttempt", back_populates="user", cascade="all, delete-orphan")
    stage2_enrollments = relationship("Stage2Enrollment", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    xp = relationship("UserXP", back_populates="user", cascade="all, delete-orphan")
    streaks = relationship("UserStreak", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    graded_submissions = relationship(
        "AssignmentSubmission",
        foreign_keys="AssignmentSubmission.graded_by",
        back_populates="grader"
    )
    supervisor_ratings = relationship("FinalSupervisorRating", back_populates="supervisor")
    task_evaluations = relationship("Stage2TaskEvaluation", back_populates="supervisor")


class Plan(Base):
    """Subscription plan model."""
    __tablename__ = "plans"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(SQLEnum(PlanType), nullable=False, unique=True)
    description = Column(String, nullable=True)
    monthly_price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="plan")
    courses = relationship("Course", back_populates="plan", cascade="all, delete-orphan")
    stage2_tasks = relationship("Stage2Task", back_populates="plan", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="plan")


# ============================================================================
# Course Content Models
# ============================================================================

class Course(Base):
    """Course model."""
    __tablename__ = "courses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    plan = relationship("Plan", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    final_exams = relationship("FinalExam", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="course")


class Section(Base):
    """Course section model."""
    __tablename__ = "sections"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="sections")
    lessons = relationship("Lesson", back_populates="section", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="section", cascade="all, delete-orphan")


class Lesson(Base):
    """Lesson model."""
    __tablename__ = "lessons"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    section_id = Column(GUID(), ForeignKey("sections.id"), nullable=False)
    title = Column(String, nullable=False)
    video_provider_id = Column(String, nullable=True)
    video_duration_seconds = Column(Integer, nullable=True)
    notes_pdf_url = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_free_preview = Column(Boolean, default=False, nullable=False)
    requires_completion = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    section = relationship("Section", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class Quiz(Base):
    """Quiz model."""
    __tablename__ = "quizzes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(GUID(), ForeignKey("lessons.id"), nullable=True)
    section_id = Column(GUID(), ForeignKey("sections.id"), nullable=True)
    title = Column(String, nullable=False)
    pass_threshold = Column(Integer, default=80, nullable=False)
    max_attempts = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    section = relationship("Section", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """Question model."""
    __tablename__ = "questions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(GUID(), ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(String, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=True)
    points = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class Assignment(Base):
    """Assignment model."""
    __tablename__ = "assignments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(GUID(), ForeignKey("lessons.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    max_score = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    lesson = relationship("Lesson", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class FinalExam(Base):
    """Final exam model."""
    __tablename__ = "final_exams"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    pass_threshold = Column(Integer, default=80, nullable=False)
    max_attempts = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="final_exams")
    attempts = relationship("ExamAttempt", back_populates="exam", cascade="all, delete-orphan")


# ============================================================================
# Enrollment & Progress Models
# ============================================================================

class Enrollment(Base):
    """Course enrollment model."""
    __tablename__ = "enrollments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    stage = Column(Integer, default=1, nullable=False)
    stage1_completed = Column(Boolean, default=False, nullable=False)
    stage2_completed = Column(Boolean, default=False, nullable=False)
    stage1_deadline = Column(DateTime, nullable=True)
    stage1_locked = Column(Boolean, default=False, nullable=False)
    stage2_enrollment_id = Column(GUID(), ForeignKey("stage2_enrollments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    stage2_enrollment = relationship("Stage2Enrollment", back_populates="enrollment", foreign_keys=[stage2_enrollment_id])


class LessonProgress(Base):
    """Lesson progress tracking model."""
    __tablename__ = "lesson_progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    lesson_id = Column(GUID(), ForeignKey("lessons.id"), nullable=False)
    watched = Column(Boolean, default=False, nullable=False)
    watched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class QuizAttempt(Base):
    """Quiz attempt model."""
    __tablename__ = "quiz_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    quiz_id = Column(GUID(), ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")


class AssignmentSubmission(Base):
    """Assignment submission model."""
    __tablename__ = "assignment_submissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    assignment_id = Column(GUID(), ForeignKey("assignments.id"), nullable=False)
    file_url = Column(String, nullable=True)
    text_answer = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    graded_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="assignment_submissions", foreign_keys=[user_id])
    assignment = relationship("Assignment", back_populates="submissions")
    grader = relationship("User", back_populates="graded_submissions", foreign_keys=[graded_by])


class ExamAttempt(Base):
    """Exam attempt model."""
    __tablename__ = "exam_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    exam_id = Column(GUID(), ForeignKey("final_exams.id"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="exam_attempts")
    exam = relationship("FinalExam", back_populates="attempts")


# ============================================================================
# Stage 2 Models
# ============================================================================

class Stage2Task(Base):
    """Stage 2 practical task model."""
    __tablename__ = "stage2_tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    plan = relationship("Plan", back_populates="stage2_tasks")
    evaluations = relationship("Stage2TaskEvaluation", back_populates="task", cascade="all, delete-orphan")


class LabPartner(Base):
    """Lab partner/employer organization model."""
    __tablename__ = "lab_partners"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    contact_email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    stage2_enrollments = relationship("Stage2Enrollment", back_populates="lab_partner", cascade="all, delete-orphan")
    job_listings = relationship("JobListing", back_populates="employer")


class Stage2Enrollment(Base):
    """Stage 2 enrollment in a lab partnership model."""
    __tablename__ = "stage2_enrollments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    lab_partner_id = Column(GUID(), ForeignKey("lab_partners.id"), nullable=False)
    status = Column(SQLEnum(Stage2Status), default=Stage2Status.PENDING, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="stage2_enrollments")
    lab_partner = relationship("LabPartner", back_populates="stage2_enrollments")
    enrollment = relationship("Enrollment", back_populates="stage2_enrollment", foreign_keys="Enrollment.stage2_enrollment_id")
    task_evaluations = relationship("Stage2TaskEvaluation", back_populates="stage2_enrollment", cascade="all, delete-orphan")
    supervisor_ratings = relationship("FinalSupervisorRating", back_populates="stage2_enrollment", cascade="all, delete-orphan")


class Stage2TaskEvaluation(Base):
    """Stage 2 task evaluation by supervisor model."""
    __tablename__ = "stage2_task_evaluations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    stage2_enrollment_id = Column(GUID(), ForeignKey("stage2_enrollments.id"), nullable=False)
    task_id = Column(GUID(), ForeignKey("stage2_tasks.id"), nullable=False)
    supervisor_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    stage2_enrollment = relationship("Stage2Enrollment", back_populates="task_evaluations")
    task = relationship("Stage2Task", back_populates="evaluations")
    supervisor = relationship("User", back_populates="task_evaluations")


class FinalSupervisorRating(Base):
    """Final supervisor rating for Stage 2 model."""
    __tablename__ = "final_supervisor_ratings"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    stage2_enrollment_id = Column(GUID(), ForeignKey("stage2_enrollments.id"), nullable=False)
    supervisor_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    overall_score = Column(Integer, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    stage2_enrollment = relationship("Stage2Enrollment", back_populates="supervisor_ratings")
    supervisor = relationship("User", back_populates="supervisor_ratings")


# ============================================================================
# Gamification & Achievement Models
# ============================================================================

class Badge(Base):
    """Achievement badge model."""
    __tablename__ = "badges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    criteria_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    """User badge award model."""
    __tablename__ = "user_badges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    badge_id = Column(GUID(), ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")


class UserXP(Base):
    """User experience points model."""
    __tablename__ = "user_xp"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="xp")


class UserStreak(Base):
    """User activity streak model."""
    __tablename__ = "user_streaks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, unique=True)
    streak_count = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="streaks")


class Certification(Base):
    """User certification model."""
    __tablename__ = "certifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cert_url = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="certifications")
    course = relationship("Course", back_populates="certifications")


# ============================================================================
# Job & Application Models
# ============================================================================

class JobListing(Base):
    """Job listing model."""
    __tablename__ = "job_listings"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employer_id = Column(GUID(), ForeignKey("lab_partners.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    required_badges = Column(JSON, nullable=True)
    location = Column(String, nullable=True)
    type = Column(SQLEnum(JobType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    employer = relationship("LabPartner", back_populates="job_listings")
    applications = relationship("Application", back_populates="job_listing", cascade="all, delete-orphan")


class Application(Base):
    """Job application model."""
    __tablename__ = "applications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    job_id = Column(GUID(), ForeignKey("job_listings.id"), nullable=False)
    cover_letter = Column(String, nullable=True)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    job_listing = relationship("JobListing", back_populates="applications")


# ============================================================================
# Payment Models
# ============================================================================

class Payment(Base):
    """Payment transaction model."""
    __tablename__ = "payments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    payment_gateway_ref = Column(String, nullable=True, unique=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.INITIATED, nullable=False)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=True)
    for_stage_unlock = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="payments")
    plan = relationship("Plan", back_populates="payments")
