# PR #238 Round 2 Fixes - N+1 Queries & New Review Comments

## Context

### Original Request
PR #238의 2차 리뷰에서 발견된 15개 테스트 실패(N+1 쿼리)와 3개의 새로운 리뷰 코멘트를 해결한다.

### Problem Analysis
**테스트 실패 원인**: `nplusone` 라이브러리가 N+1 쿼리를 감지하여 테스트 실패

**Research Findings (from explore agent):**
1. `NovelService.list` - `.select_related("author")` 누락
2. `CommentService.list` - `reply_count` annotate 필요 (SerializerMethodField 대신)
3. `WikiSnapshotViewSet.list` - `wiki.snapshots.all()` → `wiki.snapshots` 변경
4. `WikiService.retrieve` - Prefetch with ordering 추가

**새로운 리뷰 코멘트 분석:**
- 5개 중 2개는 이미 해결됨 (wallet charge, subscription payment)
- 3개 미해결: map_services, tasks branch_id, context-aware.spec.ts

---

## Work Objectives

### Core Objective
모든 테스트를 통과시키고 새로운 리뷰 코멘트를 해결한다.

### Concrete Deliverables
- N+1 쿼리 수정 (3개 핵심 수정)
- 새로운 리뷰 코멘트 해결 (3개)

### Definition of Done
- [x] `poetry run pytest` 전체 테스트 통과 (579 passed, 0 failures)
- [x] `poetry run ruff check apps/` 린터 에러 0개 (2 pre-existing E501 in ai/services.py)
- [x] 모든 새 리뷰 코멘트 해결

### Must NOT Have (Guardrails)
- 기존에 해결된 코멘트 재수정 금지
- 모델 구조 변경 금지
- 새로운 의존성 추가 금지

---

## TODOs

### Part A: N+1 Query Fixes (Test Failures)

- [x] 1. Fix Novel views N+1 - add select_related("author")

  **What to do**:
  - `NovelService.list()` 메서드에서 `.select_related("author")` 추가
  - `NovelListSerializer`가 `author = AuthorSerializer(read_only=True)` 사용

  **References**:
  - `backend/apps/novels/services/novel_service.py:77` - 수정 대상
  - `backend/apps/novels/tests/test_views.py::TestNovelList` - 실패 테스트
  - `backend/apps/novels/tests/test_integration/test_novel_api.py::TestNovelCRUD::test_list_novels` - 실패 테스트

  **Specific Change**:
  ```python
  # BEFORE (line 77)
  queryset = Novel.objects.filter(deleted_at__isnull=True)
  
  # AFTER
  queryset = Novel.objects.filter(deleted_at__isnull=True).select_related("author")
  ```

   **Acceptance Criteria**:
  - [x] `poetry run pytest apps/novels/tests/test_views.py::TestNovelList -x` PASS
  - [x] `poetry run pytest apps/novels/tests/test_integration/test_novel_api.py::TestNovelCRUD::test_list_novels -x` PASS

  **Parallelizable**: YES (with 2, 3)

  **Commit**: Groups with 2-3


- [x] 2. Fix Comment views N+1 - annotate reply_count

  **What to do**:
  - `CommentService.list()` 메서드에서 `annotate(reply_count=Count(...))` 추가
  - `CommentSerializer`에서 `SerializerMethodField` → `IntegerField` 변경
  - `get_reply_count()` 메서드 제거

  **References**:
  - `backend/apps/interactions/services/__init__.py:593-605` - CommentService.list
  - `backend/apps/interactions/serializers.py:220-247` - CommentSerializer
  - `backend/apps/interactions/tests/test_comment_views.py` - 실패 테스트

  **Specific Change**:
  ```python
  # CommentService.list (services/__init__.py)
  from django.db.models import Count, Q
  
  base_queryset = Comment.objects.filter(
      chapter_id=chapter_id,
      deleted_at__isnull=True,
  ).select_related("user").annotate(
      reply_count=Count("replies", filter=Q(replies__deleted_at__isnull=True))
  ).order_by("-created_at")
  
  # CommentSerializer (serializers.py)
  reply_count = serializers.IntegerField(read_only=True)  # Remove get_reply_count method
  ```

   **Acceptance Criteria**:
  - [x] `poetry run pytest apps/interactions/tests/test_comment_views.py -x` PASS

  **Parallelizable**: YES (with 1, 3)

  **Commit**: Groups with 1, 3


