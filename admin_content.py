import enum
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import AnyHttpUrl, BaseModel, Field, root_validator
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

from app.core.security import RoleChecker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nano_lab_academy.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class QuestionType(str, enum.Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    short_answer = "short_answer"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    courses = relationship("Course", back_populates="plan", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    plan = relationship("Plan", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    final_exams = relationship("FinalExam", back_populates="course", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    course = relationship("Course", back_populates="sections")
    lessons = relationship("Lesson", back_populates="section", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="section", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    video_provider_id = Column(String(255), nullable=False)
    notes_pdf_url = Column(String(2048), nullable=True)
    is_free_preview = Column(Boolean, nullable=False, default=False)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    section = relationship("Section", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="lesson", cascade="all, delete-orphan")


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        CheckConstraint(
            "(lesson_id IS NOT NULL AND section_id IS NULL) OR (lesson_id IS NULL AND section_id IS NOT NULL)",
            name="quiz_exactly_one_parent",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lesson = relationship("Lesson", back_populates="quizzes")
    section = relationship("Section", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    question_type = Column(SAEnum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    instructions = Column(Text, nullable=True)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lesson = relationship("Lesson", back_populates="assignments")


class FinalExam(Base):
    __tablename__ = "final_exams"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    passing_score = Column(Integer, nullable=False, default=70)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    course = relationship("Course", back_populates="final_exams")


class PlanBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class PlanRead(PlanBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class CourseBase(BaseModel):
    plan_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    plan_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class CourseRead(CourseBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class SectionBase(BaseModel):
    course_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    order_index: int = Field(default=0, ge=0)


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    course_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    order_index: Optional[int] = Field(default=None, ge=0)


class SectionRead(SectionBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class LessonBase(BaseModel):
    section_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    video_provider_id: str = Field(min_length=1, max_length=255)
    notes_pdf_url: Optional[AnyHttpUrl] = None
    is_free_preview: bool = False
    order_index: int = Field(default=0, ge=0)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    section_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    video_provider_id: Optional[str] = Field(default=None, min_length=1, max_length=255)
    notes_pdf_url: Optional[AnyHttpUrl] = None
    is_free_preview: Optional[bool] = None
    order_index: Optional[int] = Field(default=None, ge=0)


class LessonRead(BaseModel):
    id: int
    section_id: int
    title: str
    video_provider_id: str
    notes_pdf_url: Optional[str] = None
    is_free_preview: bool
    order_index: int

    class Config:
        orm_mode = True
        from_attributes = True


class QuizBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    lesson_id: Optional[int] = Field(default=None, ge=1)
    section_id: Optional[int] = Field(default=None, ge=1)

    @root_validator(skip_on_failure=True)
    def validate_parent(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        lesson_id = values.get("lesson_id")
        section_id = values.get("section_id")
        if (lesson_id is None and section_id is None) or (lesson_id is not None and section_id is not None):
            raise ValueError("Quiz must be linked to either lesson_id or section_id (exactly one).")
        return values


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    lesson_id: Optional[int] = Field(default=None, ge=1)
    section_id: Optional[int] = Field(default=None, ge=1)

    @root_validator(skip_on_failure=True)
    def validate_parent(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        lesson_id = values.get("lesson_id")
        section_id = values.get("section_id")
        if lesson_id is not None and section_id is not None:
            raise ValueError("Quiz cannot be linked to both lesson and section.")
        return values


class QuizRead(QuizBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class QuestionBase(BaseModel):
    quiz_id: int = Field(ge=1)
    prompt: str = Field(min_length=1)
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str = Field(min_length=1, max_length=255)

    @root_validator(skip_on_failure=True)
    def validate_options_by_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        qtype = values.get("question_type")
        options = values.get("options")
        correct_answer = values.get("correct_answer")
        if qtype == QuestionType.multiple_choice:
            if not options or len(options) < 2:
                raise ValueError("multiple_choice requires at least 2 options.")
            if correct_answer and correct_answer not in options:
                raise ValueError("correct_answer must be one of options for multiple_choice.")
        elif qtype == QuestionType.true_false:
            normalized = {"true", "false"}
            if correct_answer and correct_answer.lower() not in normalized:
                raise ValueError("correct_answer must be true or false for true_false.")
            values["options"] = ["true", "false"]
        elif qtype == QuestionType.short_answer:
            if options:
                raise ValueError("short_answer must not include options.")
        return values


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    quiz_id: Optional[int] = Field(default=None, ge=1)
    prompt: Optional[str] = Field(default=None, min_length=1)
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @root_validator(skip_on_failure=True)
    def validate_payload(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        qtype = values.get("question_type")
        options = values.get("options")
        correct_answer = values.get("correct_answer")
        if qtype == QuestionType.multiple_choice and options and correct_answer and correct_answer not in options:
            raise ValueError("correct_answer must be one of options for multiple_choice.")
        if qtype == QuestionType.true_false and correct_answer and correct_answer.lower() not in {"true", "false"}:
            raise ValueError("correct_answer must be true or false for true_false.")
        if qtype == QuestionType.short_answer and options:
            raise ValueError("short_answer must not include options.")
        return values


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    prompt: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str

    class Config:
        orm_mode = True
        from_attributes = True


class AssignmentBase(BaseModel):
    lesson_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    instructions: Optional[str] = None
    due_at: Optional[datetime] = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    lesson_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    instructions: Optional[str] = None
    due_at: Optional[datetime] = None


class AssignmentRead(AssignmentBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class FinalExamBase(BaseModel):
    course_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    passing_score: int = Field(default=70, ge=0, le=100)


class FinalExamCreate(FinalExamBase):
    pass


class FinalExamUpdate(BaseModel):
    course_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    passing_score: Optional[int] = Field(default=None, ge=0, le=100)


class FinalExamRead(FinalExamBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class SectionReorderItem(BaseModel):
    section_id: int = Field(ge=1)
    order_index: int = Field(ge=0)


class LessonReorderItem(BaseModel):
    lesson_id: int = Field(ge=1)
    order_index: int = Field(ge=0)


router = APIRouter(
    prefix="/admin/content",
    tags=["admin-content"],
    dependencies=[Depends(RoleChecker(["admin"]))],
)


def _get_or_404(db: Session, model: Any, item_id: int, name: str):
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found.")
    return item


@router.post("/plans", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    plan = Plan(**payload.dict())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/plans", response_model=List[PlanRead])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).order_by(Plan.id.asc()).all()


@router.get("/plans/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Plan, plan_id, "Plan")


@router.put("/plans/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db)):
    plan = _get_or_404(db, Plan, plan_id, "Plan")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = _get_or_404(db, Plan, plan_id, "Plan")
    db.delete(plan)
    db.commit()


@router.post("/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Plan, payload.plan_id, "Plan")
    course = Course(**payload.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=List[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.id.asc()).all()


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Course, course_id, "Course")


@router.put("/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    course = _get_or_404(db, Course, course_id, "Course")
    updates = payload.dict(exclude_unset=True)
    if "plan_id" in updates:
        _get_or_404(db, Plan, updates["plan_id"], "Plan")
    for field, value in updates.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = _get_or_404(db, Course, course_id, "Course")
    db.delete(course)
    db.commit()


@router.post("/sections", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(payload: SectionCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Course, payload.course_id, "Course")
    section = Section(**payload.dict())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@router.get("/sections", response_model=List[SectionRead])
def list_sections(db: Session = Depends(get_db)):
    return db.query(Section).order_by(Section.course_id.asc(), Section.order_index.asc(), Section.id.asc()).all()


@router.get("/sections/{section_id}", response_model=SectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Section, section_id, "Section")


@router.put("/sections/{section_id}", response_model=SectionRead)
def update_section(section_id: int, payload: SectionUpdate, db: Session = Depends(get_db)):
    section = _get_or_404(db, Section, section_id, "Section")
    updates = payload.dict(exclude_unset=True)
    if "course_id" in updates:
        _get_or_404(db, Course, updates["course_id"], "Course")
    for field, value in updates.items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)
    return section


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(section_id: int, db: Session = Depends(get_db)):
    section = _get_or_404(db, Section, section_id, "Section")
    db.delete(section)
    db.commit()


@router.put("/courses/{course_id}/sections/reorder", response_model=List[SectionRead])
def reorder_sections(course_id: int, payload: List[SectionReorderItem], db: Session = Depends(get_db)):
    _get_or_404(db, Course, course_id, "Course")
    section_ids = [item.section_id for item in payload]
    if len(section_ids) != len(set(section_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate section_id in payload.")

    sections = (
        db.query(Section)
        .filter(Section.id.in_(section_ids), Section.course_id == course_id)
        .all()
    )
    if len(sections) != len(section_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All sections must belong to the course.",
        )
    section_by_id = {section.id: section for section in sections}
    for item in payload:
        section_by_id[item.section_id].order_index = item.order_index

    db.commit()
    return (
        db.query(Section)
        .filter(Section.course_id == course_id)
        .order_by(Section.order_index.asc(), Section.id.asc())
        .all()
    )


@router.post("/lessons", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Section, payload.section_id, "Section")
    lesson_data = payload.dict()
    if lesson_data.get("notes_pdf_url") is not None:
        lesson_data["notes_pdf_url"] = str(lesson_data["notes_pdf_url"])
    lesson = Lesson(**lesson_data)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/lessons", response_model=List[LessonRead])
def list_lessons(db: Session = Depends(get_db)):
    return db.query(Lesson).order_by(Lesson.section_id.asc(), Lesson.order_index.asc(), Lesson.id.asc()).all()


@router.get("/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Lesson, lesson_id, "Lesson")


@router.put("/lessons/{lesson_id}", response_model=LessonRead)
def update_lesson(lesson_id: int, payload: LessonUpdate, db: Session = Depends(get_db)):
    lesson = _get_or_404(db, Lesson, lesson_id, "Lesson")
    updates = payload.dict(exclude_unset=True)
    if "section_id" in updates:
        _get_or_404(db, Section, updates["section_id"], "Section")
    if "notes_pdf_url" in updates and updates["notes_pdf_url"] is not None:
        updates["notes_pdf_url"] = str(updates["notes_pdf_url"])
    for field, value in updates.items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = _get_or_404(db, Lesson, lesson_id, "Lesson")
    db.delete(lesson)
    db.commit()


@router.put("/sections/{section_id}/lessons/reorder", response_model=List[LessonRead])
def reorder_lessons(section_id: int, payload: List[LessonReorderItem], db: Session = Depends(get_db)):
    _get_or_404(db, Section, section_id, "Section")
    lesson_ids = [item.lesson_id for item in payload]
    if len(lesson_ids) != len(set(lesson_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate lesson_id in payload.")

    lessons = (
        db.query(Lesson)
        .filter(Lesson.id.in_(lesson_ids), Lesson.section_id == section_id)
        .all()
    )
    if len(lessons) != len(lesson_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All lessons must belong to the section.",
        )
    lesson_by_id = {lesson.id: lesson for lesson in lessons}
    for item in payload:
        lesson_by_id[item.lesson_id].order_index = item.order_index

    db.commit()
    return (
        db.query(Lesson)
        .filter(Lesson.section_id == section_id)
        .order_by(Lesson.order_index.asc(), Lesson.id.asc())
        .all()
    )


@router.post("/quizzes", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def create_quiz(payload: QuizCreate, db: Session = Depends(get_db)):
    if payload.lesson_id is not None:
        _get_or_404(db, Lesson, payload.lesson_id, "Lesson")
    if payload.section_id is not None:
        _get_or_404(db, Section, payload.section_id, "Section")
    quiz = Quiz(**payload.dict())
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/quizzes", response_model=List[QuizRead])
def list_quizzes(db: Session = Depends(get_db)):
    return db.query(Quiz).order_by(Quiz.id.asc()).all()


@router.get("/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Quiz, quiz_id, "Quiz")


@router.put("/quizzes/{quiz_id}", response_model=QuizRead)
def update_quiz(quiz_id: int, payload: QuizUpdate, db: Session = Depends(get_db)):
    quiz = _get_or_404(db, Quiz, quiz_id, "Quiz")
    updates = payload.dict(exclude_unset=True)

    new_lesson_id = updates.get("lesson_id", quiz.lesson_id)
    new_section_id = updates.get("section_id", quiz.section_id)
    if (new_lesson_id is None and new_section_id is None) or (
        new_lesson_id is not None and new_section_id is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz must be linked to either lesson_id or section_id (exactly one).",
        )
    if new_lesson_id is not None:
        _get_or_404(db, Lesson, new_lesson_id, "Lesson")
    if new_section_id is not None:
        _get_or_404(db, Section, new_section_id, "Section")

    for field, value in updates.items():
        setattr(quiz, field, value)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = _get_or_404(db, Quiz, quiz_id, "Quiz")
    db.delete(quiz)
    db.commit()


@router.post("/questions", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Quiz, payload.quiz_id, "Quiz")
    question = Question(**payload.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/questions", response_model=List[QuestionRead])
def list_questions(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.id.asc()).all()


@router.get("/questions/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Question, question_id, "Question")


@router.put("/questions/{question_id}", response_model=QuestionRead)
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)):
    question = _get_or_404(db, Question, question_id, "Question")
    updates = payload.dict(exclude_unset=True)
    if "quiz_id" in updates:
        _get_or_404(db, Quiz, updates["quiz_id"], "Quiz")

    qtype = updates.get("question_type", question.question_type)
    options = updates.get("options", question.options)
    correct_answer = updates.get("correct_answer", question.correct_answer)
    if qtype == QuestionType.multiple_choice:
        if not options or len(options) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="multiple_choice requires at least 2 options.",
            )
        if correct_answer not in options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="correct_answer must be one of options for multiple_choice.",
            )
    elif qtype == QuestionType.true_false:
        if str(correct_answer).lower() not in {"true", "false"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="correct_answer must be true or false for true_false.",
            )
        updates["options"] = ["true", "false"]
    elif qtype == QuestionType.short_answer and options:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="short_answer must not include options.",
        )

    for field, value in updates.items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = _get_or_404(db, Question, question_id, "Question")
    db.delete(question)
    db.commit()


@router.post("/assignments", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Lesson, payload.lesson_id, "Lesson")
    assignment = Assignment(**payload.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/assignments", response_model=List[AssignmentRead])
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).order_by(Assignment.id.asc()).all()


@router.get("/assignments/{assignment_id}", response_model=AssignmentRead)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Assignment, assignment_id, "Assignment")


@router.put("/assignments/{assignment_id}", response_model=AssignmentRead)
def update_assignment(assignment_id: int, payload: AssignmentUpdate, db: Session = Depends(get_db)):
    assignment = _get_or_404(db, Assignment, assignment_id, "Assignment")
    updates = payload.dict(exclude_unset=True)
    if "lesson_id" in updates:
        _get_or_404(db, Lesson, updates["lesson_id"], "Lesson")
    for field, value in updates.items():
        setattr(assignment, field, value)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = _get_or_404(db, Assignment, assignment_id, "Assignment")
    db.delete(assignment)
    db.commit()


@router.post("/final-exams", response_model=FinalExamRead, status_code=status.HTTP_201_CREATED)
def create_final_exam(payload: FinalExamCreate, db: Session = Depends(get_db)):
    _get_or_404(db, Course, payload.course_id, "Course")
    final_exam = FinalExam(**payload.dict())
    db.add(final_exam)
    db.commit()
    db.refresh(final_exam)
    return final_exam


@router.get("/final-exams", response_model=List[FinalExamRead])
def list_final_exams(db: Session = Depends(get_db)):
    return db.query(FinalExam).order_by(FinalExam.id.asc()).all()


@router.get("/final-exams/{final_exam_id}", response_model=FinalExamRead)
def get_final_exam(final_exam_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, FinalExam, final_exam_id, "Final exam")


@router.put("/final-exams/{final_exam_id}", response_model=FinalExamRead)
def update_final_exam(final_exam_id: int, payload: FinalExamUpdate, db: Session = Depends(get_db)):
    final_exam = _get_or_404(db, FinalExam, final_exam_id, "Final exam")
    updates = payload.dict(exclude_unset=True)
    if "course_id" in updates:
        _get_or_404(db, Course, updates["course_id"], "Course")
    for field, value in updates.items():
        setattr(final_exam, field, value)
    db.commit()
    db.refresh(final_exam)
    return final_exam


@router.delete("/final-exams/{final_exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_final_exam(final_exam_id: int, db: Session = Depends(get_db)):
    final_exam = _get_or_404(db, FinalExam, final_exam_id, "Final exam")
    db.delete(final_exam)
    db.commit()


Base.metadata.create_all(bind=engine)
