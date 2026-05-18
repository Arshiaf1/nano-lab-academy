from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .framework import HTTPException, Router


DB_PATH = Path(__file__).resolve().parent / "gamification.db"
router = Router(prefix="/gamification")


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
            CREATE TABLE IF NOT EXISTS user_xp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_streaks (
                user_id TEXT PRIMARY KEY,
                streak_count INTEGER NOT NULL DEFAULT 0,
                last_activity_date TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                score REAL,
                passed INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS badges (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                criteria_type TEXT NOT NULL,
                source TEXT,
                threshold INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_badges (
                user_id TEXT NOT NULL,
                badge_id TEXT NOT NULL,
                awarded_at TEXT NOT NULL,
                PRIMARY KEY (user_id, badge_id),
                FOREIGN KEY (badge_id) REFERENCES badges(id)
            );
            """
        )
        _seed_badges(connection)


def _seed_badges(connection: sqlite3.Connection) -> None:
    existing = connection.execute("SELECT COUNT(*) AS count FROM badges").fetchone()
    if existing is not None and int(existing["count"]) > 0:
        return

    connection.executemany(
        """
        INSERT INTO badges (id, name, description, criteria_type, source, threshold)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            ("quiz_perfect_5", "Quiz Perfect 5", "Achieve 5 perfect quiz scores.", "perfect_count", "quiz", 5),
            ("quiz_pass_10", "Quiz Grinder", "Pass 10 quizzes.", "passed_count", "quiz", 10),
            ("assignment_pass_3", "Assignment Ace", "Pass 3 assignments.", "passed_count", "assignment", 3),
            ("streak_7", "7-Day Streak", "Maintain a 7-day learning streak.", "current_streak", None, 7),
            ("xp_500", "XP 500", "Earn 500 total XP.", "xp_total", None, 500),
        ],
    )


def award_xp(user_id: str, amount: int, source: str) -> None:
    with _connect() as connection:
        connection.execute(
            "INSERT INTO user_xp (user_id, amount, source, created_at) VALUES (?, ?, ?, ?)",
            (user_id, amount, source, _utc_timestamp()),
        )


def update_streak(user_id: str) -> int:
    today = date.today()
    yesterday = today - timedelta(days=1)

    with _connect() as connection:
        row = connection.execute(
            "SELECT streak_count, last_activity_date FROM user_streaks WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        if row is None:
            streak_count = 1
        else:
            last_activity_date = date.fromisoformat(row["last_activity_date"])
            if last_activity_date == today:
                streak_count = int(row["streak_count"]) + 1
            elif last_activity_date == yesterday:
                streak_count = int(row["streak_count"]) + 1
            else:
                streak_count = 1

        connection.execute(
            """
            INSERT INTO user_streaks (user_id, streak_count, last_activity_date, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                streak_count = excluded.streak_count,
                last_activity_date = excluded.last_activity_date,
                updated_at = excluded.updated_at
            """,
            (user_id, streak_count, today.isoformat(), _utc_timestamp()),
        )
        return streak_count


def record_activity(
    user_id: str,
    *,
    event_type: str,
    source: str,
    score: float | None = None,
    passed: bool | None = None,
) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO user_activity (user_id, event_type, source, score, passed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, event_type, source, score, None if passed is None else int(passed), _utc_timestamp()),
        )


def _metric_value(connection: sqlite3.Connection, user_id: str, criteria_type: str, source: str | None) -> int:
    if criteria_type == "xp_total":
        row = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) AS value FROM user_xp WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["value"]) if row else 0

    if criteria_type == "current_streak":
        row = connection.execute(
            "SELECT COALESCE(streak_count, 0) AS value FROM user_streaks WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["value"]) if row else 0

    if criteria_type == "event_count":
        row = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM user_activity
            WHERE user_id = ? AND source = ? AND event_type = 'submission'
            """,
            (user_id, source),
        ).fetchone()
        return int(row["value"]) if row else 0

    if criteria_type == "perfect_count":
        row = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM user_activity
            WHERE user_id = ? AND source = ? AND score >= 100
            """,
            (user_id, source),
        ).fetchone()
        return int(row["value"]) if row else 0

    if criteria_type == "passed_count":
        row = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM user_activity
            WHERE user_id = ? AND source = ? AND passed = 1
            """,
            (user_id, source),
        ).fetchone()
        return int(row["value"]) if row else 0

    return 0


def check_and_award_badges(user_id: str) -> list[str]:
    awarded: list[str] = []
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT b.id, b.criteria_type, b.source, b.threshold
            FROM badges b
            LEFT JOIN user_badges ub ON ub.badge_id = b.id AND ub.user_id = ?
            WHERE ub.badge_id IS NULL
            """,
            (user_id,),
        ).fetchall()

        for badge in rows:
            metric_value = _metric_value(connection, user_id, str(badge["criteria_type"]), badge["source"])
            if metric_value < int(badge["threshold"]):
                continue
            connection.execute(
                "INSERT INTO user_badges (user_id, badge_id, awarded_at) VALUES (?, ?, ?)",
                (user_id, badge["id"], _utc_timestamp()),
            )
            awarded.append(str(badge["id"]))

    return awarded


def get_user_status(user_id: str) -> dict[str, Any]:
    with _connect() as connection:
        xp_row = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total_xp FROM user_xp WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        streak_row = connection.execute(
            "SELECT COALESCE(streak_count, 0) AS streak_count FROM user_streaks WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        badges_rows = connection.execute(
            """
            SELECT b.id, b.name, b.description, ub.awarded_at
            FROM user_badges ub
            JOIN badges b ON b.id = ub.badge_id
            WHERE ub.user_id = ?
            ORDER BY ub.awarded_at DESC
            """,
            (user_id,),
        ).fetchall()

    return {
        "user_id": user_id,
        "total_xp": int(xp_row["total_xp"]) if xp_row else 0,
        "current_streak": int(streak_row["streak_count"]) if streak_row else 0,
        "badges": [
            {
                "id": str(row["id"]),
                "name": str(row["name"]),
                "description": str(row["description"]),
                "awarded_at": str(row["awarded_at"]),
            }
            for row in badges_rows
        ],
    }


def get_leaderboard(period: str) -> list[dict[str, Any]]:
    period_modifiers = {
        "daily": "-1 day",
        "weekly": "-7 days",
        "monthly": "-30 days",
        "all_time": None,
    }
    if period not in period_modifiers:
        raise HTTPException(status_code=400, detail="period must be one of daily, weekly, monthly, all_time")

    with _connect() as connection:
        if period_modifiers[period] is None:
            rows = connection.execute(
                """
                SELECT user_id, COALESCE(SUM(amount), 0) AS xp_earned
                FROM user_xp
                GROUP BY user_id
                ORDER BY xp_earned DESC, user_id ASC
                LIMIT 10
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT user_id, COALESCE(SUM(amount), 0) AS xp_earned
                FROM user_xp
                WHERE created_at >= datetime('now', ?)
                GROUP BY user_id
                ORDER BY xp_earned DESC, user_id ASC
                LIMIT 10
                """,
                (period_modifiers[period],),
            ).fetchall()

    return [{"user_id": str(row["user_id"]), "xp_earned": int(row["xp_earned"])} for row in rows]


@router.get("/status")
def gamification_status(user_id: str = "me") -> dict[str, Any]:
    return get_user_status(user_id)


@router.get("/leaderboard")
def gamification_leaderboard(period: str = "weekly") -> dict[str, Any]:
    return {"period": period, "leaders": get_leaderboard(period)}


_initialize()
