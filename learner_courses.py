from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Session

from admin_content import Base, Course, Lesson, Plan, Section, engine, get_db
from app.core.security import RoleChecker


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(Integer, nullable=False, default=1)
    stage1_deadline = Column(DateTime, nullable=False)
    stage1_locked = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True)
    watched_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class LearnerStat(Base):
    __tablename__ = "learner_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    total_xp = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class PreviewLessonOut(BaseModel):
    lesson_id: int
    title: str


class AvailableCourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    free_preview_lessons: List[PreviewLessonOut]


class AvailablePlanOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    courses: List[AvailableCourseOut]


class EnrollmentCreateIn(BaseModel):
    plan_id: int = Field(ge=1)


class EnrollmentOut(BaseModel):
    id: int
    plan_id: int
    stage: int
    stage1_deadline: datetime
    stage1_locked: bool
    is_active: bool
    completion_status: str
    completed_lessons: int
    total_lessons: int


class CourseLessonOut(BaseModel):
    title: str
    locked: bool
    id: Optional[int] = None
    video_url: Optional[str] = None
    notes_pdf_url: Optional[str] = None
    is_free_preview: Optional[bool] = None
    order_index: Optional[int] = None


class CourseSectionOut(BaseModel):
    id: int
    title: str
    order_index: int
    lessons: List[CourseLessonOut]


class CourseTreeOut(BaseModel):
    id: int
    title: str
    sections: List[CourseSectionOut]


class LessonDetailOut(BaseModel):
    id: int
    section_id: int
    title: str
    video_url: str
    notes_pdf_url: Optional[str] = None
    is_free_preview: bool
    order_index: int


class LessonProgressOut(BaseModel):
    lesson_id: int
    watched: bool
    xp_awarded: int
    total_xp: int
    current_streak: int


router = APIRouter(tags=["learner-courses"])


def _get_current_user(request: Request) -> Any:
    user = getattr(request.state, "user", None)
    if user is None:
        user = getattr(request, "user", None)
    if user is None or getattr(user, "id", None) is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user


def _get_active_enrollment(db: Session, user_id: int) -> Optional[Enrollment]:
    now = datetime.utcnow()
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == user_id,
            Enrollment.is_active.is_(True),
            Enrollment.stage1_locked.is_(False),
            Enrollment.stage1_deadline >= now,
        )
        .order_by(Enrollment.created_at.desc())
        .first()
    )
    return enrollment


def _lesson_plan_id(db: Session, lesson_id: int) -> Optional[int]:
    row = (
        db.query(Course.plan_id)
        .join(Section, Section.course_id == Course.id)
        .join(Lesson, Lesson.section_id == Section.id)
        .filter(Lesson.id == lesson_id)
        .first()
    )
    if row is None:
        return None
    return row[0]


def _is_lesson_unlocked(db: Session, user_id: int, lesson: Lesson) -> bool:
    if lesson.is_free_preview:
        return True
    enrollment = _get_active_enrollment(db, user_id)
    if enrollment is None:
        return False
    lesson_plan_id = _lesson_plan_id(db, lesson.id)
    return lesson_plan_id == enrollment.plan_id


def _completion_counts(db: Session, enrollment: Enrollment) -> Tuple[int, int]:
    total_lessons = (
        db.query(Lesson)
        .join(Section, Section.id == Lesson.section_id)
        .join(Course, Course.id == Section.course_id)
        .filter(Course.plan_id == enrollment.plan_id)
        .count()
    )
    completed_lessons = (
        db.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Section, Section.id == Lesson.section_id)
        .join(Course, Course.id == Section.course_id)
        .filter(
            LessonProgress.user_id == enrollment.user_id,
            Course.plan_id == enrollment.plan_id,
        )
        .count()
    )
    return completed_lessons, total_lessons


