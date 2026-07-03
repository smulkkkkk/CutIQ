# CutIQ Phase 1: Foundation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Monorepo com Docker Compose funcionando, autenticação via Supabase, schema do banco criado e dashboard shell protegido com rota de login/cadastro.

**Architecture:** Next.js 15 (App Router) no frontend e FastAPI no backend em monorepo único. Supabase Auth emite JWTs que o FastAPI valida via `supabase.auth.get_user(token)`. O middleware do Next.js protege rotas via cookie de sessão do Supabase SSR.

**Tech Stack:** Next.js 15, React 19, TypeScript 5, Tailwind CSS v3, shadcn/ui, Framer Motion v11, FastAPI 0.115, Python 3.12, Pydantic v2, supabase-py 2.x, @supabase/ssr, Docker Compose.

## Global Constraints

- Python 3.12+; FastAPI 0.115+; Pydantic v2 (não v1)
- Next.js 15 App Router exclusivamente — nenhum arquivo em `pages/`
- TypeScript strict mode (`"strict": true` no tsconfig)
- Todas as rotas da API FastAPI prefixadas com `/api`
- RLS habilitado em todas as tabelas; workers usam `service_role` key
- Tailwind CSS v3 (não v4)
- Componentes shadcn/ui em `apps/frontend/components/ui/`
- Nenhum CSS customizado fora de `app/globals.css`
- Diretório raiz do projeto: `c:\Users\samue\projetos\CutIQ`
- Comandos de shell assumem Git Bash ou WSL (não PowerShell)

---

## Mapa de Arquivos

### Raiz do monorepo
| Arquivo | Responsabilidade |
|---------|-----------------|
| `.gitignore` | Ignora node_modules, __pycache__, .env, .next, dist |
| `.env.example` | Template de todas as variáveis de ambiente |
| `docker-compose.yml` | Orquestra frontend, backend, worker, redis |

### Backend (`apps/backend/`)
| Arquivo | Responsabilidade |
|---------|-----------------|
| `Dockerfile` | Imagem Python 3.12 para API e worker |
| `requirements.txt` | Dependências Python pinadas |
| `pyproject.toml` | Config pytest (asyncio_mode=auto) |
| `app/main.py` | App FastAPI, CORS, routers |
| `app/core/config.py` | Settings via pydantic-settings |
| `app/core/supabase.py` | Singleton do cliente Supabase admin |
| `app/api/deps.py` | Middleware de auth (valida JWT) |
| `app/api/routes/auth.py` | GET /api/auth/me |
| `app/models/user.py` | Dataclass Profile (domínio) |
| `app/schemas/auth.py` | Pydantic ProfileResponse (I/O da API) |
| `app/repositories/base.py` | BaseRepository com acesso ao Supabase |
| `app/repositories/users.py` | Operações de profiles no banco |
| `tests/conftest.py` | Fixtures: AsyncClient, mock_supabase_user |
| `tests/api/test_health.py` | Testa GET /health |
| `tests/api/test_auth.py` | Testa GET /api/auth/me |
| `tests/repositories/test_users.py` | Testa UserRepository |
| `migrations/001_initial_schema.sql` | Schema completo (todas as tabelas do spec) |

### Frontend (`apps/frontend/`)
| Arquivo | Responsabilidade |
|---------|-----------------|
| `Dockerfile` | Imagem Node 20 para Next.js |
| `package.json` | Deps do projeto |
| `next.config.ts` | Config Next.js (rewrites para API) |
| `tailwind.config.ts` | Tema e paths do Tailwind |
| `tsconfig.json` | TypeScript strict + path aliases |
| `middleware.ts` | Proteção de rotas via Supabase SSR |
| `app/globals.css` | Variáveis CSS do shadcn + base styles |
| `app/layout.tsx` | Root layout (fonts, Toaster) |
| `app/(auth)/layout.tsx` | Layout centralizado para login/register |
| `app/(auth)/login/page.tsx` | Página de login |
| `app/(auth)/register/page.tsx` | Página de cadastro |
| `app/(dashboard)/layout.tsx` | Layout com Sidebar + Header |
| `app/(dashboard)/dashboard/page.tsx` | Home do dashboard (stats placeholder) |
| `components/layout/Sidebar.tsx` | Sidebar com logo e navegação |
| `components/layout/Header.tsx` | Header com avatar e menu do usuário |
| `components/navigation/NavLinks.tsx` | Links ativos com highlight |
| `components/forms/LoginForm.tsx` | Form de login com Supabase Auth |
| `components/forms/RegisterForm.tsx` | Form de cadastro com Supabase Auth |
| `components/dashboard/StatsCard.tsx` | Card de estatística genérico |
| `lib/supabase/client.ts` | createBrowserClient |
| `lib/supabase/server.ts` | createServerClient (App Router) |
| `lib/api/client.ts` | Fetch wrapper tipado para FastAPI |
| `lib/hooks/useUser.ts` | Hook para ler usuário autenticado |
| `types/index.ts` | Tipos compartilhados (Profile, Plan, etc.) |

---

