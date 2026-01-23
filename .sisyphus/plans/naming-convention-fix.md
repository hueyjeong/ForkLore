# Naming Convention Fix: Complete Frontend camelCase Migration (All 9 Domains)

## Context

### Original Request
Frontend 타입 정의에서 snake_case를 사용하는 부분과 Backend API 응답의 camelCase 불일치를 수정

### Interview Summary
**Key Discussions**:
- Backend 조사: `CamelCaseJSONRenderer` 이미 설정됨 - 자동 변환 동작 중
- Frontend 조사: **9개 도메인 전체**가 snake_case 사용 중이었으나, 현재 많은 부분이 camelCase로 변환됨.
- 런타임 에러 가능성: Backend는 camelCase 전송, Frontend는 snake_case 기대 (남아있는 부분들에서 발생 가능)
- User decisions:
  - **9개 도메인 전체를 한 번에 수정** (Momus review Round 2 후 확정)
  - 하위 호환성 불필요 (개발 단계, 외부 소비자 없음)
  - Full TDD 접근 (RED-GREEN-REFACTOR)
  - Test fixture도 타입 변경과 동시에 일괄 수정

**Research Findings (Updated 2024-01-23)**:
- Backend: `StandardJSONRenderer`가 `CamelCaseJSONRenderer` 확장 - 자동 변환 정상 동작.
- Frontend 타입 불일치 현황:
  - ✅ **COMPLETED** (camelCase): `auth`, `common`, `novels`, `branches`, `chapters`, `interactions`, `subscription`, `maps`, `wallet`
  - ⚠️ **PARTIALLY COMPLETED**: `wiki.types.ts` (`branch_id` 하나 남음)
  - ❌ **MISMATCH** (snake_case): `ai.types.ts` (전체 snake_case)
- Zod Schemas & Mocks 현황:
  - ❌ **MISMATCH** (snake_case): `frontend/tests/e2e/fixtures/mock-schemas.ts` 내 모든 스키마.
  - ❌ **MISMATCH** (snake_case): E2E 테스트 및 유닛 테스트 내 하드코딩된 mock 데이터들.
- Backend 1개 inconsistency:
  - ❌ **PENDING**: `apps/users/serializers.py:30` - 수동 camelCase 지정 (`"profileImageUrl"`).

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
- All 11 type files verified.
- **Note**: Some domains were already converted since the last review, but many parts (Zod, Mocks, specific components) are still pending.

---

## Work Objectives

### Core Objective
**Frontend의 모든 타입 정의, Zod 스키마, Mock 데이터를 Backend API 응답 형식(camelCase)과 완전히 일치시켜 런타임 타입 에러를 방지하고 일관된 명명 규칙을 확립한다.**

### Concrete Deliverables
1. Backend: `apps/users/serializers.py` 1개 inconsistency 수정 (`profileImageUrl` -> `profile_image_url`)
2. Frontend: 남은 타입 파일 camelCase 변환 (`ai.types.ts`, `wiki.types.ts` 일부)
3. Frontend: **Zod schemas in `mock-schemas.ts` 전체 camelCase 변환** (Critical)
4. Frontend: 모든 테스트 파일(`*.test.ts`, `*.spec.ts`)의 mock 데이터 camelCase 변환
5. Frontend: 변경된 타입을 사용하는 모든 component 코드 업데이트 (남은 부분 위주)

### Definition of Done
- [ ] Backend: `poetry run pytest apps/users/tests/test_auth_api.py -v` → PASS
- [ ] Backend: `poetry run pytest tests/e2e/test_response_format.py -v` → PASS
- [ ] Frontend: `pnpm typecheck` → No errors
- [ ] Frontend: `pnpm test` → All tests PASS
- [ ] Frontend: All components accessing renamed properties updated
- [ ] Frontend: No snake_case property access in **ALL domains** (comprehensive grep verification)

---

## Verification Strategy

### TDD Workflow (RED-GREEN-REFACTOR)
1. **RED**: Zod 스키마나 타입을 변경하여 테스트 또는 타입 체크가 실패하도록 함.
2. **GREEN**: 관련 코드(컴포넌트, mock 데이터)를 수정하여 통과시킴.
3. **REFACTOR**: 불필요한 snake_case 잔재 제거 및 검증.

