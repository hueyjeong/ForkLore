# ForkLore

**ForkLore**는 독자가 스토리를 포크(fork)하여 브랜치형 서사를 만들 수 있는 인터랙티브 웹소설 플랫폼입니다.

Django REST Framework 백엔드와 Next.js App Router 프론트엔드로 구성된 하이브리드 아키텍처를 사용합니다.

## 🚀 Quick Start

### 통합 개발 환경 (권장)

백엔드와 프론트엔드를 한 번에 실행:

```bash
./dev.sh
```

이 스크립트는 다음을 자동으로 처리합니다:
- PostgreSQL/Redis 컨테이너 상태 확인 및 자동 시작
- 포트 충돌 감지 (8080, 3000)
- 미적용 마이그레이션 확인
- 백엔드(8080)와 프론트엔드(3000) 병렬 실행
- Ctrl+C로 모든 프로세스 종료

**접속 URL:**
- Backend API: http://localhost:8080
- Frontend: http://localhost:3000
- API Docs (Swagger): http://localhost:8080/api/docs/

### 개별 실행

#### Backend (Django)

```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver 8080
```

#### Frontend (Next.js)

```bash
cd frontend
pnpm install
pnpm dev
```

#### Infrastructure (Docker)

```bash
docker compose up -d db redis  # DB와 Redis만 실행
```

## 📋 Prerequisites

- **Python 3.12+** with [Poetry](https://python-poetry.org/)
- **Node.js 20+** with [pnpm](https://pnpm.io/)
- **Docker** and Docker Compose
- PostgreSQL 18+ (Docker 사용 시 자동)
- Redis 7+ (Docker 사용 시 자동)

## 📂 Project Structure

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
├── docs/                     # Architecture & specifications
├── docker-compose.yml        # Infrastructure services
└── dev.sh                    # Unified dev environment script
```

## 🧪 Testing

### Backend

```bash
cd backend
poetry run pytest                       # Run all tests
poetry run pytest --cov=apps            # With coverage
poetry run pytest apps/novels/tests/    # Specific app
```

### Frontend

```bash
cd frontend
pnpm test                               # Run Vitest tests
pnpm test:watch                         # Watch mode
```

## 🛠️ Development Commands

### Backend

```bash
# Linting & Formatting
poetry run ruff check apps/
poetry run ruff format apps/

# Create superuser
poetry run python manage.py createsuperuser

# Make migrations
poetry run python manage.py makemigrations
```

### Frontend

```bash
# Linting & Formatting
pnpm lint
pnpm lint:fix

# Type checking
pnpm type-check

# Production build
pnpm build
```

## 🐳 Docker

전체 스택을 Docker로 실행:

```bash
docker compose up -d                    # Start all services
docker compose exec backend poetry run python manage.py migrate
docker compose logs -f backend          # View logs
docker compose down                     # Stop all services
```

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | AI 개발 가이드라인 |
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/api-specification.md](docs/api-specification.md) | REST API specs |
| [docs/database-schema.md](docs/database-schema.md) | DB schema (PostgreSQL + pgvector) |
| [docs/backend-architecture.md](docs/backend-architecture.md) | Backend architecture details |
| [backend/README.md](backend/README.md) | Backend setup & API docs |

## 🔑 Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgres://postgres:password@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
DEBUG=True
```

### Frontend (.env.local)

프론트엔드는 기본적으로 `http://localhost:8080/api`를 백엔드 API로 사용합니다.
다른 포트를 사용하려면:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

## 🌿 Git Workflow

- **Base Branch**: `develop`
- **Branch Naming**: `feat/#<issue>-<description>`, `fix/#<issue>-<description>`
- **Commit Format**: `type(scope): message` (feat, fix, refactor, docs, test, chore)

## 📝 Code Style

### Python
- Type hints REQUIRED
- Google-style docstrings
- Service layer pattern (business logic in `services.py`)
- TDD: Write tests before implementation

### TypeScript
- No `any`, `@ts-ignore`, `@ts-expect-error`
- Named exports preferred
- Prettier: no semicolons, single quotes

## 🤝 Contributing

1. Issue 생성 또는 할당받기
2. `feat/#<issue>-<description>` 브랜치 생성
3. TDD 원칙에 따라 테스트 작성 후 구현
4. Linting/Testing 통과 확인
5. Pull Request 생성 (→ `develop`)

## 📄 License

This project is licensed under the MIT License.

---

*Developed with ❤️ for ForkLore Storytellers.*