## Task 1: Monorepo scaffold + Docker Compose

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `apps/backend/Dockerfile`
- Create: `apps/frontend/Dockerfile`
- Create: `apps/backend/app/__init__.py` (vazio)
- Create: `apps/backend/tests/__init__.py` (vazio)

**Interfaces:**
- Produces: ambiente Docker rodando com `docker compose up`

- [ ] **Step 1: Criar estrutura de diretórios**

```bash
cd c:/Users/samue/projetos/CutIQ
mkdir -p apps/frontend apps/backend/app/api/routes apps/backend/app/core \
  apps/backend/app/models apps/backend/app/schemas apps/backend/app/repositories \
  apps/backend/app/workers apps/backend/app/websocket apps/backend/app/integrations \
  apps/backend/app/services apps/backend/app/constants apps/backend/app/utils \
  apps/backend/tests/api apps/backend/tests/repositories apps/backend/tests/services \
  apps/backend/tests/workers apps/backend/migrations infra/nginx
touch apps/backend/app/__init__.py apps/backend/app/api/__init__.py \
  apps/backend/app/api/routes/__init__.py apps/backend/app/core/__init__.py \
  apps/backend/app/models/__init__.py apps/backend/app/schemas/__init__.py \
  apps/backend/app/repositories/__init__.py apps/backend/tests/__init__.py \
  apps/backend/tests/api/__init__.py apps/backend/tests/repositories/__init__.py
```

- [ ] **Step 2: Criar `.gitignore`**

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
dist/
.pytest_cache/

# Node
node_modules/
.next/
out/

# Env
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Docker
*.log
```

- [ ] **Step 3: Criar `.env.example`**

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Cloudflare R2 (preencher na Fase 2)
CLOUDFLARE_R2_ENDPOINT=
CLOUDFLARE_R2_ACCESS_KEY=
CLOUDFLARE_R2_SECRET_KEY=
CLOUDFLARE_R2_BUCKET=

# Stripe (preencher na Fase 5)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_STARTER_MONTHLY=
STRIPE_PRICE_STARTER_ANNUAL=
STRIPE_PRICE_PRO_MONTHLY=
STRIPE_PRICE_PRO_ANNUAL=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

# Anthropic (preencher na Fase 3)
ANTHROPIC_API_KEY=

# Redis
REDIS_URL=redis://redis:6379

# Whisper (preencher na Fase 2)
WHISPER_MODEL=medium
WHISPER_DEVICE=cpu

# App
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVIRONMENT=development
```

- [ ] **Step 4: Criar `docker-compose.yml`**

```yaml
services:
  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file: .env
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./apps/frontend:/app
      - /app/node_modules
      - /app/.next

  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - redis
    volumes:
      - ./apps/backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    env_file: .env
    depends_on:
      - redis
      - backend
    volumes:
      - ./apps/backend:/app
    command: python -m arq app.workers.queue.WorkerSettings

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  whisper_models:
```

- [ ] **Step 5: Criar `apps/backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 6: Criar `apps/frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
```

- [ ] **Step 7: Verificar estrutura**

```bash
ls apps/backend/app/
# esperado: __init__.py api core models repositories schemas
ls apps/frontend/
# esperado: Dockerfile (node_modules virá depois do npm install)
```

- [ ] **Step 8: Commit**

```bash
git init
git add .
git commit -m "feat: monorepo scaffold with Docker Compose"
```

---

## Task 2: FastAPI skeleton + health endpoint

**Files:**
- Create: `apps/backend/requirements.txt`
- Create: `apps/backend/pyproject.toml`
- Create: `apps/backend/app/core/config.py`
- Create: `apps/backend/app/main.py`
- Create: `apps/backend/tests/conftest.py`
- Create: `apps/backend/tests/api/test_health.py`

**Interfaces:**
- Produces: `GET /health → { "status": "ok" }`; `Settings` importável de `app.core.config`

- [ ] **Step 1: Escrever teste de health check (vai falhar)**

`apps/backend/tests/api/test_health.py`:
```python
import pytest

@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Criar `apps/backend/requirements.txt`**

```
fastapi==0.115.6
uvicorn[standard]==0.32.0
pydantic-settings==2.6.0
supabase==2.10.0
python-multipart==0.0.18
httpx==0.28.0
pytest==8.3.0
pytest-asyncio==0.24.0
anyio==4.7.0
```

- [ ] **Step 3: Criar `apps/backend/pyproject.toml`**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 4: Criar `apps/backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    redis_url: str = "redis://localhost:6379"
    environment: str = "development"

settings = Settings()
```

- [ ] **Step 5: Criar `apps/backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CutIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Criar `apps/backend/tests/conftest.py`**

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
def mock_supabase_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    return user
```

- [ ] **Step 7: Instalar dependências e rodar o teste**

```bash
cd apps/backend
pip install -r requirements.txt
pytest tests/api/test_health.py -v
```

Esperado: `PASSED`

- [ ] **Step 8: Commit**

```bash
git add apps/backend/
git commit -m "feat: FastAPI skeleton with health endpoint"
```