### Manual Verification
- **COMPREHENSIVE Grep**: `grep -r "\\..*_" app/ components/` 결과가 유효한 경우(query param sort 등) 외에는 없어야 함.

---

## Task Flow (Updated)

```
Task 0 (Backend Fix)
  ↓
Task 1 (Wiki & AI Type Fix)
  ↓
Task 2 (Zod Schemas Fix - Batch 1 & 2)
  ↓
Task 3 (Test Mocks & Fixtures Update)
  ↓
Task 4 (Component Updates & Local Schemas)
  ↓
Task 5 (Final Verification)
```

---

## TODOs

- [x] 0. Fix Backend Inconsistency (CustomTokenObtainPairSerializer)
  **Status**: COMPLETED ✅
  - Update `apps/users/serializers.py:30`
  - Change `"profileImageUrl"` to `"profile_image_url"`
  - Expected: `StandardJSONRenderer`가 자동으로 `profileImageUrl`로 변환하여 반환함.

- [x] 1. Verify auth.types.ts, common.ts, novels, branches, chapters, interactions, subscription, maps, wallet
  **Status**: ALREADY COMPLETED ✅

- [x] 2. Complete wiki.types.ts conversion
  **Status**: COMPLETED ✅
  - Update `WikiListParams` in `frontend/types/wiki.types.ts`
  - `branch_id` → `branchId`

- [x] 3. Convert ai.types.ts to camelCase
  **Status**: COMPLETED ✅
  - `chapter_id` → `chapterId`
  - `task_id` → `taskId`
  - `action_type` → `actionType`
  - `token_count` → `tokenCount`
  - `daily_limit` → `dailyLimit`
  - `usage_by_action` → `usageByAction`

- [x] 4. Update ALL Zod Schemas in mock-schemas.ts
  **Status**: COMPLETED ✅
  - `frontend/tests/e2e/fixtures/mock-schemas.ts` 내의 모든 snake_case 필드를 camelCase로 변경.
  - NovelSchema, ChapterSchema, BranchSchema, WikiSchemas, SubscriptionSchema 등 포함.

- [x] 5. Update All Test Fixtures and Hardcoded Mocks
  **Status**: COMPLETED ✅
  - `frontend/tests/**/*.test.ts`, `frontend/tests/**/*.spec.ts` 내의 모든 mock 데이터를 camelCase로 변경.
  - 예: `cover_image_url` -> `coverImageUrl`, `is_premium` -> `isPremium` 등.

- [x] 6. Update Remaining Components & Local Schemas
  **Status**: COMPLETED ✅
  - `frontend/components/feature/branches/fork-modal.tsx` 내의 로컬 Zod 스키마 및 폼 필드(`branch_type` -> `branchType`) 수정.
  - 컴포넌트 내에서 snake_case로 접근하는 남은 부분들 수정.

- [x] 7. Final Comprehensive Verification
  **Status**: COMPLETED ✅
  - `pnpm typecheck` 및 `pnpm test` 전체 실행.
  - Grep을 통한 snake_case 잔재 확인.
  - 브라우저에서 실제 데이터 렌더링 확인.

---

## Commit Strategy (Simplified)
| After Task | Message | Files |
|------------|---------|-------|
| 0 | `fix(backend): use snake_case for profile_image_url in serializer` | `backend/apps/users/serializers.py` |
| 2-3 | `refactor(types): complete wiki and ai types camelCase conversion` | `frontend/types/wiki.types.ts`, `frontend/types/ai.types.ts` |
| 4 | `test(mocks): update all Zod schemas to camelCase` | `frontend/tests/e2e/fixtures/mock-schemas.ts` |
| 5 | `test(mocks): update all test mock data to camelCase` | `frontend/tests/**/*.ts`, `frontend/tests/**/*.tsx` |
| 6 | `refactor(ui): update remaining components and local schemas to camelCase` | `frontend/app/**/*.tsx`, `frontend/components/**/*.tsx` |
| 7 | `docs: finalize naming convention migration` | Verification report |
