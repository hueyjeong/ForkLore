# Naming Convention Fix: Complete Frontend camelCase Migration (All 9 Domains)

## Context

### Original Request
Frontend 타입 정의에서 snake_case를 사용하는 부분과 Backend API 응답의 camelCase 불일치를 수정

### Interview Summary
**Key Discussions**:
- Backend 조사: `CamelCaseJSONRenderer` 이미 설정됨 - 자동 변환 동작 중
- Frontend 조사: **9개 도메인 전체**가 snake_case 사용 중
- 런타임 에러 가능성: Backend는 camelCase 전송, Frontend는 snake_case 기대
- User decisions:
  - **9개 도메인 전체를 한 번에 수정** (Momus review Round 2 후 확정)
  - 하위 호환성 불필요 (개발 단계, 외부 소비자 없음)
  - Full TDD 접근 (RED-GREEN-REFACTOR)
  - Test fixture도 타입 변경과 동시에 일괄 수정

**Research Findings**:
- Backend: `StandardJSONRenderer`가 `CamelCaseJSONRenderer` 확장 - 자동 변환 정상 동작
- Frontend 타입 불일치 (**Momus Round 2가 수정한 사실**):
  - ✅ CORRECT (camelCase): **auth, common만!**
  - ❌ MISMATCH (snake_case): **novels, branches, wiki, chapters, interactions, subscriptions, maps, wallet, ai** (9개 도메인)
- Backend 1개 inconsistency: `apps/users/serializers.py:30` - 수동 camelCase 지정

### Metis Review
**Critical Discoveries**:
1. **Zod Schema Found**: `frontend/tests/e2e/fixtures/mock-schemas.ts` - needs camelCase update
2. **Current State**: 일부 에러 발생 중 (타입 불일치로 인한 runtime errors)
3. **E2E Test Mismatch**: subscription.spec.ts uses snake_case mock data

### Momus Review History

**Round 1 - REJECTED**:
- FALSE CLAIM: Plan said "novels, branches, auth, wiki are CORRECT"
- TRUTH: Only auth is camelCase. novels, branches, wiki use snake_case
- SCOPE EXPANDED: 4 domains → 7 domains

**Round 2 - REJECTED**:
- INCOMPLETE SCOPE: Found 2 more domains with snake_case
- **wallet.types.ts**: transaction_type, balance_after, reference_type, reference_id, created_at, recent_transactions
- **ai.types.ts**: chapter_id, task_id, action_type, token_count, daily_limit, usage_by_action
- SCOPE EXPANDED: 7 domains → 9 domains

**Round 3 - Current**:
- All 11 type files verified
- auth.types.ts, common.ts: Already camelCase (no action)
- 9 domains need conversion

---

## Work Objectives

### Core Objective
**Frontend의 모든 타입 정의를 Backend API 응답 형식(camelCase)과 완전히 일치시켜 런타임 타입 에러를 방지하고 일관된 명명 규칙을 확립한다.**

### Concrete Deliverables
1. Backend: `apps/users/serializers.py` 1개 inconsistency 수정
2. Frontend: **9개 타입 파일** camelCase 변환
   - `frontend/types/novels.types.ts`
   - `frontend/types/branches.types.ts`
   - `frontend/types/wiki.types.ts`
   - `frontend/types/chapters.types.ts`
   - `frontend/types/interactions.types.ts`
   - `frontend/types/subscription.types.ts`
   - `frontend/types/maps.types.ts`
   - `frontend/types/wallet.types.ts`
   - `frontend/types/ai.types.ts`
3. Frontend: Zod schemas in `mock-schemas.ts` camelCase 변환 (if they exist for wallet/ai)
4. Frontend: 변경된 타입을 사용하는 모든 component 코드 업데이트
5. Frontend: E2E test mocks camelCase 변환

### Definition of Done
- [ ] Backend: `poetry run pytest apps/users/tests/test_auth_api.py -v` → PASS
- [ ] Backend: `poetry run pytest tests/e2e/test_response_format.py -v` → PASS
- [ ] Frontend: `pnpm typecheck` → No errors
- [ ] Frontend: `pnpm test` → All tests PASS
- [ ] Frontend: All components accessing renamed properties updated
- [ ] Frontend: No snake_case property access in **ALL 9 domains** (comprehensive grep verification)

