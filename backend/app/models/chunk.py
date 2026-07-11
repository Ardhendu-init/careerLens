from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Computed, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, index=True, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    text = Column(String(2000))
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=datetime.utcnow)
    text_search = Column(
        TSVECTOR,
        Computed("to_tsvector('english', text)", persisted=True),
        nullable=True,
    )
