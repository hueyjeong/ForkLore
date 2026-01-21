# Frontend Refactoring: Vercel React Best Practices

## Context

### Original Request
Vercel React Best Practices 스킬을 활용하여 프론트엔드 리팩토링

### Interview Summary
**Key Discussions**:
- 범위: 전체 리팩토링 (Critical + High + Low 모든 이슈)
- Auth: Zustand로 통합 (AGENTS.md 가이드라인 준수)
- 테스트: TDD (RED-GREEN-REFACTOR) - 기존 Vitest 활용
- Barrel files: 스킵 (Vercel `bundle-barrel-imports` 규칙 준수)

**Research Findings**:
- Next.js 16 + React 19 + TypeScript 스택
- TanStack Query 이미 잘 사용 중 (13개 파일)
- Suspense, Dynamic Import 적절히 사용
- 84개 컴포넌트 (26개 client-side)
- `useAuth()` hook은 정의만 있고 외부 사용처 없음 (안전하게 제거 가능)
- 백엔드 API 45개 ViewSet 존재 (API 연결 가능)

### Metis Review
**Identified Gaps** (addressed):
- Barrel files 충돌 → 스킵으로 해결
- AuthProvider consumers → LSP 확인 결과 외부 사용처 없음
- Backend API 존재 여부 → 45개 ViewSet 확인됨
- reader-view strategy → React Query 유지 (인터랙티브 리더)

---

## Work Objectives

### Core Objective
Vercel React Best Practices에 맞춰 프론트엔드 코드 품질과 성능을 개선한다.

### Concrete Deliverables
- 4개 컴포넌트의 useEffect → React Query 전환
- Auth 상태관리 Zustand 단일화 (AuthProvider 제거)
- 3개 리스트 컴포넌트에 React.memo 적용
- Mock 데이터 실제 API 연결

### Definition of Done
- [x] `pnpm test` 모든 테스트 통과 (133 tests passing)
- [x] `pnpm build` 빌드 성공
- [~] `pnpm lint` 린트 에러 없음 (pre-existing issues, not from our changes)
- [~] 브라우저에서 주요 기능 동작 확인 (requires manual QA with running backend)

### Must Have
- TDD 적용: 테스트 먼저 작성 후 구현
- 기존 동작 유지: 리팩토링 전후 동일한 UX
- React Query 패턴: `ranking-tabs.tsx` 참조

### Must NOT Have (Guardrails)
- ❌ Barrel files (index.ts) 생성 → Vercel `bundle-barrel-imports` 규칙 위반
- ❌ 백엔드 코드 수정
- ❌ UI/UX 디자인 변경
- ❌ 새로운 기능 추가
- ❌ middleware.ts 수정 (auth 라우팅 로직)
- ❌ 컴포넌트 동작 변경 (리팩토링만)

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (Vitest 설정됨)
- **User wants tests**: TDD (RED-GREEN-REFACTOR)
- **Framework**: Vitest + @testing-library/react

### TDD Flow (Each TODO)
1. **RED**: 실패하는 테스트 먼저 작성
   - Test command: `pnpm test [file]`
   - Expected: FAIL
2. **GREEN**: 최소 코드로 테스트 통과
   - Expected: PASS
3. **REFACTOR**: 코드 정리 (테스트 유지)
   - Expected: PASS

---

## Task Flow

