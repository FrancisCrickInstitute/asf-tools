"""
Base Model for SQLAlchemy ORM
"""

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BaseModel(Base):
    """
    Flexible Base Model:
    - Works with UUIDs, composite keys, and custom primary keys.
    - Provides `created_at` timestamps.
    - `to_dict()` method for dictionary conversion.
    """

    __abstract__ = True  # Prevents table creation for this base class

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        """Readable debugging output."""
        return f"<{self.__class__.__name__} {self.to_dict()}>"
