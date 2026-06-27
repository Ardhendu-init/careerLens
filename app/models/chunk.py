from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, index=True, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    text = Column(String(2000))
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=datetime.utcnow)
