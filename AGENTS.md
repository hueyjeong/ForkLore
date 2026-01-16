# ForkLore - AI Agent Guide

Interactive web novel platform. Django 5.1 + Next.js 16. **TDD required.**

## Quick Commands

### Backend (Django)
```bash
cd backend

# Setup
poetry install && poetry run python manage.py migrate

# Tests
poetry run pytest apps/novels/tests/test_services.py::TestClass::test_method -v  # Single test
poetry run pytest apps/novels/tests/test_services.py::TestClass -v                # Single class
poetry run pytest apps/novels/tests/ -v --cov=apps/novels --cov-report=term-missing
poetry run pytest --cov=apps --cov-report=term-missing                             # Full coverage

# Lint & format
poetry run ruff check apps/ && poetry run ruff format apps/  # Check + format
poetry run ruff check --fix apps/                             # Auto-fix

# Dev server
poetry run python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend

pnpm install && pnpm dev           # Dev: http://localhost:3000

# Tests
pnpm test -- input.test.tsx        # Single file
pnpm test -- --run                 # All tests (no watch)

# Lint & format
pnpm lint -- --fix && npx prettier --write .

# Build
pnpm build && pnpm start
```

### Docker
```bash
docker compose up -d
docker compose exec backend poetry run python manage.py migrate
docker compose down
```

## Code Style

### Python (Backend)
| Rule | Description |
|------|-------------|
| Imports | stdlib -> django -> third-party -> local (ruff auto-sorts) |
| Type hints | Required on ALL functions |
| Docstrings | Google style (Args/Returns/Raises) |
| Line length | 100 characters |
| Error messages | Korean for user-facing errors |
| Business logic | Services, NOT views |

```python
from django.db import transaction
from rest_framework.exceptions import ValidationError

class NovelService:
    @transaction.atomic
    def create(self, author: User, data: dict) -> Novel:
        """Create novel with main branch.
        
        Args:
            author: User creating the novel
            data: Novel data dict
        Returns:
            Created Novel instance
        Raises:
            ValidationError: If data invalid
        """
        if not data.get("title"):
            raise ValidationError("제목은 필수입니다.")
```

### TypeScript (Frontend)
| Rule | Description |
|------|-------------|
| Exports | Named exports preferred |
| Naming | camelCase (vars/funcs), PascalCase (types/components) |
| Files | types/*.types.ts, lib/api/*.api.ts, stores/*.ts |
| Type safety | NEVER use `as any`, `@ts-ignore`, `@ts-expect-error` |

```typescript
// lib/api/novels.api.ts
export interface NovelResponse { id: number; title: string; }

export async function fetchNovels(): Promise<NovelResponse[]> {
  const response = await apiClient.get('/novels');
  return response.data;
}
```

## API Response Format

**CRITICAL**: Views return RAW data. `StandardJSONRenderer` wraps automatically.

```python
# CORRECT
def retrieve(self, request, pk=None):
    novel = Novel.objects.filter(pk=pk).first()
    if not novel:
        raise NotFound("소설을 찾을 수 없습니다.")
    return Response(NovelSerializer(novel).data)

# WRONG - creates double wrapping
return Response({"success": True, "data": serializer.data})
```

Output: `{"success": true, "data": {...}, "timestamp": "..."}`

Use DRF exceptions: `NotFound`, `PermissionDenied`, `ValidationError`

## Testing (TDD Required)

```
apps/<app>/tests/
├── test_services.py      # Unit tests
├── test_views.py         # View tests  
└── test_integration/     # API workflow tests
```

```python
@pytest.fixture
def author(db):
    return baker.make('users.User', email='author@test.com')

@pytest.mark.django_db
class TestNovelAPI:
    def test_create_novel(self, author_client):
        response = author_client.post(reverse('novel-list'), 
                                       {'title': 'Test', 'genre': 'FANTASY'})
        assert response.status_code == 201
```

**Coverage**: 95%+ required (current: 95%, 545 tests)

## Project Structure

```
backend/
├── apps/{users,novels,contents,interactions,ai}/
├── common/           # Renderers, exceptions, pagination
└── config/settings/  # base.py, local.py, test.py

frontend/
├── app/              # Next.js App Router
├── components/       # shadcn/ui
├── lib/              # Utils, API client
├── stores/           # Zustand
└── types/            # TypeScript types
```

## Git Workflow

| Rule | Format |
|------|--------|
| Branch | `feat/#123-feature-name`, `fix/#123-bug-name` |
| Base | `develop` (never force-push main/develop) |
| Commit | `type(scope): message` (feat, fix, refactor, docs, test) |
| PR | Always required, include `Closes #123` |

## Key Rules

1. **TDD**: Write tests BEFORE implementation
2. **No secrets**: Use `env('VAR_NAME')` via django-environ
3. **No type suppression**: Never `as any`, `@ts-ignore`
4. **Service pattern**: Business logic in services, not views
5. **Coverage**: Maintain 95%+

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
- `docs/frontend/` - Frontend guides (Shadcn, MCP, Skills, Hooks, Next.js, React)
