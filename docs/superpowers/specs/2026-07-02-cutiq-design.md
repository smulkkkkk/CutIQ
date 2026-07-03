# CutIQ — Design Spec
**Data:** 2026-07-02  
**Status:** Aprovado  
**Escopo:** MVP completo (Fases 1–5)

---

## 1. Visão Geral

CutIQ é um SaaS que transforma vídeos longos em Shorts virais automaticamente usando IA. O usuário faz upload de um vídeo (ou importa por URL do YouTube), e o sistema transcreve, analisa os melhores momentos com IA, e gera clips em formato 9:16 com legendas animadas, face zoom e pontuação de viralidade.

### Decisões Chave
- **AI Stack:** Whisper local (faster-whisper) para transcrição + Claude API (Anthropic) para análise de momentos e virality score
- **Queue:** ARQ (async Python, Redis-backed) — substitui BullMQ por ser nativo ao ecosistema FastAPI/asyncio
- **Storage:** Cloudflare R2 com upload direto via presigned URL (frontend → R2, sem passar pelo backend)
- **Auth:** Supabase Auth com JWT validado no FastAPI via middleware

---

## 2. Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| Backend | FastAPI (Python 3.12) |
| Banco de dados | Supabase (PostgreSQL) com RLS |
| Autenticação | Supabase Auth |
| Armazenamento | Cloudflare R2 (presigned URLs) |
| Pagamentos | Stripe (Hosted Checkout + Webhooks) |
| Filas | Redis + ARQ |
| Transcrição | faster-whisper (local, CPU/GPU) |
| Análise IA | Claude API (Anthropic) |
| Renderização | FFmpeg (subprocess via integrations/) |
| Deploy | Docker + Docker Compose |
| Tempo real | WebSocket nativo FastAPI |

---

## 3. Fases do MVP

| Fase | Nome | Entrega |
|------|------|---------|
| 1 | Foundation | Monorepo, Docker, Auth, Dashboard shell, schema DB |
| 2 | Pipeline | Upload, R2, YouTube import, ARQ workers, Whisper |
| 3 | IA + Cortes | Claude analysis, virality score, clips gerados |
| 4 | Renderização | FFmpeg output, legendas, face zoom, reframe 9:16, watermark, export |
| 5 | Pagamentos | Stripe planos, créditos, limites, webhooks |

**Fases futuras (pós-MVP):**
- Fase 6: Editor visual + templates de legenda
- Fase 7: Analytics de uso + Painel administrativo

---

## 4. Estrutura do Monorepo

