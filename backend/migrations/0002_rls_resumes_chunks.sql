-- Row Level Security as defense-in-depth on top of the FastAPI ownership
-- checks (app/auth.py, routers/resume.py, routers/analyze.py) — not a
-- replacement for them.
--
-- CAVEAT: the backend connects to Postgres with a direct connection string
-- (DATABASE_URL, transaction pooler), not through Supabase's PostgREST/anon
-- key layer, so `auth.uid()` is NOT populated for the backend's own queries
-- and these policies do not constrain them. They protect every *other* access
-- path instead: the Supabase Studio SQL editor, a future client hitting
-- Supabase directly with the anon key, or a leaked anon key. Run this once
-- against Supabase (SQL editor or psql).

ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage their own resumes" ON resumes
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage chunks of their own resumes" ON chunks
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM resumes
            WHERE resumes.id = chunks.resume_id
              AND resumes.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM resumes
            WHERE resumes.id = chunks.resume_id
              AND resumes.user_id = auth.uid()
        )
    );
