# Prompt: Add Supabase Auth to CareerLens

## Context

CareerLens is a live FastAPI + Next.js RAG app (backend on Render, frontend on Vercel,
Supabase/Postgres + pgvector for storage). Right now there is no authentication:

- The frontend gets a `resume_id` back from `POST /resume/` and holds it in React
  `useState` (lost on refresh) — no persistence, no ownership.
- `POST /analyze/` accepts any `resume_id` from the client with zero ownership check.
  Anyone who has or guesses a `resume_id` can query it.
- There is no `user_id` concept anywhere in the schema.

Goal: add real Supabase Auth so that resumes are tied to an authenticated user, both
frontend and backend enforce ownership, and refreshing the page no longer loses state
or creates duplicate resume rows.

Repo structure (monorepo):
```
careerlens/
├── backend/app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/ (schemas.py, resume.py, chunk.py)
│   ├── routers/ (health.py, resume.py, analyze.py)
│   ├── services/ (embedding.py, retrieval.py, llm.py)
│   └── utils/text.py
└── frontend/src/app/
    ├── page.tsx               # useState for resumeId currently
    ├── components/            # ResumeForm, AnalyzeForm, AnalysisResultView, etc.
    ├── actions/                # resume.ts, analyze.ts — Server Actions (avoids CORS)
    └── lib/ (api.ts, types.ts)
```

Backend uses FastAPI + SQLAlchemy against Supabase Postgres (transaction pooler in
prod). Frontend uses Next.js 16 App Router with Server Actions calling the FastAPI
backend directly (no client-side fetch to the API).

## What to build

### 1. Supabase Auth setup
- Use Supabase's built-in Auth (email/password to start — magic link can come later).
- Frontend: install `@supabase/ssr` (Next.js App Router compatible package), set up
  a Supabase client for Server Components/Actions and one for the browser.
- Add login and signup pages/forms under `frontend/src/app/`.
- Add a middleware (or layout-level check) that protects the main app routes and
  redirects unauthenticated users to `/login`.

### 2. Database migration
- Add a `user_id` (UUID, references `auth.users`) column to the `Resume` model/table.
- Since there's currently one real resume in production (mine), write the migration
  so it's safe to backfill that existing row with my user_id once I've created my
  account — don't silently drop existing data.
- Add an index on `user_id` for lookup performance.

### 3. Backend: enforce ownership
- Every protected FastAPI route (`/resume/`, `/analyze/`) must verify the Supabase
  JWT sent from the frontend and extract the authenticated `user_id` from it —
  don't trust a `user_id` or `resume_id` passed directly in the request body for
  ownership purposes.
- `POST /resume/`: attach the authenticated `user_id` to the created Resume row.
- `POST /analyze/`: look up the resume by `resume_id`, then verify
  `resume.user_id == authenticated_user_id` before proceeding — return 403/404
  (prefer 404 to avoid leaking existence) if it doesn't match.
- Add a `GET /resume/me` (or similar) endpoint that returns the current user's
  existing resume (if any), so the frontend can check "does this user already have
  a resume" without relying on localStorage.

### 4. Frontend: replace resumeId state with real ownership flow
- On load (server-side, in a Server Component), check the authenticated session and
  call the new `GET /resume/me` endpoint.
- If a resume exists, skip straight to the analyze view. If not, show `ResumeForm`.
- Keep a small "Upload a different resume" action for the rare case a user wants to
  replace their resume — this should probably just overwrite/replace their existing
  row rather than creating a second one (your call on whether to support multiple
  resumes per user now or later — ask me if unsure).
- Remove reliance on the `useState` resumeId / localStorage entirely — the server
  session is now the source of truth.

### 5. Supabase Row Level Security (defense in depth)
- Add RLS policies on the `resumes` and `chunks` tables so that even a direct DB
  query can only return rows matching `auth.uid()`. This is a safety net on top of
  the FastAPI-level checks, not a replacement for them.

## How I want you to work

- **Explain before you build.** Before writing migration or auth-flow code, walk me
  through the plan and any decisions with trade-offs (e.g. session storage approach,
  cookie vs. header JWT passing between Next.js Server Actions and FastAPI) — I want
  to understand *why*, not just get a diff.
- **Flag anything destructive.** Call out clearly any step that could affect existing
  production data before running it.
- **Keep changes reviewable.** Prefer smaller, logically grouped commits (e.g. "DB
  migration + model change", "backend JWT verification", "frontend auth pages",
  "frontend resumeId → session refactor") over one giant change.
- **Note testing.** Suggest what to manually test (or add a pytest case for) once
  ownership checks are in, especially the 404-on-mismatched-resume_id behavior.