```
cutiq/
├── apps/
│   ├── frontend/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── projects/[id]/
│   │   │   │   ├── upload/
│   │   │   │   └── billing/
│   │   │   └── (admin)/
│   │   │       └── admin/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── navigation/
│   │   │   ├── forms/
│   │   │   ├── modals/
│   │   │   ├── charts/
│   │   │   ├── dashboard/
│   │   │   ├── player/
│   │   │   └── billing/
│   │   ├── lib/
│   │   │   ├── supabase/
│   │   │   ├── api/
│   │   │   └── hooks/
│   │   ├── types/
│   │   ├── notifications/
│   │   │   ├── ws-provider.tsx
│   │   │   └── use-job-progress.ts
│   │   └── middleware.ts
│   │
│   └── backend/
│       ├── app/
│       │   ├── main.py
│       │   ├── api/
│       │   │   ├── deps.py
│       │   │   └── routes/
│       │   │       ├── auth.py
│       │   │       ├── projects.py
│       │   │       ├── videos.py
│       │   │       ├── clips.py
│       │   │       └── billing.py
│       │   ├── models/
│       │   │   ├── project.py
│       │   │   ├── clip.py
│       │   │   ├── job.py
│       │   │   └── user.py
│       │   ├── schemas/
│       │   │   ├── project.py
│       │   │   ├── clip.py
│       │   │   ├── billing.py
│       │   │   └── job.py
│       │   ├── repositories/
│       │   │   ├── base.py
│       │   │   ├── projects.py
│       │   │   ├── clips.py
│       │   │   ├── jobs.py
│       │   │   └── users.py
│       │   ├── services/
│       │   │   ├── processing.py
│       │   │   ├── virality.py
│       │   │   ├── credits.py
│       │   │   └── export.py
│       │   ├── integrations/
│       │   │   ├── claude.py
│       │   │   ├── whisper.py
│       │   │   ├── ffmpeg.py
│       │   │   ├── r2.py
│       │   │   ├── stripe.py
│       │   │   └── youtube.py
│       │   ├── workers/
│       │   │   ├── queue.py
│       │   │   ├── transcribe.py
│       │   │   ├── analyze.py
│       │   │   └── render.py
│       │   ├── websocket/
│       │   │   ├── manager.py
│       │   │   └── events.py
│       │   ├── constants/
│       │   │   ├── plans.py
│       │   │   └── ffmpeg.py
│       │   ├── utils/
│       │   │   ├── time.py
│       │   │   ├── video.py
│       │   │   └── text.py
│       │   └── core/
│       │       ├── config.py
│       │       └── supabase.py
│       ├── tests/
│       │   ├── api/
│       │   ├── services/
│       │   ├── workers/
│       │   └── repositories/
│       ├── Dockerfile
│       └── requirements.txt
│
├── infra/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/nginx.conf
│
└── docs/
    └── superpowers/specs/
```

**Fluxo de dependências (uma direção apenas):**
```
routes → schemas
routes → services → repositories → Supabase
services → integrations
workers → services + repositories + websocket
```

---

## 5. Schema do Banco de Dados

### Tabelas

```sql
CREATE TABLE profiles (
  id                 uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  full_name          text,
  avatar_url         text,
  plan               text NOT NULL DEFAULT 'free',
  credits_used       int  NOT NULL DEFAULT 0,
  credits_limit      int  NOT NULL DEFAULT 3,
  stripe_customer_id text,
  is_admin           boolean DEFAULT false,
  created_at         timestamptz DEFAULT now(),
  updated_at         timestamptz DEFAULT now()
);

CREATE TABLE projects (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  title      text NOT NULL,
  status     text NOT NULL DEFAULT 'created',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE videos (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id       uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  user_id          uuid NOT NULL REFERENCES profiles,
  source_type      text NOT NULL,
  source_url       text,
  r2_key           text,
  filename         text NOT NULL,
  duration_seconds float,
  size_bytes       bigint,
  status           text NOT NULL DEFAULT 'pending',
  created_at       timestamptz DEFAULT now()
);

CREATE TABLE transcriptions (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id   uuid NOT NULL REFERENCES videos ON DELETE CASCADE,
  language   text,
  content    text,
  segments   jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE clips (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id       uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  video_id         uuid NOT NULL REFERENCES videos,
  title            text,
  start_time       float NOT NULL,
  end_time         float NOT NULL,
  duration         float GENERATED ALWAYS AS (end_time - start_time) STORED,
  virality_score   int CHECK (virality_score BETWEEN 0 AND 100),
  virality_reasons jsonb,
  status           text NOT NULL DEFAULT 'pending',
  r2_key           text,
  thumbnail_r2_key text,
  resolution       text DEFAULT '720p',
  has_watermark    boolean DEFAULT true,
  caption_style    text DEFAULT 'default',
  created_at       timestamptz DEFAULT now(),
  updated_at       timestamptz DEFAULT now()
);

CREATE TABLE jobs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    uuid NOT NULL REFERENCES projects ON DELETE CASCADE,
  type          text NOT NULL,
  status        text NOT NULL DEFAULT 'queued',
  progress      int  DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  error_message text,
  arq_job_id    text,
  started_at    timestamptz,
  completed_at  timestamptz,
  created_at    timestamptz DEFAULT now()
);

CREATE TABLE subscriptions (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  stripe_subscription_id text UNIQUE NOT NULL,
  stripe_price_id        text NOT NULL,
  plan                   text NOT NULL,
  billing_period         text NOT NULL,
  status                 text NOT NULL,
  current_period_start   timestamptz,
  current_period_end     timestamptz,
  created_at             timestamptz DEFAULT now(),
  updated_at             timestamptz DEFAULT now()
);

CREATE TABLE credit_transactions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES profiles ON DELETE CASCADE,
  project_id  uuid REFERENCES projects,
  amount      int NOT NULL,
  type        text NOT NULL,
  description text,
  created_at  timestamptz DEFAULT now()
);
```

