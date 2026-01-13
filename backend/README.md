# ForkLore Backend

ForkLore is an interactive web novel platform where readers can fork stories to create their own branching narratives. The backend is built with Django and provides a robust REST API for managing users, novels, branching systems, AI-powered suggestions, and social interactions.

## 🚀 Tech Stack

- **Framework**: Python 3.12, Django 5.1, Django Rest Framework (DRF) 3.15
- **Database**: PostgreSQL 18 + pgvector (for vector search/embeddings)
- **Task Queue**: Redis + Celery + Django Celery Beat
- **AI Integration**: Gemini API (`google-generativeai`)
- **Documentation**: drf-spectacular (OpenAPI 3.1)
- **Authentication**: SimpleJWT + Social Auth (Google, Kakao)

## 📋 Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/) (Dependency management)
- PostgreSQL 18+ with [pgvector](https://github.com/pgvector/pgvector) extension
- Redis (for Celery and Caching)

## 🛠️ Quick Start

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Run migrations:**
   ```bash
   poetry run python manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   poetry run python manage.py runserver
   ```

## 📂 Project Structure

The project follows a modular structure within the `apps/` directory:

- `apps/users/`: Custom User model, Authentication (JWT), and Profile management.
- `apps/novels/`: Novel metadata, genre management, and core branching narrative logic.
- `apps/contents/`: Chapter management, Markdown-to-HTML conversion, Wiki, and Map data.
- `apps/interactions/`: Social features including comments (paragraph-level), likes, subscriptions, and wallet/coin management.
- `apps/ai/`: Gemini API integration for RAG (Retrieval-Augmented Generation), wiki suggestions, and consistency checking.
- `common/`: Shared base models, standard JSON renderers, custom exception handlers, and pagination classes.

## 🧪 Running Tests

We follow TDD (Test-Driven Development) principles. Tests are managed via `pytest`.

- **Run all tests:**
  ```bash
  poetry run pytest
  ```

- **Run a specific test file:**
  ```bash
  poetry run pytest apps/novels/tests/test_services.py
  ```

- **Run with coverage report:**
  ```bash
  poetry run pytest --cov=apps --cov-report=term-missing
  ```

## 📖 API Documentation

The API documentation is automatically generated using `drf-spectacular`.

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **OpenAPI Schema**: `/api/schema/`

## ⚙️ Environment Variables

Key environment variables required in `.env`:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string for Celery |
| `GEMINI_API_KEY` | API Key for Google Gemini (AI features) |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enable/disable debug mode |
| `GOOGLE_CLIENT_ID` / `_SECRET` | OAuth credentials for Google Login |
| `KAKAO_CLIENT_ID` / `_SECRET` | OAuth credentials for Kakao Login |

## 🐳 Docker

You can run the entire stack (including DB and Redis) using Docker Compose from the root directory:

```bash
# Start all services
docker compose up -d

# Run migrations in the backend container
docker compose exec backend poetry run python manage.py migrate
```

## 🛠️ Development

### Linting & Formatting
We use `ruff` for both linting and formatting:
```bash
poetry run ruff check apps/
poetry run ruff format apps/
```

### Code Style
- Follow Google-style docstrings.
- Business logic should be placed in **Service** classes, not in Views.
- TDD is mandatory: Write tests before implementation.

---
*Developed with ❤️ for ForkLore Storytellers.*
