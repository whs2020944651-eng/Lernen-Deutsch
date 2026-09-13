"""
Unit tests for vocab_db.py module and vocabulary CLI commands.
"""

import csv
import os
import sqlite3
import pytest
from unittest.mock import patch

import vocab_db
import main


@pytest.fixture
def temp_db(tmp_path):
    """Provide a temporary database path for isolated testing."""
    db_file = tmp_path / "test_vocabulary.db"
    return str(db_file)


def test_init_db(temp_db):
    """Test database schema initialization and table creation."""
    vocab_db.init_db(temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(vocabulary)")
    cols = {row[1] for row in cursor.fetchall()}
    conn.close()

    expected = {
        "id", "word", "translation", "difficulty", "last_reviewed",
        "review_count", "part_of_speech", "example", "frequency",
        "created_at", "updated_at"
    }
    assert expected.issubset(cols)


def test_add_word(temp_db):
    """Test adding a single vocabulary word."""
    entry = vocab_db.add_word("Buch", "book", difficulty="easy", part_of_speech="noun", example="Das Buch ist gut.", db_path=temp_db)
    assert entry["word"] == "Buch"
    assert entry["translation"] == "book"
    assert entry["difficulty"] == "easy"
    assert entry["frequency"] == 1
    assert entry["review_count"] == 0
    assert entry["last_reviewed"] is None


def test_add_word_duplicate(temp_db):
    """Test adding duplicate word updates translation, difficulty, and increments frequency."""
    vocab_db.add_word("Haus", "building", difficulty="hard", db_path=temp_db)
    updated = vocab_db.add_word("Haus", "house", difficulty="easy", db_path=temp_db)
    assert updated["word"] == "Haus"
    assert updated["translation"] == "house"
    assert updated["difficulty"] == "easy"
    assert updated["frequency"] == 2


def test_add_word_validation(temp_db):
    """Test empty word or translation raises ValueError."""
    with pytest.raises(ValueError):
        vocab_db.add_word("", "apple", db_path=temp_db)
    with pytest.raises(ValueError):
        vocab_db.add_word("Apfel", "  ", db_path=temp_db)


def test_get_word(temp_db):
    """Test retrieving word case-insensitively and non-existent word."""
    vocab_db.add_word("Katze", "cat", db_path=temp_db)
    res = vocab_db.get_word("katze", db_path=temp_db)
    assert res is not None
    assert res["word"] == "Katze"
    assert res["translation"] == "cat"

    assert vocab_db.get_word("Hund", db_path=temp_db) is None


def test_list_words(temp_db):
    """Test listing words with sorting and filtering."""
    vocab_db.add_word("Apfel", "apple", difficulty="easy", db_path=temp_db)
    vocab_db.add_word("Banane", "banana", difficulty="medium", db_path=temp_db)
    vocab_db.add_word("Zitrone", "lemon", difficulty="hard", db_path=temp_db)

    all_words = vocab_db.list_words(db_path=temp_db)
    assert len(all_words) == 3
    assert all_words[0]["word"] == "Apfel"

    easy_words = vocab_db.list_words(difficulty="easy", db_path=temp_db)
    assert len(easy_words) == 1
    assert easy_words[0]["word"] == "Apfel"

    limited = vocab_db.list_words(limit=2, db_path=temp_db)
    assert len(limited) == 2


def test_update_word(temp_db):
    """Test updating fields on existing word."""
    vocab_db.add_word("Auto", "car", difficulty="medium", db_path=temp_db)
    success = vocab_db.update_word("Auto", translation="automobile", difficulty="easy", db_path=temp_db)
    assert success is True

    word = vocab_db.get_word("Auto", db_path=temp_db)
    assert word["translation"] == "automobile"
    assert word["difficulty"] == "easy"

    missing = vocab_db.update_word("NonExistent", translation="none", db_path=temp_db)
    assert missing is False


def test_delete_word(temp_db):
    """Test deleting vocabulary word."""
    vocab_db.add_word("Fenster", "window", db_path=temp_db)
    assert vocab_db.delete_word("Fenster", db_path=temp_db) is True
    assert vocab_db.get_word("Fenster", db_path=temp_db) is None
    assert vocab_db.delete_word("Fenster", db_path=temp_db) is False


def test_spaced_repetition_review(temp_db):
    """Test review prioritization and recording."""
    vocab_db.add_word("Mutter", "mother", db_path=temp_db)
    vocab_db.add_word("Vater", "father", db_path=temp_db)

    # Initially both have last_reviewed=None
    review_queue = vocab_db.get_words_for_review(limit=2, db_path=temp_db)
    assert len(review_queue) == 2

    # Record review for Mutter (success)
    res = vocab_db.record_review("Mutter", success=True, db_path=temp_db)
    assert res["review_count"] == 1
    assert res["last_reviewed"] is not None

    # Next queue should have Vater first because Vater has never been reviewed
    new_queue = vocab_db.get_words_for_review(limit=2, db_path=temp_db)
    assert new_queue[0]["word"] == "Vater"


def test_record_review_difficulty_adjustment(temp_db):
    """Test difficulty adjustment on review success/failure."""
    vocab_db.add_word("schwer", "difficult", difficulty="hard", db_path=temp_db)
    # Successful review downgrades hard -> medium
    res = vocab_db.record_review("schwer", success=True, db_path=temp_db)
    assert res["difficulty"] == "medium"

    # Failed review upgrades back to hard
    res2 = vocab_db.record_review("schwer", success=False, db_path=temp_db)
    assert res2["difficulty"] == "hard"


def test_export_csv(temp_db, tmp_path):
    """Test exporting vocabulary words to CSV."""
    vocab_db.add_word("Schlüssel", "key", difficulty="medium", part_of_speech="noun", example="Wo ist mein Schlüssel?", db_path=temp_db)
    vocab_db.add_word("Mädchen", "girl", difficulty="easy", db_path=temp_db)

    out_file = tmp_path / "export.csv"
    exported_path = vocab_db.export_csv(file_path=str(out_file), db_path=temp_db)
    assert os.path.exists(exported_path)

    with open(exported_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert "word" in reader.fieldnames
    assert "translation" in reader.fieldnames
    assert "difficulty" in reader.fieldnames
    assert "last_reviewed" in reader.fieldnames
    assert "review_count" in reader.fieldnames

    words = {r["word"] for r in rows}
    assert "Schlüssel" in words
    assert "Mädchen" in words


def test_get_vocabulary_stats(temp_db):
    """Test aggregate stats calculation."""
    vocab_db.add_word("Wort1", "trans1", difficulty="easy", db_path=temp_db)
    vocab_db.add_word("Wort2", "trans2", difficulty="hard", db_path=temp_db)
    vocab_db.record_review("Wort1", success=True, db_path=temp_db)

    stats = vocab_db.get_vocabulary_stats(temp_db)
    assert stats["total_words"] == 2
    assert stats["reviewed_words"] == 1
    assert stats["difficulty_counts"].get("easy") == 1
    assert stats["difficulty_counts"].get("hard") == 1


def test_migration_from_legacy_schema(temp_db):
    """Test safe schema migration from old table with missing columns."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            translation TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO vocabulary (word, translation) VALUES ('alt', 'old')")
    conn.commit()
    conn.close()

    # Calling init_db should add missing columns without error
    vocab_db.init_db(temp_db)
    word = vocab_db.get_word("alt", db_path=temp_db)
    assert word["translation"] == "old"
    assert word["difficulty"] == "medium"
    assert word["review_count"] == 0


def test_cli_handle_vocab_commands(temp_db, tmp_path):
    """Test main.py CLI vocab command handlers."""
    # Test vocab add
    assert main.handle_vocab_command("vocab add Apfel apple easy", db_path=temp_db) is True
    entry = vocab_db.get_word("Apfel", db_path=temp_db)
    assert entry is not None
    assert entry["translation"] == "apple"

    # Test vocab list
    assert main.handle_vocab_command("vocab list", db_path=temp_db) is True

    # Test vocab review with simulated correct answer
    with patch("builtins.input", return_value="apple"):
        assert main.handle_vocab_command("vocab review", db_path=temp_db) is True

    # Test vocab export
    csv_dest = str(tmp_path / "cli_export.csv")
    assert main.handle_vocab_command(f"vocab export {csv_dest}", db_path=temp_db) is True
    assert os.path.exists(csv_dest)
