# AGENTS: Interactions App

**Module Scope:** User interactions (Likes, Comments, Subscriptions)
**Complexity Level:** HIGH (High Volume, God Object Service)

## OVERVIEW
The `interactions` app manages high-volume user engagement data. It is currently a complexity hotspot due to a monolithic `services.py` file.

## STRUCTURE & REFACTORING ROADMAP
The current `services.py` is too large. Future refactoring should split it into:
- `services/likes.py`: Like/Unlike logic.
- `services/comments.py`: Comment threads and moderation.
- `services/subscriptions.py`: Library management.
- `services/wallet.py`: Coin transactions.

## HIGH-VOLUME HANDLING
- **Writes**: Use Celery tasks for non-critical updates (e.g., stats).
- **Reads**: Use Redis for caching hot interaction counts.
- **Aggregates**: Use denormalized fields on `Novel` for `view_count` and `like_count`.

## CONVENTIONS
- **Aggregation**: Use `annotate` and `prefetch_related` to avoid N+1 queries.
- **Caching**: Implement write-through or write-behind caching for counters.
- **Idempotency**: Ensure all interaction endpoints are idempotent.

## CRITICAL WARNING
**DO NOT add new logic to `InteractionService` without refactoring first.**
If you must touch it, extract the relevant domain logic into a dedicated service file.
