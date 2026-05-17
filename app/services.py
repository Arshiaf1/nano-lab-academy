from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .store import (
    Assignment,
    Certification,
    LearningPlan,
    Quiz,
    QuizQuestion,
    Section,
    SectionCompletion,
    Submission,
    add_xp,
    awarded_badges,
    get_certification_for_user_plan,
    get_learning_plan,
    get_lesson,
    get_section_completion_for_user,
    is_stage2_completed,
    list_certifications,
    list_section_completions,
    list_submissions_for,
    next_certification_id,
    next_section_completion_id,
    next_submission_id,
    save_certification,
    save_section_completion,
    save_submission,
    utcnow,
    watched_lessons,
)


def normalize_text(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "t", "yes", "y", "1"}:
            return True
        if lowered in {"false", "f", "no", "n", "0"}:
            return False
    return None


def question_public_view(question: QuizQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "prompt": question.prompt,
        "question_type": question.question_type,
        "options": question.options,
        "points": question.points,
    }


def assignment_public_view(assignment: Assignment) -> dict[str, Any]:
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "instructions": assignment.instructions,
        "pass_threshold": assignment.pass_threshold,
    }


def check_and_award_badges(user_id: str, *, passed: bool, perfect: bool, source: str) -> list[str]:
    awarded_badges.setdefault(user_id, set())
    badge_ids: list[str] = []

    if passed and "quiz_pass" not in awarded_badges[user_id]:
        awarded_badges[user_id].add("quiz_pass")
        badge_ids.append("quiz_pass")

    if perfect and "quiz_perfect" not in awarded_badges[user_id]:
        awarded_badges[user_id].add("quiz_perfect")
        badge_ids.append("quiz_perfect")

    if source == "assignment" and passed and "assignment_pass" not in awarded_badges[user_id]:
        awarded_badges[user_id].add("assignment_pass")
        badge_ids.append("assignment_pass")

    return badge_ids


def quiz_xp_for_score(score: float, pass_threshold: float) -> int:
    if score >= 100:
        return 100
    if score >= pass_threshold:
        return 50
    return 0


def create_quiz_attempt_submission(
    *,
    quiz: Quiz,
    user_id: str,
    answers: list[dict[str, Any]],
) -> Submission:
    answer_map = {answer["question_id"]: answer["answer"] for answer in answers}
    results: list[dict[str, Any]] = []
    earned_points = 0.0
    total_points = 0.0
    needs_manual_review = False

    for question in quiz.questions:
        total_points += question.points
        provided_answer = answer_map.get(question.id)

        if question.question_type == "mc":
            is_correct = normalize_text(provided_answer) == normalize_text(question.correct_answer)
            points = question.points if is_correct else 0.0
            earned_points += points
            results.append(
                {
                    "question_id": question.id,
                    "question_type": question.question_type,
                    "answer": provided_answer,
                    "is_correct": is_correct,
                    "needs_review": False,
                    "earned_points": points,
                }
            )
            continue

        if question.question_type == "true_false":
            provided_bool = normalize_bool(provided_answer)
            is_correct = provided_bool is not None and provided_bool == normalize_bool(question.correct_answer)
            points = question.points if is_correct else 0.0
            earned_points += points
            results.append(
                {
                    "question_id": question.id,
                    "question_type": question.question_type,
                    "answer": provided_answer,
                    "is_correct": is_correct,
                    "needs_review": False,
                    "earned_points": points,
                }
            )
            continue

        needs_manual_review = True
        results.append(
            {
                "question_id": question.id,
                "question_type": question.question_type,
                "answer": provided_answer,
                "is_correct": None,
                "needs_review": True,
                "earned_points": 0.0,
            }
        )

    score = round((earned_points / total_points) * 100, 2) if total_points else 0.0
    passed = score >= quiz.pass_threshold
    submission = Submission(
        id=next_submission_id(),
        kind="quiz",
        user_id=user_id,
        related_id=quiz.id,
        status="pending_review" if needs_manual_review else "graded",
        score=score,
        passed=passed,
        xp_awarded=0,
        manual_review_required=needs_manual_review,
        payload={
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "answers": answers,
            "results": results,
            "provisional_score": score,
            "pass_threshold": quiz.pass_threshold,
        },
    )

    if not needs_manual_review:
        submission.xp_awarded = quiz_xp_for_score(score, quiz.pass_threshold)
        if submission.xp_awarded:
            add_xp(user_id, submission.xp_awarded)
        submission.badge_ids = check_and_award_badges(
            user_id,
            passed=passed,
            perfect=score >= 100,
            source="quiz",
        )

    submission.updated_at = utcnow()
    return save_submission(submission)


def create_assignment_submission(
    *,
    assignment: Assignment,
    user_id: str,
    file_url: str | None,
    text_answer: str | None,
) -> Submission:
    submission = Submission(
        id=next_submission_id(),
        kind="assignment",
        user_id=user_id,
        related_id=assignment.id,
        status="pending_review",
        score=None,
        passed=None,
        xp_awarded=20,
        manual_review_required=True,
        payload={
            "assignment_id": assignment.id,
            "assignment_title": assignment.title,
            "file_url": file_url,
            "text_answer": text_answer,
            "pass_threshold": assignment.pass_threshold,
        },
    )
    add_xp(user_id, 20)
    submission.updated_at = utcnow()
    return save_submission(submission)


