from pydantic import BaseModel


class ResumeUpload(BaseModel):
    text: str


class JDInput(BaseModel):
    jd_text: str
    resume_id: int


class AnalysisResult(BaseModel):
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    positioning_advice: str
