# ForkLore - AI Agent Guide

Interactive web novel platform. Django 5.1 + Next.js 16. **TDD required.**

## Quick Commands

### Backend (Django)
```bash
cd backend

# Setup
poetry install
poetry run python manage.py migrate

# Run single test (class method)
poetry run pytest apps/novels/tests/test_services.py::TestNovelServiceCreate::test_create_novel_success -v

# Run single test class
poetry run pytest apps/novels/tests/test_services.py::TestNovelServiceCreate -v

# Run test file
poetry run pytest apps/novels/tests/test_services.py -v

# Run app tests with coverage
poetry run pytest apps/novels/tests/ -v --cov=apps/novels --cov-report=term-missing

# All tests with coverage
poetry run pytest --cov=apps --cov-report=term-missing

# Lint and format
poetry run ruff check apps/           # Lint only
poetry run ruff format apps/          # Format only
poetry run ruff check --fix apps/     # Auto-fix issues

# Dev server
poetry run python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install

# Development
pnpm dev                           # Dev server (http://localhost:3000)

# Testing
pnpm test                          # Run all vitest tests
pnpm test -- input.test.tsx        # Single test file
pnpm test -- --run                 # Run once without watch mode

# Linting & Formatting
pnpm lint                          # ESLint check
pnpm lint -- --fix                 # ESLint auto-fix
npx prettier --write .             # Format all files

# Build
pnpm build                         # Production build
pnpm start                         # Start production server
```

### Docker
```bash
docker compose up -d                                                    # Start all services
docker compose exec backend poetry run python manage.py migrate        # Run migrations
docker compose logs -f backend                                          # View logs
docker compose down                                                     # Stop all services
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

### Test Structure

```
backend/apps/
├── users/tests/
│   └── test_auth_api.py              # Integration tests (19 tests)
└── novels/tests/
    ├── test_services.py               # Unit tests (services)
    ├── test_views.py                  # Unit tests (views)
    └── test_integration/              # Integration tests
        ├── conftest.py                # Shared fixtures (author, reader, clients)
        ├── test_novel_api.py          # Novel CRUD (4 tests)
        ├── test_branch_api.py         # Branch management (5 tests)
        └── test_link_request_workflow.py  # Link requests (6 tests)
```

### Unit Tests (Services & Views)

```python
# 1. Unit tests for services (mock external deps)
@patch("apps.ai.services.genai")
def test_embed_text(self, mock_genai):
    mock_genai.embed_content.return_value = {"embedding": [0.1] * 3072}
    service = AIService()
    result = service.embed_text("test")
    assert result is not None

# Test fixtures: model_bakery
branch = baker.make("novels.Branch", author=user)
chapter = baker.make("contents.Chapter", branch=branch, content="test")
```

### Integration Tests (Real HTTP Workflows)

**Location**: `apps/<app_name>/tests/test_integration/`

**Shared Fixtures** (`conftest.py`):
```python
import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def author(db):
    """Author user for testing"""
    return baker.make(User, email="author@test.com")

@pytest.fixture
def reader(db):
    """Reader user for testing"""
    return baker.make(User, email="reader@test.com")

@pytest.fixture
def api_client():
    """Unauthenticated API client"""
    return APIClient()

@pytest.fixture
def author_client(api_client, author):
    """Authenticated client for author"""
    api_client.force_authenticate(user=author)
    return api_client

@pytest.fixture
def reader_client(api_client, reader):
    """Authenticated client for reader"""
    api_client.force_authenticate(user=reader)
    return api_client
```

**Integration Test Example**:
```python
import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

@pytest.mark.django_db
class TestNovelCRUD:
    def test_create_novel_creates_main_branch(self, author_client):
        """Test novel creation automatically creates main branch"""
        url = reverse("novel-list")
        data = {
            "title": "Test Novel",
            "description": "Test description",
            "genre": "FANTASY",
        }
        
        response = author_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Test Novel"
        # Verify main branch was created
        assert response.data["main_branch"] is not None
    
    def test_non_author_cannot_update_novel(self, author, reader_client):
        """Test non-authors cannot modify novels"""
        novel = baker.make("novels.Novel", author=author)
        url = reverse("novel-detail", kwargs={"pk": novel.pk})
        data = {"title": "Hacked Title"}
        
        response = reader_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
```

**Coverage requirement: 95%+ (current: 95%, 545 tests)**

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
