# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-16
**Stack:** Django 5.1 (Backend) + Next.js 16 (Frontend)

## OVERVIEW
Interactive web novel platform. Hybrid architecture with Django REST Framework (DRF) serving a Next.js App Router frontend. TDD is strictly enforced.

## STRUCTURE
```
.
├── backend/            # Django 5.1 + DRF 3.15
│   ├── apps/           # Domain modules (novels, users, etc.)
│   └── config/         # Settings & WSGI/ASGI
├── frontend/           # Next.js 16 + React 19
│   ├── app/            # App Router pages
│   └── components/     # shadcn/ui + custom components
└── docs/               # Architecture & Specifications
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Business Logic** | `backend/apps/*/services.py` | NEVER in Views/Models. Service pattern required. |
| **API Endpoints** | `backend/apps/*/views.py` | DRF ViewSets. Thin wrappers around Services. |
| **Data Models** | `backend/apps/*/models.py` | PostgreSQL 18 + pgvector. |
| **Pages/Routes** | `frontend/app/` | Next.js App Router conventions. |
| **UI Components** | `frontend/components/` | shadcn/ui based. |
| **Global State** | `frontend/stores/` | Zustand. |
| **Tests** | `backend/apps/*/tests/` | Pytest. TDD required (95%+ coverage). |

## CONVENTIONS
### General
- **TDD**: Write tests BEFORE implementation.
- **Git**: `feat/#123-desc`, `fix/#123-desc`.
- **No Secrets**: Use `env()` (django-environ / next env).

### Backend (Python)
- **Type Hints**: REQUIRED on all functions/methods.
- **Docstrings**: Google Style (Args/Returns/Raises).
- **Error Handling**: Use DRF exceptions (`ValidationError`, `NotFound`).
- **Imports**: `stdlib` -> `django` -> `3rd-party` -> `local`.

### Frontend (TypeScript)
- **Strict Typing**: NO `as any`, `@ts-ignore`.
- **Exports**: Named exports preferred over default.
- **Naming**: `PascalCase` components, `camelCase` functions.

## ANTI-PATTERNS
- **God Views**: Logic in views/serializers. Move to `services.py`.
- **Type Suppression**: Using `any` to bypass TS errors.
- **Hardcoded Config**: Using string literals instead of env vars.
- **Force Push**: Never force push to shared branches.

## COMMANDS
```bash
# Backend
cd backend && poetry run pytest                 # Run tests
cd backend && poetry run python manage.py runserver

# Frontend
cd frontend && pnpm test                        # Run tests
cd frontend && pnpm dev                         # Dev server

# Docker
docker compose up -d                            # Full stack
```