@router.get("/courses/available", response_model=List[AvailablePlanOut])
def get_available_courses(db: Session = Depends(get_db)):
    plans = db.query(Plan).order_by(Plan.id.asc()).all()
    courses = db.query(Course).order_by(Course.id.asc()).all()
    sections = db.query(Section).order_by(Section.order_index.asc(), Section.id.asc()).all()
    lessons = (
        db.query(Lesson)
        .filter(Lesson.is_free_preview.is_(True))
        .order_by(Lesson.order_index.asc(), Lesson.id.asc())
        .all()
    )

    sections_by_course: Dict[int, List[Section]] = {}
    for section in sections:
        sections_by_course.setdefault(section.course_id, []).append(section)

    lessons_by_section: Dict[int, List[Lesson]] = {}
    for lesson in lessons:
        lessons_by_section.setdefault(lesson.section_id, []).append(lesson)

    courses_by_plan: Dict[int, List[Course]] = {}
    for course in courses:
        courses_by_plan.setdefault(course.plan_id, []).append(course)

    result: List[AvailablePlanOut] = []
    for plan in plans:
        course_items: List[AvailableCourseOut] = []
        for course in courses_by_plan.get(plan.id, []):
            previews: List[PreviewLessonOut] = []
            for section in sections_by_course.get(course.id, []):
                for lesson in lessons_by_section.get(section.id, []):
                    previews.append(PreviewLessonOut(lesson_id=lesson.id, title=lesson.title))
                    if len(previews) == 3:
                        break
                if len(previews) == 3:
                    break
            course_items.append(
                AvailableCourseOut(
                    id=course.id,
                    name=course.title,
                    description=course.description,
                    free_preview_lessons=previews,
                )
            )
        price_value = getattr(plan, "price", None)
        result.append(
            AvailablePlanOut(
                id=plan.id,
                name=plan.title,
                description=plan.description,
                price=price_value,
                courses=course_items,
            )
        )
    return result


@router.post(
    "/enrollments",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["learner"]))],
)
def create_enrollment(payload: EnrollmentCreateIn, request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request)
    if db.get(Plan, payload.plan_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    active = _get_active_enrollment(db, user.id)
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active enrollment.",
        )

    enrollment = Enrollment(
        user_id=user.id,
        plan_id=payload.plan_id,
        stage=1,
        stage1_deadline=datetime.utcnow() + timedelta(days=90),
        stage1_locked=False,
        is_active=True,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    completed, total = _completion_counts(db, enrollment)
    return EnrollmentOut(
        id=enrollment.id,
        plan_id=enrollment.plan_id,
        stage=enrollment.stage,
        stage1_deadline=enrollment.stage1_deadline,
        stage1_locked=enrollment.stage1_locked,
        is_active=True,
        completion_status="completed" if total > 0 and completed >= total else "in_progress",
        completed_lessons=completed,
        total_lessons=total,
    )


@router.get(
    "/enrollments/my",
    response_model=EnrollmentOut,
    dependencies=[Depends(RoleChecker(["learner"]))],
)
def get_my_enrollment(request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request)
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id)
        .order_by(Enrollment.created_at.desc())
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")
    completed, total = _completion_counts(db, enrollment)
    active = (
        enrollment.is_active
        and not enrollment.stage1_locked
        and enrollment.stage1_deadline >= datetime.utcnow()
    )
    return EnrollmentOut(
        id=enrollment.id,
        plan_id=enrollment.plan_id,
        stage=enrollment.stage,
        stage1_deadline=enrollment.stage1_deadline,
        stage1_locked=enrollment.stage1_locked,
        is_active=active,
        completion_status="completed" if total > 0 and completed >= total else "in_progress",
        completed_lessons=completed,
        total_lessons=total,
    )