---

## Task 3: Supabase client + JWT auth middleware

**Files:**
- Create: `apps/backend/app/core/supabase.py`
- Create: `apps/backend/app/api/deps.py`
- Create: `apps/backend/tests/api/test_deps.py`

**Interfaces:**
- Produces: `get_current_user` dependency injetável em qualquer rota; retorna `gotrue.User`

- [ ] **Step 1: Escrever teste do middleware (vai falhar)**

`apps/backend/tests/api/test_deps.py`:
```python
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from app.api.deps import get_current_user

# App temporário para testar o dep isolado
_test_app = FastAPI()

@_test_app.get("/protected")
async def protected_route(user=__import__('fastapi').Depends(get_current_user)):
    return {"user_id": user.id}

@pytest.fixture
async def dep_client():
    async with AsyncClient(
        transport=ASGITransport(app=_test_app), base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_no_token_returns_403(dep_client):
    response = await dep_client.get("/protected")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_invalid_token_returns_401(dep_client):
    with patch("app.api.deps.get_supabase") as mock_get:
        from supabase import AuthApiError
        mock_sb = MagicMock()
        mock_sb.auth.get_user.side_effect = AuthApiError("invalid", 401, {})
        mock_get.return_value = mock_sb

        response = await dep_client.get(
            "/protected", headers={"Authorization": "Bearer bad-token"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_valid_token_returns_user(dep_client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_get:
        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_get.return_value = mock_sb

        response = await dep_client.get(
            "/protected", headers={"Authorization": "Bearer valid-token"}
        )
    assert response.status_code == 200
    assert response.json()["user_id"] == "test-user-id"
```

- [ ] **Step 2: Criar `apps/backend/app/core/supabase.py`**

```python
from supabase import create_client, Client
from app.core.config import settings

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
    return _client
```

- [ ] **Step 3: Criar `apps/backend/app/api/deps.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import AuthApiError
from app.core.supabase import get_supabase

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    supabase = get_supabase()
    try:
        response = supabase.auth.get_user(token)
        return response.user
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
```

- [ ] **Step 4: Rodar os testes**

```bash
cd apps/backend
pytest tests/api/test_deps.py -v
```

Esperado: 3 testes `PASSED`

- [ ] **Step 5: Commit**

```bash
git add apps/backend/app/core/supabase.py apps/backend/app/api/deps.py \
  apps/backend/tests/api/test_deps.py
git commit -m "feat: Supabase client and JWT auth middleware"
```

---

## Task 4: User domain layer (model + schema + repository)

**Files:**
- Create: `apps/backend/app/models/user.py`
- Create: `apps/backend/app/schemas/auth.py`
- Create: `apps/backend/app/repositories/base.py`
- Create: `apps/backend/app/repositories/users.py`
- Create: `apps/backend/tests/repositories/test_users.py`
- Create: `apps/backend/tests/repositories/__init__.py`

**Interfaces:**
- Produces: `UserRepository.get_by_id(user_id: str) -> Profile | None`
- Produces: `UserRepository.upsert_profile(user_id: str, full_name: str | None) -> Profile`
- Produces: `ProfileResponse` Pydantic model para a API

- [ ] **Step 1: Escrever testes do repository (vão falhar)**

`apps/backend/tests/repositories/test_users.py`:
```python
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

MOCK_PROFILE_DATA = {
    "id": "test-user-id",
    "full_name": "Test User",
    "avatar_url": None,
    "plan": "free",
    "credits_used": 0,
    "credits_limit": 3,
    "is_admin": False,
    "stripe_customer_id": None,
    "created_at": "2026-07-02T00:00:00+00:00",
    "updated_at": "2026-07-02T00:00:00+00:00",
}

@pytest.fixture
def repo_with_mock():
    with patch("app.repositories.base.get_supabase") as mock_get:
        mock_sb = MagicMock()
        mock_get.return_value = mock_sb
        from app.repositories.users import UserRepository
        repo = UserRepository()
        repo.client = mock_sb
        yield repo, mock_sb

def test_get_by_id_returns_profile(repo_with_mock):
    repo, mock_sb = repo_with_mock
    mock_sb.table().select().eq().single().execute.return_value = MagicMock(
        data=MOCK_PROFILE_DATA
    )
    profile = repo.get_by_id("test-user-id")
    assert profile is not None
    assert profile.id == "test-user-id"
    assert profile.plan == "free"
    assert profile.credits_limit == 3

def test_get_by_id_returns_none_when_not_found(repo_with_mock):
    repo, mock_sb = repo_with_mock
    mock_sb.table().select().eq().single().execute.return_value = MagicMock(data=None)
    profile = repo.get_by_id("nonexistent")
    assert profile is None
```

- [ ] **Step 2: Criar `apps/backend/app/models/user.py`**

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Profile:
    id: str
    full_name: str | None
    avatar_url: str | None
    plan: str
    credits_used: int
    credits_limit: int
    is_admin: bool
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 3: Criar `apps/backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class ProfileResponse(BaseModel):
    id: str
    full_name: str | None = None
    avatar_url: str | None = None
    plan: str
    credits_used: int
    credits_limit: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Criar `apps/backend/app/repositories/base.py`**

```python
from app.core.supabase import get_supabase

