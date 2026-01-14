# ForkLore - AI Agent Guide

Interactive web novel platform. Django 5.1 + Next.js 16. **TDD required.**

## Quick Commands

### Backend (Django)
```bash
cd backend

# Setup
poetry install && poetry run python manage.py migrate

# Tests - Single test method
poetry run pytest apps/novels/tests/test_services.py::TestNovelServiceCreate::test_create_novel_success -v

# Tests - Single class
poetry run pytest apps/novels/tests/test_services.py::TestNovelServiceCreate -v

# Tests - File/app/all with coverage
poetry run pytest apps/novels/tests/test_services.py -v
poetry run pytest apps/novels/tests/ -v --cov=apps/novels --cov-report=term-missing
poetry run pytest --cov=apps --cov-report=term-missing

# Lint & format (ruff)
poetry run ruff check apps/           # Lint only
poetry run ruff format apps/          # Format only
poetry run ruff check --fix apps/     # Auto-fix

# Dev server
poetry run python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend

# Development
pnpm install
pnpm dev                           # http://localhost:3000

# Tests (vitest)
pnpm test                          # All tests (watch mode)
pnpm test -- input.test.tsx        # Single file
pnpm test -- --run                 # No watch

# Lint & format
pnpm lint                          # ESLint check
pnpm lint -- --fix                 # Auto-fix
npx prettier --write .             # Format

# Build
pnpm build && pnpm start           # Production
```

### Docker
```bash
docker compose up -d                                                    # Start
docker compose exec backend poetry run python manage.py migrate        # Migrate
docker compose logs -f backend                                          # Logs
docker compose down                                                     # Stop
```

## Code Style

### Python (Backend)
- **Imports**: stdlib → django → third-party → local (ruff auto-sorts)
- **Type hints**: Required on all functions
- **Docstrings**: Google style (Args/Returns/Raises)
- **Line length**: 100 characters
- **Service pattern**: Business logic in services, not views
- **Error messages**: Korean for user-facing errors
- **Testing**: model_bakery for fixtures, pytest for all tests

```python
# Service example
from django.db import transaction
from rest_framework.exceptions import NotFound
from apps.novels.models import Novel

class NovelService:
    @transaction.atomic
    def create(self, author: User, data: dict) -> Novel:
        """Create novel with main branch.
        
        Args:
            author: User creating the novel
            data: Novel data (title, description, genre)
            
        Returns:
            Created Novel instance
            
        Raises:
            ValidationError: If data is invalid
        """
        if not data.get("title"):
            raise ValidationError("제목은 필수입니다.")
        ...
```

### TypeScript (Frontend)
- **Exports**: Named exports preferred
- **Naming**: camelCase (vars/functions), PascalCase (types/components)
- **Organization**: types/*.types.ts, lib/api/*.api.ts, stores/*.ts
- **No type suppression**: Never use `as any`, `@ts-ignore`, `@ts-expect-error`
- **Testing**: Vitest + React Testing Library

```typescript
// lib/api/novels.api.ts
export interface NovelResponse {
  id: number;
  title: string;
}

export async function fetchNovels(): Promise<NovelResponse[]> {
  const response = await apiClient.get('/novels');
  return response.data;
}
```

## API Response Format

**CRITICAL**: All responses auto-wrapped by `StandardJSONRenderer`. Views return raw data.

```python
# ✅ CORRECT - Renderer wraps automatically
def retrieve(self, request, pk=None):
    novel = Novel.objects.filter(pk=pk).first()
    if not novel:
        raise NotFound("소설을 찾을 수 없습니다.")  # Exception handler formats
    return Response(NovelSerializer(novel).data)  # Renderer wraps

# ❌ WRONG - Manual wrapping creates double wrapping
return Response({"success": True, "data": serializer.data})

# ❌ WRONG - Manual error responses
return Response({"error": "Not found"}, status=404)
```

**Output format**:
```json
{
  "success": true,
  "message": null,
  "data": { "id": 1, "title": "..." },
  "timestamp": "2026-01-14T16:17:00+09:00"
}
```

**DRF Exceptions**: Use `NotFound`, `PermissionDenied`, `ValidationError`, etc.

## Testing Strategy

**TDD Required**: RED → GREEN → REFACTOR

### Test Organization
```
apps/<app>/tests/
├── test_services.py      # Unit tests (mock external deps)
├── test_views.py         # Unit tests (view logic)
└── test_integration/     # Integration tests (real HTTP)
    ├── conftest.py       # Shared fixtures
    └── test_*.py         # API workflows
```

### Fixtures (conftest.py)
```python
import pytest
from model_bakery import baker
from rest_framework.test import APIClient

@pytest.fixture
def author(db):
    return baker.make('users.User', email='author@test.com')

@pytest.fixture
def author_client(api_client, author):
    api_client.force_authenticate(user=author)
    return api_client
```

### Test Example
```python
@pytest.mark.django_db
class TestNovelAPI:
    def test_create_novel(self, author_client):
        url = reverse('novel-list')
        data = {'title': 'Test', 'genre': 'FANTASY'}
        response = author_client.post(url, data, format='json')
        assert response.status_code == 201
        assert response.data['title'] == 'Test'
```

**Coverage**: 95%+ required (current: 95%, 545 tests)

## Project Structure

```
backend/
├── apps/
│   ├── users/        # Auth, profiles
│   ├── novels/       # Novel, Branch
│   ├── contents/     # Chapter, Wiki, Map
│   ├── interactions/ # Comments, Subscriptions, Wallet
│   └── ai/           # Embeddings, RAG
├── common/           # Renderers, exceptions, pagination
└── config/settings/  # base.py, local.py, test.py

frontend/
├── app/              # Next.js App Router
├── components/       # UI (shadcn/ui)
├── lib/              # Utils, API client
├── stores/           # Zustand state
└── types/            # TypeScript types
```

## Git Workflow

1. **Branch naming**: `feat/#123-feature-name`, `fix/#123-bug-name`
2. **Base branch**: `develop` (never force-push to `main`/`develop`)
3. **PR required**: Always create PR, include `Closes #123`
4. **Commit format**: `type(scope): message` (feat, fix, refactor, docs, test)

## Key Rules

- **TDD**: Write tests BEFORE implementation
- **No secrets**: Use `env('VAR_NAME')` via django-environ
- **No type suppression**: Never `as any`, `@ts-ignore`, `@ts-expect-error`
- **Service pattern**: Business logic in services, not views
- **DRF exceptions**: Use exceptions, not manual error responses
- **Coverage**: Maintain 95%+ test coverage

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, Django 5.1, DRF 3.15, Celery, Redis |
| Frontend | Next.js 16, React 19, TypeScript 5, Tailwind 4 |
| Database | PostgreSQL 18 + pgvector |
| AI | Gemini API (text-embedding-004, gemini-1.5-flash) |
| Auth | SimpleJWT + NextAuth.js v5 |
| Testing | pytest, vitest, model_bakery, React Testing Library |

## Documentation

- `docs/PRD.md` - Product requirements
- `docs/database-schema.md` - DB schema (v4)
- `docs/api-specification.md` - REST API spec
- `docs/backend-tasks.md` - Task tracking
