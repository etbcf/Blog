import datetime
import sqlite3

import pytest

from flaskr.db import get_db


def test_adapt_datetime(setup_db):
    db = setup_db

    # Insert a datetime value into the database
    now = datetime.datetime.now().replace(microsecond=0)  # Same precision
    db.execute(
        "INSERT INTO post (title, body, author_id, created) VALUES (?, ?, ?, ?)",
        ("Test Title", "Test Body", 1, now),
    )
    db.commit()

    # Retrieve the value to make sure it was inserted correctly
    result = db.execute(
        "SELECT created FROM post WHERE title = ?", ("Test Title",)
    ).fetchone()
    assert result is not None

    # Compare the datetime values directly
    created = result["created"]
    assert created == now


def test_get_close_db(app):
    with app.app_context():
        db = get_db()  # Get a database connection
        assert (
            db is get_db()
        )  # Ensure the same connection is returned on repeated calls

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")  # Try to execute a query after the context is closed

    assert "closed" in str(
        e.value
    )  # Ensure the error message mentions that the connection is closed


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False  # This class will track whether `init_db` has been called

    def fake_init_db():
        Recorder.called = True  # Set to True when the fake `init_db` is called

    monkeypatch.setattr(
        "flaskr.db.init_db", fake_init_db
    )  # Replace the real `init_db` with the fake one
    result = runner.invoke(args=["init-db"])  # Run the CLI command 'init-db'
    assert (
        "Initialized" in result.output
    )  # Check if the command output contains "Initialized"
    assert Recorder.called  # Ensure that `fake_init_db` was called
