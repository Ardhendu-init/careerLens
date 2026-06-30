# CareerLens

> AI-powered resume vs job description analyzer. Paste your resume once, then check your fit against any job description — get a match score, matched skills, gaps, and personalized positioning advice. Powered by a RAG pipeline built from scratch.

**🔗 Live app:** [career-lens-tan.vercel.app](https://career-lens-tan.vercel.app)
**🔗 API docs:** [careerlens-a8jl.onrender.com/docs](https://careerlens-a8jl.onrender.com/docs)

---

## What it does

1. Paste your resume — it's chunked and embedded into a vector database
2. Paste any job description — CareerLens retrieves the most relevant parts of your resume using semantic search
3. An LLM analyzes the match and returns a structured breakdown: match score, skills you have, skills you're missing, and how to position yourself for the role

No generic "chat with your PDF" — this is a focused tool solving a real, specific problem with a complete RAG pipeline underneath.

---

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js 16     │  HTTP   │   FastAPI         │  SQL    │   Supabase       │
│   (Vercel)       │ ──────► │   (Render)        │ ──────► │   PostgreSQL     │
│                  │         │                   │         │   + pgvector     │
│  Server Actions  │         │  /resume/         │         │                  │
│  ScoreRing       │         │  /analyze/        │         └─────────────────┘
│  SkillChips      │         │  /health          │                  ▲
└─────────────────┘         └─────────┬─────────┘                  │
                                       │                             │
                                       ▼                             │
                              ┌──────────────────┐                  │
                              │  Google Gemini    │                  │
                              │  embeddings +     │──────────────────┘
                              │  generation       │   (vector storage)
                              └──────────────────┘
```

**Resume ingestion (`POST /resume/`):**
```
raw text → chunked by paragraph → each chunk embedded (Gemini) → stored in pgvector
```

**JD analysis (`POST /analyze/`):**
```
JD text → embedded → cosine similarity search against stored chunks
        → top 5 relevant chunks retrieved → sent to Gemini with structured prompt
        → JSON response: match_score, matched_skills, missing_skills, positioning_advice
```

---

## Tech stack

**Backend**
- FastAPI — async-ready Python web framework
- SQLAlchemy + Supabase (PostgreSQL) — data layer
- pgvector — vector similarity search, no separate vector DB needed
- Google Gemini (`gemini-embedding-001`, `gemini-2.5-flash`) — embeddings + generation
- Pydantic — request/response validation, settings management
- pytest — test coverage on core pipeline logic
- uv — dependency management

**Frontend**
- Next.js 16 (App Router, Server Actions)
- React 19 (`useActionState`)
- TypeScript
- Tailwind CSS
- Custom animated SVG score visualization

**Infrastructure**
- Render — backend hosting
- Vercel — frontend hosting
- Supabase — managed PostgreSQL + pgvector
- GitHub Actions–ready monorepo structure

---

## Why these choices

**pgvector over a dedicated vector DB (Pinecone, Weaviate)** — Supabase was already
in the stack for relational data; adding the pgvector extension avoided a second
service and kept the architecture simple without sacrificing search quality.

**Server Actions over client-side fetch** — requests to the backend happen
server-to-server from Next.js, which sidesteps CORS entirely and keeps the API
URL out of the browser's network tab.

**Domain-specific RAG over generic document chat** — rather than building another
"chat with your PDF" clone, CareerLens solves one well-defined problem end to end,
which made the demo concrete and the scope achievable.

---

## Local development

**Backend**
```bash
cd backend
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env   # fill in DATABASE_URL and GEMINI_API_KEY
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Backend runs on `localhost:8000`, frontend on `localhost:3000`.

---

## Running tests

```bash
cd backend
pytest -v
```

---

## API reference

| Method | Endpoint    | Description                                      |
|--------|-------------|---------------------------------------------------|
| GET    | `/health`   | Health check                                       |
| POST   | `/resume/`  | Upload resume text — chunks, embeds, stores it    |
| POST   | `/analyze/` | Submit a JD — returns structured match analysis   |

Full interactive docs (Swagger UI) auto-generated at `/docs` on the live API.

---

## Project structure

```
careerlens/
├── backend/
│   ├── app/
│   │   ├── routers/        # health, resume, analyze
│   │   ├── services/       # embedding, retrieval, llm
│   │   ├── models/         # SQLAlchemy models (resume, chunk) + Pydantic schemas
│   │   ├── utils/          # text chunking
│   │   ├── main.py         # FastAPI app + router wiring
│   │   ├── config.py       # Pydantic settings
│   │   └── database.py     # SQLAlchemy engine + session
│   └── tests/              # pytest coverage on core pipeline
└── frontend/
    └── app/
        ├── components/     # ResumeForm, AnalyzeForm, ScoreRing, etc.
        ├── actions/        # Server Actions calling the API
        ├── lib/            # typed API client + shared types
        ├── utils/          # shared action helpers
        ├── layout.tsx      # root layout
        └── page.tsx        # main page
```

---

## Notes on deployment

The backend runs on Render's free tier, which spins down after periods of
inactivity — the first request after idle may take 30-60 seconds to respond
while the service wakes up. Subsequent requests are fast.

The Supabase connection uses the **transaction pooler** (not direct connection)
for the deployed backend, since Render's network doesn't support the IPv6
address Supabase's direct connection resolves to in some regions.

---

## Built by

Ardhendu Pramanik — [LinkedIn](https://www.linkedin.com/in/ardhendup/) · [GitHub](https://github.com/Ardhendu-init) · [Portfolio](https://ardhendu-pramanik.vercel.app/)

Built as a hands-on project to learn RAG, FastAPI, and Python backend
development from scratch alongside an existing Next.js/React background.