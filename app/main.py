from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.chunk import Chunk
from app.models.resume import Resume
from app.routers.health import router as health_router
from app.routers.resume import router as resume_router

app = FastAPI(
    title="CareerLens API",
    description="RAG-powered resume vs job description analyzer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(resume_router)

Base.metadata.create_all(bind=engine)