@router.get(
    "/courses/my",
    response_model=List[CourseTreeOut],
    dependencies=[Depends(RoleChecker(["learner"]))],
)
def get_my_courses(request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request)
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id)
        .order_by(Enrollment.created_at.desc())
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")

    enrollment_active_unlocked = (
        enrollment.is_active
        and not enrollment.stage1_locked
        and enrollment.stage1_deadline >= datetime.utcnow()
    )

    courses = db.query(Course).filter(Course.plan_id == enrollment.plan_id).order_by(Course.id.asc()).all()
    course_ids = [course.id for course in courses]
    if not course_ids:
        return []

    sections = (
        db.query(Section)
        .filter(Section.course_id.in_(course_ids))
        .order_by(Section.course_id.asc(), Section.order_index.asc(), Section.id.asc())
        .all()
    )
    section_ids = [section.id for section in sections]
    lessons = []
    if section_ids:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.section_id.in_(section_ids))
            .order_by(Lesson.section_id.asc(), Lesson.order_index.asc(), Lesson.id.asc())
            .all()
        )

    sections_by_course: Dict[int, List[Section]] = {}
    for section in sections:
        sections_by_course.setdefault(section.course_id, []).append(section)

    lessons_by_section: Dict[int, List[Lesson]] = {}
    for lesson in lessons:
        lessons_by_section.setdefault(lesson.section_id, []).append(lesson)

    response: List[CourseTreeOut] = []
    for course in courses:
        section_items: List[CourseSectionOut] = []
        for section in sections_by_course.get(course.id, []):
            lesson_items: List[CourseLessonOut] = []
            for lesson in lessons_by_section.get(section.id, []):
                unlocked = lesson.is_free_preview or enrollment_active_unlocked
                if unlocked:
                    lesson_items.append(
                        CourseLessonOut(
                            id=lesson.id,
                            title=lesson.title,
                            video_url=lesson.video_provider_id,
                            notes_pdf_url=lesson.notes_pdf_url,
                            is_free_preview=lesson.is_free_preview,
                            order_index=lesson.order_index,
                            locked=False,
                        )
                    )
                else:
                    lesson_items.append(CourseLessonOut(title=lesson.title, locked=True))
            section_items.append(
                CourseSectionOut(
                    id=section.id,
                    title=section.title,
                    order_index=section.order_index,
                    lessons=lesson_items,
                )
            )
        response.append(CourseTreeOut(id=course.id, title=course.title, sections=section_items))
    return response


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetailOut,
    dependencies=[Depends(RoleChecker(["learner"]))],
)
def get_lesson_details(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request)
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
    if not _is_lesson_unlocked(db, user.id, lesson):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lesson is locked.")
    return LessonDetailOut(
        id=lesson.id,
        section_id=lesson.section_id,
        title=lesson.title,
        video_url=lesson.video_provider_id,
        notes_pdf_url=lesson.notes_pdf_url,
        is_free_preview=lesson.is_free_preview,
        order_index=lesson.order_index,
    )


@router.post(
    "/lessons/{lesson_id}/progress",
    response_model=LessonProgressOut,
    dependencies=[Depends(RoleChecker(["learner"]))],
)
def mark_lesson_progress(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request)
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
    if not _is_lesson_unlocked(db, user.id, lesson):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lesson is locked.")

    enrollment = _get_active_enrollment(db, user.id)
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active enrollment required.")
    if _lesson_plan_id(db, lesson.id) != enrollment.plan_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lesson is outside enrolled plan.")

    xp_awarded = 0
    today = date.today()

    stats: Optional[LearnerStat] = None
    with db.begin_nested():
        progress = (
            db.query(LessonProgress)
            .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
            .first()
        )
        stats = db.query(LearnerStat).filter(LearnerStat.user_id == user.id).first()
        if stats is None:
            stats = LearnerStat(user_id=user.id, total_xp=0, current_streak=0, last_activity_date=None)
            db.add(stats)

        if progress is None:
            progress = LessonProgress(user_id=user.id, lesson_id=lesson.id, enrollment_id=enrollment.id)
            db.add(progress)
            xp_awarded = 10
            if stats.last_activity_date == today:
                pass
            else:
                yesterday = today - timedelta(days=1)
                if stats.last_activity_date == yesterday:
                    stats.current_streak += 1
                else:
                    stats.current_streak = 1
            stats.total_xp += 10
            stats.last_activity_date = today

    db.commit()
    if stats is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stats not available.")

    return LessonProgressOut(
        lesson_id=lesson.id,
        watched=True,
        xp_awarded=xp_awarded,
        total_xp=stats.total_xp,
        current_streak=stats.current_streak,
    )


Base.metadata.create_all(bind=engine)