class BaseRepository:
    def __init__(self, table: str):
        self.table = table
        self.client = get_supabase()
```

- [ ] **Step 5: Criar `apps/backend/app/repositories/users.py`**

```python
from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.user import Profile

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("profiles")

    def get_by_id(self, user_id: str) -> Profile | None:
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not response.data:
            return None
        return self._to_model(response.data)

    def upsert_profile(self, user_id: str, full_name: str | None = None) -> Profile:
        self.client.table(self.table).upsert(
            {"id": user_id, "full_name": full_name}
        ).execute()
        return self.get_by_id(user_id)

    def _to_model(self, data: dict) -> Profile:
        return Profile(
            id=data["id"],
            full_name=data.get("full_name"),
            avatar_url=data.get("avatar_url"),
            plan=data["plan"],
            credits_used=data["credits_used"],
            credits_limit=data["credits_limit"],
            is_admin=data["is_admin"],
            stripe_customer_id=data.get("stripe_customer_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
```

- [ ] **Step 6: Rodar testes**

```bash
cd apps/backend
pytest tests/repositories/test_users.py -v
```

Esperado: 2 testes `PASSED`

- [ ] **Step 7: Commit**

```bash
git add apps/backend/app/models/ apps/backend/app/schemas/ \
  apps/backend/app/repositories/ apps/backend/tests/repositories/
git commit -m "feat: user domain layer (model, schema, repository)"
```

---

## Task 5: Auth API route

**Files:**
- Create: `apps/backend/app/api/routes/auth.py`
- Modify: `apps/backend/app/main.py` (include router)
- Create: `apps/backend/tests/api/test_auth.py`

**Interfaces:**
- Consumes: `get_current_user` de `app.api.deps`; `UserRepository` de `app.repositories.users`
- Produces: `GET /api/auth/me → ProfileResponse`

- [ ] **Step 1: Escrever teste da rota (vai falhar)**

`apps/backend/tests/api/test_auth.py`:
```python
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

MOCK_PROFILE = MagicMock(
    id="test-user-id",
    full_name="Test User",
    avatar_url=None,
    plan="free",
    credits_used=0,
    credits_limit=3,
    is_admin=False,
    created_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
    updated_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
)

@pytest.mark.asyncio
async def test_get_me_without_token(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_me_with_invalid_token(client):
    with patch("app.api.deps.get_supabase") as mock_get:
        from supabase import AuthApiError
        mock_sb = MagicMock()
        mock_sb.auth.get_user.side_effect = AuthApiError("invalid", 401, {})
        mock_get.return_value = mock_sb

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer bad"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_returns_profile(client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_deps_sb, \
         patch("app.api.routes.auth.UserRepository") as mock_repo_cls:

        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_deps_sb.return_value = mock_sb

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = MOCK_PROFILE
        mock_repo_cls.return_value = mock_repo

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-user-id"
    assert data["plan"] == "free"
    assert data["credits_limit"] == 3

@pytest.mark.asyncio
async def test_get_me_profile_not_found(client, mock_supabase_user):
    with patch("app.api.deps.get_supabase") as mock_deps_sb, \
         patch("app.api.routes.auth.UserRepository") as mock_repo_cls:

        mock_sb = MagicMock()
        mock_sb.auth.get_user.return_value = MagicMock(user=mock_supabase_user)
        mock_deps_sb.return_value = mock_sb

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_cls.return_value = mock_repo

        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid"}
        )

    assert response.status_code == 404
```

- [ ] **Step 2: Criar `apps/backend/app/api/routes/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from app.api.deps import get_current_user
from app.repositories.users import UserRepository
from app.schemas.auth import ProfileResponse

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    repo = UserRepository()
    profile = repo.get_by_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Contact support.",
        )
    return profile
```

- [ ] **Step 3: Atualizar `apps/backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth

app = FastAPI(title="CutIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Rodar todos os testes do backend**

```bash
cd apps/backend
pytest -v
```

Esperado: todos os testes `PASSED` (health + deps + auth + repository)

- [ ] **Step 5: Commit**

```bash
git add apps/backend/app/api/routes/auth.py apps/backend/app/main.py \
  apps/backend/tests/api/test_auth.py
git commit -m "feat: auth API route GET /api/auth/me"
```

---

## Task 6: Database migration

**Files:**
- Create: `apps/backend/migrations/001_initial_schema.sql`

**Interfaces:**
- Produces: todas as tabelas do spec existindo no Supabase com RLS ativo

- [ ] **Step 1: Criar `apps/backend/migrations/001_initial_schema.sql`**

```sql
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
```

- [ ] **Step 2: Executar a migration no Supabase**

1. Acesse o [Supabase Dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. Vá em **SQL Editor** → **New query**
4. Cole o conteúdo de `migrations/001_initial_schema.sql`
5. Clique em **Run**
6. Esperado: `Success. No rows returned`

- [ ] **Step 3: Verificar tabelas criadas**

No Supabase Dashboard → **Table Editor**, confirme que existem as tabelas:
`profiles`, `projects`, `videos`, `transcriptions`, `clips`, `jobs`, `subscriptions`, `credit_transactions`

- [ ] **Step 4: Commit**

```bash
git add apps/backend/migrations/
git commit -m "feat: initial database schema with RLS and auto-profile trigger"
```

---

## Task 7: Next.js 15 bootstrap + Tailwind + shadcn/ui

**Files:**
- Create: `apps/frontend/package.json`
- Create: `apps/frontend/tsconfig.json`
- Create: `apps/frontend/next.config.ts`
- Create: `apps/frontend/tailwind.config.ts`
- Create: `apps/frontend/postcss.config.mjs`
- Create: `apps/frontend/app/globals.css`
- Create: `apps/frontend/app/layout.tsx`

**Interfaces:**
- Produces: Next.js rodando em `http://localhost:3000` com shadcn/ui disponível

- [ ] **Step 1: Criar `apps/frontend/package.json`**

```json
{
  "name": "cutiq-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.1.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@supabase/supabase-js": "^2.47.0",
    "@supabase/ssr": "^0.5.2",
    "framer-motion": "^11.15.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0",
    "lucide-react": "^0.468.0",
    "sonner": "^1.7.1",
    "@radix-ui/react-slot": "^1.1.1",
    "@radix-ui/react-label": "^2.1.1",
    "@radix-ui/react-avatar": "^1.1.2",
    "@radix-ui/react-dropdown-menu": "^2.1.4",
    "@radix-ui/react-separator": "^1.1.1"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "tailwindcss": "^3.4.17",
    "postcss": "^8",
    "autoprefixer": "^10",
    "eslint": "^9",
    "eslint-config-next": "15.1.6"
  }
}
```

- [ ] **Step 2: Criar `apps/frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 3: Criar `apps/frontend/next.config.ts`**

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '*.r2.dev' },
      { protocol: 'https', hostname: '*.supabase.co' },
    ],
  },
}

export default nextConfig
```

- [ ] **Step 4: Criar `apps/frontend/tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
}

export default config
```

- [ ] **Step 5: Criar `apps/frontend/postcss.config.mjs`**

```javascript
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

export default config
```

- [ ] **Step 6: Criar `apps/frontend/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --primary: 262 83% 58%;
    --primary-foreground: 0 0% 100%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 262 83% 58%;
    --radius: 0.75rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --primary: 262 83% 68%;
    --primary-foreground: 0 0% 100%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 50%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 262 83% 68%;
  }
}

@layer base {
  * { @apply border-border; }
  body { @apply bg-background text-foreground; }
}
```

- [ ] **Step 7: Instalar shadcn/ui e adicionar componentes base**

```bash
cd apps/frontend
npm install
npx shadcn@latest init -d
# Responder: Default style → Default, Base color → Slate, CSS variables → Yes
npx shadcn@latest add button input label avatar dropdown-menu separator
```

- [ ] **Step 8: Criar `apps/frontend/app/layout.tsx`**

```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CutIQ — Cortes Virais com IA',
  description: 'Transforme vídeos longos em Shorts virais automaticamente',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  )
}
```

- [ ] **Step 9: Verificar que o Next.js sobe**

```bash
cd apps/frontend
npm run dev
```

Abrir `http://localhost:3000` — esperado: página 404 padrão do Next.js (sem erros no console)

- [ ] **Step 10: Commit**

```bash
git add apps/frontend/
git commit -m "feat: Next.js 15 bootstrap with Tailwind CSS and shadcn/ui"
```

---

## Task 8: Supabase frontend clients + tipos

**Files:**
- Create: `apps/frontend/lib/supabase/client.ts`
- Create: `apps/frontend/lib/supabase/server.ts`
- Create: `apps/frontend/lib/utils.ts`
- Create: `apps/frontend/types/index.ts`

**Interfaces:**
- Produces: `createClient()` (browser), `createClient()` (server async), tipos `Profile` e `Plan`

- [ ] **Step 1: Criar `apps/frontend/lib/utils.ts`**

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 2: Criar `apps/frontend/types/index.ts`**

```typescript
export type Plan = 'free' | 'starter' | 'pro'

export interface Profile {
  id: string
  full_name: string | null
  avatar_url: string | null
  plan: Plan
  credits_used: number
  credits_limit: number
  is_admin: boolean
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  user_id: string
  title: string
  status: 'created' | 'uploading' | 'transcribing' | 'analyzing' | 'rendering' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface Clip {
  id: string
  project_id: string
  video_id: string
  title: string | null
  start_time: number
  end_time: number
  duration: number
  virality_score: number | null
  virality_reasons: string[] | null
  status: 'pending' | 'rendering' | 'ready' | 'failed'
  r2_key: string | null
  thumbnail_r2_key: string | null
  resolution: '720p' | '1080p' | '4k'
  has_watermark: boolean
  caption_style: string
  created_at: string
  updated_at: string
}

export interface JobProgressEvent {
  stage:
    | 'transcribing'
    | 'transcribed'
    | 'analyzing'
    | 'analyzed'
    | 'rendering'
    | 'clip_ready'
    | 'completed'
    | 'failed'
  progress?: number
  clips_count?: number
  clip_id?: string
  thumbnail_url?: string
  message?: string
}
```

- [ ] **Step 3: Criar diretório e `apps/frontend/lib/supabase/client.ts`**

```bash
mkdir -p apps/frontend/lib/supabase
```

```typescript
import { createBrowserClient } from '@supabase/ssr'

export const createClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
```

- [ ] **Step 4: Criar `apps/frontend/lib/supabase/server.ts`**

```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export const createClient = async () => {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {}
        },
      },
    }
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add apps/frontend/lib/ apps/frontend/types/
git commit -m "feat: Supabase browser/server clients and shared types"
```

---

## Task 9: Auth pages (login + cadastro)

**Files:**
- Create: `apps/frontend/components/forms/LoginForm.tsx`
- Create: `apps/frontend/components/forms/RegisterForm.tsx`
- Create: `apps/frontend/app/(auth)/layout.tsx`
- Create: `apps/frontend/app/(auth)/login/page.tsx`
- Create: `apps/frontend/app/(auth)/register/page.tsx`

**Interfaces:**
- Consumes: `createClient()` de `@/lib/supabase/client`
- Produces: fluxo completo de login e cadastro com redirecionamento para `/dashboard`

- [ ] **Step 1: Criar diretório de forms**

```bash
mkdir -p apps/frontend/components/forms
mkdir -p apps/frontend/app/\(auth\)/login
mkdir -p apps/frontend/app/\(auth\)/register
```

- [ ] **Step 2: Criar `apps/frontend/components/forms/LoginForm.tsx`**

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'

export function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const supabase = createClient()
    const { error } = await supabase.auth.signInWithPassword({ email, password })

    if (error) {
      toast.error(error.message)
      setLoading(false)
      return
    }

    router.push('/dashboard')
    router.refresh()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="voce@exemplo.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Senha</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Entrando...' : 'Entrar'}
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Não tem conta?{' '}
        <Link href="/register" className="text-primary underline-offset-4 hover:underline">
          Cadastre-se
        </Link>
      </p>
    </form>
  )
}
```

- [ ] **Step 3: Criar `apps/frontend/components/forms/RegisterForm.tsx`**

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'

export function RegisterForm() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password.length < 8) {
      toast.error('A senha deve ter ao menos 8 caracteres')
      return
    }
    setLoading(true)

    const supabase = createClient()
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: name } },
    })

    if (error) {
      toast.error(error.message)
      setLoading(false)
      return
    }

    toast.success('Conta criada! Verifique seu email para confirmar.')
    router.push('/login')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Nome completo</Label>
        <Input
          id="name"
          type="text"
          placeholder="Seu Nome"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="voce@exemplo.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Senha</Label>
        <Input
          id="password"
          type="password"
          placeholder="Mín. 8 caracteres"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Criando conta...' : 'Criar conta grátis'}
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Já tem conta?{' '}
        <Link href="/login" className="text-primary underline-offset-4 hover:underline">
          Entrar
        </Link>
      </p>
    </form>
  )
}
```

- [ ] **Step 4: Criar `apps/frontend/app/(auth)/layout.tsx`**

```tsx
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-primary">
            <span className="text-2xl font-black text-primary-foreground">C</span>
          </div>
          <h1 className="text-2xl font-bold">CutIQ</h1>
          <p className="text-sm text-muted-foreground">Cortes virais com IA</p>
        </div>
        <div className="rounded-xl border bg-card p-6 shadow-sm">{children}</div>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Criar `apps/frontend/app/(auth)/login/page.tsx`**

```tsx
import type { Metadata } from 'next'
import { LoginForm } from '@/components/forms/LoginForm'

export const metadata: Metadata = { title: 'Entrar — CutIQ' }

export default function LoginPage() {
  return (
    <>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Bem-vindo de volta</h2>
        <p className="text-sm text-muted-foreground">Entre na sua conta</p>
      </div>
      <LoginForm />
    </>
  )
}
```

- [ ] **Step 6: Criar `apps/frontend/app/(auth)/register/page.tsx`**

```tsx
import type { Metadata } from 'next'
import { RegisterForm } from '@/components/forms/RegisterForm'

export const metadata: Metadata = { title: 'Criar conta — CutIQ' }

export default function RegisterPage() {
  return (
    <>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Criar conta grátis</h2>
        <p className="text-sm text-muted-foreground">3 projetos gratuitos por mês</p>
      </div>
      <RegisterForm />
    </>
  )
}
```

- [ ] **Step 7: Testar manualmente**

```bash
cd apps/frontend && npm run dev
```

1. Acesse `http://localhost:3000/register` — deve mostrar o form de cadastro
2. Crie uma conta com um email real
3. Acesse `http://localhost:3000/login` e entre com as credenciais
4. Deve redirecionar para `/dashboard` (404 por ora — route não existe ainda)

- [ ] **Step 8: Commit**

```bash
git add apps/frontend/components/forms/ apps/frontend/app/\(auth\)/
git commit -m "feat: login and register pages with Supabase Auth"
```

---

## Task 10: Route protection middleware

**Files:**
- Create: `apps/frontend/middleware.ts`

**Interfaces:**
- Consumes: session cookie do Supabase SSR
- Produces: redirect para `/login` se não autenticado; redirect para `/dashboard` se já logado e tentar acessar `/login` ou `/register`

- [ ] **Step 1: Criar `apps/frontend/middleware.ts`**

```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const {
    data: { user },
  } = await supabase.auth.getUser()

  const pathname = request.nextUrl.pathname
  const isAuthRoute = pathname === '/login' || pathname === '/register'

  if (!user && !isAuthRoute) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }

  if (user && isAuthRoute) {
    const url = request.nextUrl.clone()
    url.pathname = '/dashboard'
    return NextResponse.redirect(url)
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon\\.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

- [ ] **Step 2: Testar proteção de rota**

Com o servidor rodando:
1. Abra uma aba anônima e acesse `http://localhost:3000/dashboard`
2. Deve redirecionar para `http://localhost:3000/login`
3. Faça login
4. Tente acessar `http://localhost:3000/login` estando logado
5. Deve redirecionar para `http://localhost:3000/dashboard`

- [ ] **Step 3: Commit**

```bash
git add apps/frontend/middleware.ts
git commit -m "feat: route protection middleware with Supabase SSR"
```

---

## Task 11: Dashboard layout shell (sidebar + header)

**Files:**
- Create: `apps/frontend/lib/hooks/useUser.ts`
- Create: `apps/frontend/components/navigation/NavLinks.tsx`
- Create: `apps/frontend/components/layout/Sidebar.tsx`
- Create: `apps/frontend/components/layout/Header.tsx`
- Create: `apps/frontend/app/(dashboard)/layout.tsx`

**Interfaces:**
- Consumes: `createClient()` browser para ler sessão; `Profile` type
- Produces: layout responsivo com sidebar, header com avatar e navegação ativa

- [ ] **Step 1: Criar diretórios**

```bash
mkdir -p apps/frontend/lib/hooks
mkdir -p apps/frontend/components/layout
mkdir -p apps/frontend/components/navigation
mkdir -p apps/frontend/app/\(dashboard\)/dashboard
```

- [ ] **Step 2: Criar `apps/frontend/lib/hooks/useUser.ts`**

```typescript
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { User } from '@supabase/supabase-js'

export function useUser() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const supabase = createClient()

    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user)
      setLoading(false)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  return { user, loading }
}
```

- [ ] **Step 3: Criar `apps/frontend/components/navigation/NavLinks.tsx`**

```tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FolderOpen, Upload, CreditCard } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/projects', label: 'Projetos', icon: FolderOpen },
  { href: '/upload', label: 'Novo Vídeo', icon: Upload },
  { href: '/billing', label: 'Planos', icon: CreditCard },
]

export function NavLinks() {
  const pathname = usePathname()

  return (
    <nav className="flex flex-col gap-1">
      {links.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            pathname === href || pathname.startsWith(href + '/')
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <Icon className="size-4 shrink-0" />
          {label}
        </Link>
      ))}
    </nav>
  )
}
```

- [ ] **Step 4: Criar `apps/frontend/components/layout/Sidebar.tsx`**

```tsx
'use client'

import { motion } from 'framer-motion'
import { NavLinks } from '@/components/navigation/NavLinks'

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -16, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.2 }}
      className="flex h-screen w-60 shrink-0 flex-col border-r bg-background px-4 py-6"
    >
      <div className="mb-8 flex items-center gap-2 px-3">
        <div className="flex size-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-black text-primary-foreground">C</span>
        </div>
        <span className="text-lg font-bold tracking-tight">CutIQ</span>
      </div>
      <NavLinks />
    </motion.aside>
  )
}
```

- [ ] **Step 5: Criar `apps/frontend/components/layout/Header.tsx`**

```tsx
'use client'

import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useUser } from '@/lib/hooks/useUser'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LogOut, User } from 'lucide-react'

export function Header() {
  const router = useRouter()
  const { user } = useUser()

  const handleSignOut = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  const initials = user?.email?.slice(0, 2).toUpperCase() ?? 'U'

  return (
    <header className="flex h-14 items-center justify-end border-b bg-background px-6">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="rounded-full outline-none ring-ring ring-offset-2 focus:ring-2">
            <Avatar className="size-8 cursor-pointer">
              <AvatarImage src={user?.user_metadata?.avatar_url} />
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <div className="px-2 py-1.5 text-xs text-muted-foreground truncate">
            {user?.email}
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <User className="mr-2 size-4" />
            Perfil
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleSignOut} className="text-destructive">
            <LogOut className="mr-2 size-4" />
            Sair
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
```

- [ ] **Step 6: Criar `apps/frontend/app/(dashboard)/layout.tsx`**

```tsx
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-muted/20 p-6">{children}</main>
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Testar layout**

```bash
npm run dev
```

1. Faça login
2. Deve mostrar sidebar com logo e nav links, header com avatar
3. Clique no avatar → deve mostrar dropdown com email e botão sair
4. Clique em Sair → deve redirecionar para `/login`

- [ ] **Step 8: Commit**

```bash
git add apps/frontend/lib/hooks/ apps/frontend/components/layout/ \
  apps/frontend/components/navigation/ apps/frontend/app/\(dashboard\)/layout.tsx
git commit -m "feat: dashboard shell with sidebar, header and user menu"
```

---

## Task 12: Dashboard home page + API client

**Files:**
- Create: `apps/frontend/lib/api/client.ts`
- Create: `apps/frontend/components/dashboard/StatsCard.tsx`
- Create: `apps/frontend/app/(dashboard)/dashboard/page.tsx`

**Interfaces:**
- Consumes: `Profile` type; `GET /api/auth/me` do backend
- Produces: dashboard home com stats cards e saudação personalizada

- [ ] **Step 1: Criar `apps/frontend/lib/api/client.ts`**

```typescript
import { createClient } from '@/lib/supabase/client'

async function getAuthHeader(): Promise<Record<string, string>> {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) return {}
  return { Authorization: `Bearer ${session.access_token}` }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const authHeader = await getAuthHeader()
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail ?? 'API error')
  }
  return res.json()
}

