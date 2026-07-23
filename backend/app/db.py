import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    return os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/prdash"
    )


engine = create_engine(_database_url())
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    Base.metadata.create_all(engine)