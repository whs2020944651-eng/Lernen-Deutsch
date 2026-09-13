"""
vocab_db.py - SQLite Database Module for Vocabulary Management

Provides schema definition, CRUD operations, spaced repetition helpers,
and CSV export functionality for the German language learning platform.
"""

import csv
import io
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB_PATH = "vocabulary.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create and return a SQLite database connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initialize SQLite database schema for vocabulary management.
    Ensures table exists and performs safe migration for missing columns.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL COLLATE NOCASE,
            translation TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            last_reviewed TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            part_of_speech TEXT DEFAULT '',
            example TEXT DEFAULT '',
            frequency INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check and add columns if upgrading from earlier schema versions
    cursor.execute("PRAGMA table_info(vocabulary)")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    columns_to_ensure = [
        ("difficulty", "TEXT DEFAULT 'medium'"),
        ("last_reviewed", "TIMESTAMP"),
        ("review_count", "INTEGER DEFAULT 0"),
        ("part_of_speech", "TEXT DEFAULT ''"),
        ("example", "TEXT DEFAULT ''"),
        ("frequency", "INTEGER DEFAULT 1"),
        ("created_at", "TIMESTAMP"),
        ("updated_at", "TIMESTAMP"),
    ]

    for col_name, col_def in columns_to_ensure:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE vocabulary ADD COLUMN {col_name} {col_def}")

    # Index for fast word lookups and spaced repetition queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_vocab_review 
        ON vocabulary(last_reviewed, review_count)
    """)

    conn.commit()
    conn.close()


def add_word(
    word: str,
    translation: str,
    difficulty: str = "medium",
    part_of_speech: str = "",
    example: str = "",
    db_path: str = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """
    Add a new vocabulary word or update existing word translation and difficulty.
    Handles case-insensitive deduplication safely.
    """
    word = word.strip()
    translation = translation.strip()
    if not word:
        raise ValueError("Word cannot be empty.")
    if not translation:
        raise ValueError("Translation cannot be empty.")

    difficulty = difficulty.strip().lower() if difficulty else "medium"
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM vocabulary WHERE LOWER(word) = LOWER(?)", (word,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE vocabulary
            SET word = ?,
                translation = ?,
                difficulty = ?,
                frequency = frequency + 1,
                part_of_speech = CASE WHEN ? != '' THEN ? ELSE part_of_speech END,
                example = CASE WHEN ? != '' THEN ? ELSE example END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (word, translation, difficulty, part_of_speech.strip(), part_of_speech.strip(),
              example.strip(), example.strip(), existing["id"]))
        word_id = existing["id"]
    else:
        cursor.execute("""
            INSERT INTO vocabulary (word, translation, difficulty, part_of_speech, example)
            VALUES (?, ?, ?, ?, ?)
        """, (word, translation, difficulty, part_of_speech.strip(), example.strip()))
        word_id = cursor.lastrowid

    conn.commit()
    cursor.execute("SELECT * FROM vocabulary WHERE id = ?", (word_id,))
    row = cursor.fetchone()
    result = dict(row) if row else {}
    conn.close()
    return result


def get_word(word: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve a single word entry by exact word match (case-insensitive)."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vocabulary WHERE LOWER(word) = LOWER(?)", (word.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def list_words(
    limit: Optional[int] = None,
    difficulty: Optional[str] = None,
    sort_by: str = "word",
    db_path: str = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """
    List vocabulary words with optional filters, ordering, and limit.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    valid_sorts = {
        "word": "word ASC",
        "created_at": "created_at DESC",
        "frequency": "frequency DESC",
        "review_count": "review_count DESC",
        "last_reviewed": "last_reviewed DESC",
    }
    order_clause = valid_sorts.get(sort_by, "word ASC")

    query = "SELECT * FROM vocabulary"
    params: List[Any] = []

    if difficulty:
        query += " WHERE LOWER(difficulty) = LOWER(?)"
        params.append(difficulty.strip())

    query += f" ORDER BY {order_clause}"

    if limit is not None and limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_word(
    word: str,
    translation: Optional[str] = None,
    difficulty: Optional[str] = None,
    example: Optional[str] = None,
    part_of_speech: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> bool:
    """Update specific fields of an existing vocabulary entry."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    updates = []
    params = []

    if translation is not None:
        updates.append("translation = ?")
        params.append(translation.strip())

    if difficulty is not None:
        diff_val = difficulty.strip().lower()
        if diff_val in {"easy", "medium", "hard"}:
            updates.append("difficulty = ?")
            params.append(diff_val)

    if example is not None:
        updates.append("example = ?")
        params.append(example.strip())

    if part_of_speech is not None:
        updates.append("part_of_speech = ?")
        params.append(part_of_speech.strip())

    if not updates:
        conn.close()
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    sql = f"UPDATE vocabulary SET {', '.join(updates)} WHERE LOWER(word) = LOWER(?)"
    params.append(word.strip())

    cursor.execute(sql, tuple(params))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def delete_word(word: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Delete a vocabulary entry by word."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vocabulary WHERE LOWER(word) = LOWER(?)", (word.strip(),))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def get_words_for_review(
    limit: int = 5,
    db_path: str = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """
    Select candidate words for spaced repetition practice.
    Prioritizes words never reviewed first, then words least recently reviewed.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM vocabulary
        ORDER BY 
            CASE WHEN last_reviewed IS NULL THEN 0 ELSE 1 END ASC,
            last_reviewed ASC,
            review_count ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_review(
    word: str,
    success: bool,
    db_path: str = DEFAULT_DB_PATH,
) -> Optional[Dict[str, Any]]:
    """
    Record review attempt for spaced repetition tracking.
    Increments review_count and updates last_reviewed timestamp.
    Adjusts difficulty based on success (e.g. promoting hard -> medium -> easy).
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vocabulary WHERE LOWER(word) = LOWER(?)", (word.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    current_difficulty = row["difficulty"] or "medium"
    new_difficulty = current_difficulty

    if success:
        if current_difficulty == "hard":
            new_difficulty = "medium"
        elif current_difficulty == "medium" and (row["review_count"] or 0) >= 3:
            new_difficulty = "easy"
    else:
        new_difficulty = "hard"

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE vocabulary
        SET review_count = review_count + 1,
            last_reviewed = ?,
            difficulty = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (now_iso, new_difficulty, row["id"]))

    conn.commit()
    cursor.execute("SELECT * FROM vocabulary WHERE id = ?", (row["id"],))
    updated_row = cursor.fetchone()
    result = dict(updated_row) if updated_row else None
    conn.close()
    return result


def export_csv(
    file_path: str = "vocabulary_export.csv",
    db_path: str = DEFAULT_DB_PATH,
) -> str:
    """
    Export all vocabulary words to a CSV file with required schema headers.
    Returns the absolute path of the generated CSV file.
    """
    init_db(db_path)
    words = list_words(sort_by="word", db_path=db_path)

    fieldnames = [
        "word",
        "translation",
        "difficulty",
        "last_reviewed",
        "review_count",
        "part_of_speech",
        "example",
    ]

    # Normalize output path
    resolved_path = os.path.abspath(file_path)
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

    with open(resolved_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for w in words:
            writer.writerow({
                "word": w.get("word", ""),
                "translation": w.get("translation", ""),
                "difficulty": w.get("difficulty", "medium"),
                "last_reviewed": w.get("last_reviewed") or "",
                "review_count": w.get("review_count", 0),
                "part_of_speech": w.get("part_of_speech", ""),
                "example": w.get("example", ""),
            })

    return resolved_path


def get_vocabulary_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Retrieve aggregate statistics regarding vocabulary progress."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total_words = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE review_count > 0")
    reviewed_words = cursor.fetchone()[0]

    cursor.execute("""
        SELECT difficulty, COUNT(*) as cnt 
        FROM vocabulary 
        GROUP BY difficulty
    """)
    difficulty_counts = {row["difficulty"]: row["cnt"] for row in cursor.fetchall()}

    conn.close()
    return {
        "total_words": total_words,
        "reviewed_words": reviewed_words,
        "difficulty_counts": difficulty_counts,
    }
