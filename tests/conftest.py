import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db

# This reads the data.sql file into memory. The os.path.dirname(__file__)
# finds the directory where conftest.py is located, and data.sql is read
# as binary ('rb'). The decode('utf8') converts it into a string that can
# be executed later.
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()  # Create a temporary file for the test database

    app = create_app(
        {
            "TESTING": True,  # Run in testing mode (disables error catching, etc.)
            "DATABASE": db_path,  # Use the temporary file as the database
        }
    )

    with app.app_context():  # Push the app context for accessing the database
        init_db()  # Initialize the database schema
        get_db().executescript(
            _data_sql
        )  # Populate the database with the test data from data.sql

    yield app  # This returns the app to the test function

    os.close(db_fd)  # Cleanup: close the temporary database file
    os.unlink(db_path)  # Remove the temporary database file after tests


@pytest.fixture
def setup_db(app):
    with app.app_context():
        init_db()
        yield get_db()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self.client = client

    def login(self, username="test", password="test"):
        return self.client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self.client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