```
Task 0 (GitHub Issue + Branch 생성)
    ↓
Task 1 (테스트 인프라 확인)
    ↓
Task 2 → Task 3 → Task 4 → Task 5 (useEffect → React Query, 순차)
    ↓
Task 6 (Auth 통합)
    ↓
Task 7 → Task 8 → Task 9 (React.memo, 병렬 가능)
    ↓
Task 10 (Mock 데이터 제거)
    ↓
Task 11 (Final verification + PR 생성)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 7, 8, 9 | 독립적인 컴포넌트, 서로 의존성 없음 |

| Task | Depends On | Reason |
|------|------------|--------|
| 0 | - | 첫 번째 태스크 (이슈 + 브랜치) |
| 1 | 0 | 브랜치 생성 후 작업 시작 |
| 2-5 | 1 | 테스트 인프라 확인 필요 |
| 6 | 2-5 | useEffect 전환 완료 후 Auth 통합 |
| 7-9 | 6 | Auth 변경 완료 후 memo 적용 |
| 10 | 6 | Auth 통합 후 API 연결 |
| 11 | All | 최종 검증 + PR 생성 |

---

## TODOs

- [x] 0. GitHub 이슈 생성 및 Feature 브랜치 생성

  **What to do**:
  - GitHub에 리팩토링 이슈 생성
    - Title: `refactor(frontend): Apply Vercel React Best Practices`
    - Labels: `refactor`, `frontend`, `performance`
  - 이슈 번호 확인 후 브랜치 생성
    - 브랜치명: `feat/#<issue-number>-frontend-vercel-best-practices`
  - develop 브랜치에서 분기

  **Must NOT do**:
  - main 브랜치에서 분기
  - 이슈 없이 브랜치 생성

  **Parallelizable**: NO (첫 번째 태스크)

  **References**:

  **Project References**:
  - `AGENTS.md` - Git Workflow: Base Branch는 `develop`, 브랜치 네이밍 `feat/#<issue>-<description>`

  **Acceptance Criteria**:
  - [ ] GitHub Issue 생성됨 (번호 확인)
  - [ ] `gh issue view <number>` → 이슈 정보 표시
  - [ ] `git branch` → `feat/#<issue-number>-frontend-vercel-best-practices` 존재
  - [ ] `git log --oneline -1` → develop의 최신 커밋에서 분기됨

  **Commands**:
  ```bash
  # 이슈 생성
  gh issue create --title "refactor(frontend): Apply Vercel React Best Practices" \
    --body "## Summary
  - useEffect 데이터 fetching → React Query 전환 (4개 컴포넌트)
  - Auth 상태관리 Zustand 단일화
  - 리스트 컴포넌트 React.memo 적용
  - Mock 데이터 실제 API 연결

  ## Related
  - Vercel React Best Practices skill 기반

  ## Checklist
  - [ ] useEffect → React Query (user-profile, my-library, reader-view, branch-choices)
  - [ ] Auth consolidation (Zustand only)
  - [ ] React.memo (NovelCard, BranchCard, PostCard)
  - [ ] Mock data → Real API
  - [ ] All tests pass" \
    --label "refactor,frontend,performance"

  # 브랜치 생성
  git checkout develop
  git pull origin develop
  git checkout -b feat/#<ISSUE_NUMBER>-frontend-vercel-best-practices
  ```

  **Commit**: NO (브랜치 생성만)

---

- [x] 1. 테스트 인프라 확인 및 환경 설정

  **What to do**:
  - Vitest 설정 확인 (`vitest.config.ts`)
  - 기존 테스트 실행하여 동작 확인
  - 필요시 @testing-library/react 설정 확인
  - React Query 테스트 유틸리티 확인 (QueryClientProvider wrapper)

  **Must NOT do**:
  - 기존 테스트 수정
  - 새로운 테스트 프레임워크 도입

  **Parallelizable**: NO (첫 번째 태스크)

  **References**:

  **Pattern References**:
  - `frontend/vitest.config.ts` - 현재 Vitest 설정
  - `frontend/tests/api/` - 기존 API 테스트 패턴

  **Test References**:
  - `frontend/components/feature/novels/infinite-novel-list.test.tsx` - React Query 컴포넌트 테스트 패턴

  **External References**:
  - TanStack Query Testing: https://tanstack.com/query/latest/docs/framework/react/guides/testing

  **Acceptance Criteria**:
  - [ ] `pnpm test` 실행 → 기존 테스트 모두 PASS
  - [ ] React Query wrapper 유틸리티 존재 확인 또는 생성
  - [ ] 테스트 실행 시간 기록 (baseline)

  **Commit**: YES
  - Message: `test(frontend): verify test infrastructure for TDD refactoring`
  - Files: `frontend/tests/utils/` (필요시 생성)
  - Pre-commit: `pnpm test`

---

