from flashrank import Ranker, RerankRequest
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embedding import embed_text

_ranker: Ranker | None = None


def _get_ranker() -> Ranker:
    # Lazy-loaded: Ranker() downloads a model file from Hugging Face on first
    # use. Doing this at import time would block app startup on a network
    # call, and any transient failure would crash the whole API instead of
    # just the rerank path.
    global _ranker
    if _ranker is None:
        _ranker = Ranker()
    return _ranker


def get_relevant_chunk(
    jd_text: str, resume_id: int, db: Session, limit: int = 5
) -> list[str]:

    jd_vector = embed_text(jd_text)

    vector_results = (
        db.query(Chunk)
        .filter(Chunk.resume_id == resume_id)
        .order_by(Chunk.embedding.cosine_distance(jd_vector))
        .limit(20)
        .all()
    )
    keyword_results = (
        db.query(Chunk)
        .filter(Chunk.resume_id == resume_id)
        .filter(Chunk.text_search.op("@@")(func.plainto_tsquery("english", jd_text)))
        .order_by(
            func.ts_rank(
                Chunk.text_search, func.plainto_tsquery("english", jd_text)
            ).desc()
        )
        .limit(20)
        .all()
    )

    # Step 1 — build lookup
    all_chunks = {chunk.id: chunk.text for chunk in vector_results + keyword_results}

    # Step 2 — score with RRF
    scores = {}
    for rank, chunk in enumerate(vector_results, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (60 + rank)
    for rank, chunk in enumerate(keyword_results, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (60 + rank)

    # Step 3 — sort and return
    sorted_ids = sorted(scores, key=lambda id: scores[id], reverse=True)
    return [all_chunks[id] for id in sorted_ids[:limit]]


def rerank_chunks(jd_text: str, chunks: list[str]) -> list[str]:
    passages = [{"id": i, "text": chunk} for i, chunk in enumerate(chunks)]

    request = RerankRequest(query=jd_text, passages=passages)
    results = _get_ranker().rerank(request)
    return [r["text"] for r in results]  # ✅ return reranked texts in order