- [x] 3. Fix Wiki views N+1 - use prefetched snapshots

  **What to do**:
  - `WikiSnapshotViewSet.list()` 에서 `wiki.snapshots.all()` → `wiki.snapshots` 변경
  - `WikiService.retrieve()` 에서 Prefetch 객체로 snapshots ordering 추가

  **References**:
  - `backend/apps/contents/views.py:768` - WikiSnapshotViewSet.list
  - `backend/apps/contents/services.py:368-372` - WikiService.retrieve
  - `backend/apps/contents/tests/test_wiki_views.py` - 실패 테스트

  **Specific Changes**:
  ```python
  # views.py line 768
  # BEFORE
  serializer = WikiSnapshotSerializer(wiki.snapshots.all(), many=True)
  # AFTER
  serializer = WikiSnapshotSerializer(wiki.snapshots, many=True)
  
  # services.py WikiService.retrieve
  from django.db.models import Prefetch
  return (
      WikiEntry.objects.select_related("branch")
      .prefetch_related(
          "tags", 
          Prefetch("snapshots", WikiSnapshot.objects.order_by("valid_from_chapter"))
      )
      .get(id=wiki_id)
  )
  ```

   **Acceptance Criteria**:
  - [x] `poetry run pytest apps/contents/tests/test_wiki_views.py -x` PASS

  **Parallelizable**: YES (with 1, 2)

  **Commit**: Groups with 1-2


### Part B: New Review Comments (Verified 3 remaining)

- [x] 4. Restore select_related("branch") in map_services.py

  **What to do**:
  - `MapService.retrieve()` 메서드에서 `select_related("branch")` 복원
  - N+1 방지를 위해 branch eager loading 유지

  **References**:
  - `backend/apps/contents/map_services.py:138` - 수정 대상
  - PR Comment ID: 2708759157

  **Specific Change**:
  ```python
  # BEFORE (line 138)
  return Map.objects.prefetch_related("snapshots__layers__map_objects").get(id=map_id)
  
  # AFTER
  return Map.objects.select_related("branch").prefetch_related("snapshots__layers__map_objects").get(id=map_id)
  ```

   **Acceptance Criteria**:
  - [x] Line 138: `Map.objects.select_related("branch").prefetch_related(...)`
  - [x] 기존 테스트 통과

  **Parallelizable**: YES (with 5, 6)

  **Commit**: YES
  - Message: `perf(contents): restore select_related for branch in MapService`


- [x] 5. Validate branch_id from Redis key in sync task (SECURITY)

  **What to do**:
  - `sync_drafts_to_db` 태스크에서 Redis 키의 `branch_id` 파싱 및 검증
  - `Chapter.objects.get(id=chapter_id, branch_id=branch_id)` 로 검증
  - 불일치 시 경고 로그 후 건너뛰기

  **References**:
  - `backend/apps/contents/tasks.py:93-133` - 수정 대상
  - PR Comment ID: 2708819127

  **Specific Changes**:
  ```python
  # BEFORE
  _prefix, _branch_id, chapter_id_str = parts
  try:
      chapter_id = int(chapter_id_str)
  except ValueError:
      ...
  
  # Inside transaction:
  chapter = Chapter.objects.get(id=chapter_id)
  
  # AFTER
  _prefix, branch_id_str, chapter_id_str = parts
  try:
      branch_id = int(branch_id_str)  # Parse branch_id
      chapter_id = int(chapter_id_str)
  except ValueError:
      logger.warning(f"Invalid IDs in key: {key_str}")
      continue
  
  # Inside transaction - validate branch ownership:
  chapter = Chapter.objects.select_for_update().get(
      id=chapter_id,
      branch_id=branch_id  # CRITICAL: Validate chapter belongs to branch
  )
  ```

  **Acceptance Criteria**:
  - [ ] `branch_id` 파싱 및 int 변환 추가
  - [ ] `Chapter.objects.get(id=chapter_id, branch_id=branch_id)` 검증
  - [ ] DoesExist 시 경고 로그 후 continue (다른 브랜치 챕터 업데이트 방지)

  **Parallelizable**: YES (with 4, 6)

  **Commit**: YES
  - Message: `fix(contents): validate branch_id in draft sync task`


