# ForkLore - AI Agent Guide

Interactive web novel platform. Django 5.1 + Next.js 16. **TDD required.**

## Quick Commands

### Backend (Django)
```bash
cd backend

# Setup
poetry install
poetry run python manage.py migrate

# Run single test
poetry run pytest apps/novels/tests/test_services.py::TestNovelService::test_create -v

# Run test file
poetry run pytest apps/novels/tests/test_services.py -v

# Run app tests with coverage
poetry run pytest apps/novels/tests/ -v --cov=apps/novels --cov-report=term-missing

# All tests
poetry run pytest --cov=apps

# Lint
poetry run ruff check apps/
poetry run ruff format apps/

# Server
poetry run python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install
pnpm dev                           # Dev server
pnpm test                          # Run vitest
pnpm test -- auth.test.tsx         # Single test file
pnpm lint                          # ESLint
pnpm build                         # Production build
```

### Docker
```bash
docker compose up -d
docker compose exec backend poetry run python manage.py migrate
```

## Code Style

### Python (Backend)
```python
# Imports: stdlib → django → third-party → local (ruff handles this)
from django.db import transaction
from rest_framework import status
from apps.novels.models import Novel

# Type hints required
def create(self, author: User, data: dict) -> Novel:

# Docstrings: Google style
def method(self, arg: str) -> bool:
    """Short description.

    Args:
        arg: Description

    Returns:
        Description

    Raises:
        ValueError: When invalid
    """

# Service pattern: Business logic in services, not views
class NovelService:
    @transaction.atomic
    def create(self, author, data: dict) -> Novel:
        ...

# Error messages in Korean for user-facing errors
raise ValueError("제목은 필수입니다.")

# Line length: 100 (ruff configured)
```

### TypeScript (Frontend)
```typescript
// Named exports preferred
export interface LoginRequest { ... }
export function useAuth() { ... }

// Types in separate files: types/*.types.ts
// API calls: lib/api/*.api.ts
// Stores: stores/*.ts (Zustand)

// camelCase for variables/functions, PascalCase for types/components
const userData: UserResponse = await fetchUser();
```

## Project Structure

```
backend/
├── apps/
│   ├── users/       # Auth, profiles
│   ├── novels/      # Novel, Branch
│   ├── contents/    # Chapter, Wiki, Map
│   ├── interactions/# Comments, Subscriptions, Wallet
│   └── ai/          # Embeddings, RAG
├── common/          # Base models, utils
└── config/settings/ # base.py, local.py, test.py

frontend/
├── app/             # Next.js App Router
├── components/      # UI (shadcn/ui)
├── lib/             # Utils, API client
├── stores/          # Zustand stores
└── types/           # TypeScript types
```

## Testing (TDD Required)

**Workflow: RED → GREEN → REFACTOR**

```python
# 1. Unit tests for services (mock external deps)
@patch("apps.ai.services.genai")
def test_embed_text(self, mock_genai):
    mock_genai.embed_content.return_value = {"embedding": [0.1] * 3072}
    ...

# 2. Integration tests for views (real HTTP)
def test_create_novel(self):
    response = self.client.post("/api/v1/novels/", data, format="json")
    assert response.status_code == 201

# Test fixtures: model_bakery
branch = baker.make("novels.Branch", author=user)
chapter = baker.make("contents.Chapter", branch=branch, content="test")
```

**Coverage requirement: 70%+**

## Key Rules

1. **TDD**: Write tests BEFORE implementation
2. **No secrets in code**: Use `env('VAR_NAME')` via django-environ
3. **No type suppression**: Never use `as any`, `@ts-ignore`, `@ts-expect-error`
4. **Branch naming**: `feat/#123-feature-name`, `fix/#123-bug-name`
5. **Base branch**: `develop` (never force-push to `main`/`develop`)
6. **PR required**: Always create PR after push, include `Closes #123`

## API Patterns

```python
# ViewSet with nested routes
class BranchViewSet(GenericViewSet):
    @action(detail=False, methods=["post"], url_path="wiki-suggestions")
    def wiki_suggestions(self, request, **kwargs):
        branch_pk = kwargs.get("branch_pk")  # From nested router
        ...

# Service instantiation (not static)
service = NovelService()
result = service.create(user, data)

# Response format
return Response({"data": result}, status=status.HTTP_200_OK)
```

## Tech Stack Reference

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, Django 5.1, DRF 3.15, Celery |
| Frontend | Next.js 16, React 19, TypeScript 5, Tailwind 4 |
| Database | PostgreSQL 18 + pgvector |
| AI | Gemini API (text-embedding-004, gemini-1.5-flash) |
| Auth | SimpleJWT + NextAuth.js v5 |

## Design Docs

- `docs/PRD.md` - Product requirements
- `docs/database-schema.md` - DB schema (v4)
- `docs/api-specification.md` - REST API spec
- `docs/backend-tasks.md` - Task tracking
