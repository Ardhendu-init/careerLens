from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models.resume import Resume
from app.models.schemas import JDInput
from app.services.llm import analyze_match
from app.services.retrieval import get_relevant_chunk, rerank_chunks

router = APIRouter(prefix="/analyze")


@router.post("/")
def analyze_resume(
    jd_input: JDInput,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    resume = db.query(Resume).filter(Resume.id == jd_input.resume_id).first()
    if not resume or str(resume.user_id) != user_id:
        # 404 rather than 403 so a guessed resume_id doesn't confirm existence.
        raise HTTPException(status_code=404, detail="Resume not found")

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
