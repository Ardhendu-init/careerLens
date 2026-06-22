from fastapi import APIRouter

from app.models.schemas import ResumeUpload

router = APIRouter(prefix="/resume")


@router.post("/", status_code=201)
def resume_upload(resume: ResumeUpload):
    return {"message": "Resume received", "status": "success"}
