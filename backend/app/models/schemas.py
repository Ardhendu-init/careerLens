from datetime import datetime

from pydantic import BaseModel


class ResumeUpload(BaseModel):
    text: str


class ResumeOut(BaseModel):
    id: int
    created_at: datetime
    preview: str

    model_config = {"from_attributes": True}


class JDInput(BaseModel):
    jd_text: str
    resume_id: int


class AnalysisResult(BaseModel):
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    positioning_advice: str
