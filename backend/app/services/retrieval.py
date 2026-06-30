from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embedding import embed_text


def get_relevant_chunk(
    jd_text: str, resume_id: int, db: Session, limit: int = 5
) -> list[str]:

    jd_vector = embed_text(jd_text)

    results = (
        db.query(Chunk)
        .filter(Chunk.resume_id == resume_id)
        .order_by(Chunk.embedding.cosine_distance(jd_vector))
        .limit(limit)
        .all()
    )
    return [chunk.text for chunk in results]