- [x] 6. Add tracking to test.fixme in context-aware.spec.ts

  **What to do**:
  - `test.fixme` 위에 TODO/티켓 참조 코멘트 추가
  - 이유와 담당자 명시

  **References**:
  - `frontend/tests/e2e/reader/context-aware.spec.ts:51-100` - 수정 대상
  - 기존 fork-lifecycle.spec.ts의 패턴 참조

  **Specific Changes**:
  ```typescript
  // BEFORE
  test.fixme('Wiki Visibility by Chapter', async ({ page }) => {
  
  // AFTER  
  // TODO: Blocked - Wiki context filtering not integrated in frontend
  // Waiting on: WikiService.list current_chapter parameter implementation
  test.fixme('Wiki Visibility by Chapter', async ({ page }) => {
  
  // Similarly for Paragraph Comment test
  // TODO: Blocked - Paragraph-level comment UI not implemented
  // Waiting on: ParagraphCommentModal component
  test.fixme('Paragraph Comment', async ({ page }) => {
  ```

   **Acceptance Criteria**:
  - [x] 각 `test.fixme` 위에 `// TODO: Blocked - reason` 형식 코멘트
  - [x] `Waiting on:` 설명 포함

  **Parallelizable**: YES (with 4, 5)

  **Commit**: YES
  - Message: `docs(e2e): add tracking comments to fixme tests`

---

## CANCELLED TODOs

- [x] 7. ~~Add payment verification for wallet top-ups~~ - ALREADY FIXED in PR #238 (line 924-936 already has payment_key validation)

- [x] 8. ~~Add payment validation for subscriptions~~ - ALREADY FIXED in PR #238 (line 118-164 already has payment validation)

---

## Verification Strategy

### Test Commands
```bash
# All tests must pass
cd backend && poetry run pytest

# Specific test groups (run after each fix)
poetry run pytest apps/novels/tests/test_views.py::TestNovelList -v
poetry run pytest apps/novels/tests/test_integration/test_novel_api.py::TestNovelCRUD::test_list_novels -v
poetry run pytest apps/interactions/tests/test_comment_views.py -v
poetry run pytest apps/contents/tests/test_wiki_views.py -v
poetry run pytest apps/interactions/tests/test_reading_views.py -v
```

### Final Checklist
- [x] 모든 15개 테스트 실패 해결 (579 passed, 0 failures)
- [x] 3개 새 리뷰 코멘트 해결 (map_services, tasks, context-aware.spec.ts)
- [x] 린터 에러 0개 (2 pre-existing E501 in ai/services.py)
- [x] PR에 resolved 코멘트 작성 (#3775281239)

---

## Task Flow

```
[N+1 Fixes 1-3] → [Review Comments 4-6] → [Commit] → [Push]
      ↓ (parallel)          ↓ (parallel)
   All can run           All can run
   independently         independently
```

## Commit Strategy

| After Tasks | Message | Files |
|-------------|---------|-------|
| 1-3 | `perf: fix N+1 queries in Novel, Comment, Wiki views` | services, serializers, views |
| 4-6 | `fix: address remaining PR #238 review comments` | map_services, tasks, e2e spec |
