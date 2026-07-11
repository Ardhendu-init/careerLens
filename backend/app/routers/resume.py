from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models.chunk import Chunk
from app.models.resume import Resume
from app.models.schemas import ResumeOut, ResumeUpload
from app.services.embedding import embed_text
from app.utils.text import chunk_text

router = APIRouter(prefix="/resume")

PREVIEW_LENGTH = 120


def _to_resume_out(resume: Resume) -> ResumeOut:
    preview = resume.text[:PREVIEW_LENGTH]
    if len(resume.text) > PREVIEW_LENGTH:
        preview += "…"
    return ResumeOut(id=resume.id, created_at=resume.created_at, preview=preview)


@router.post("/", status_code=201)
def resume_upload(
    resume: ResumeUpload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    db_resume = Resume(text=resume.text, user_id=user_id)
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


@router.get("/me", response_model=ResumeOut)
def resume_get_most_recent(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    return _to_resume_out(resume)


@router.get("/", response_model=list[ResumeOut])
def resume_list(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return [_to_resume_out(r) for r in resumes]
