from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .store import (
    Assignment,
    Enrollment,
    Payment,
    Quiz,
    QuizQuestion,
    Submission,
    UserAccount,
    add_xp,
    awarded_badges,
    next_submission_id,
    save_submission,
    utcnow,
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


def serialize_user(user: UserAccount) -> dict[str, Any]:
    data = asdict(user)
    if user.plan_active_until is not None:
        data["plan_active_until"] = user.plan_active_until.isoformat()
    data["updated_at"] = user.updated_at.isoformat()
    return data


def serialize_enrollment(enrollment: Enrollment) -> dict[str, Any]:
    data = asdict(enrollment)
    if enrollment.stage1_deadline is not None:
        data["stage1_deadline"] = enrollment.stage1_deadline.isoformat()
    data["updated_at"] = enrollment.updated_at.isoformat()
    return data


def serialize_payment(payment: Payment) -> dict[str, Any]:
    data = asdict(payment)
    data["created_at"] = payment.created_at.isoformat()
    data["updated_at"] = payment.updated_at.isoformat()
    if payment.paid_at is not None:
        data["paid_at"] = payment.paid_at.isoformat()
    return data