### Must Have
- TDD 워크플로우 준수 (RED → GREEN → REFACTOR)
- **모든 9개 도메인**의 snake_case 필드를 camelCase로 변환
- Zod schemas 업데이트 (`mock-schemas.ts`)
- 타입 변경으로 인한 모든 TypeScript 에러 해결
- Test fixture 일괄 업데이트

### Must NOT Have (Guardrails)
- Backend serializer 필드명 변경 금지 (snake_case 유지, renderer가 변환)
- 하위 호환성 레이어 추가 금지 (불필요)
- 점진적 마이그레이션 금지 (한 번에 모두 수정)
- `any` 타입 사용 금지 (타입 안전성 보장)
- auth.types.ts, common.ts 수정 금지 (이미 올바름)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (Frontend: Vitest, Backend: pytest)
- **User wants tests**: TDD (Tests-first)
- **Framework**: Frontend: Vitest, Backend: pytest

### TDD Workflow (RED-GREEN-REFACTOR)

Each TODO follows:
1. **RED**: Write failing test or verify TypeScript errors
2. **GREEN**: Update types/code to fix
3. **REFACTOR**: Clean up and verify

### Manual Verification

**Grep Verification (COMPREHENSIVE - All 9 Domains)**:
```bash
cd frontend
# Search for ANY snake_case in type definitions
grep -r "_" types/ --include="*.ts" | grep -v "^types/common.ts" | grep -v "^types/auth.types.ts"
# Expected: ZERO matches (all camelCase except auth/common)

# Search for snake_case property access
grep -r "\\..*_" app/ components/ --include="*.ts" --include="*.tsx"
# Expected: ZERO matches
```

---

## Task Flow

```
Task 0 (Backend)
  ↓
Task 1 (auth/common - verification only)
  ↓
Task 2-4 (novels, branches, wiki) → Task 5 (Zod batch 1)
  ↓
Task 6-9 (chapters, interactions, subscriptions, maps) → Task 10 (Zod batch 2)
  ↓
Task 11-12 (wallet, ai) → Task 13 (Zod batch 3 if needed)
  ↓
Task 14 (Component Updates - ALL domains)
  ↓
Task 15 (Final Comprehensive Verification)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 2, 3, 4 | Independent type files (novels, branches, wiki) |
| B | 6, 7, 8, 9 | Independent type files (chapters, interactions, subscriptions, maps) |
| C | 11, 12 | Independent type files (wallet, ai) |

| Task | Depends On | Reason |
|------|------------|--------|
| 0 | - | Backend fix (independent) |
| 1 | 0 | Verification |
| 2, 3, 4 | 1 | First batch (parallel) |
| 5 | 2, 3, 4 | Zod schemas for batch 1 |
| 6, 7, 8, 9 | 5 | Second batch (parallel) |
| 10 | 6, 7, 8, 9 | Zod schemas for batch 2 |
| 11, 12 | 10 | Third batch (parallel) |
| 13 | 11, 12 | Zod schemas for batch 3 (if exist) |
| 14 | 13 | Component updates depend on all types |
| 15 | 14 | Final verification |

---

## TODOs

- [ ] 0. Fix Backend Inconsistency (CustomTokenObtainPairSerializer)

  **What to do**:
  - Update `apps/users/serializers.py:30`
  - Change `"profileImageUrl"` to `"profile_image_url"`
  - Let renderer handle camelCase conversion

  **Parallelizable**: NO

  **References**:
  - `backend/apps/users/serializers.py:23-35`
  - `backend/common/renderers.py:8-19`

  **Acceptance Criteria**:
  - [ ] Read: `backend/apps/users/serializers.py:23-35`
  - [ ] Update line 30: `"profileImageUrl"` → `"profile_image_url"`
  - [ ] Run: `cd backend && poetry run pytest apps/users/tests/test_auth_api.py -v`
  - [ ] Expected: All tests PASS

  **Commit**: YES
  - Message: `fix(users): use auto camelCase conversion in CustomTokenObtainPairSerializer`
  - Files: `backend/apps/users/serializers.py`

---

- [ ] 1. Verify auth.types.ts and common.ts (Already Correct - No Changes)

  **What to do**:
  - Read `frontend/types/auth.types.ts` and `frontend/types/common.ts`
  - Verify all properties are camelCase
  - Document that these domains are already correct
  - Use as reference pattern for other 9 domains

  **Parallelizable**: NO (verification step)

  **References**:
  - `frontend/types/auth.types.ts`
  - `frontend/types/common.ts`

  **Acceptance Criteria**:
  - [ ] Read: `frontend/types/auth.types.ts`
  - [ ] Verify: `profileImageUrl`, `birthDate`, `authProvider` (all camelCase)
  - [ ] Read: `frontend/types/common.ts`
  - [ ] Verify: Already camelCase
  - [ ] No changes needed

  **Commit**: NO (verification only)

---

- [ ] 2. Convert novels.types.ts to camelCase

  **What to do**:
  - Update `frontend/types/novels.types.ts`
  - Rename all snake_case properties to camelCase

  **Snake_case properties to convert**:
  - `cover_image_url` → `coverImageUrl`
  - `age_rating` → `ageRating`
  - `is_exclusive` → `isExclusive`
  - `is_premium` → `isPremium`
  - `allow_branching` → `allowBranching`
  - `total_view_count` → `totalViewCount`
  - `total_like_count` → `totalLikeCount`
  - `average_rating` → `averageRating`
  - `total_chapter_count` → `totalChapterCount`
  - `branch_count` → `branchCount`
  - `linked_branch_count` → `linkedBranchCount`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`

  **Parallelizable**: YES (with 3, 4)

  **References**:
  - `frontend/types/novels.types.ts:61-78`
  - `frontend/types/auth.types.ts` - correct camelCase pattern

  **Acceptance Criteria**:
  - [ ] Read: `frontend/types/novels.types.ts`
  - [ ] Update all snake_case properties to camelCase
  - [ ] Run: `cd frontend && pnpm typecheck`
  - [ ] Expected: Type errors resolved (or new errors in components)

  **Commit**: YES
  - Message: `refactor(types): convert novels.types.ts to camelCase`
  - Files: `frontend/types/novels.types.ts`