def finalize_grade(submission: Submission, score: float) -> Submission:
    submission.score = round(score, 2)
    submission.status = "graded"
    submission.manual_review_required = False
    submission.updated_at = utcnow()

    if submission.kind == "quiz":
        quiz_pass_threshold = float(submission.payload.get("pass_threshold", 70.0))
        submission.passed = submission.score >= quiz_pass_threshold
        current_xp = quiz_xp_for_score(submission.score, quiz_pass_threshold)
        if current_xp > submission.xp_awarded:
            add_xp(submission.user_id, current_xp - submission.xp_awarded)
            submission.xp_awarded = current_xp
        submission.badge_ids = check_and_award_badges(
            submission.user_id,
            passed=bool(submission.passed),
            perfect=submission.score >= 100,
            source="quiz",
        )
        submission.payload["final_score"] = submission.score
        return save_submission(submission)

    if submission.kind == "assignment":
        assignment_pass_threshold = float(submission.payload.get("pass_threshold", 70.0))
        submission.passed = submission.score >= assignment_pass_threshold
        submission.payload["final_score"] = submission.score
        return save_submission(submission)

    return save_submission(submission)


def serialize_submission(submission: Submission) -> dict[str, Any]:
    data = asdict(submission)
    data["created_at"] = submission.created_at.isoformat()
    data["updated_at"] = submission.updated_at.isoformat()
    return data


def _missing_mandatory_lessons(user_id: str, section: Section) -> list[int]:
    watched = watched_lessons(user_id)
    missing: list[int] = []
    for lesson_id in section.lesson_ids:
        lesson = get_lesson(lesson_id)
        if lesson is None or not lesson.mandatory:
            continue
        if lesson_id not in watched:
            missing.append(lesson_id)
    return missing


def _missing_passed_quizzes(user_id: str, section: Section) -> list[int]:
    missing: list[int] = []
    for quiz_id in section.quiz_ids:
        attempts = list_submissions_for(user_id=user_id, kind="quiz", related_id=quiz_id)
        if not any(attempt.status == "graded" and bool(attempt.passed) for attempt in attempts):
            missing.append(quiz_id)
    return missing


def _missing_assignments_at_least_80(user_id: str, section: Section) -> list[int]:
    missing: list[int] = []
    for assignment_id in section.assignment_ids:
        attempts = list_submissions_for(user_id=user_id, kind="assignment", related_id=assignment_id)
        if not any(
            attempt.status == "graded" and attempt.score is not None and float(attempt.score) >= 80.0
            for attempt in attempts
        ):
            missing.append(assignment_id)
    return missing


def validate_section_completion(user_id: str, section: Section) -> dict[str, list[int]]:
    return {
        "missing_mandatory_lessons": _missing_mandatory_lessons(user_id, section),
        "missing_passed_quizzes": _missing_passed_quizzes(user_id, section),
        "missing_assignments_at_least_80": _missing_assignments_at_least_80(user_id, section),
    }


def confirm_section_completion(user_id: str, section: Section) -> tuple[SectionCompletion | None, dict[str, list[int]]]:
    existing = get_section_completion_for_user(user_id, section.id)
    if existing is not None:
        return existing, {"missing_mandatory_lessons": [], "missing_passed_quizzes": [], "missing_assignments_at_least_80": []}

    validation = validate_section_completion(user_id, section)
    if any(validation.values()):
        return None, validation

    completion = SectionCompletion(
        id=next_section_completion_id(),
        user_id=user_id,
        section_id=section.id,
    )
    completion.completed_at = utcnow()
    return save_section_completion(completion), validation


def list_my_certifications(user_id: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for certification in list_certifications(user_id=user_id):
        plan = get_learning_plan(certification.plan_id)
        results.append(
            {
                "id": certification.id,
                "user_id": certification.user_id,
                "plan_id": certification.plan_id,
                "plan_name": plan.name if plan else None,
                "certificate_url": certification.certificate_url,
                "certificate_text": certification.certificate_text,
                "created_at": certification.created_at.isoformat(),
            }
        )
    return results


def _all_plan_sections_completed(user_id: str, plan: LearningPlan) -> bool:
    completed_section_ids = {completion.section_id for completion in list_section_completions(user_id=user_id)}
    return all(section_id in completed_section_ids for section_id in plan.section_ids)


def generate_certification(user_id: str, user_name: str, plan: LearningPlan) -> tuple[Certification | None, dict[str, Any]]:
    existing = get_certification_for_user_plan(user_id, plan.id)
    if existing is not None:
        return existing, {"all_sections_completed": True, "stage2_completed": True}

    all_sections_completed = _all_plan_sections_completed(user_id, plan)
    stage2_done = is_stage2_completed(user_id)
    checks = {"all_sections_completed": all_sections_completed, "stage2_completed": stage2_done}
    if not all_sections_completed or not stage2_done:
        return None, checks

    certificate_id = next_certification_id()
    certificate_url = f"https://mock.nano-lab-academy.local/certificates/{certificate_id}.pdf"
    certificate_text = f"Congratulations {user_name} for completing {plan.name}"
    certification = Certification(
        id=certificate_id,
        user_id=user_id,
        plan_id=plan.id,
        certificate_url=certificate_url,
        certificate_text=certificate_text,
    )
    save_certification(certification)

    awarded_badges.setdefault(user_id, set()).add("Certified")
    return certification, checks
