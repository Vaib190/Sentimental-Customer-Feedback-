"""SQLite storage for analyzed customer reviews."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("reviews.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_text TEXT NOT NULL,
                label TEXT NOT NULL,
                score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
                theme TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def save_review(review_text: str, label: str, score: int, theme: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO reviews (review_text, label, score, theme) VALUES (?, ?, ?, ?)",
            (review_text, label, score, theme),
        )


def get_reviews(limit: int = 100) -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            "SELECT id, review_text, label, score, theme, created_at "
            "FROM reviews ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