---

- [ ] 3. Convert branches.types.ts to camelCase

  **What to do**:
  - Update `frontend/types/branches.types.ts`

  **Snake_case properties**:
  - `novel_id` → `novelId`
  - `cover_image_url` → `coverImageUrl`
  - `is_main` → `isMain`
  - `branch_type` → `branchType`
  - `canon_status` → `canonStatus`
  - `parent_branch_id` → `parentBranchId`
  - `fork_point_chapter` → `forkPointChapter`
  - `vote_count` → `voteCount`
  - `vote_threshold` → `voteThreshold`
  - `view_count` → `viewCount`
  - `chapter_count` → `chapterCount`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`

  **Parallelizable**: YES (with 2, 4)

  **References**:
  - `frontend/types/branches.types.ts:37-55`

  **Acceptance Criteria**:
  - [ ] Update types
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: YES
  - Message: `refactor(types): convert branches.types.ts to camelCase`
  - Files: `frontend/types/branches.types.ts`

---

- [ ] 4. Convert wiki.types.ts to camelCase

  **What to do**:
  - Update `frontend/types/wiki.types.ts`

  **Snake_case properties**:
  - `display_order` → `displayOrder`
  - `created_at` → `createdAt`
  - `valid_from_chapter` → `validFromChapter`
  - `contributor_type` → `contributorType`
  - `image_url` → `imageUrl`
  - `first_appearance` → `firstAppearance`
  - `hidden_note` → `hiddenNote`
  - `ai_metadata` → `aiMetadata`
  - `branch_id` → `branchId` (in params)

  **Parallelizable**: YES (with 2, 3)

  **References**:
  - `frontend/types/wiki.types.ts:16-53`

  **Acceptance Criteria**:
  - [ ] Update types
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: YES
  - Message: `refactor(types): convert wiki.types.ts to camelCase`
  - Files: `frontend/types/wiki.types.ts`

---

- [ ] 5. Update Zod Schemas (Batch 1: novels, branches, wiki)

  **What to do**:
  - Update `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - Update NovelSchema, BranchSchema, WikiTagSchema, WikiEntrySchema to match new types

  **Parallelizable**: NO (depends on 2, 3, 4)

  **References**:
  - `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - Updated types from tasks 2, 3, 4

  **Acceptance Criteria**:
  - [ ] Read: `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - [ ] Update NovelSchema, BranchSchema, WikiSchemas to camelCase
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: YES
  - Message: `test: update NovelSchema, BranchSchema, WikiSchemas to camelCase`
  - Files: `frontend/tests/e2e/fixtures/mock-schemas.ts`

---

