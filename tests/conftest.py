"""Shared pytest fixtures for the ACEest Fitness Flask app."""

import os
import sys
import tempfile

import pytest

# Make the application package importable when tests run from any directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402


@pytest.fixture
def app():
    """Create a fresh app backed by a temporary SQLite database per test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    application = create_app(database=db_path)
    application.config.update(TESTING=True)

    yield application

    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
