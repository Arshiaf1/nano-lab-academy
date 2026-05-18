from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .framework import HTTPException, Router


DB_PATH = Path(__file__).resolve().parent / "gamification.db"
router = Router(prefix="/stage")
_ALLOWED_WHEN_LOCKED = {"/stage/status", "/stage/check-stage1", "/stage/check-stage2", "/stage/payment/unlock"}


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _initialize() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS course_quizzes (
                course_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                PRIMARY KEY (course_id, quiz_id)
            );

            CREATE TABLE IF NOT EXISTS course_assignments (
                course_id INTEGER NOT NULL,
                assignment_id INTEGER NOT NULL,
                PRIMARY KEY (course_id, assignment_id)
            );

            CREATE TABLE IF NOT EXISTS course_exams (
                course_id INTEGER NOT NULL,
                exam_id INTEGER NOT NULL,
                is_final INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (course_id, exam_id)
            );

            CREATE TABLE IF NOT EXISTS course_enrollments (
                user_id TEXT PRIMARY KEY,
                course_id INTEGER NOT NULL,
                enrolled_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_stages (
                user_id TEXT PRIMARY KEY,
                stage INTEGER NOT NULL DEFAULT 1,
                stage1_completed INTEGER NOT NULL DEFAULT 0,
                stage1_locked INTEGER NOT NULL DEFAULT 0,
                stage1_deadline TEXT NOT NULL,
                stage2_completed INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                quiz_id INTEGER NOT NULL,
                score REAL,
                passed INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assignment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                assignment_id INTEGER NOT NULL,
                score REAL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS exam_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                exam_id INTEGER NOT NULL,
                score REAL NOT NULL,
                passed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS final_supervisor_ratings (
                user_id TEXT PRIMARY KEY,
                approved INTEGER NOT NULL,
                overall_score REAL NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        _seed_course_catalog(connection)


def _seed_course_catalog(connection: sqlite3.Connection) -> None:
    connection.execute("INSERT OR IGNORE INTO courses (id, name) VALUES (1, 'Nano Lab Starter')")
    connection.execute("INSERT OR IGNORE INTO course_quizzes (course_id, quiz_id) VALUES (1, 1)")
    connection.execute("INSERT OR IGNORE INTO course_assignments (course_id, assignment_id) VALUES (1, 1)")
    connection.execute("INSERT OR IGNORE INTO course_exams (course_id, exam_id, is_final) VALUES (1, 1, 1)")


def _ensure_user_stage(user_id: str) -> None:
    with _connect() as connection:
        enrollment = connection.execute(
            "SELECT course_id FROM course_enrollments WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if enrollment is None:
            connection.execute(
                "INSERT INTO course_enrollments (user_id, course_id, enrolled_at) VALUES (?, 1, ?)",
                (user_id, _utc_timestamp()),
            )

        stage_row = connection.execute(
            "SELECT user_id FROM user_stages WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if stage_row is None:
            deadline = (date.today() + timedelta(days=14)).isoformat()
            connection.execute(
                """
                INSERT INTO user_stages (user_id, stage, stage1_completed, stage1_locked, stage1_deadline, stage2_completed, updated_at)
                VALUES (?, 1, 0, 0, ?, 0, ?)
                """,
                (user_id, deadline, _utc_timestamp()),
            )


def _sync_stage1_lock(user_id: str) -> dict[str, Any]:
    _ensure_user_stage(user_id)
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT stage, stage1_completed, stage1_locked, stage1_deadline, stage2_completed
            FROM user_stages
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Stage state not found")

        completed = bool(row["stage1_completed"])
        locked = bool(row["stage1_locked"])
        deadline = date.fromisoformat(str(row["stage1_deadline"]))
        if not completed and not locked and date.today() > deadline:
            locked = True
            connection.execute(
                "UPDATE user_stages SET stage1_locked = 1, updated_at = ? WHERE user_id = ?",
                (_utc_timestamp(), user_id),
            )

        return {
            "stage": int(row["stage"]),
            "stage1_completed": completed,
            "stage1_locked": locked,
            "stage1_deadline": str(row["stage1_deadline"]),
            "stage2_completed": bool(row["stage2_completed"]),
        }


def enforce_stage1_access(user_id: str, path: str, *, is_free_content: bool = False) -> None:
    state = _sync_stage1_lock(user_id)
    if state["stage1_locked"] and not is_free_content and path not in _ALLOWED_WHEN_LOCKED:
        raise HTTPException(
            status_code=403,
            detail="Stage 1 is locked because the deadline passed. Complete payment to unlock access.",
        )


def record_quiz_attempt(user_id: str, quiz_id: int, score: float | None, passed: bool | None) -> None:
    _ensure_user_stage(user_id)
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO quiz_attempts (user_id, quiz_id, score, passed, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, quiz_id, score, None if passed is None else int(passed), _utc_timestamp()),
        )


def record_assignment_submission(user_id: str, assignment_id: int, score: float | None) -> None:
    _ensure_user_stage(user_id)
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO assignment_submissions (user_id, assignment_id, score, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, assignment_id, score, _utc_timestamp()),
        )


def record_exam_attempt(user_id: str, exam_id: int, score: float) -> None:
    _ensure_user_stage(user_id)
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO exam_attempts (user_id, exam_id, score, passed, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, exam_id, score, int(score >= 80), _utc_timestamp()),
        )


def _get_user_course_id(connection: sqlite3.Connection, user_id: str) -> int | None:
    row = connection.execute(
        "SELECT course_id FROM course_enrollments WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return int(row["course_id"]) if row else None


def _quiz_progress(connection: sqlite3.Connection, user_id: str, course_id: int) -> tuple[int, int]:
    quiz_rows = connection.execute(
        "SELECT quiz_id FROM course_quizzes WHERE course_id = ? ORDER BY quiz_id",
        (course_id,),
    ).fetchall()
    total = len(quiz_rows)
    passed_count = 0
    for quiz_row in quiz_rows:
        latest = connection.execute(
            """
            SELECT passed
            FROM quiz_attempts
            WHERE user_id = ? AND quiz_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT 1
            """,
            (user_id, int(quiz_row["quiz_id"])),
        ).fetchone()
        if latest is not None and latest["passed"] == 1:
            passed_count += 1
    return passed_count, total


def _assignment_progress(connection: sqlite3.Connection, user_id: str, course_id: int) -> tuple[int, int]:
    assignment_rows = connection.execute(
        "SELECT assignment_id FROM course_assignments WHERE course_id = ? ORDER BY assignment_id",
        (course_id,),
    ).fetchall()
    total = len(assignment_rows)
    passed_count = 0
    for assignment_row in assignment_rows:
        latest = connection.execute(
            """
            SELECT score
            FROM assignment_submissions
            WHERE user_id = ? AND assignment_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT 1
            """,
            (user_id, int(assignment_row["assignment_id"])),
        ).fetchone()
        if latest is not None and latest["score"] is not None and float(latest["score"]) >= 80:
            passed_count += 1
    return passed_count, total


def _exam_progress(connection: sqlite3.Connection, user_id: str, course_id: int) -> tuple[int, int]:
    exam_rows = connection.execute(
        "SELECT exam_id FROM course_exams WHERE course_id = ? AND is_final = 1 ORDER BY exam_id",
        (course_id,),
    ).fetchall()
    total = len(exam_rows)
    passed_count = 0
    for exam_row in exam_rows:
        attempt = connection.execute(
            """
            SELECT id
            FROM exam_attempts
            WHERE user_id = ? AND exam_id = ? AND score >= 80
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT 1
            """,
            (user_id, int(exam_row["exam_id"])),
        ).fetchone()
        if attempt is not None:
            passed_count += 1
    return passed_count, total


def _to_percentage(done: int, total: int) -> float:
    if total <= 0:
        return 100.0
    return round((done / total) * 100, 2)


def _status_payload(user_id: str) -> dict[str, Any]:
    state = _sync_stage1_lock(user_id)
    with _connect() as connection:
        course_id = _get_user_course_id(connection, user_id)
        if course_id is None:
            raise HTTPException(status_code=404, detail="User is not enrolled in any course")

        quiz_done, quiz_total = _quiz_progress(connection, user_id, course_id)
        assignment_done, assignment_total = _assignment_progress(connection, user_id, course_id)
        exam_done, exam_total = _exam_progress(connection, user_id, course_id)
        total_items = quiz_total + assignment_total + exam_total
        done_items = quiz_done + assignment_done + exam_done

    return {
        "user_id": user_id,
        "current_stage": state["stage"],
        "stage1_completed": state["stage1_completed"],
        "stage1_locked": state["stage1_locked"],
        "deadline": state["stage1_deadline"],
        "stage1_deadline": state["stage1_deadline"],
        "stage2_completed": state["stage2_completed"],
        "progress_percentages": {
            "quizzes": _to_percentage(quiz_done, quiz_total),
            "assignments": _to_percentage(assignment_done, assignment_total),
            "final_exam": _to_percentage(exam_done, exam_total),
            "overall": _to_percentage(done_items, total_items),
        },
    }


@router.get("/status")
def get_stage_status(user_id: str = "me") -> dict[str, Any]:
    return _status_payload(user_id)


@router.post("/check-stage1")
def check_stage1(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    _ensure_user_stage(user_id)
    missing: dict[str, list[dict[str, Any]]] = {"quizzes": [], "assignments": [], "final_exams": []}

    with _connect() as connection:
        course_id = _get_user_course_id(connection, user_id)
        if course_id is None:
            raise HTTPException(status_code=404, detail="User is not enrolled in any course")

        quiz_rows = connection.execute(
            "SELECT quiz_id FROM course_quizzes WHERE course_id = ? ORDER BY quiz_id",
            (course_id,),
        ).fetchall()
        for quiz_row in quiz_rows:
            quiz_id = int(quiz_row["quiz_id"])
            latest = connection.execute(
                """
                SELECT score, passed
                FROM quiz_attempts
                WHERE user_id = ? AND quiz_id = ?
                ORDER BY datetime(created_at) DESC, id DESC
                LIMIT 1
                """,
                (user_id, quiz_id),
            ).fetchone()
            if latest is None:
                missing["quizzes"].append({"quiz_id": quiz_id, "reason": "missing_attempt"})
                continue
            if latest["passed"] != 1:
                missing["quizzes"].append({"quiz_id": quiz_id, "reason": "latest_attempt_not_passed", "score": latest["score"]})

        assignment_rows = connection.execute(
            "SELECT assignment_id FROM course_assignments WHERE course_id = ? ORDER BY assignment_id",
            (course_id,),
        ).fetchall()
        for assignment_row in assignment_rows:
            assignment_id = int(assignment_row["assignment_id"])
            latest = connection.execute(
                """
                SELECT score
                FROM assignment_submissions
                WHERE user_id = ? AND assignment_id = ?
                ORDER BY datetime(created_at) DESC, id DESC
                LIMIT 1
                """,
                (user_id, assignment_id),
            ).fetchone()
            if latest is None:
                missing["assignments"].append({"assignment_id": assignment_id, "reason": "missing_submission"})
                continue
            if latest["score"] is None or float(latest["score"]) < 80:
                missing["assignments"].append(
                    {"assignment_id": assignment_id, "reason": "latest_score_below_80", "score": latest["score"]}
                )

        exam_rows = connection.execute(
            "SELECT exam_id FROM course_exams WHERE course_id = ? AND is_final = 1 ORDER BY exam_id",
            (course_id,),
        ).fetchall()
        for exam_row in exam_rows:
            exam_id = int(exam_row["exam_id"])
            latest_pass = connection.execute(
                """
                SELECT id
                FROM exam_attempts
                WHERE user_id = ? AND exam_id = ? AND score >= 80
                ORDER BY datetime(created_at) DESC, id DESC
                LIMIT 1
                """,
                (user_id, exam_id),
            ).fetchone()
            if latest_pass is None:
                missing["final_exams"].append({"exam_id": exam_id, "reason": "no_attempt_with_score_gte_80"})

        success = all(not items for items in missing.values())
        if success:
            connection.execute(
                """
                UPDATE user_stages
                SET stage1_completed = 1, stage1_locked = 0, stage = 2, updated_at = ?
                WHERE user_id = ?
                """,
                (_utc_timestamp(), user_id),
            )

    return {
        "success": success,
        "user_id": user_id,
        "current_stage": 2 if success else 1,
        "missing_or_failed": missing,
    }


@router.post("/check-stage2")
def check_stage2(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    _ensure_user_stage(user_id)
    with _connect() as connection:
        row = connection.execute(
            "SELECT approved, overall_score FROM final_supervisor_ratings WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        approved = bool(row["approved"]) if row else False
        overall_score = float(row["overall_score"]) if row else 0.0
        success = approved and overall_score >= 80
        if success:
            connection.execute(
                """
                UPDATE user_stages
                SET stage2_completed = 1, stage = 3, updated_at = ?
                WHERE user_id = ?
                """,
                (_utc_timestamp(), user_id),
            )

    return {
        "success": success,
        "stub": True,
        "user_id": user_id,
        "current_stage": 3 if success else 2,
        "requirements": {
            "final_supervisor_ratings_approved": approved,
            "overall_score": overall_score,
            "overall_score_required": 80,
        },
    }


@router.get("/payment/unlock")
def payment_unlock_status(user_id: str = "me") -> dict[str, Any]:
    state = _sync_stage1_lock(user_id)
    return {
        "user_id": user_id,
        "stage1_locked": state["stage1_locked"],
        "payment_required": bool(state["stage1_locked"]),
    }


@router.post("/payment/unlock")
def payment_unlock(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    _ensure_user_stage(user_id)
    with _connect() as connection:
        connection.execute(
            "UPDATE user_stages SET stage1_locked = 0, updated_at = ? WHERE user_id = ?",
            (_utc_timestamp(), user_id),
        )
    return {"success": True, "user_id": user_id, "stage1_locked": False}


_initialize()