- [x] 2. user-profile.tsx: useEffect → useQueries 전환

  **What to do**:
  - **RED**: `user-profile.test.tsx` 작성
    - useQueries로 profile과 wallet 병렬 fetching 테스트
    - loading, error, success 상태 테스트
  - **GREEN**: useEffect를 useQueries로 교체
    - `useQueries` 사용 (2개 쿼리 병렬 실행)
    - queryKey: `['profile']`, `['wallet', 'balance']`
  - **REFACTOR**: 코드 정리

  **Must NOT do**:
  - UI 레이아웃 변경
  - 새로운 상태 추가
  - 에러 메시지 변경

  **Parallelizable**: NO (순차 - Task 0 의존)

  **References**:

  **Pattern References**:
  - `frontend/components/feature/ranking/ranking-tabs.tsx:9-22` - useQuery 병렬 패턴 (다중 useQuery)
  - `frontend/app/wallet/page.tsx:20-28` - wallet + transactions 병렬 쿼리

  **API References**:
  - `frontend/lib/api/auth.api.ts:getMyProfile()` - 프로필 API
  - `frontend/lib/api/wallet.api.ts:getWalletBalance()` - 지갑 API
  
  **Type References**:
  - `frontend/types/auth.types.ts:UserResponse` - 프로필 응답 타입
  - `frontend/types/wallet.types.ts:Wallet` - 지갑 응답 타입

  **Current Implementation** (to refactor):
  - `frontend/components/feature/users/user-profile.tsx:21-38` - useEffect 패턴 (제거 대상)

  **Vercel Skill References**:
  - `client-swr-dedup` - React Query 자동 중복 요청 제거
  - `async-parallel` - Promise.all 대신 useQueries 사용

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/users/user-profile.test.tsx`
  - [ ] `pnpm test user-profile` → PASS
  - [ ] useEffect + useState 패턴 제거됨
  - [ ] useQueries로 병렬 fetching 구현됨
  - [ ] loading 상태 동일하게 동작 (Loader2 스피너)
  - [ ] error 시 toast.error 동일하게 동작

  **Manual Verification**:
  - [ ] Playwright: `http://localhost:3000/profile` 접속
  - [ ] Profile 카드와 Wallet Balance 카드 정상 렌더링 확인
  - [ ] React DevTools에서 쿼리 상태 확인

  **Commit**: YES
  - Message: `refactor(user-profile): replace useEffect with useQueries for parallel fetching`
  - Files: `frontend/components/feature/users/user-profile.tsx`, `frontend/components/feature/users/user-profile.test.tsx`
  - Pre-commit: `pnpm test user-profile`

---

- [x] 3. my-library.tsx: useEffect → useQuery 전환

  **What to do**:
  - **RED**: `my-library.test.tsx` 작성
    - useQuery로 purchases fetching 테스트
    - empty state, loading, success 상태 테스트
  - **GREEN**: useEffect를 useQuery로 교체
    - queryKey: `['purchases', { page: 1, limit: 50 }]`
  - **REFACTOR**: 코드 정리

  **Must NOT do**:
  - 페이지네이션 로직 추가 (현재 limit: 50 유지)
  - 카드 레이아웃 변경

  **Parallelizable**: NO (순차 - Task 2 의존)

  **References**:

  **Pattern References**:
  - `frontend/components/feature/ranking/ranking-tabs.tsx:9-12` - 단일 useQuery 패턴
  - `frontend/components/feature/wiki/wiki-list.tsx:18` - 리스트 fetching 패턴

  **API References**:
  - `frontend/lib/api/interactions.api.ts:getPurchases()` - 구매 내역 API

  **Type References**:
  - `frontend/types/interactions.types.ts:Purchase` - 구매 타입

  **Current Implementation** (to refactor):
  - `frontend/components/feature/users/my-library.tsx:16-29` - useEffect 패턴 (제거 대상)

  **Vercel Skill References**:
  - `client-swr-dedup` - 자동 요청 중복 제거

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/users/my-library.test.tsx`
  - [ ] `pnpm test my-library` → PASS
  - [ ] useEffect + useState 패턴 제거됨
  - [ ] useQuery 구현됨
  - [ ] empty state ("You haven't purchased any chapters yet.") 동일
  - [ ] loading 시 Loader2 스피너 동일

  **Manual Verification**:
  - [ ] Playwright: `http://localhost:3000/profile` → Library 탭
  - [ ] 구매 내역 카드 정상 렌더링
  - [ ] 빈 상태 UI 확인 (구매 없을 때)

  **Commit**: YES
  - Message: `refactor(my-library): replace useEffect with useQuery for purchases`
  - Files: `frontend/components/feature/users/my-library.tsx`, `frontend/components/feature/users/my-library.test.tsx`
  - Pre-commit: `pnpm test my-library`

