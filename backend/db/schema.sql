-- Yojana Saathi — Supabase schema.
-- Run once in Supabase Dashboard → SQL Editor → New query → paste → Run.
-- Safe to re-run (IF NOT EXISTS everywhere).
--
-- The backend talks to Supabase with the SERVICE ROLE key, which bypasses
-- Row Level Security. RLS is still enabled so the public ANON key (shipped to
-- the browser) cannot read or write these tables directly.

-- App-level user profile (login identities live in Supabase's auth.users).
CREATE TABLE IF NOT EXISTS public.users (
    id                 UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    phone              TEXT,
    name               TEXT,
    profile            JSONB NOT NULL DEFAULT '{}',
    preferred_language TEXT  NOT NULL DEFAULT 'en',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Government schemes (source of truth; filled by scripts/seed_db.py).
CREATE TABLE IF NOT EXISTS public.schemes (
    id                 TEXT PRIMARY KEY,           -- e.g. "pm-mudra-shishu"
    title              TEXT NOT NULL,
    title_hi           TEXT,
    title_kn           TEXT,
    description        TEXT,
    eligibility_text   TEXT,
    benefits_text      TEXT,
    funding_amount     BIGINT,                     -- INR
    category           TEXT[] NOT NULL DEFAULT '{}',
    target_group       TEXT[] NOT NULL DEFAULT '{}',
    ministry           TEXT,
    state              TEXT NOT NULL DEFAULT 'all',
    min_age            INT,
    max_age            INT,
    max_income         BIGINT,
    documents_required TEXT[] NOT NULL DEFAULT '{}',
    application_url    TEXT,
    deadline           DATE,
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    raw_data           JSONB,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Applications submitted through the app.
-- user_id points at auth.users so a logged-in user's id is accepted directly;
-- it is nullable because guests can apply too.
CREATE TABLE IF NOT EXISTS public.applications (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    scheme_id             TEXT REFERENCES public.schemes(id),
    status                TEXT NOT NULL DEFAULT 'draft',  -- draft|applied|under_review|approved|rejected
    eligibility_score     INT,
    eligibility_reasoning TEXT,
    form_data             JSONB NOT NULL DEFAULT '{}',
    applied_at            TIMESTAMPTZ,
    last_checked          TIMESTAMPTZ,
    status_history        JSONB NOT NULL DEFAULT '[]',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schemes_category    ON public.schemes USING GIN (category);
CREATE INDEX IF NOT EXISTS idx_schemes_state       ON public.schemes (state);
CREATE INDEX IF NOT EXISTS idx_applications_user   ON public.applications (user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON public.applications (status);

ALTER TABLE public.users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schemes      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

-- Scheme catalogue is public information: anyone may read it.
DROP POLICY IF EXISTS "schemes are public" ON public.schemes;
CREATE POLICY "schemes are public" ON public.schemes FOR SELECT USING (true);

-- Logged-in users may read their own profile and applications.
DROP POLICY IF EXISTS "own profile" ON public.users;
CREATE POLICY "own profile" ON public.users FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "own applications" ON public.applications;
CREATE POLICY "own applications" ON public.applications FOR SELECT USING (auth.uid() = user_id);
