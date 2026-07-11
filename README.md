# CareerLens

> AI-powered resume vs job description analyzer. Paste your resume once, then check your fit against any job description — get a match score, matched skills, gaps, and personalized positioning advice. Powered by a production-grade RAG pipeline built from scratch.

**🔗 Live app:** [career-lens-tan.vercel.app](https://career-lens-tan.vercel.app)
**🔗 API docs:** [careerlens-a8jl.onrender.com/docs](https://careerlens-a8jl.onrender.com/docs)

---

## What it does

1. Paste your resume — it's chunked and embedded into a vector database
2. Paste any job description — CareerLens retrieves the most relevant resume sections using hybrid search (semantic + keyword)
3. A reranker re-scores the candidates for precision
4. An LLM analyzes the match and returns a structured breakdown: match score, skills you have, skills you're missing, and how to position yourself for the role

No generic "chat with your PDF" — a focused tool solving one well-defined problem, with a production-grade retrieval pipeline underneath.

---

## Architecture

```
┌─────────────────┐         ┌──────────────────────────┐         ┌─────────────────┐
│   Next.js 16     │  HTTP   │   FastAPI                 │  SQL    │   Supabase       │
│   (Vercel)       │ ──────► │   (Render)                │ ──────► │   PostgreSQL     │
│                  │         │                           │         │   + pgvector     │
│  Server Actions  │         │  POST /resume/            │         │   + tsvector     │
│  ScoreRing SVG   │         │  POST /analyze/           │         └─────────────────┘
│  SkillChips      │         │  GET  /health             │                  ▲
└─────────────────┘         └──────────┬────────────────┘                  │
                                        │                                    │
                                        ▼                                    │
                               ┌──────────────────┐                         │
                               │  Google Gemini    │─────────────────────────┘
                               │  embeddings +     │   (vector + tsvector storage)
                               │  generation       │
                               └──────────────────┘
                                        ▲
                               ┌──────────────────┐
                               │  FlashRank        │
                               │  (cross-encoder   │
                               │   reranker)       │
                               └──────────────────┘
```

---

## The RAG Pipeline (v3)

**Resume ingestion (`POST /resume/`):**
```
raw text
  → chunked by paragraph (utils/text.py)
  → each chunk embedded with Gemini (gemini-embedding-001, 768-dim)
  → stored in pgvector + tsvector auto-generated for keyword search
```

**JD analysis (`POST /analyze/`):**
```
JD text
  → embed with Gemini
  → vector search: cosine similarity against resume chunks (top 20)
  → keyword search: PostgreSQL full-text (tsvector @@, ts_rank) (top 20)
  → RRF merge: score = Σ 1/(60 + rank) across both lists
  → FlashRank reranking: cross-encoder re-scores top 20 by actual relevance
  → top 5 chunks sent to Gemini 2.5 Flash with structured prompt
  → returns JSON: match_score, matched_skills, missing_skills, positioning_advice
```

**Why hybrid search + reranking?**
Pure vector search finds chunks by semantic meaning but misses exact keyword matches — a resume that says "PostgreSQL" may not rank highest for a JD requiring "PostgreSQL" if embedding similarity is moderate. Keyword search catches exact matches. RRF merges both lists, rewarding chunks that rank well in both. FlashRank then re-scores by actual relevance, not just similarity.

| Version | Retrieval | Match Score | Skills Found |
|---|---|---|---|
| v1 | Pure vector search | 65% | 11 |
| v2 | Hybrid search (vector + keyword + RRF) | 77% | 12 |
| v3 | Hybrid + FlashRank reranking | 73% | 13 |

v3 is more calibrated — slightly lower score but higher skill precision and better positioning advice.

---

## Tech Stack

**Backend**
- FastAPI — service-layer architecture (routers / services / models)
- SQLAlchemy + Supabase (PostgreSQL) — ORM + managed database
- pgvector — vector similarity search (cosine distance)
- PostgreSQL tsvector — full-text keyword search (hybrid search sparse side)
- FlashRank — cross-encoder reranking (~4MB Nano model, CPU-only, no API cost)
- Google Gemini (`gemini-embedding-001`, `gemini-2.5-flash`) — embeddings + generation
- Pydantic — request/response validation + settings management (SecretStr for credentials)
- pytest — test coverage on core pipeline logic
- uv — dependency management

**Frontend**
- Next.js 16 (App Router, Server Actions)
- React 19 (`useActionState`)
- TypeScript — end-to-end typed API client
- Tailwind CSS
- Custom animated SVG score visualization (hand-built with strokeDasharray/strokeDashoffset)

**Infrastructure**
- Render — backend hosting (free tier, cold starts after inactivity)
- Vercel — frontend hosting
- Supabase — managed PostgreSQL + pgvector + tsvector
- GitHub Actions–ready monorepo structure

---

## Why these choices

**Hybrid search over pure vector search** — exact keyword matching for technical skills (framework names, tool names) complements semantic matching. Resume chunks are short; keywords matter as much as meaning.

**pgvector + tsvector over a dedicated vector DB** — Supabase was already in the stack. Adding `tsvector` as a generated column gives full-text search with zero new infrastructure.

**FlashRank over Cohere Rerank** — no API cost, no rate limits, runs on CPU. The Nano model (~4MB) fits comfortably within Render's free tier 512MB RAM.

**Server Actions over client-side fetch** — requests happen server-to-server from Next.js to FastAPI, sidesteps CORS entirely and keeps the API URL out of the browser's network tab.

**resume_id scoping** — every chunk query filters by `resume_id` so users only retrieve their own resume chunks. Multi-user isolation is enforced at the database query level, not just application logic.

---

## Local development

**Backend**
```bash
cd backend
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env   # fill in DATABASE_URL and GEMINI_API_KEY
uvicorn app.main:app --reload
# runs on localhost:8000
```

**Supabase setup (one-time)**
```sql
-- Run in Supabase SQL Editor
create extension if not exists vector;

-- After first server start (creates resumes + chunks tables):
-- Add tsvector column for hybrid search
ALTER TABLE chunks
ADD COLUMN text_search tsvector
GENERATED ALWAYS AS (to_tsvector('english', text)) STORED;

CREATE INDEX chunks_text_search_idx ON chunks USING GIN (text_search);
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
# runs on localhost:3000
```

---

## Running tests

```bash
cd backend
pytest -v
```

3 tests covering: chunk splitting, chunk filtering, empty-chunk early return in analyze pipeline.

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/resume/` | Upload resume text — chunk, embed, store |
| POST | `/analyze/` | Submit JD + resume_id — returns structured match analysis |

Interactive docs (Swagger UI) at `/docs` on the live API.

**`POST /analyze/` request shape:**
```json
{
  "jd_text": "We are looking for a Senior Frontend Engineer...",
  "resume_id": 1
}
```

---

## Project structure

```
careerlens/
├── README.md
├── backend/
│   ├── app/
│   │   ├── routers/         # health, resume, analyze
│   │   ├── services/        # embedding, retrieval (hybrid+RRF+rerank), llm
│   │   ├── models/          # SQLAlchemy models + Pydantic schemas
│   │   └── utils/           # text chunking
│   └── tests/
└── frontend/
    └── src/app/
        ├── components/      # ResumeForm, AnalyzeForm, ScoreRing, SkillChips, etc.
        ├── actions/         # Server Actions (uploadResume, analyzeResume)
        └── lib/             # typed API client, shared types
```

---

## Deployment notes

**Backend (Render free tier):** Spins down after inactivity — first request after idle may take 30-60 seconds to wake up. Subsequent requests are fast.

**Database connection:** Uses Supabase's **Transaction pooler** in production (`*.pooler.supabase.com:6543`) rather than the direct connection, because Render's network cannot reach Supabase's direct-connection IPv6 address. Local development uses the direct connection with no changes.

**tsvector column:** Generated automatically by PostgreSQL (`GENERATED ALWAYS AS ... STORED`) — no application-level maintenance needed. GIN index ensures keyword search stays fast at scale.

---

## Limitations

- Resume chunking is paragraph-based — very short or non-paragraph-structured resumes produce fewer, larger chunks
- No conversation memory — each analysis is stateless
- FlashRank Nano model is lightweight but not state-of-the-art; a larger reranker (Cohere, cross-encoder/ms-marco) would improve precision at the cost of latency/API budget
- Render cold starts (30-60s) on the free tier — not suitable for latency-sensitive production use

---

## Future improvements

- Eval harness (RAGAS) for quantitative before/after retrieval quality measurement
- MCP server wrapping `/analyze` for Claude Desktop integration
- Docker containerization for portable local development
- Streaming responses for progressive analysis rendering
- Multi-document support (compare against multiple JDs simultaneously)

---

## Built by

Ardhendu Pramanik — [LinkedIn](https://www.linkedin.com/in/ardhendup/) · [GitHub](https://github.com/Ardhendu-init) · [Portfolio](https://ardhendu-pramanik.vercel.app/)

Built as a hands-on project to learn RAG, FastAPI, and Python backend development from scratch alongside an existing Next.js/React background. Every layer of the pipeline — chunking, embedding, hybrid search, reranking, structured generation — was built without framework abstraction to understand what each step actually does.