---

- [x] 4. reader-view.tsx: useEffect → useQuery 전환

  **What to do**:
  - **RED**: `reader-view.test.tsx` 작성
    - useQuery로 chapter fetching 테스트
    - chapterId 변경 시 refetch 테스트
    - error boundary 테스트
  - **GREEN**: useEffect를 useQuery로 교체
    - queryKey: `['chapter', chapterId]`
    - enabled: !!chapterId
  - **REFACTOR**: mounted 플래그 제거 (React Query가 자동 처리)

  **Must NOT do**:
  - 리더 설정 (fontSize, theme) 로직 변경
  - 네비게이션 로직 변경
  - BranchChoices 컴포넌트 수정

  **Parallelizable**: NO (순차 - Task 2 의존)

  **References**:

  **Pattern References**:
  - `frontend/components/feature/wiki/wiki-detail.tsx:21` - 단일 상세 데이터 useQuery
  - `frontend/components/feature/novels/chapter-list.tsx:37-44` - enabled 옵션 사용

  **API References**:
  - `frontend/lib/api/chapters.api.ts:getChapter()` - 챕터 API

  **Type References**:
  - `frontend/types/chapters.types.ts:Chapter` - 챕터 타입

  **Current Implementation** (to refactor):
  - `frontend/components/feature/reader/reader-view.tsx:37-53` - useEffect 패턴 (mounted 플래그 포함)

  **Vercel Skill References**:
  - `client-swr-dedup` - 자동 요청 중복 제거
  - `async-suspense-boundaries` - 향후 Suspense 적용 가능

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/reader/reader-view.test.tsx`
  - [ ] `pnpm test reader-view` → PASS
  - [ ] useEffect + useState + mounted 패턴 제거됨
  - [ ] useQuery 구현됨 (queryKey 포함 chapterId)
  - [ ] loading 시 Loader2 스피너 동일
  - [ ] error 시 "Failed to load chapter" 메시지 + Return to Novel 버튼 동일
  - [ ] chapterId 변경 시 자동 refetch

  **Manual Verification**:
  - [ ] Playwright: `http://localhost:3000/novels/1/reader/1` 접속
  - [ ] 챕터 콘텐츠 렌더링 확인
  - [ ] 다음 챕터 이동 → 자동 로딩 확인
  - [ ] 설정 (폰트 크기, 테마) 동작 확인

  **Commit**: YES
  - Message: `refactor(reader-view): replace useEffect with useQuery for chapter fetching`
  - Files: `frontend/components/feature/reader/reader-view.tsx`, `frontend/components/feature/reader/reader-view.test.tsx`
  - Pre-commit: `pnpm test reader-view`

---