### Índices

```sql
CREATE INDEX ON projects (user_id, created_at DESC);
CREATE INDEX ON clips (project_id, virality_score DESC);
CREATE INDEX ON jobs (project_id, status);
CREATE INDEX ON credit_transactions (user_id, created_at DESC);
```

### RLS

Todas as tabelas têm RLS habilitado com política `user_id = auth.uid()`. Workers e webhooks usam `service_role` key (bypass automático).

---

## 6. Pipeline de Processamento

### Fluxo completo

```
Upload/Import → POST /api/videos → presigned URL R2
     ↓
Confirma upload → POST /api/videos/{id}/process
     ↓
[ARQ] JOB 1: transcribe
  - Baixa vídeo do R2
  - Extrai áudio (ffmpeg)
  - Roda faster-whisper → segments
  - Salva transcription no DB
  - Emite WS: { stage: "transcribed" }
  - Enfileira JOB 2
     ↓
[ARQ] JOB 2: analyze
  - Carrega transcrição
  - Chunks de ~4000 tokens
  - Claude API → [{ start, end, title, score, reasons[] }]
  - Normaliza scores 0–100
  - Salva clips no DB (status: pending)
  - Emite WS: { stage: "analyzed", clips_count: N }
  - Enfileira N × JOB 3
     ↓
[ARQ] JOB 3: render (N em paralelo)
  - Corte FFmpeg no timestamp
  - Reframe 9:16
  - Face zoom: OpenCV/MediaPipe detecta coordenadas do rosto → FFmpeg aplica crop dinâmico
  - Legendas animadas (ASS overlay)
  - Watermark (se plano Free)
  - Encode H.264/AAC na resolução do plano
  - Upload para R2
  - Gera thumbnail
  - Atualiza clip status → "ready"
  - Emite WS: { stage: "clip_ready", clip_id }
```

### Comportamento em falha

| Situação | Comportamento |
|----------|--------------|
| Whisper falha | Job `failed`, crédito não debitado, WS notifica |
| Claude falha | Retry 3× com backoff exponencial |
| FFmpeg falha num clip | Só aquele clip fica `failed`, demais continuam |
| Upload R2 falha | Retry 3×, depois job `failed` |

### Prompt Claude

```
Dado a transcrição de um vídeo de {duration}s, identifique os 5–10 melhores
momentos para Shorts virais. Para cada momento, retorne:
- start_time e end_time (segundos)
- title (max 60 chars)
- virality_score (0–100)
- reasons (array de 2–4 motivos concretos)

Critérios: gancho nos primeiros 3s, intensidade emocional, conclusão clara,
sem corte no meio de raciocínio.

Transcrição: {transcript_chunks}

Responda SOMENTE em JSON válido.
```

---

## 7. Planos e Sistema de Créditos

### Planos

| | FREE | STARTER | PRO | ANNUAL |
|--|------|---------|-----|--------|
| Preço | $0 | $19/mês | $49/mês | $470/ano |
| Créditos/mês | 3 | 25 | ilimitado | ilimitado |
| Resolução | 720p | 1080p | 1080p/4K | 1080p/4K |
| Watermark | ✓ | ✗ | ✗ | ✗ |
| Duração máx. | 30 min | 2 horas | 4 horas | 4 horas |
| Clips/projeto | 3 | 10 | ilimitado | ilimitado |
| Prioridade fila | baixa | normal | alta | alta |