export const api = {
  auth: {
    me: () => apiFetch<import('@/types').Profile>('/api/auth/me'),
  },
}
```

- [ ] **Step 2: Criar `apps/frontend/components/dashboard/StatsCard.tsx`**

```tsx
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  className?: string
}

export function StatsCard({ title, value, description, icon: Icon, className }: StatsCardProps) {
  return (
    <div className={cn('rounded-xl border bg-card p-5 shadow-sm', className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="size-4 text-primary" />
        </div>
      </div>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      {description && (
        <p className="mt-1 text-xs text-muted-foreground">{description}</p>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Criar `apps/frontend/app/(dashboard)/dashboard/page.tsx`**

```tsx
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { Video, Scissors, Star, Zap } from 'lucide-react'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const firstName = user.user_metadata?.full_name?.split(' ')[0] ?? 'usuário'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Olá, {firstName} 👋</h1>
        <p className="text-muted-foreground">
          Pronto para criar seus próximos cortes virais?
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Projetos criados"
          value="0"
          description="Nenhum projeto ainda"
          icon={Video}
        />
        <StatsCard
          title="Clips gerados"
          value="0"
          description="Aguardando primeiro upload"
          icon={Scissors}
        />
        <StatsCard
          title="Score médio"
          value="—"
          description="Virality score"
          icon={Star}
        />
        <StatsCard
          title="Créditos restantes"
          value="3"
          description="Plano Gratuito"
          icon={Zap}
        />
      </div>

      <div className="rounded-xl border bg-card p-8 text-center">
        <Video className="mx-auto mb-4 size-12 text-muted-foreground/40" />
        <h2 className="text-lg font-semibold">Nenhum projeto ainda</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Faça upload do seu primeiro vídeo para começar
        </p>
        <a
          href="/upload"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Zap className="size-4" />
          Criar primeiro projeto
        </a>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Verificar integração frontend → backend**

Com o backend rodando (`uvicorn app.main:app --reload` em `apps/backend`):
1. Abra `http://localhost:3000/dashboard`
2. Deve mostrar dashboard com saudação e 4 stats cards
3. Abra DevTools → Network → nenhum erro 4xx/5xx

- [ ] **Step 5: Commit**

```bash
git add apps/frontend/lib/api/ apps/frontend/components/dashboard/ \
  apps/frontend/app/\(dashboard\)/dashboard/
git commit -m "feat: dashboard home page with stats cards and API client"
```

---

## Verificação Final da Fase 1

Antes de considerar esta fase completa, verifique:

- [ ] `docker compose up` sobe todos os containers sem erro
- [ ] `http://localhost:8000/health` retorna `{"status": "ok"}`
- [ ] `cd apps/backend && pytest` passa todos os testes
- [ ] `http://localhost:3000/login` mostra form de login
- [ ] `http://localhost:3000/register` mostra form de cadastro
- [ ] Criar conta → receber email de confirmação (Supabase)
- [ ] Fazer login → ser redirecionado para `/dashboard`
- [ ] `/dashboard` mostra sidebar + header + cards + saudação personalizada
- [ ] Clicar em "Sair" → redirecionar para `/login`
- [ ] Tentar acessar `/dashboard` sem login → redirecionar para `/login`
- [ ] Tabelas existem no Supabase com RLS habilitado

---

## Próximos Passos

Após esta fase estar completa e verificada, o próximo plano é:
`docs/superpowers/plans/2026-07-02-phase2-pipeline.md`

**Conteúdo da Fase 2:** Upload de vídeo com presigned URL → Cloudflare R2, importação por URL do YouTube (yt-dlp), ARQ workers, transcrição com faster-whisper.
