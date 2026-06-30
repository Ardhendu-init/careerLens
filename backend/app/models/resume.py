from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(10000))
    created_at = Column(DateTime, default=datetime.utcnow)
