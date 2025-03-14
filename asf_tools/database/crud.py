"""
This module contains CRUD operations for an sqlacademy database.
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import select, text
from sqlalchemy.orm import Session


log = logging.getLogger(__name__)

T = TypeVar("T")


class DatabaseCrud:
    """
    Generic CRUD operations for both:
    - SQLAlchemy ORM models
    - Raw SQL queries (returning dicts)
    """

    def __init__(self, model: Optional[Type[T]] = None, table_name: Optional[str] = None):
        """
        :param model: (Optional) SQLAlchemy model class for ORM-based queries.
        :param table_name: (Optional) Table name for raw SQL queries if not using models.
        """
        if not model and not table_name:
            raise ValueError("Either 'model' or 'table_name' must be provided.")
        self.model = model
        self.table_name = table_name

    def _convert_result(self, result, as_dict: bool):
        """Converts SQLAlchemy row results into dict or model objects."""
        if self.model is not None and as_dict is False:
            return result.scalars().all()
        return [dict(row._mapping) for row in result.fetchall()]  # pylint: disable=protected-access

    def get(self, db: Session, where_clause: str, params: Dict[str, Any], as_dict: bool = False) -> List[Any]:
        """
        Get records based on a WHERE condition.
        Returns a list of either ORM model objects or dictionaries.

        :param db: SQLAlchemy session
        :param where_clause: WHERE clause (e.g., "id = :id" or "created_at > :date")
        :param params: Dictionary of parameters to bind to the query
        :param as_dict: If True, return results as a list of dictionaries instead of model instances
        :return: List of records (models or dictionaries)
        """
        if self.model:
            query = select(self.model).where(text(where_clause))
        else:
            query = text(f"SELECT * FROM {self.table_name} WHERE {where_clause}")

        result = db.execute(query, params)
        return self._convert_result(result, as_dict)

    def get_simple(self, db: Session, column: str, value: str, as_dict: bool = False) -> List[Any]:
        """
        Get records based on a simple WHERE condition.
        Returns a list of either ORM model objects or dictionaries.

        :param db: SQLAlchemy session
        :param column: Column name (e.g., "id" or "created_at")
        :param value: Value to match
        :param as_dict: If True, return results as a list of dictionaries instead of model instances
        :return: List of records (models or dictionaries)
        """
        where_clause = f"{column} = :{column}"
        params = {column: value}
        return self.get(db, where_clause, params, as_dict)

    def get_all(self, db: Session, as_dict: bool = False) -> List[Any]:
        """
        Get all records.
        Returns a list of either ORM model objects or dictionaries.

        :param
        db: SQLAlchemy session
        :param as_dict: If True, return results as a list of dictionaries instead of model instances
        :return: List of records (models or dictionaries)
        """
        if self.model:
            query = select(self.model)
        else:
            query = text(f"SELECT * FROM {self.table_name}")
        result = db.execute(query)
        return self._convert_result(result, as_dict)

    def create(self, db: Session, obj_in: Any) -> None:
        """
        Insert a new record into the database.

        - Uses ORM models if `model` is provided.
        - Uses raw SQL if only `table_name` is provided.
        """
        if self.model:
            if isinstance(obj_in, self.model):
                obj = obj_in  # Use as is
            elif isinstance(obj_in, dict):
                obj = self.model(**obj_in)  # Convert dict to model instance
            else:
                raise TypeError(f"Invalid input type: {type(obj_in)}. Expected {self.model} or dict.")

            db.add(obj)
            db.commit()
        else:
            columns = ", ".join(obj_in.keys())
            values = ", ".join([f":{k}" for k in obj_in.keys()])
            query = text(f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})")
            db.execute(query, obj_in)
            db.commit()

    def update(self, db: Session, obj_id: int, obj_in: Dict[str, Any]) -> None:
        """
        Update a record in the database.
        - Supports both ORM and raw SQL.
        """
        if self.model:
            obj = db.query(self.model).filter(self.model.id == obj_id).first()
            if obj:
                for key, value in obj_in.items():
                    setattr(obj, key, value)  # Update attributes
                db.commit()
        else:
            set_clause = ", ".join([f"{k} = :{k}" for k in obj_in.keys()])
            obj_in["obj_id"] = obj_id
            query = text(f"UPDATE {self.table_name} SET {set_clause} WHERE id = :obj_id")
            db.execute(query, obj_in)
            db.commit()

    def delete(self, db: Session, obj_id: int) -> None:
        """
        Delete a record from the database.
        - Supports both ORM and raw SQL.
        """
        if self.model:
            db.query(self.model).filter(self.model.id == obj_id).delete()
            db.commit()
        else:
            query = text(f"DELETE FROM {self.table_name} WHERE id = :obj_id")
            db.execute(query, {"obj_id": obj_id})
            db.commit()
