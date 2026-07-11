-- Run once against the Supabase project (SQL editor or psql).
-- Adds ownership to resumes. Nullable so it does NOT fail or drop the
-- existing row — backfill happens manually afterward (see below).

ALTER TABLE resumes
    ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users (id);

CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes (user_id);

-- After creating your account in Supabase Auth, find your user id
-- (Authentication -> Users in the dashboard, or `select id from auth.users;`)
-- and backfill the existing row:
--
-- UPDATE resumes SET user_id = '<your-user-uuid>' WHERE id = <existing-resume-id>;
--
-- Once every row has a user_id, tighten the column in a follow-up migration:
--
-- ALTER TABLE resumes ALTER COLUMN user_id SET NOT NULL;