- [ ] 6. Convert chapters.types.ts to camelCase

  **Snake_case properties**:
  - `chapter_number` → `chapterNumber`
  - `content_html` → `contentHtml`
  - `word_count` → `wordCount`
  - `access_type` → `accessType`
  - `scheduled_at` → `scheduledAt`
  - `published_at` → `publishedAt`
  - `view_count` → `viewCount`
  - `like_count` → `likeCount`
  - `comment_count` → `commentCount`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`
  - `prev_chapter` → `prevChapter`
  - `next_chapter` → `nextChapter`

  **Parallelizable**: YES (with 7, 8, 9)

  **Commit**: YES
  - Message: `refactor(types): convert chapters.types.ts to camelCase`
  - Files: `frontend/types/chapters.types.ts`

---

- [ ] 7. Convert interactions.types.ts to camelCase

  **Snake_case properties**:
  - `is_spoiler` → `isSpoiler`
  - `is_pinned` → `isPinned`
  - `parent_id` → `parentId`
  - `reply_count` → `replyCount`
  - `paragraph_index` → `paragraphIndex`
  - `selection_start` → `selectionStart`
  - `selection_end` → `selectionEnd`
  - `quoted_text` → `quotedText`
  - `like_count` → `likeCount`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`

  **Parallelizable**: YES (with 6, 8, 9)

  **Commit**: YES
  - Message: `refactor(types): convert interactions.types.ts to camelCase`
  - Files: `frontend/types/interactions.types.ts`

---

- [ ] 8. Convert subscription.types.ts to camelCase

  **Snake_case properties**:
  - `started_at` → `startedAt`
  - `expires_at` → `expiresAt`
  - `cancelled_at` → `cancelledAt`
  - `auto_renew` → `autoRenew`
  - `price_paid` → `pricePaid`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`

  **Parallelizable**: YES (with 6, 7, 9)

  **Commit**: YES
  - Message: `refactor(types): convert subscription.types.ts to camelCase`
  - Files: `frontend/types/subscription.types.ts`

---

- [ ] 9. Convert maps.types.ts to camelCase

  **Snake_case properties**:
  - `source_map_id` → `sourceMapId`
  - `layer_type` → `layerType`
  - `z_index` → `zIndex`
  - `is_visible` → `isVisible`
  - `style_json` → `styleJson`
  - `object_type` → `objectType`
  - `wiki_entry_id` → `wikiEntryId`
  - `created_at` → `createdAt`
  - `updated_at` → `updatedAt`

  **Parallelizable**: YES (with 6, 7, 8)

  **Commit**: YES
  - Message: `refactor(types): convert maps.types.ts to camelCase`
  - Files: `frontend/types/maps.types.ts`

---

- [ ] 10. Update Zod Schemas (Batch 2: chapters, interactions, subscriptions, maps)

  **What to do**:
  - Update `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - Update ChapterSchema, Comment/Subscription schemas, Map-related schemas (if they exist)

  **Parallelizable**: NO (depends on 6, 7, 8, 9)

  **Commit**: YES
  - Message: `test: update ChapterSchema, InteractionSchemas, MapSchemas to camelCase`
  - Files: `frontend/tests/e2e/fixtures/mock-schemas.ts`

---

- [ ] 11. Convert wallet.types.ts to camelCase

  **What to do**:
  - Update `frontend/types/wallet.types.ts`

  **Snake_case properties** (verified by Momus Round 2):
  - `transaction_type` → `transactionType`
  - `balance_after` → `balanceAfter`
  - `reference_type` → `referenceType`
  - `reference_id` → `referenceId`
  - `created_at` → `createdAt`
  - `recent_transactions` → `recentTransactions`

  **Parallelizable**: YES (with 12)

  **References**:
  - `frontend/types/wallet.types.ts:33-46` (Momus verified)

  **Acceptance Criteria**:
  - [ ] Read: `frontend/types/wallet.types.ts`
  - [ ] Update all snake_case properties
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: YES
  - Message: `refactor(types): convert wallet.types.ts to camelCase`
  - Files: `frontend/types/wallet.types.ts`

---

