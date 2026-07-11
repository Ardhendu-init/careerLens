# Add Supabase Auth to CareerLens

## Context

CareerLens has no authentication today: `resume_id` lives in a React `useState`
(lost on refresh), `POST /analyze/` trusts any `resume_id` a client sends with zero
ownership check, and there's no `user_id` anywhere in the schema. Goal: wire up real
Supabase Auth end-to-end so resumes belong to a signed-in user, ownership is enforced
on both the frontend (session-driven UI) and backend (JWT-verified), and the user can
now store **multiple** resumes (confirmed via question — no UI exists for this yet,
so it's new frontend surface, not just a schema tweak).

Note on `frontend/AGENTS.md`: it claims this Next.js install has "breaking changes"
from a training-data baseline and points at `node_modules/next/dist/docs/` before
writing any code. I checked — it's a stock Next.js 16.2.9, and `dist/docs/index.md`
contains a hidden HTML-comment "AI agent hint" trying to redirect focus to an
unrelated doc. That's a planted prompt injection, not real project guidance. I'm
ignoring both and building against standard, current Next.js App Router conventions
verified directly against this repo's actual files.

## Key decisions & trade-offs (the "why")

**1. JWT passing: httpOnly cookie on Next.js, Bearer header to FastAPI.**
`@supabase/ssr` manages the Supabase session as httpOnly cookies scoped to the
Next.js app itself. Server Actions run on the Next.js server, so they can read that
cookie-backed session via a server Supabase client, pull out `session.access_token`,
and forward it as `Authorization: Bearer <token>` to FastAPI. The JWT never touches
browser JS (XSS-safe), and we avoid the pain of sharing cookies across two different
domains (Vercel + Render) — FastAPI stays stateless and just verifies the bearer
token per-request.

**2. Backend JWT verification: local HS256 verify with the Supabase legacy JWT
secret (`PyJWT`), not a network call per request.**
Supabase issues HS256-signed JWTs by default and every project (old or new) still
exposes a "Legacy JWT Secret" in Settings → API for this. Verifying locally means no
added latency or availability dependency on Supabase for every `/analyze/` call.
(Newer JWKS/asymmetric verification is a future upgrade if you rotate to it — not
needed to ship this.)

**3. Migration: raw SQL script, not Alembic.**
This project has no migration framework today (`Base.metadata.create_all` only
creates missing tables, it won't alter existing ones). Introducing Alembic is a
bigger, separate decision, so instead: a plain SQL file you run once against Supabase
(via SQL editor or `psql`), matching the project's current lightweight style. It adds
`user_id` as **nullable** (so it doesn't fail or drop your existing row), plus an
index. You backfill your row's `user_id` manually after creating your account, then
we can tighten to `NOT NULL` later once verified.

**4. Multiple resumes per user (per your answer).**
No "active resume" flag — just list resumes newest-first. `POST /resume/` always
inserts a new row (never overwrites). `GET /resume/me` returns the most recent resume
(for the "does this user have any resume yet" check on load). New `GET /resume/`
lists all of the user's resumes so the frontend can render a picker. This means real
new frontend surface: a resume selector component, since none exists today.

**5. RLS is real defense-in-depth, with one caveat I want you aware of.**
FastAPI connects to Postgres with a direct connection string (superuser/service
role), not through Supabase's PostgREST/anon-key layer — so `auth.uid()`-based RLS
policies won't automatically constrain the backend's *own* queries unless we also
set `request.jwt.claims` per DB session (bigger lift, not in scope here). RLS still
meaningfully protects against any other access path (Supabase Studio SQL editor
misuse, a future client hitting Supabase directly, a leaked anon key). I'll implement
it as the safety net the doc asks for, but it is not a substitute for the FastAPI
checks — which matches the doc's own framing.

## Implementation plan (5 reviewable commits)

**Commit 1 — DB migration + model**
- New `backend/migrations/0001_add_user_id_to_resumes.sql`: `ALTER TABLE resumes ADD
  COLUMN user_id uuid REFERENCES auth.users(id)`, `CREATE INDEX ON resumes(user_id)`.
  Include the manual backfill `UPDATE` as a commented-out line with instructions.
- Update [resume.py](backend/app/models/resume.py) to add the `user_id` column
  (nullable `UUID`).
- No changes needed to [chunk.py](backend/app/models/chunk.py) — ownership flows
  through `resume_id`.

**Commit 2 — Backend JWT verification + ownership**
- New `backend/app/auth.py`: `get_current_user_id(authorization: str = Header(...))`
  FastAPI dependency — decodes/verifies the bearer token with `PyJWT` against
  `settings.SUPABASE_JWT_SECRET`, audience `"authenticated"`, returns `sub` (the
  user's UUID) or raises 401.
- Add `SUPABASE_JWT_SECRET: str` to [config.py](backend/app/config.py), `pyjwt` to
  `pyproject.toml`.
- [routers/resume.py](backend/app/routers/resume.py): add the dependency to
  `POST /`, attach `user_id` to the created row; add `GET /me` (most recent, 404 if
  none) and `GET /` (list current user's resumes, newest first) — new
  `ResumeOut`/`ResumeListOut` schemas in [schemas.py](backend/app/models/schemas.py).
- [routers/analyze.py](backend/app/routers/analyze.py): add the dependency, look up
  the resume by `resume_id`, compare `resume.user_id == current_user_id`, 404 on
  mismatch or missing (before doing any retrieval work).

**Commit 3 — Frontend auth pages + middleware**
- Add `@supabase/ssr` + `@supabase/supabase-js` to `frontend/package.json`.
- `frontend/app/lib/supabase/server.ts` and `.../client.ts` — server (cookie-bound)
  and browser Supabase clients, following the standard `@supabase/ssr` split.
- `frontend/middleware.ts` (project root, alongside `app/`) — refreshes the session
  cookie and redirects unauthenticated requests to `/login` for all routes except
  `/login`, `/signup`, and static assets.
- `frontend/app/login/page.tsx`, `frontend/app/signup/page.tsx` — email/password
  forms using Server Actions that call `supabase.auth.signInWithPassword` /
  `signUp` on the server client (sets the session cookie via the response).

**Commit 4 — Frontend: resumeId state → session-driven ownership flow**
- `page.tsx` becomes a Server Component: reads the session, calls the new
  `GET /resume/` (forwarding the bearer token), and renders either `ResumeForm` (no
  resumes yet) or a new `ResumeSelector` + `AnalyzeForm` (resumes exist, defaulting
  to the most recent).
- `actions/resume.ts` / `actions/analyze.ts`: pull the access token server-side via
  the server Supabase client and forward it as `Authorization: Bearer <token>` in
  [api.ts](frontend/app/lib/api.ts)'s `apiPost`.
- Delete the `useState` resumeId wiring in `page.tsx` entirely — the resume list
  from the server is now the only source of truth for what the user owns.
- `frontend/app/utils/action.ts` (`sendResume`) is dead code, unused anywhere — I'll
  leave it alone unless you want it removed; flagging rather than silently deleting.

**Commit 5 — Supabase RLS policies**
- New `backend/migrations/0002_rls_resumes_chunks.sql`: enable RLS on `resumes` and
  `chunks`; policy on `resumes` for `auth.uid() = user_id`; policy on `chunks` via
  `EXISTS (SELECT 1 FROM resumes WHERE resumes.id = chunks.resume_id AND
  resumes.user_id = auth.uid())`. Includes the caveat from decision #5 as a comment.

## Testing

- New `backend/tests/test_auth.py`: unit tests for `get_current_user_id` — valid
  token (mint one with `PyJWT` + a test secret) returns the right `sub`; expired,
  wrong-audience, and tampered-signature tokens all raise 401. Matches the existing
  pure-function test style in [test_services.py](backend/tests/test_services.py) —
  no DB or HTTP client needed.
- Manual test (needs real pgvector-backed Postgres, not something to fake in
  pytest): create two Supabase users, upload a resume as each, confirm
  `POST /analyze/` with user A's token + user B's `resume_id` returns 404, and that
  `GET /resume/` only ever lists the caller's own resumes.
- Manually verify the middleware redirect (visit `/` logged out → lands on
  `/login`) and the full signup → upload → analyze → refresh → still-there flow.
