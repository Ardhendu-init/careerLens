from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# 1. Create engine
engine = create_engine(settings.DATABASE_URL)

# 2. Create SessionLocal — sessionmaker takes autocommit, autoflush, and bind as arguments
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