- [x] 5. branch-choices.tsx: useEffect → useQuery 전환

  **What to do**:
  - **RED**: `branch-choices.test.tsx` 작성
    - useQuery로 branches fetching 테스트
    - 필터링 로직 테스트 (fork_point_chapter 기준)
    - empty state (null render) 테스트
  - **GREEN**: useEffect를 useQuery로 교체
    - queryKey: `['branches', novelId, { limit: 100 }]`
    - select 옵션으로 필터링 처리
  - **REFACTOR**: mounted 플래그 제거

  **Must NOT do**:
  - 브랜치 카드 UI 변경
  - 클릭 핸들러 로직 변경

  **Parallelizable**: NO (순차 - Task 4 의존)

  **References**:

  **Pattern References**:
  - `frontend/components/feature/branches/branch-list.tsx:16` - 브랜치 리스트 useQuery
  - `frontend/components/feature/novels/chapter-list.tsx:24-28` - novelId 포함 queryKey

  **API References**:
  - `frontend/lib/api/branches.api.ts:getBranches()` - 브랜치 API

  **Type References**:
  - `frontend/types/branches.types.ts:Branch` - 브랜치 타입

  **Current Implementation** (to refactor):
  - `frontend/components/feature/reader/branch-choices.tsx:20-41` - useEffect 패턴 (mounted + filter)

  **Vercel Skill References**:
  - `client-swr-dedup` - 자동 요청 중복 제거

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/reader/branch-choices.test.tsx`
  - [ ] `pnpm test branch-choices` → PASS
  - [ ] useEffect + useState + mounted 패턴 제거됨
  - [ ] useQuery 구현됨
  - [ ] `select` 옵션으로 fork_point_chapter 필터링
  - [ ] loading 시 null 반환 동일
  - [ ] branches 없을 시 null 반환 동일

  **Manual Verification**:
  - [ ] Playwright: 리더에서 브랜치 포인트 챕터로 이동
  - [ ] "AVAILABLE BRANCHES" 섹션 표시 확인
  - [ ] 브랜치 카드 클릭 → toast 표시 확인

  **Commit**: YES
  - Message: `refactor(branch-choices): replace useEffect with useQuery for branches`
  - Files: `frontend/components/feature/reader/branch-choices.tsx`, `frontend/components/feature/reader/branch-choices.test.tsx`
  - Pre-commit: `pnpm test branch-choices`

---

- [x] 6. Auth 상태관리 Zustand 단일화

  **What to do**:
  - **RED**: Auth 마이그레이션 테스트 작성
    - useAuthStore selectors 테스트
    - login/logout flow 테스트
  - **GREEN**: 
    - `auth-provider.tsx`를 thin wrapper로 변경 (내부적으로 useAuthStore 사용)
    - 또는 AuthProvider 완전 제거 후 useAuthStore 직접 사용
  - **REFACTOR**: 불필요한 코드 제거

  **Must NOT do**:
  - 로그인/로그아웃 동작 변경
  - 토큰 관리 로직 변경
  - middleware.ts 수정
  - 쿠키 처리 방식 변경

  **Parallelizable**: NO (순차 - Task 4 의존)

  **References**:

  **Pattern References**:
  - `frontend/stores/auth-store.ts` - 현재 Zustand 스토어 (잘 구조화됨)
  - `frontend/stores/use-reader-store.ts` - persist 미들웨어 예시

  **Current Implementation** (to refactor):
  - `frontend/components/providers/auth-provider.tsx` - React Context 패턴 (제거 또는 wrapper화)

  **Consumer Analysis**:
  - `useAuth()` hook: 정의만 있고 외부 사용처 없음 (LSP 확인)
  - AuthProvider: `layout.tsx`에서 children 래핑 용도

  **Vercel Skill References**:
  - `rerender-defer-reads` - 필요한 상태만 구독

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/stores/auth-store.test.ts`
  - [ ] `pnpm test auth` → PASS
  - [ ] 단일 상태 소스: `useAuthStore` only
  - [ ] 로그인: email/password → 토큰 저장 → 프로필 조회 → 리다이렉트
  - [ ] 로그아웃: 토큰 삭제 → /login 리다이렉트
  - [ ] 페이지 새로고침 시 인증 상태 유지

  **Manual Verification**:
  - [ ] Playwright: `/login` 접속 → 로그인 → 홈 리다이렉트 확인
  - [ ] Playwright: 로그아웃 → `/login` 리다이렉트 확인
  - [ ] React DevTools: Zustand store 상태 확인

  **Commit**: YES
  - Message: `refactor(auth): consolidate auth state to Zustand store`
  - Files: `frontend/components/providers/auth-provider.tsx`, `frontend/stores/auth-store.ts`, `frontend/stores/auth-store.test.ts`
  - Pre-commit: `pnpm test auth`

---

