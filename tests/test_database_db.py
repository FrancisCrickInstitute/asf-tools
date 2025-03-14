"""
Tests for the database_postgres_db and crud module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import pytest
from assertpy import assert_that
from sqlalchemy import Column, Integer, String, text

from asf_tools.database.base_model import BaseModel
from asf_tools.database.crud import DatabaseCrud
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


class TableTest(BaseModel):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class TestDatabase:
    def test_postgres_construct_url(self):
        # Setup
        user = "user"
        password = "password"
        host = "localhost"
        port = 5432
        db = "database"
        expected = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        # Test
        result = construct_postgres_url(user, password, host, port, db)

        # Assert
        assert_that(result).is_equal_to(expected)

    def test_db_get_session(self):
        # Setup
        db = Database(TEST_DATABASE_URL)

        # Test
        with db.db_session() as session:
            result = session

        # Assert
        assert_that(result).is_not_none()

    def test_db_get_one_row_to_dict(self):
        # Setup
        stmt = text("SELECT * FROM test_table WHERE id = 1")

        # Test
        result = dict(self.db.execute(stmt).fetchone()._mapping)  # pylint: disable=protected-access

        # Assert
        assert_that(result).is_equal_to({"id": 1, "name": "test1"})

    def test_db_get_multi_row_to_dict(self):
        # Setup
        stmt = text("SELECT * FROM test_table")

        # Test
        result = [dict(row._mapping) for row in self.db.execute(stmt).fetchall()]  # pylint: disable=protected-access

        # Assert
        assert_that(result).is_length(2)
        assert_that(result).contains({"id": 1, "name": "test1"})
        assert_that(result).contains({"id": 2, "name": "test2"})

    def test_db_crud_init(self):
        # Assert and Test
        assert_that(DatabaseCrud).raises(ValueError).when_called_with()

    def test_db_crud_get_single_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")
        where_clause = "id = :id"
        params = {"id": 1}

        # Test
        result = crud.get(self.db, where_clause, params, as_dict=True)

        # Assert
        assert_that(result).is_length(1)
        assert_that(result[0]).is_equal_to({"id": 1, "name": "test1"})

    def test_db_crud_get_single_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)
        where_clause = "id = :id"
        params = {"id": 1}

        # Test
        result = crud.get(self.db, where_clause, params)

        # Assert
        assert_that(result).is_length(1)
        assert_that(result[0].to_dict()).is_equal_to({"id": 1, "name": "test1"})

    def test_db_crud_get_simple_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")

        # Test
        result = crud.get_simple(self.db, "id", 1, as_dict=True)

        # Assert
        assert_that(result).is_length(1)
        assert_that(result[0]).is_equal_to({"id": 1, "name": "test1"})

    def test_db_crud_get_simple_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)

        # Test
        result = crud.get_simple(self.db, "id", 2)

        # Assert
        assert_that(result).is_length(1)
        assert_that(result[0].to_dict()).is_equal_to({"id": 2, "name": "test2"})

    def test_db_crud_get_all_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")

        # Test
        result = crud.get_all(self.db, as_dict=True)

        # Assert
        assert_that(result).is_length(2)
        assert_that(result).contains({"id": 1, "name": "test1"})
        assert_that(result).contains({"id": 2, "name": "test2"})

    def test_db_crud_get_all_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)

        # Test
        result = crud.get_all(self.db)

        # Assert
        assert_that(result).is_length(2)
        assert_that(result[0].to_dict()).is_equal_to({"id": 1, "name": "test1"})
        assert_that(result[1].to_dict()).is_equal_to({"id": 2, "name": "test2"})

    def test_db_crud_create_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")
        obj_in = {"id": 3, "name": "test3"}

        # Test
        crud.create(self.db, obj_in)

        # Assert
        result = crud.get_simple(self.db, "id", 3, as_dict=True)
        assert_that(result).is_length(1)
        assert_that(result[0]).is_equal_to(obj_in)

    def test_db_crud_create_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)
        obj_in = TableTest(id=4, name="test4")

        # Test
        crud.create(self.db, obj_in)

        # Assert
        result = crud.get_simple(self.db, "id", 4)
        assert_that(result).is_length(1)
        assert_that(result[0].to_dict()).is_equal_to(obj_in.to_dict())

    def test_db_crud_create_model_dict(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)
        obj_in = {"id": 5, "name": "test5"}

        # Test
        crud.create(self.db, obj_in)

        # Assert
        result = crud.get_simple(self.db, "id", 5, as_dict=True)
        assert_that(result).is_length(1)

    def test_db_crud_update_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")
        obj_in = {"id": 1, "name": "test1_updated"}

        # Test
        crud.update(self.db, 1, obj_in)

        # Assert
        result = crud.get_simple(self.db, "id", 1, as_dict=True)
        assert_that(result).is_length(1)
        assert_that(result[0]["name"]).is_equal_to("test1_updated")

    def test_db_crud_update_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)
        obj_in = {"id": 2, "name": "test2_updated"}

        # Test
        crud.update(self.db, 2, obj_in)

        # Assert
        result = crud.get_simple(self.db, "id", 2)
        assert_that(result).is_length(1)
        assert_that(result[0].name).is_equal_to("test2_updated")

    def test_db_crud_delete_dict(self):
        # Setup
        crud = DatabaseCrud(table_name="test_table")

        # Test
        crud.delete(self.db, 2)

        # Assert
        result = crud.get_simple(self.db, "id", 2, as_dict=True)
        assert_that(result).is_length(0)

    def test_db_crud_delete_model(self):
        # Setup
        crud = DatabaseCrud(model=TableTest)

        # Test
        crud.delete(self.db, 1)

        # Assert
        result = crud.get_simple(self.db, "id", 1)
        assert_that(result).is_length(0)
