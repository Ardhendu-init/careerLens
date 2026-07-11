from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import JDInput
from app.services.llm import analyze_match
from app.services.retrieval import get_relevant_chunk, rerank_chunks

router = APIRouter(prefix="/analyze")


@router.post("/")
def analyze_resume(jd_input: JDInput, db: Session = Depends(get_db)):
    hybrid_result = get_relevant_chunk(
        jd_text=jd_input.jd_text, resume_id=jd_input.resume_id, db=db, limit=20
    )
    if not hybrid_result:
        raise HTTPException(
            status_code=404, detail="No resume found. Upload your resume first."
        )

    reranked = rerank_chunks(jd_text=jd_input.jd_text, chunks=hybrid_result)
    resume_chunks = reranked[:5]

    res = analyze_match(jd_text=jd_input.jd_text, resume_chunks=resume_chunks)
    return res
