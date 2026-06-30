from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import JDInput
from app.services.llm import analyze_match
from app.services.retrieval import get_relevant_chunk

router = APIRouter(prefix="/analyze")


@router.post("/")
def analyze_resume(jd_input: JDInput, db: Session = Depends(get_db)):
    resume_chunks = get_relevant_chunk(
        jd_text=jd_input.jd_text, resume_id=jd_input.resume_id, db=db
    )
    if not resume_chunks:
        raise HTTPException(
            status_code=404, detail="No resume found. Upload your resume first."
        )

    res = analyze_match(jd_text=jd_input.jd_text, resume_chunks=resume_chunks)
    return res