### Fluxo Stripe

1. Frontend → `POST /api/billing/checkout` → retorna `checkout_url`
2. Redirect para Stripe Hosted Checkout
3. Stripe → `POST /api/billing/webhook`
   - `checkout.session.completed` → cria subscription, atualiza plano
   - `invoice.paid` → reseta `credits_used = 0`
   - `customer.subscription.updated` → atualiza plano
   - `customer.subscription.deleted` → reverte para Free

### Regra de crédito

- Crédito debitado apenas quando o job `transcribe` **inicia** (não no upload)
- Planos Pro não têm limite de créditos (verificação é pulada)
- Falha no job não debita crédito

---

## 8. WebSocket — Progresso em Tempo Real

**Conexão:** `ws://backend/ws/{project_id}?token={jwt}`

**Eventos emitidos pelo backend:**

```typescript
type JobProgressEvent =
  | { stage: "transcribing"; progress: number }
  | { stage: "transcribed"; duration: number }
  | { stage: "analyzing"; progress: number }
  | { stage: "analyzed"; clips_count: number }
  | { stage: "rendering"; clip_id: string; progress: number }
  | { stage: "clip_ready"; clip_id: string; thumbnail_url: string }
  | { stage: "completed" }
  | { stage: "failed"; message: string }
```

**Frontend:** `notifications/ws-provider.tsx` mantém a conexão e distribui eventos via React Context. `use-job-progress.ts` é o hook consumido pelos componentes.

---

## 9. Docker Compose (desenvolvimento)

```yaml
services:
  frontend:
    build: ./apps/frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_SUPABASE_URL
      - NEXT_PUBLIC_SUPABASE_ANON_KEY
      - NEXT_PUBLIC_API_URL=http://backend:8000

  backend:
    build: ./apps/backend
    ports: ["8000:8000"]
    depends_on: [redis]
    volumes:
      - ./apps/backend:/app
      - whisper_models:/models
    environment:
      - SUPABASE_URL
      - SUPABASE_SERVICE_ROLE_KEY
      - ANTHROPIC_API_KEY
      - CLOUDFLARE_R2_*
      - STRIPE_SECRET_KEY
      - STRIPE_WEBHOOK_SECRET
      - REDIS_URL=redis://redis:6379

  worker:
    build: ./apps/backend
    command: python -m arq app.workers.queue.WorkerSettings
    depends_on: [redis, backend]
    volumes:
      - whisper_models:/models
    environment:
      - *backend-env

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  whisper_models:
```

---

## 10. Variáveis de Ambiente

### Backend (`.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
ANTHROPIC_API_KEY=
CLOUDFLARE_R2_ENDPOINT=
CLOUDFLARE_R2_ACCESS_KEY=
CLOUDFLARE_R2_SECRET_KEY=
CLOUDFLARE_R2_BUCKET=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_STARTER_MONTHLY=
STRIPE_PRICE_STARTER_ANNUAL=
STRIPE_PRICE_PRO_MONTHLY=
STRIPE_PRICE_PRO_ANNUAL=
REDIS_URL=redis://localhost:6379
WHISPER_MODEL=medium
WHISPER_DEVICE=cpu
```

### Frontend (`.env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

---

## 11. Fora do Escopo do MVP

- Editor visual de legendas (Fase 6)
- Templates customizados de identidade visual (Fase 6)
- Analytics de uso detalhado (Fase 7)
- Painel administrativo (Fase 7)
- Export em formato MOV (Pro, Fase 4+)
- OAuth social (Google, GitHub) — auth por email/senha no MVP
- Internacionalização (i18n)
