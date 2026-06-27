from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resume import Resume
from app.models.schemas import ResumeUpload

router = APIRouter(prefix="/resume")


@router.post("/", status_code=201)
def resume_upload(resume: ResumeUpload, db: Session = Depends(get_db)):
    db_resume = Resume(text=resume.text)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume
