# Work Plan: Fix API Integration Issues #219 & #224

**Created**: 2026-01-23  
**Issues**: #219 (API 모듈 연동), #224 (페이지 API 통합)  
**Branch**: `fix/#219-#224-api-integration`  
**Base**: `develop`

---

## Context

### Original Request
사용자가 #219, #224 이슈 실패 상태 보고. DB에는 시드 데이터가 있지만 프론트엔드 페이지에서 데이터가 표시되지 않음.

### Interview Summary
**Key Discussions**:
- Backend 서버 상태: 8000(docker), 8001(poetry) 둘 다 실행 중
- Seed 데이터: `seed_db` command로 80개 작품 생성 완료
- 증상: 빈 배열 반환 (API는 응답하지만 데이터 없음)
- Backend fix strategy: A (config/urls.py 수정) - Oracle 권장
- Compatibility: NO (깔끔하게 변경)
- Scope: 모든 모듈 한 번에
- Test strategy: Manual first, then E2E tests

**Research Findings**:
- **Root Cause**: Backend URL 라우팅 중복
  - `config/urls.py`: `path("api/v1/novels/", include("apps.novels.urls"))`
  - `apps/novels/urls.py`: `router.register(r"novels", NovelViewSet)`
  - 결과: `/api/v1/novels/novels/` (중복!)
- **Frontend 상태**: 이미 올바른 경로 기대 (`/api/v1/novels/`)
- **Oracle 권장**: Backend-first fix (config/urls.py 변경)
- **Metis 발견**: 프론트엔드 수정 불필요! 백엔드만 고치면 즉시 작동

### Metis Review
**Identified Gaps**:
- Frontend `novels.api.ts` 수정 불필요 (이미 올바름)
- 추가 영향 범위: `branches`, `link-requests` 엔드포인트도 이동
- Risk: 프론트엔드를 불필요하게 수정하면 오히려 망가짐
- 하드코딩된 URL 확인 필요

---

## Work Objectives

### Core Objective
백엔드 URL 라우팅을 일관되게 수정하여 프론트엔드와 통합 가능하도록 함

### Concrete Deliverables
1. `backend/config/urls.py` 수정 (novels 앱 마운트 포인트 변경)
2. Backend pytest 통과
3. Manual verification (curl + 브라우저)
4. Playwright E2E 테스트 작성
5. 모든 페이지에서 데이터 정상 표시

### Definition of Done
- [x] curl로 `/api/v1/novels/?page=1&size=5` 호출 시 80개 작품 데이터 반환
- [x] 프론트엔드 홈페이지 추천 리스트에 작품 표시
- [x] 프론트엔드 작품 목록 페이지에서 무한 스크롤 작동
- [x] Backend pytest 모두 통과
- [x] Playwright E2E 테스트 2개 이상 작성 및 통과

### Must Have
- Backend URL 일관성 (모든 앱이 `/api/v1/` 마운트)
- 프론트엔드 기존 코드 보존 (불필요한 수정 금지)
- 테스트 통과 (regression 방지)

### Must NOT Have (Guardrails)
- ❌ 프론트엔드 API 클라이언트 수정 (검증 전까지)
- ❌ 호환성 alias 추가 (사용자 요청: NO)
- ❌ 다른 앱 URL 구조 변경 (contents, interactions, ai는 이미 올바름)
- ❌ 불필요한 리팩토링 (URL 수정만 집중)
- ❌ AI-slop 패턴: 과도한 주석, 불필요한 헬퍼 함수, 과도한 추상화

---

## Verification Strategy

### Manual Verification (Phase 1)

**Backend API Testing**:
```bash
# 1. Novels endpoint
curl -s "http://localhost:8001/api/v1/novels/?page=1&size=5" | jq '.data.count'
# Expected: 80

# 2. Branches endpoint
curl -s "http://localhost:8001/api/v1/branches/" | jq '.data'
# Expected: branches list (not 404)

# 3. Link requests endpoint  
curl -s "http://localhost:8001/api/v1/link-requests/" | jq '.data'
# Expected: link requests list or empty array (not 404)
```

**Frontend Browser Testing**:
1. Start frontend: `cd frontend && pnpm dev`
2. Open: `http://localhost:3000`
3. Check:
   - 홈페이지 "맞춤 추천" 섹션에 6개 작품 표시
   - `/novels` 페이지에서 작품 카드 표시
   - 무한 스크롤 시 추가 작품 로드
4. Network 탭 확인:
   - `GET /api/v1/novels/?limit=6` → 200 OK
   - Response에 `data.results` 배열 존재

### Playwright E2E Tests (Phase 2)

**Test 1: Novels List Page**
```typescript
test('should display novels on list page', async ({ page }) => {
  await page.goto('http://localhost:3000/novels');
  
  // Wait for novels to load
  await page.waitForSelector('[data-testid="novel-card"]', { timeout: 10000 });
  
  // Verify at least 1 novel is displayed
  const novelCards = await page.locator('[data-testid="novel-card"]').count();
  expect(novelCards).toBeGreaterThan(0);
});
```

**Test 2: Homepage Recommendations**
```typescript
test('should display recommendations on homepage', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Wait for recommendations section
  await page.waitForSelector('h2:has-text("맞춤 추천")', { timeout: 10000 });
  
  // Verify novels are displayed
  const novels = await page.locator('a[href^="/novels/"]').count();
  expect(novels).toBeGreaterThan(0);
});
```

---

## Task Flow

```
Task 0 (verify) → Task 1 (backend fix) → Task 2 (backend test)
                                              ↓
                  Task 4 (E2E tests) ← Task 3 (manual verify)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| N/A | All tasks sequential | Each depends on previous |

| Task | Depends On | Reason |
|------|------------|--------|
| 0 | None | Initial verification |
| 1 | 0 | Need baseline before fix |
| 2 | 1 | Must test backend after fix |
| 3 | 2 | Backend must work before frontend test |
| 4 | 3 | E2E tests codify manual verification |

---

## TODOs

### Task 0: Pre-fix Verification (현재 상태 확인)

**What to do**:
1. 현재 백엔드 엔드포인트 동작 확인
   ```bash
   # 현재 중복 경로로 데이터 있는지 확인
   curl -s "http://localhost:8001/api/v1/novels/novels/?page=1&size=5" | jq '.data.count'
   ```
2. 프론트엔드가 기대하는 경로 확인
   ```bash
   # 프론트엔드가 호출하는 경로 (현재 404 예상)
   curl -s "http://localhost:8001/api/v1/novels/?page=1&size=5" 2>&1 | head -5
   ```
3. 하드코딩된 URL 검색
   ```bash
   grep -r "/api/v1/novels" frontend/app frontend/components --include="*.tsx" --include="*.ts"
   ```

**Must NOT do**:
- 코드 수정하지 않음 (검증만)

**Parallelizable**: NO (첫 작업)

**References**:
- `docs/api-specification.md` - API 규약 확인
- `docs/development-standards.md` - 네이밍 규칙
- `.sisyphus/drafts/api-integration-fix.md` - 분석 결과

**Acceptance Criteria**:

**Manual Execution Verification**:
- [x] Using bash commands:
  - Command: `curl -s "http://localhost:8001/api/v1/novels/novels/?page=1&size=5" | jq '.data.count'`
  - Expected output contains: `80`
  - Exit code: 0
- [x] Command: `curl -s "http://localhost:8001/api/v1/novels/?page=1&size=5" 2>&1`
  - Expected: 404 error or API root response (not novels data)
- [x] Command: `grep -r "/api/v1/novels" frontend/app frontend/components --include="*.tsx"`
  - Expected: No hardcoded URLs found (all use API clients)

**Evidence Required**:
- [x] Command output captured (copy-paste terminal output to comment)

**Commit**: NO (verification only)

---

### Task 1: Fix Backend URL Routing

**What to do**:
1. `backend/config/urls.py` 수정
   ```python
   # BEFORE (line 10):
   path("api/v1/novels/", include("apps.novels.urls")),
   
   # AFTER:
   path("api/v1/", include("apps.novels.urls")),
   ```
2. 변경사항 설명 주석 **금지** (self-explanatory)
3. 다른 앱 include는 그대로 유지
   - `path("api/v1/auth/", include("apps.users.urls.auth"))` - 유지
   - `path("api/v1/users/", include("apps.users.urls.users"))` - 유지
   - `path("api/v1/", include("apps.contents.urls"))` - 유지
   - `path("api/v1/", include("apps.interactions.urls"))` - 유지
   - `path("api/v1/", include("apps.ai.urls"))` - 유지

**Must NOT do**:
- `apps/novels/urls.py` 수정하지 않음
- 프론트엔드 파일 수정하지 않음
- 다른 앱 URL 구조 변경하지 않음

**Parallelizable**: NO (depends on 0)

**References**:
- Oracle's recommendation: ses_417188383ffeO3AdOwpxKRwBrR
- `backend/config/urls.py:10` - 수정 대상 라인
- `backend/apps/novels/urls.py` - router 구조 확인 (수정 안 함)

**Acceptance Criteria**:

**Manual Execution Verification**:
- [x] File modified: `backend/config/urls.py`
- [x] Using bash commands:
  - Command: `cd backend && poetry run python manage.py check`
  - Expected output contains: `System check identified no issues`
  - Exit code: 0
- [x] Request: `curl -s "http://localhost:8001/api/v1/novels/?page=1&size=5" | jq '.success'`
  - Response status: 200
  - Response body contains: `true`
- [x] Request: `curl -s "http://localhost:8001/api/v1/branches/" | jq '.success'`
  - Response status: 200
  - Response body contains: `true`

**Evidence Required**:
- [x] Command output captured
- [x] curl response bodies logged

**Commit**: YES
- Message: `fix(api): align novels app URL routing with other apps`
- Files: `backend/config/urls.py`
- Pre-commit: `cd backend && poetry run python manage.py check`

---

### Task 2: Run Backend Tests

**What to do**:
1. 전체 테스트 실행
   ```bash
   cd backend
   poetry run pytest
   ```
2. novels 앱 테스트 집중 실행
   ```bash
   poetry run pytest apps/novels/tests/
   ```
3. 실패한 테스트 분석
   - URL 패턴 관련 실패: 테스트 코드 수정
   - 로직 관련 실패: 코드 검토 필요 (fix 전으로 롤백 고려)

**Must NOT do**:
- 테스트를 skip하거나 삭제
- 실패를 무시하고 넘어가기

**Parallelizable**: NO (depends on 1)

**References**:
- `backend/apps/novels/tests/test_views.py` - ViewSet 테스트
- `backend/apps/novels/tests/test_services.py` - Service 테스트
- `docs/development-standards.md:4.1` - TDD 원칙

**Acceptance Criteria**:

**Manual Execution Verification**:
- [x] Using bash commands:
  - Command: `cd backend && poetry run pytest apps/novels/tests/ -v`
  - Expected output contains: `passed`
  - Exit code: 0
- [x] Command: `cd backend && poetry run pytest --co -q | grep -c test_`
  - Expected: Test count > 0 (테스트 존재 확인)

**Evidence Required**:
- [x] pytest output captured (all tests PASSED)
- [x] Any test failures documented with fix applied

**Commit**: YES (if test code needed fixes)
- Message: `test(novels): update URL patterns in tests`
- Files: `backend/apps/novels/tests/*.py` (if modified)
- Pre-commit: `poetry run pytest apps/novels/tests/`

---

### Task 3: Manual Frontend Verification

**What to do**:
1. 프론트엔드 dev 서버 시작
   ```bash
   cd frontend
   pnpm dev
   ```
2. 브라우저 테스트 (Playwright browser 사용)
   - Navigate to: `http://localhost:3000`
   - Action: Scroll to "맞춤 추천" section
   - Verify: Novel cards displayed (at least 1)
   - Screenshot: Save to `.sisyphus/evidence/task-3-homepage.png`
3. 작품 목록 페이지 테스트
   - Navigate to: `http://localhost:3000/novels`
   - Action: Wait for novel cards to load
   - Verify: Grid of novel cards displayed
   - Screenshot: Save to `.sisyphus/evidence/task-3-novels-page.png`
4. Network 탭 검증
   - 홈페이지: `GET /api/v1/novels/?limit=6` → 200 OK
   - 작품 페이지: `GET /api/v1/novels/?page=1&limit=12` → 200 OK

**Must NOT do**:
- 프론트엔드 코드 수정 (아직!)
- 에러 발생 시 임의로 수정하지 말고 원인 분석

**Parallelizable**: NO (depends on 2)

**References**:
- `frontend/components/feature/home/recommendation-list.tsx:16` - getNovels 호출
- `frontend/components/feature/novels/infinite-novel-list.tsx:54` - useInfiniteQuery
- `frontend/lib/api/novels.api.ts:10` - BASE_URL 확인

**Acceptance Criteria**:

**For Frontend/UI changes** (using Playwright browser):
- [x] Using playwright browser automation:
  - Navigate to: `http://localhost:3000`
  - Action: Wait for selector `h2:has-text("맞춤 추천")`
  - Verify: At least 1 `a[href^="/novels/"]` element exists
  - Screenshot: `.sisyphus/evidence/task-3-homepage.png`
- [x] Navigate to: `http://localhost:3000/novels`
  - Action: Wait for selector with timeout 10s
  - Verify: Novel cards rendered (count > 0)
  - Screenshot: `.sisyphus/evidence/task-3-novels-page.png`

**For API changes** (using curl):
- [x] Request: `curl -s "http://localhost:3000/api/v1/novels/?limit=6" -H "Origin: http://localhost:3000"`
  - Response status: 200 (또는 Next.js proxy 통해 8001로 전달)
  - Response body contains: `"results":[`

**Evidence Required**:
- [x] Screenshots saved
- [x] Network requests logged (curl or browser devtools)

**Commit**: NO (verification only)

---

### Task 4: Write Playwright E2E Tests

**What to do**:
1. E2E 테스트 파일 생성
   ```bash
   frontend/tests/e2e/novels-api-integration.spec.ts
   ```
2. Test 1: Homepage recommendations
   ```typescript
   import { test, expect } from '@playwright/test';
   
   test('should display novel recommendations on homepage', async ({ page }) => {
     await page.goto('http://localhost:3000');
     
     // Wait for recommendations section
     const recommendations = page.locator('h2:has-text("맞춤 추천")');
     await expect(recommendations).toBeVisible({ timeout: 10000 });
     
     // Verify novels are loaded
     const novelLinks = page.locator('a[href^="/novels/"]');
     await expect(novelLinks.first()).toBeVisible();
     
     const count = await novelLinks.count();
     expect(count).toBeGreaterThan(0);
   });
   ```
3. Test 2: Novels list page
   ```typescript
   test('should display novels on list page', async ({ page }) => {
     await page.goto('http://localhost:3000/novels');
     
     // Wait for page title
     const title = page.locator('h1:has-text("작품")');
     await expect(title).toBeVisible();
     
     // Wait for novel cards (using data-testid if available, or generic selector)
     await page.waitForSelector('[class*="card"]', { timeout: 10000 });
     
     // Verify at least 1 novel is displayed
     const cards = page.locator('[class*="card"]');
     const count = await cards.count();
     expect(count).toBeGreaterThan(0);
   });
   ```
4. 테스트 실행
   ```bash
   cd frontend
   pnpm exec playwright test novels-api-integration.spec.ts
   ```

**Must NOT do**:
- 과도한 테스트 (2개로 충분)
- UI 세부사항 테스트 (스타일, 애니메이션 등)
- 불필요한 wait/sleep (Playwright auto-wait 활용)

**Parallelizable**: NO (depends on 3)

**References**:
- `frontend/tests/e2e/` - Playwright 테스트 디렉토리 (verified)
- Playwright docs: `https://playwright.dev/docs/writing-tests`
- `frontend/package.json` - Playwright 설정 확인

**Acceptance Criteria**:

**Test Verification**:
- [x] Test file created: `frontend/tests/e2e/novels-api-integration.spec.ts`
- [x] Test covers: Homepage recommendations load
- [x] Test covers: Novels list page displays cards
- [x] Using bash commands:
  - Command: `cd frontend && pnpm exec playwright test novels-api-integration.spec.ts`
  - Expected output contains: `2 passed`
  - Exit code: 0

**Evidence Required**:
- [x] Playwright test output captured
- [x] Screenshots from test runs (if available)

**Commit**: YES
- Message: `test(e2e): add novels API integration tests`
- Files: `frontend/tests/e2e/novels-api-integration.spec.ts`
- Pre-commit: `cd frontend && pnpm exec playwright test novels-api-integration.spec.ts`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(api): align novels app URL routing with other apps` | `backend/config/urls.py` | `poetry run python manage.py check` |
| 2 (if needed) | `test(novels): update URL patterns in tests` | `backend/apps/novels/tests/*.py` | `poetry run pytest apps/novels/tests/` |
| 4 | `test(e2e): add novels API integration tests` | `frontend/tests/e2e/novels-api-integration.spec.ts` | `pnpm exec playwright test novels-api-integration.spec.ts` |

**Note**: Task 0, 3은 검증 단계로 커밋 없음

---

## Success Criteria

### Verification Commands
```bash
# Backend API works
curl -s "http://localhost:8001/api/v1/novels/?page=1&size=5" | jq '.data.count'
# Expected: 80

# Frontend homepage loads novels
# (Manual browser check or Playwright)

# All tests pass
cd backend && poetry run pytest apps/novels/tests/
cd frontend && pnpm exec playwright test novels-api-integration.spec.ts
```

### Final Checklist
- [x] All "Must Have" present
  - [ ] Backend URL 일관성 (모든 주요 앱 `/api/v1/` 마운트)
  - [ ] 프론트엔드 기존 코드 보존
  - [ ] 테스트 통과
- [x] All "Must NOT Have" absent
  - [ ] 프론트엔드 불필요한 수정 없음
  - [ ] 호환성 alias 없음
  - [ ] 과도한 리팩토링 없음
- [x] All verification commands succeed
- [x] Playwright E2E tests pass (2/2)
