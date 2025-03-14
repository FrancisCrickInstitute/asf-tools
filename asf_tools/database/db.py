"""
Postgres Database connection manager.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def construct_postgres_url(user: str, password: str, host: str, port: int, db: str) -> str:
    """
    Construct the URL for the PostgreSQL database.
    """
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


class Database:
    """
    Postgres Database connection manager.
    """

    def __init__(self, db_url: str, pool_size: int = 10, max_overflow: int = 20, echo: bool = False):

        # SQLite does not support pooling (in memory test database)
        if "sqlite" in db_url:
            self.engine = create_engine(db_url, echo=echo)
        else:
            self.engine = create_engine(db_url, pool_size=pool_size, max_overflow=max_overflow, echo=echo)

        # Create session local
        self.session_local = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def get_db_session(self):
        """Dependency-style session generator."""
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def db_session(self):
        """Context manager for handling database sessions."""
        db = self.session_local()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
