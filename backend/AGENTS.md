# BACKEND KNOWLEDGE BASE

**Domain:** Core Backend (Django)
**Path:** `backend/`

## OVERVIEW
Domain-Driven Design with Django REST Framework (DRF). The `apps` directory is the core, containing all domain modules. The service layer is the single source of truth for business logic.

## STRUCTURE
```
backend/
├── apps/           # Domain modules (users, novels, interactions)
├── config/         # Django settings, WSGI, ASGI
├── common/         # Shared utilities (logging, exceptions)
└── tests/          # E2E and integration tests
```

## WHERE TO LOOK
| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Logic** | `apps/*/services.py` | All business rules, transactions, and side effects. |
| **API** | `apps/*/views.py` | Thin wrappers for request handling and response formatting. |
| **Data** | `apps/*/selectors.py` | Complex read operations and aggregation queries. |
| **Tasks** | `apps/*/tasks.py` | Async processing via Celery (email, notifications). |
| **Signals** | `apps/*/signals.py` | Decoupled side effects (post-save hooks). |

## CONVENTIONS
- **Service Pattern**: All business logic MUST reside in `services.py`. Views only call services.
- **Selectors**: Use `selectors.py` for complex queries to keep models clean.
- **Ruff**: Enforced for linting and formatting. No unused imports.
- **Type Hints**: Mandatory for all function arguments and return values.

## ANTI-PATTERNS
- ❌ **Fat Models**: Models should only define schema and simple properties.
- ❌ **Blocking I/O**: Never perform blocking operations in views. Use Celery.
- ❌ **Direct App Imports**: Use signals or service interfaces to decouple apps.