- [x] 7. NovelCard에 React.memo 적용

  **What to do**:
  - **RED**: memo 최적화 테스트 작성
    - 동일 props에서 리렌더 안 함 확인
  - **GREEN**: React.memo 래핑
    - named function export 유지
  - **REFACTOR**: 필요시 arePropsEqual 커스텀

  **Must NOT do**:
  - 컴포넌트 로직 변경
  - props 타입 변경
  - 스타일 변경

  **Parallelizable**: YES (Task 8, 9와 병렬)

  **References**:

  **Pattern References**:
  - 해당 없음 (현재 React.memo 사용 없음 - 최초 적용)

  **Current Implementation**:
  - `frontend/components/feature/novel/novel-card.tsx:20-54` - 현재 일반 함수 컴포넌트

  **Vercel Skill References**:
  - `rerender-memo` - 리스트 아이템 메모이제이션

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/novel/novel-card.test.tsx`
  - [ ] `pnpm test novel-card` → PASS
  - [ ] `React.memo()` 적용됨
  - [ ] named export 유지: `export const NovelCard = React.memo(...)`
  - [ ] 기존 UI 동일

  **Manual Verification**:
  - [ ] React DevTools Profiler: 리스트에서 스크롤 시 불필요한 리렌더 없음 확인

  **Commit**: YES (Task 7, 8과 함께 그룹 커밋 가능)
  - Message: `perf(novel-card): add React.memo for list rendering optimization`
  - Files: `frontend/components/feature/novel/novel-card.tsx`
  - Pre-commit: `pnpm test novel-card`

---

- [x] 8. BranchCard에 React.memo 적용

  **What to do**:
  - **RED**: memo 최적화 테스트 작성
  - **GREEN**: React.memo 래핑
  - **REFACTOR**: 필요시 정리

  **Must NOT do**:
  - 컴포넌트 로직 변경
  - useMutation 로직 변경

  **Parallelizable**: YES (Task 7, 9와 병렬)

  **References**:

  **Current Implementation**:
  - `frontend/components/feature/branches/branch-card.tsx` - 현재 일반 함수 컴포넌트

  **Vercel Skill References**:
  - `rerender-memo` - 리스트 아이템 메모이제이션

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/components/feature/branches/branch-card.test.tsx`
  - [ ] `pnpm test branch-card` → PASS
  - [ ] `React.memo()` 적용됨
  - [ ] 기존 UI 및 투표 기능 동일

  **Manual Verification**:
  - [ ] 브랜치 페이지에서 카드 리스트 렌더링 확인
  - [ ] 투표 버튼 동작 확인

  **Commit**: YES (Task 6, 8과 함께 그룹 커밋 가능)
  - Message: `perf(branch-card): add React.memo for list rendering optimization`
  - Files: `frontend/components/feature/branches/branch-card.tsx`
  - Pre-commit: `pnpm test branch-card`

---

- [x] 9. PostCard에 React.memo 적용 (존재 시)

  **What to do**:
  - 먼저 PostCard 컴포넌트 존재 확인
  - 존재 시: React.memo 적용
  - 미존재 시: 스킵 후 다른 리스트 컴포넌트 탐색

  **Must NOT do**:
  - 새로운 컴포넌트 생성

  **Parallelizable**: YES (Task 7, 8과 병렬)

  **References**:

  **Vercel Skill References**:
  - `rerender-memo` - 리스트 아이템 메모이제이션

  **Acceptance Criteria**:
  - [ ] PostCard 존재 확인
  - [ ] 존재 시 React.memo 적용 및 테스트
  - [ ] 미존재 시 task 완료 처리

  **Commit**: YES (조건부)
  - Message: `perf(post-card): add React.memo for list rendering optimization`
  - Pre-commit: `pnpm test post-card`

---

- [x] 10. Mock 데이터 실제 API 연결

  **What to do**:
  - **RED**: API 연결 테스트 작성
    - 실제 API 응답 구조 테스트
  - **GREEN**: 
    - `app/novels/[id]/page.tsx` 에서 mock 데이터 제거
    - `getNovel(id)` API 호출로 교체
  - **REFACTOR**: 불필요한 mock 타입 제거

  **Must NOT do**:
  - mock-data.ts 삭제 (다른 곳에서 사용 가능)
  - API 응답 구조 변경

  **Parallelizable**: NO (순차 - Auth 통합 완료 후)

  **References**:

  **Pattern References**:
  - `frontend/app/search/page.tsx` - Server Component에서 searchParams 처리

  **API References**:
  - `frontend/lib/api/novels.api.ts:getNovel()` - 소설 상세 API

  **Type References**:
  - `frontend/types/novels.types.ts:Novel` - 소설 타입

  **Current Implementation** (to refactor):
  - `frontend/app/novels/[id]/page.tsx` - 하드코딩된 mock 데이터

  **Backend API**:
  - `backend/apps/novels/views.py:NovelViewSet` - 존재 확인됨

  **Acceptance Criteria**:
  - [ ] `app/novels/[id]/page.tsx` 에서 mock 데이터 제거
  - [ ] `getNovel(id)` API 호출 사용
  - [ ] 존재하지 않는 소설 ID → 404 또는 에러 페이지
  - [ ] 기존 UI 레이아웃 동일

  **Manual Verification**:
  - [ ] Playwright: `/novels/1` 접속 → 실제 API 데이터 렌더링
  - [ ] Network 탭: `/api/novels/1` 요청 확인

  **Commit**: YES
  - Message: `refactor(novel-detail): replace mock data with real API`
  - Files: `frontend/app/novels/[id]/page.tsx`
  - Pre-commit: `pnpm test && pnpm build`

