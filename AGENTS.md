# AGENTS.md

This file provides guidance to Opencode when working with code in this repository.

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
pnpm build                              # Production build
pnpm test                               # Run Vitest tests
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
│   │   └── ai/               # Gemini API, RAG
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

## Available Skills

All skills are located in `.claude/skills/`. Use these skills to specialize AI assistance for specific tasks.

| 스킬 이름 | 설명 |
|----------|--------|
| `api-pattern` | ForkLore API 규칙을 검증하고 적용하는 스킬 |
| `backend-development` | ForkLore 백엔드(Django/DRF) 개발 워크플로우 스킬. 이슈 기반 개발 + develop 브랜치 전략 + TDD(RED-GREEN-REFACTOR) + 서비스 레이어(views는 thin wrapper) + StandardJSONRenderer/camelCase API 규약 + drf-spectacular 문서화 + ruff/pytest 커맨드 |
| `clean-code` | Pragmatic coding standards - concise, direct, no over-engineering, no unnecessary comments |
| `code-review-checklist` | Code review guidelines covering code quality, security, and best practices |
| `commit-push-pr` | Git 커밋, Push, PR 생성 워크플로우를 표준화하는 스킬 |
| `deployment-procedures` | Production deployment principles and decision-making. Safe deployment workflows, rollback strategies, and verification |
| `docker-expert` | Docker containerization expert with deep knowledge of multi-stage builds, image optimization, container security, Docker Compose orchestration, and production deployment patterns |
| `documentation-templates` | Documentation templates and structure guidelines. README, API docs, code comments, and AI-friendly documentation |
| `frontend-development` | ForkLore 프론트엔드(Next.js 16/React 19) 개발 워크플로우 스킬. 이슈 기반 개발 + develop 브랜치 전략 + Server-First 아키텍처 + shadcn/ui 컴포넌트 + Zustand 상태관리 + Vitest/ESLint/Prettier 린트 + TDD 워크플로 |
| `frontend-pattern` | React 19 및 Next.js 16 패턴을 적용하는 스킬 |
| `github-workflow-automation` | Automate GitHub workflows with AI assistance. Includes PR reviews, issue triage, CI/CD integration, and Git operations |
| `lint-and-validate` | Automatic quality control, linting, and static analysis procedures. Use after every code modification |
| `nextjs-best-practices` | Next.js App Router principles. Server Components, data fetching, routing patterns |
| `pr-reviewer` | 코드 리뷰 체크리스트를 적용하는 PR 검토 스킬 |
| `python-patterns` | Python development principles and decision-making. Framework selection, async patterns, type hints, project structure |
| `receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable |
| `requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `skill-creator` | Guide for creating effective skills. Use when users want to create a new skill (or update an existing skill) |
| `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `tdd-flow` | RED-GREEN-REFACTOR 워크플로우를 강제하는 TDD 개발 스킬 |
| `test-fixing` | Run tests and systematically fix all failing tests using smart error grouping |
| `testing-patterns` | Jest testing patterns, factory functions, mocking strategies, and TDD workflow |
| `typescript-expert` | TypeScript and JavaScript expert with deep knowledge of type-level programming, performance optimization, monorepo management, migration strategies |
| `vercel-react-best-practices` | React and Next.js performance optimization guidelines from Vercel Engineering |
| `web-design-guidelines` | Review UI code for Web Interface Guidelines compliance |