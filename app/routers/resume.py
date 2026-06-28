from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chunk import Chunk
from app.models.resume import Resume
from app.models.schemas import ResumeUpload
from app.services.embedding import embed_text
from app.utils.text import chunk_text

router = APIRouter(prefix="/resume")


@router.post("/", status_code=201)
def resume_upload(resume: ResumeUpload, db: Session = Depends(get_db)):
    db_resume = Resume(text=resume.text)
    db.add(db_resume)
    db.flush()  # flush sends the INSERT but doesn't commit — gives us db_resume.id

    chunks = chunk_text(resume.text)

    for chunk_text_item in chunks:
        vector = embed_text(chunk_text_item)

        db_chunk = Chunk(resume_id=db_resume.id, text=chunk_text_item, embedding=vector)
        db.add(db_chunk)
    db.commit()
    db.refresh(db_resume)
    return {
        "message": "Resume uploaded",
        "resume_id": db_resume.id,
        "chunks": len(chunks),
    }
