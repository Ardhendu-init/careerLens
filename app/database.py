from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# 1. Create engine
engine = create_engine(settings.DATABASE_URL)

# 2. Create SessionLocal — sessionmaker takes autocommit, autoflush, and bind as arguments
SessionLocal = sessionmaker(bind=engine, autoflush= False,  autocommit=False)


class Base(DeclarativeBase):
    pass
