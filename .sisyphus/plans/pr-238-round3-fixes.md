# PR #238 Round 3 Review Fixes

**Branch**: `feat/#235-backend-features`
**PR**: https://github.com/hueyjeong/ForkLore/pull/238
**Created**: 2026-01-21
**Round**: 3 (CodeRabbit + Gemini new comments)

## Summary

8 unresolved review comments from Round 3 analysis.

## Tasks

### Critical (1)

- [x] **Task 1**: Celery Beat DatabaseScheduler sync
  - **File**: `backend/config/settings/base.py` (line 199)
  - **Issue**: `CELERY_BEAT_SCHEDULE` won't run under DatabaseScheduler - need to create PeriodicTask entries
  - **Reviewer**: coderabbitai
  - **Fix**: ✅ Already implemented in `ContentsConfig.ready()` (lines 9-40) - syncs to PeriodicTask on app startup
  - **Resolution**: Already handled - reply to reviewer explaining implementation

### Major (4)

- [x] **Task 2**: Title validation - reject whitespace-only on create AND normalize on update
  - **File**: `backend/apps/novels/services/novel_service.py` (lines 35-48, 136-154)
  - **Issue**: Create accepts `"   "`, update validates but stores untrimmed
  - **Reviewer**: coderabbitai
  - **Fix**: ✅ Strip and validate in both create and update paths - now normalizes title

- [x] **Task 3**: Enforce payment details for paid subscriptions
  - **File**: `backend/apps/interactions/services/__init__.py` (line 164)
  - **Issue**: If price > 0 but payment_id/order_id missing, paid subscription created without payment
  - **Reviewer**: coderabbitai
  - **Fix**: ✅ Added guard: `if price > 0 and (not payment_id or not order_id): raise ValueError`
  - **Also updated**: Serializer and view to include order_id, tests to provide payment mocks

- [ ] **Task 4**: Require payment details for wallet top-ups
  - **File**: `backend/apps/interactions/services/__init__.py` (line 934)
  - **Issue**: Can credit coins without payment verification
  - **Reviewer**: coderabbitai
  - **Resolution**: Deferred - requires larger refactor to separate admin/system credits from user-facing API
  - **Note**: Will add TODO and reply to reviewer explaining this needs separate admin path

- [x] **Task 5**: select_related("branch") removal impact analysis
  - **File**: `backend/apps/contents/map_services.py`
  - **Issue**: Concern about removing select_related("branch") causing N+1
  - **Reviewer**: gemini-code-assist
  - **Fix**: ✅ Verified - `select_related("branch")` IS present in `retrieve()` method (line 139)
  - **Resolution**: Reviewer looking at stale diff - reply to clarify

### Minor (3)

- [x] **Task 6**: Empty branch name validation on update
  - **File**: `backend/apps/novels/services/branch_service.py` (line 178)
  - **Issue**: Branch name can be set to empty/whitespace on update
  - **Reviewer**: coderabbitai
  - **Fix**: ✅ Added validation: `if field == "name" and not str(data[field]).strip(): raise ValueError`

- [x] **Task 7**: Add ticket/TODO tracking to test.fixme cases
  - **File**: `frontend/tests/e2e/reader/context-aware.spec.ts` (line 104)
  - **Issue**: test.fixme needs tracking reference
  - **Reviewer**: coderabbitai
  - **Fix**: ✅ Added TODO(#239) and TODO(#240) with GitHub issue links

- [x] **Task 8**: Title validation - also fix update to store trimmed value
  - **Merged with Task 2**

## Parallelization Map

### Group A (Major - can run in parallel)
- Task 2: novel_service.py title validation
- Task 3: subscription payment validation
- Task 4: wallet payment validation
- Task 5: map_services.py branch analysis

### Group B (Minor - can run in parallel)
- Task 6: branch_service.py name validation
- Task 7: E2E test.fixme tracking

### Sequential
- Task 1: Celery Beat (need to verify existing implementation first)

## Verification Commands

```bash
cd backend && poetry run pytest apps/novels/tests/ apps/interactions/tests/ apps/contents/tests/ -v
cd backend && poetry run ruff check apps/
```