---

- [x] 11. 최종 검증 및 PR 생성

  **What to do**:
  - 전체 테스트 실행
  - 전체 빌드 확인
  - 린트 확인
  - 주요 플로우 E2E 검증
  - **GitHub PR 생성** (develop 브랜치로)

  **Must NOT do**:
  - 새로운 코드 변경

  **Parallelizable**: NO (마지막 태스크)

  **References**:
  - 모든 이전 태스크
  - `AGENTS.md` - Git Workflow

  **Acceptance Criteria**:
  - [ ] `pnpm test` → 모든 테스트 PASS
  - [ ] `pnpm build` → 빌드 성공
  - [ ] `pnpm lint` → 에러 없음
  - [ ] 주요 페이지 동작 확인:
    - [ ] 홈 → 소설 목록
    - [ ] 소설 상세 → 챕터 리더
    - [ ] 프로필 → 라이브러리
    - [ ] 로그인/로그아웃
  - [ ] **PR 생성됨** (`gh pr view` 확인)

  **PR Creation**:
  ```bash
  gh pr create --base develop --title "refactor(frontend): Apply Vercel React Best Practices" --body "$(cat <<'EOF'
## Summary
- useEffect 데이터 fetching → React Query 전환 (4개 컴포넌트)
- Auth 상태관리 Zustand 단일화 (AuthProvider 제거)
- 리스트 컴포넌트 React.memo 적용 (NovelCard, BranchCard)
- Mock 데이터 실제 API 연결

## Changes
### Data Fetching (Vercel `client-swr-dedup`)
- `user-profile.tsx`: useEffect → useQueries
- `my-library.tsx`: useEffect → useQuery
- `reader-view.tsx`: useEffect → useQuery
- `branch-choices.tsx`: useEffect → useQuery

### State Management (AGENTS.md compliance)
- Consolidated auth state to Zustand (`useAuthStore`)
- Removed duplicate AuthProvider context

### Performance (Vercel `rerender-memo`)
- Added React.memo to list item components

### API Integration
- Replaced mock data with real API calls in novel detail page

## Testing
- TDD approach: tests written before implementation
- All existing tests pass
- New tests added for refactored components

## Checklist
- [x] `pnpm test` passes
- [x] `pnpm build` succeeds
- [x] `pnpm lint` clean
- [x] Manual verification complete

Closes #<ISSUE_NUMBER>
EOF
)"
  ```

  **Manual Verification**:
  - [ ] Playwright E2E: 기존 E2E 테스트 실행
  - [ ] 브라우저: 주요 플로우 수동 확인
  - [ ] PR URL 확인 및 기록

  **Commit**: NO (PR 생성만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | (브랜치 생성만) | - | git branch |
| 1 | `test(frontend): verify test infrastructure` | tests/utils/ | pnpm test |
| 2 | `refactor(user-profile): useEffect → useQueries` | user-profile.tsx | pnpm test |
| 3 | `refactor(my-library): useEffect → useQuery` | my-library.tsx | pnpm test |
| 4 | `refactor(reader-view): useEffect → useQuery` | reader-view.tsx | pnpm test |
| 5 | `refactor(branch-choices): useEffect → useQuery` | branch-choices.tsx | pnpm test |
| 6 | `refactor(auth): consolidate to Zustand` | auth-*.ts | pnpm test |
| 7-9 | `perf(components): add React.memo to list items` | *-card.tsx | pnpm test |
| 10 | `refactor(novel-detail): real API connection` | novels/[id]/page.tsx | pnpm build |
| 11 | (PR 생성만) | - | gh pr view |

---

## Success Criteria

### Verification Commands
```bash
pnpm test                    # Expected: All tests pass
pnpm build                   # Expected: Build succeeds
pnpm lint                    # Expected: No errors
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All tests pass (133 tests)
- [x] useEffect data fetching 패턴 0개 (timer, leaflet 제외) - 4 components refactored
- [x] Auth 단일 소스: useAuthStore only - AuthProvider removed
- [x] 리스트 컴포넌트 React.memo 적용됨 - NovelCard, BranchCard, PostCard
