# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ForkLore** is an interactive web novel platform where readers can fork stories to create branching narratives. Hybrid architecture with Django REST Framework backend and Next.js App Router frontend.

## Commands

### Backend (Django)
```bash
cd backend
poetry install                          # Install dependencies
poetry run python manage.py migrate     # Run migrations
poetry run python manage.py runserver   # Start dev server (port 8000)
poetry run pytest                       # Run all tests
poetry run pytest apps/novels/tests/test_views.py::TestNovelViewSet::test_create  # Single test
poetry run pytest --cov=apps            # With coverage
poetry run ruff check apps/             # Lint
poetry run ruff format apps/            # Format
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install                            # Install dependencies
pnpm dev                                # Start dev server (port 3000)
pnpm start                              # Start production server
pnpm build                              # Production build
pnpm test                               # Run Vitest tests
pnpm e2e                                # Run Playwright E2E tests
pnpm e2e:install                        # Install Playwright browsers
pnpm e2e:report                         # Show E2E test reports
pnpm lint                               # Run ESLint
```

### Docker (Full Stack)
```bash
docker compose up -d                    # Start DB, Redis, Backend, Celery
docker compose exec backend poetry run python manage.py migrate
```

## Architecture

```
├── backend/                  # Django 5.1 + DRF 3.15 (Python 3.12+)
│   ├── apps/                 # Domain modules
│   │   ├── users/            # Auth, JWT, profiles
│   │   ├── novels/           # Novel metadata, branching
│   │   ├── contents/         # Chapters, Wiki, Maps
│   │   ├── interactions/     # Comments, likes, subscriptions
│   │   ├── ai/               # Gemini API, RAG
│   │   └── core/             # E2E testing endpoints
│   ├── config/               # Django settings (base, local, test, production)
│   └── common/               # Shared utilities (renderers, exceptions, pagination)
├── frontend/                 # Next.js 16 + React 19 (TypeScript)
│   ├── app/                  # App Router pages
│   ├── components/           # shadcn/ui + custom components
│   ├── lib/                  # Utilities, API clients, Zod schemas
│   ├── hooks/                # Custom React hooks
│   └── stores/               # Zustand stores
└── docs/                     # Architecture & specifications
```

## Critical Patterns

### TDD is Mandatory
Write tests BEFORE implementation (RED → GREEN → REFACTOR).

### Backend: Service Layer Pattern
All business logic MUST reside in `services.py`. Views are thin wrappers.

```python
# apps/novels/services.py
class NovelService:
    @transaction.atomic
    def create(self, author: User, data: dict) -> Novel:
        """Google-style docstring with Args/Returns/Raises."""
        return novel

# apps/novels/views.py - thin wrapper only
class NovelViewSet(ModelViewSet):
    def create(self, request):
        serializer = NovelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        novel = NovelService().create(request.user, serializer.validated_data)
        return Response(NovelSerializer(novel).data, status=201)
```

### API Response Format
Views return raw data. StandardJSONRenderer wraps automatically:
```json
{"success": true, "data": {...}, "timestamp": "..."}
```

### Frontend: Next.js 15+ Async Params
```typescript
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { id } = await params;
}
```

## Code Style

### Python
- Type hints REQUIRED on all functions
- Docstrings: Google Style (Args/Returns/Raises)
- Linter: Ruff (line-length: 100)
- Imports: stdlib → django → 3rd-party → local

### TypeScript
- NO `as any`, `@ts-ignore`, `@ts-expect-error`
- Named exports preferred over default
- Prettier: no semicolons, single quotes, tab width 2

## Git Workflow

- **Base Branch**: `develop`
- **Branch Naming**: `feat/#<issue>-<description>`, `fix/#<issue>-<description>`
- **Commit Format**: `type(scope): message` (feat, fix, refactor, docs, test, chore)
- **Never force push** to main/develop

## Anti-Patterns

- Business logic in Views/Serializers → Use `services.py`
- `any` type in TypeScript → Use proper typing
- Hardcoded secrets → Use environment variables
- `useEffect` for data fetching → Use Server Components or React Query

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `docs/PRD.md` | Product requirements |
| `docs/api-specification.md` | REST API specs |
| `docs/database-schema.md` | DB schema (PostgreSQL + pgvector) |
| `docs/backend-architecture.md` | Backend architecture details |
| `docs/development-guidelines.md` | Development rules |
