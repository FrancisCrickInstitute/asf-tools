"""
Tests for the database_postgres_db and crud module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import pytest
from assertpy import assert_that

from sqlalchemy import text

from asf_tools.database.db import Database, construct_postgres_url

TEST_DATABASE_URL = "sqlite:///:memory:"

# Create class level mock database
@pytest.fixture(scope="class", autouse=True)
def mock_database(request):
    db = Database(TEST_DATABASE_URL)
    with db.db_session() as session:
        session.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"))
        session.execute(text("INSERT INTO test_table (id, name) VALUES (1, 'test1')"))
        session.execute(text("INSERT INTO test_table (id, name) VALUES (2, 'test2')"))
        session.commit()
        request.cls.db = session
        yield session


class TestDatabase:
    def test_postgres_construct_url(self):
        # Setup
        user = "user"
        password = "password"
        host = "localhost"
        port = 5432
        db = "database"
        expected = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        # Test
        result = construct_postgres_url(user, password, host, port, db)

        # Assert
        assert_that(result).is_equal_to(expected)

    def test_db_get_session(self):
        # Setup
        db = Database(TEST_DATABASE_URL)

        # Test
        with db.db_session() as session:
            result = session

        # Assert
        assert_that(result).is_not_none()

    def test_db_get_one_row_to_dict(self):
        # Setup
        stmt = text("SELECT * FROM test_table WHERE id = 1")

        # Test
        result = dict(self.db.execute(stmt).fetchone()._mapping)  # pylint: disable=protected-access

        # Assert
        assert_that(result).is_equal_to({"id": 1, "name": "test1"})

    def test_db_get_multi_row_to_dict(self):
        # Setup
        stmt = text("SELECT * FROM test_table")

        # Test
        result = [dict(row._mapping) for row in self.db.execute(stmt).fetchall()]  # pylint: disable=protected-access

        # Assert
        assert_that(result).is_length(2)
        assert_that(result).contains({"id": 1, "name": "test1"})
        assert_that(result).contains({"id": 2, "name": "test2"})
