-- ========================================
-- CutIQ - Schema Inicial
-- Executar no SQL Editor do Supabase
-- ========================================

-- Profiles (estende auth.users)
CREATE TABLE IF NOT EXISTS profiles (
  id                 uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  full_name          text,
  avatar_url         text,
  plan               text NOT NULL DEFAULT 'free'
                     CHECK (plan IN ('free', 'starter', 'pro')),
  credits_used       int  NOT NULL DEFAULT 0,
  credits_limit      int  NOT NULL DEFAULT 3,
  stripe_customer_id text,
  is_admin           boolean NOT NULL DEFAULT false,
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now()
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  title      text NOT NULL,
  status     text NOT NULL DEFAULT 'created'
             CHECK (status IN ('created','uploading','transcribing','analyzing','rendering','completed','failed')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Videos
CREATE TABLE IF NOT EXISTS videos (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id       uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  user_id          uuid NOT NULL REFERENCES profiles,
  source_type      text NOT NULL CHECK (source_type IN ('upload', 'youtube')),
  source_url       text,
  r2_key           text,
  filename         text NOT NULL,
  duration_seconds float,
  size_bytes       bigint,
  status           text NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending', 'ready', 'failed')),
  created_at       timestamptz NOT NULL DEFAULT now()
);

-- Transcriptions
CREATE TABLE IF NOT EXISTS transcriptions (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id   uuid NOT NULL REFERENCES videos ON DELETE CASCADE,
  language   text,
  content    text,
  segments   jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Clips
CREATE TABLE IF NOT EXISTS clips (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id       uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  video_id         uuid NOT NULL REFERENCES videos,
  title            text,
  start_time       float NOT NULL,
  end_time         float NOT NULL,
  duration         float GENERATED ALWAYS AS (end_time - start_time) STORED,
  virality_score   int CHECK (virality_score BETWEEN 0 AND 100),
  virality_reasons jsonb,
  status           text NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending', 'rendering', 'ready', 'failed')),
  r2_key           text,
  thumbnail_r2_key text,
  resolution       text NOT NULL DEFAULT '720p'
                   CHECK (resolution IN ('720p', '1080p', '4k')),
  has_watermark    boolean NOT NULL DEFAULT true,
  caption_style    text NOT NULL DEFAULT 'default',
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);

-- Jobs
CREATE TABLE IF NOT EXISTS jobs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  type          text NOT NULL CHECK (type IN ('transcribe', 'analyze', 'render')),
  status        text NOT NULL DEFAULT 'queued'
                CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
  progress      int  NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  error_message text,
  arq_job_id    text,
  started_at    timestamptz,
  completed_at  timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- Subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  stripe_subscription_id text UNIQUE NOT NULL,
  stripe_price_id        text NOT NULL,
  plan                   text NOT NULL CHECK (plan IN ('starter', 'pro')),
  billing_period         text NOT NULL CHECK (billing_period IN ('monthly', 'annual')),
  status                 text NOT NULL
                         CHECK (status IN ('active', 'canceled', 'past_due', 'trialing')),
  current_period_start   timestamptz,
  current_period_end     timestamptz,
  created_at             timestamptz NOT NULL DEFAULT now(),
  updated_at             timestamptz NOT NULL DEFAULT now()
);

-- Credit Transactions
CREATE TABLE IF NOT EXISTS credit_transactions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  project_id  uuid REFERENCES projects,
  amount      int NOT NULL,
  type        text NOT NULL
              CHECK (type IN ('usage', 'monthly_reset', 'plan_upgrade', 'refund')),
  description text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- ========================================
-- Índices
-- ========================================
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clips_project_score ON clips (project_id, virality_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_project_status ON jobs (project_id, status);
CREATE INDEX IF NOT EXISTS idx_credit_tx_user_created ON credit_transactions (user_id, created_at DESC);

-- ========================================
-- Row Level Security
-- ========================================
ALTER TABLE profiles           ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects           ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos             ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcriptions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE clips              ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs               ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

-- Policies: usuário vê apenas seus próprios dados
CREATE POLICY "own profiles"    ON profiles            FOR ALL USING (id = auth.uid());
CREATE POLICY "own projects"    ON projects            FOR ALL USING (user_id = auth.uid());
CREATE POLICY "own videos"      ON videos              FOR ALL USING (user_id = auth.uid());
CREATE POLICY "own clips"       ON clips               FOR ALL
  USING (project_id IN (SELECT id FROM projects WHERE user_id = auth.uid()));
CREATE POLICY "own jobs"        ON jobs                FOR ALL
  USING (project_id IN (SELECT id FROM projects WHERE user_id = auth.uid()));
CREATE POLICY "own transcriptions" ON transcriptions   FOR ALL
  USING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "own subscriptions"  ON subscriptions    FOR ALL USING (user_id = auth.uid());
CREATE POLICY "own transactions"   ON credit_transactions FOR ALL USING (user_id = auth.uid());

-- ========================================
-- Trigger: cria profile automaticamente após signup
-- ========================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (
    new.id,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
