"""Shared pytest fixtures."""
import sys
import os

# Ensure the project root is on the path so modules are importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch


@pytest.fixture
def temp_db(tmp_path):
    """Provide a fresh, isolated SQLite database for each test."""
    db_file = str(tmp_path / "test_church.db")
    with patch("database.DB_PATH", db_file):
        import database as db
        db.init_db()
        yield db