- [ ] 12. Convert ai.types.ts to camelCase

  **What to do**:
  - Update `frontend/types/ai.types.ts`

  **Snake_case properties** (verified by Momus Round 2):
  - `chapter_id` → `chapterId`
  - `task_id` → `taskId`
  - `action_type` → `actionType`
  - `token_count` → `tokenCount`
  - `daily_limit` → `dailyLimit`
  - `usage_by_action` → `usageByAction`

  **Parallelizable**: YES (with 11)

  **References**:
  - `frontend/types/ai.types.ts:40-108` (Momus verified)

  **Acceptance Criteria**:
  - [ ] Read: `frontend/types/ai.types.ts`
  - [ ] Update all snake_case properties
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: YES
  - Message: `refactor(types): convert ai.types.ts to camelCase`
  - Files: `frontend/types/ai.types.ts`

---

- [ ] 13. Update Zod Schemas (Batch 3: wallet, ai - if they exist)

  **What to do**:
  - Check if wallet/ai schemas exist in `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - If YES: Update to camelCase
  - If NO: Skip (no action needed)

  **Parallelizable**: NO (depends on 11, 12)

  **Acceptance Criteria**:
  - [ ] Read: `frontend/tests/e2e/fixtures/mock-schemas.ts`
  - [ ] Search for WalletSchema, AISchema, CoinTransactionSchema
  - [ ] If found: Update to camelCase
  - [ ] If not found: Document "No schemas exist for wallet/ai"
  - [ ] Run: `cd frontend && pnpm typecheck`

  **Commit**: IF schemas exist
  - Message: `test: update WalletSchema, AISchemas to camelCase`
  - Files: `frontend/tests/e2e/fixtures/mock-schemas.ts`

---

- [ ] 14. Update All Component Code Using Renamed Properties

  **What to do**:
  - Search ALL 9 domains for snake_case property access
  - Update each occurrence to camelCase
  - Fix ALL TypeScript errors

  **Comprehensive Search Commands**:
  ```bash
  cd frontend
  # Search components
  grep -rn "\\..*_at" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_count" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_id" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_type" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_url" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_after" app/ components/ --include="*.tsx" --include="*.ts"
  grep -rn "\\..*_limit" app/ components/ --include="*.tsx" --include="*.ts"
  ```

  **Must NOT do**:
  - Skip any files
  - Use `any` to bypass errors

  **Parallelizable**: NO (depends on all type updates)

  **References**:
  - Updated types from all previous tasks
  - Momus verified 16 component files use snake_case

  **Acceptance Criteria**:
  - [ ] Run all grep commands above
  - [ ] For each match: Update property access to camelCase
  - [ ] Run: `cd frontend && pnpm typecheck`
  - [ ] Expected: ZERO errors
  - [ ] Run: `cd frontend && pnpm test`
  - [ ] Expected: All tests PASS

  **Commit**: YES
  - Message: `refactor(components): update all property access to camelCase across 9 domains`
  - Files: `frontend/app/**/*.tsx`, `frontend/components/**/*.tsx`

---

- [ ] 15. Final Comprehensive Verification (ALL 9 Domains)

  **What to do**:
  - Run full test suite
  - **COMPREHENSIVE grep verification** (Momus requirement)
  - Verify ZERO snake_case in ALL 9 domains
  - Create verification report

  **Parallelizable**: NO (depends on all tasks)

  **Acceptance Criteria**:

  **Full Test Suite**:
  - [ ] Backend: `cd backend && poetry run pytest -v` → PASS
  - [ ] Frontend: `cd frontend && pnpm test` → PASS
  - [ ] Frontend: `cd frontend && pnpm typecheck` → No errors
  - [ ] Frontend: `cd frontend && pnpm build` → Success

  **COMPREHENSIVE Grep (CRITICAL - Momus Requirement)**:
  - [ ] Types verification:
    ```bash
    cd frontend
    grep -r "_" types/ --include="*.ts" | grep -v "types/common.ts" | grep -v "types/auth.types.ts"
    ```
    Expected: **ZERO matches** (excluding auth/common)
  
  - [ ] Components verification:
    ```bash
    cd frontend
    grep -rn "\\..*_" app/ components/ --include="*.tsx" --include="*.ts" | grep -v "// " | grep -v "import"
    ```
    Expected: **ZERO matches**
  
  - [ ] Zod schemas verification:
    ```bash
    cd frontend
    grep -n "_at\\|_count\\|_id\\|_type\\|_url\\|_after\\|_limit" tests/e2e/fixtures/mock-schemas.ts
    ```
    Expected: **ZERO matches**

  **Manual Integration Verification**:
  - [ ] Start backend: `cd backend && poetry run python manage.py runserver`
  - [ ] Start frontend: `cd frontend && pnpm dev`
  - [ ] Test novels page: Navigate to `/novels` → Data displays correctly
  - [ ] Test chapters page: Navigate to `/novels/1` → No undefined properties
  - [ ] Test interactions: Post comment → Data displays correctly
  - [ ] Test wallet page (if exists): Navigate to `/wallet` → Transactions display correctly
  - [ ] Browser console: No TypeScript/runtime errors
  - [ ] Network tab: Verify API responses are in camelCase

  **Documentation**:
  - [ ] Create verification report documenting:
    - All 9 domains converted
    - auth/common verified as already correct
    - Backend inconsistency fixed
    - Grep results (zero matches)
    - Test results (all passing)

  **Commit**: YES
  - Message: `docs: verify complete naming convention migration (9 domains)`
  - Files: Verification report (create `.sisyphus/verification-reports/naming-convention-fix.md`)

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 0 | `fix(users): use auto camelCase conversion in CustomTokenObtainPairSerializer` | `backend/apps/users/serializers.py` |
| 2 | `refactor(types): convert novels.types.ts to camelCase` | `frontend/types/novels.types.ts` |
| 3 | `refactor(types): convert branches.types.ts to camelCase` | `frontend/types/branches.types.ts` |
| 4 | `refactor(types): convert wiki.types.ts to camelCase` | `frontend/types/wiki.types.ts` |
| 5 | `test: update NovelSchema, BranchSchema, WikiSchemas to camelCase` | `frontend/tests/e2e/fixtures/mock-schemas.ts` |
| 6 | `refactor(types): convert chapters.types.ts to camelCase` | `frontend/types/chapters.types.ts` |
| 7 | `refactor(types): convert interactions.types.ts to camelCase` | `frontend/types/interactions.types.ts` |
| 8 | `refactor(types): convert subscription.types.ts to camelCase` | `frontend/types/subscription.types.ts` |
| 9 | `refactor(types): convert maps.types.ts to camelCase` | `frontend/types/maps.types.ts` |
| 10 | `test: update ChapterSchema, InteractionSchemas, MapSchemas to camelCase` | `frontend/tests/e2e/fixtures/mock-schemas.ts` |
| 11 | `refactor(types): convert wallet.types.ts to camelCase` | `frontend/types/wallet.types.ts` |
| 12 | `refactor(types): convert ai.types.ts to camelCase` | `frontend/types/ai.types.ts` |
| 13 | `test: update WalletSchema, AISchemas to camelCase (if exist)` | `frontend/tests/e2e/fixtures/mock-schemas.ts` |
| 14 | `refactor(components): update all property access to camelCase across 9 domains` | `frontend/app/**/*.tsx`, `frontend/components/**/*.tsx` |
| 15 | `docs: verify complete naming convention migration (9 domains)` | Verification report |

---

## Success Criteria

### Verification Commands (COMPREHENSIVE)
```bash
# Backend
cd backend
poetry run pytest apps/users/tests/test_auth_api.py -v
poetry run pytest tests/e2e/test_response_format.py -v

# Frontend
cd frontend
pnpm typecheck  # ZERO errors
pnpm test  # All pass
pnpm build  # Success

# CRITICAL: Comprehensive grep (MUST return nothing)
cd frontend
grep -r "_" types/ --include="*.ts" | grep -v "types/common.ts" | grep -v "types/auth.types.ts"
# Expected: ZERO matches

grep -rn "\\..*_" app/ components/ --include="*.tsx" --include="*.ts" | grep -v "// " | grep -v "import"
# Expected: ZERO matches

grep -n "_at\\|_count\\|_id\\|_type\\|_url\\|_after\\|_limit" tests/e2e/fixtures/mock-schemas.ts
# Expected: ZERO matches
```

### Final Checklist
- [ ] All 9 domains converted: novels, branches, wiki, chapters, interactions, subscriptions, maps, wallet, ai
- [ ] Auth/common domains verified (already correct)
- [ ] Backend inconsistency fixed
- [ ] All TypeScript errors resolved
- [ ] All tests passing
- [ ] Zod schemas updated (for domains that have them)
- [ ] Components updated
- [ ] **ZERO snake_case remnants** (comprehensive grep verification passes)
- [ ] Backend returns camelCase
- [ ] Frontend consumes camelCase correctly
- [ ] Wallet page works (if exists)
- [ ] AI features work (if implemented)
