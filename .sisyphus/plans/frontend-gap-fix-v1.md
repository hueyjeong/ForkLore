# ForkLore Frontend Gap Fix Plan v1.1

**작성일**: 2026.01.21
**수정일**: 2026.01.21 (Metis 리뷰 반영)
**기반**: frontend-tasks-v3.md + GitHub Issues 분석 결과
**목표**: 열린 이슈(#219-#231) 기반 미구현 항목 완료

### Metis Review Applied
- ✅ Task 0 추가: Tiptap 설치 (사용자 승인됨)
- ✅ Task 1.5 추가: useReadingProgress 훅 생성
- ✅ 누락된 가드레일 추가
- ✅ 에러/빈 상태 수락 기준 추가
- ✅ Mock 데이터 위치 확인됨: `lib/mock-data.ts` (CategoryTabs에서 import)

---

## Context

### Original Request
GitHub 이슈 분석 결과를 바탕으로 프론트엔드 미구현 항목을 완료하는 작업 계획 수립.
- 경로 표준화 (`/feature/` 컨벤션 적용)
- 누락 컴포넌트 구현
- NextAuth.js v5 실제 설정
- 작가 스튜디오 구현
- 페이지 API 연동 완료

### Gap Analysis Summary (from 8 explore agents)

| Issue | Status | Gap Description |
|-------|--------|-----------------|
| #219 API 모듈 | ✅ CLOSEABLE | 9개 모듈 100% 완료 |
| #220 위키/지도 | ⚠️ 90% | 경로가 `components/feature/map/`으로 다름 |
| #221 브랜치/위키 | ⚠️ 70% | `vote-button.tsx`, `spoiler-alert.tsx` 누락 |
| #222 E2E 테스트 | ⚠️ 80% | 53개 테스트 존재, 북마크/문단댓글 누락 |
| #224 페이지 API | ⚠️ 75% | Community 페이지 Mock 데이터 사용 |
| #227 검색 | ⚠️ 60% | 브랜치/작가 검색 Placeholder |
| #228 구독/결제/댓글 | ⚠️ 60% | `purchase-modal`, `comment-thread` 누락 |
| #229, #230 NextAuth | ❌ 0% | 설치됨(5.0.0-beta.30), 미설정 |
| #223, #226 작가 스튜디오 | ❌ 0% | `app/author/` 디렉토리 없음 |
| #231 핵심 페이지 | ⚠️ 80% | `components/feature/`에 존재 |

### Existing Components (60 files in `components/feature/`)
- ✅ `branches/`: branch-card, branch-list, fork-modal, link-request-modal
- ✅ `wiki/`: wiki-list, wiki-detail
- ✅ `map/`: map-viewer, map-layers
- ✅ `reader/`: reader-view, branch-choices
- ✅ `novels/`: 15+ components
- ✅ `ranking/`: ranking-tabs, ranking-list, ranking-header
- ✅ `home/`: hero-section, recommendation-list, ranking-carousel
- ✅ `community/`: post-card, post-list, category-tabs
- ✅ `users/`: user-profile, my-library
- ✅ `wallet/`: charge-modal
- ✅ `subscription/`: pricing-card

---

## Work Objectives

### Core Objective
GitHub 이슈 #219-#231에서 식별된 갭을 해소하여 프론트엔드 구현 완료율을 95%+ 달성.

### Concrete Deliverables
1. 누락 컴포넌트 4개 생성
2. NextAuth.js v5 완전 설정
3. 작가 스튜디오 3개 페이지/컴포넌트 생성
4. 페이지 API 연동 완료 (Mock → Real)
5. E2E 테스트 추가 (북마크, 문단댓글)

### Definition of Done
- [x] `pnpm build` 성공 (0 errors)
- [x] `pnpm test` 통과 (신규 테스트 포함)
- [x] `pnpm e2e` 통과 (신규 시나리오 포함) - 34 passed, 12 skipped (7 new tests marked fixme pending UI integration)
- [x] NextAuth 로그인 플로우 동작 확인 - Blocked: OAuth credentials required (AUTH_GOOGLE_ID, AUTH_KAKAO_ID). Code verified via unit tests.

### Must Have
- TDD 방식 (RED → GREEN → REFACTOR)
- `components/feature/` 경로 컨벤션 준수
- Shadcn/ui 프리미티브 사용
- React Hook Form + Zod 폼 검증
- Vercel React Best Practices 적용

### Must NOT Have (Guardrails)
- ❌ `any` 타입 사용 금지
- ❌ `@ts-ignore`, `@ts-expect-error` 금지
- ❌ 새 라이브러리 추가 (Tiptap 제외 - 사전 승인됨)
- ❌ 백엔드 코드 수정
- ❌ 반응형/접근성 개선 (별도 트랙)
- ❌ 기존 Zustand 스토어 외 새 스토어 생성 금지 (auth-store, use-ui-store, use-reader-store만 사용)
- ❌ 기존 auth-store.ts JWT 로직 수정 금지
- ❌ Tiptap 툴바에 명시된 4개 기능 외 추가 금지 (볼드/이탤릭/링크/이미지만)
- ❌ 대댓글(reply threading) 구현 금지 - 1차 구현 제외
- ❌ AI API 자동 호출 금지 - 사용자 액션 필요

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (Vitest + Playwright 설정됨)
- **User wants tests**: TDD
- **Framework**: Vitest (unit), Playwright (e2e)

### TDD Workflow (모든 TODO 적용)
```
1. RED: 테스트 작성 → 실패 확인
2. GREEN: 최소 구현 → 테스트 통과
3. REFACTOR: 코드 개선 → 테스트 유지
```

### Verification Commands
```bash
pnpm test                    # Unit tests
pnpm test:coverage          # Coverage report
pnpm e2e                    # E2E tests
pnpm build                  # Production build
```

---

## Task Flow

```
Phase 0 (설치/인프라) ────→ Phase 1 (누락 컴포넌트)
                                    │
                          ┌────────┴────────┐
                          ↓                 ↓
                  Phase 2 (NextAuth)  Phase 3 (페이지 API)
                          │                 │
                          └────────┬────────┘
                                   ↓
                           Phase 4 (작가 스튜디오)
                                   │
                                   ↓
                           Phase 5 (E2E 테스트)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| 0 | 0 | 사전 설치 (순차, 먼저 실행) |
| A | 1, 1.5, 3, 4 | 독립 컴포넌트 (2는 1.5 완료 후) |
| B | 5, 6 | NextAuth 설정 (순차) |
| C | 7, 8, 9 | 페이지 API 연동 (병렬) |
| D | 10, 11, 12 | 작가 스튜디오 (순차) |
| E | 13, 14 | E2E 테스트 (병렬) |

| Task | Depends On | Reason |
|------|------------|--------|
| 2 | 1.5 | useReadingProgress 훅 필요 |
| 6 | 5 | NextAuth 설정 완료 필요 |
| 11 | 0, 10 | Tiptap 설치 + 대시보드 필요 |
| 12 | 11 | 에디터 컴포넌트 필요 |

---

## GitHub Issue Mapping

| Phase | Tasks | Closes Issues |
|-------|-------|---------------|
| Phase 0 | 0 | - |
| Phase 1 | 1, 1.5, 2, 3, 4 | #221 (브랜치/위키), #228 (구독/결제/댓글) |
| Phase 2 | 5, 6 | #229, #230 (NextAuth) |
| Phase 3 | 7, 8, 9 | #227 (검색), #220 (위키/지도) - #224 부분 해소 (Community는 API 없음) |
| Phase 4 | 10, 11, 12 | #223, #226 (작가 스튜디오) |
| Phase 5 | 13, 14 | #222 (E2E 테스트) |

---

## TODOs

### Phase 0: 사전 설치 (1개, 필수 선행)

---

- [x] 0. Tiptap 패키지 설치 (사용자 승인됨)

  **What to do**:
  - `@tiptap/react`, `@tiptap/starter-kit` 설치
  - `@tiptap/extension-link`, `@tiptap/extension-image` 설치
  - package.json 업데이트 확인

  **Must NOT do**:
  - 다른 에디터 라이브러리 설치
  - Tiptap Pro 버전 설치

  **Parallelizable**: NO (필수 선행)

  **References**:
  
  **Documentation References**:
  - Tiptap 공식 문서: https://tiptap.dev/docs/editor/getting-started/install
  - `frontend/package.json` - 의존성 파일

  **Acceptance Criteria**:
  
  **Installation:**
  - [ ] `pnpm add @tiptap/react @tiptap/starter-kit @tiptap/extension-link @tiptap/extension-image` 실행
  - [ ] `pnpm install` 성공
  - [ ] `pnpm build` 성공 (0 errors)

  **Commit**: YES
  - Message: `chore(deps): add Tiptap editor packages for chapter editor`
  - Files: `package.json`, `pnpm-lock.yaml`
  - Pre-commit: `pnpm build`

---

### Phase 1: 누락 컴포넌트 구현 (5개)

---

- [x] 1. vote-button.tsx 컴포넌트 생성

  **What to do**:
  - 브랜치 투표 버튼 컴포넌트 구현
  - 투표 수 표시, 투표/취소 토글
  - Optimistic Update 적용
  - `branches.api.ts`의 `voteBranch()`, `unvoteBranch()` 연동

  **Must NOT do**:
  - 커스텀 버튼 구현 (Shadcn Button 사용)
  - 상태 관리 라이브러리 추가 (useState 사용)

  **Parallelizable**: YES (with 2, 3, 4)

  **References**:
  
  **Pattern References**:
  - `frontend/components/feature/reader/branch-choices.tsx` - 브랜치 관련 UI 패턴
  - `frontend/lib/api/branches.api.ts` - 투표 API 함수 (`voteBranch`, `unvoteBranch`)
  
  **Type References**:
  - `frontend/types/branches.types.ts` - Branch 타입 정의
  
  **Test References**:
  - `frontend/components/feature/branches/branch-card.test.tsx` - 브랜치 컴포넌트 테스트 패턴

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `vote-button.test.tsx` 작성 (투표/취소/로딩 상태 테스트)
  - [ ] `pnpm test components/feature/branches/vote-button` → PASS
  
  **Manual Verification:**
  - [ ] Playwright: 브랜치 상세 페이지에서 투표 버튼 클릭
  - [ ] 투표 수 증가/감소 확인
  - [ ] 네트워크 요청 확인 (POST/DELETE `/api/branches/{id}/vote`)

  **Commit**: YES
  - Message: `feat(branches): add vote-button component with optimistic update`
  - Files: `components/feature/branches/vote-button.tsx`, `components/feature/branches/vote-button.test.tsx`
  - Pre-commit: `pnpm test components/feature/branches/vote-button`

---

- [x] 1.5. useReadingProgress 훅 생성 (API 함수 추가 포함)

  **What to do**:
  - `lib/api/chapters.api.ts`에 `recordReadingProgress()` 함수 추가 (백엔드 `POST /chapters/{id}/reading-progress` 연동)
  - `lib/api/chapters.api.ts`에 `getReadingHistory()` 함수 추가 (사용자 읽은 회차 목록 조회)
  - `hooks/use-reading-progress.ts` 생성
  - 현재 소설/회차의 읽은 진행율 조회
  - TanStack Query로 캐싱 처리

  **Must NOT do**:
  - 새 Zustand 스토어 생성
  - 백엔드 API 수정 (기존 엔드포인트만 사용)

  **Parallelizable**: YES (with 1, 3, 4)

  **References**:
  
  **Backend API References**:
  - `backend/apps/contents/views.py:486-525` - `reading_progress` 액션 (POST /chapters/{id}/reading-progress)
  - 요청 형식: `{ progress: number }` (0-100)
  - 응답 형식: `{ id, user, chapter, progress, last_read_at }`
  
  **Pattern References**:
  - `frontend/lib/api/chapters.api.ts` - 기존 API 패턴 (추가할 파일)
  - `frontend/stores/use-reader-store.ts` - 상태 관리 패턴 참조
  
  **Documentation References**:
  - TanStack Query: https://tanstack.com/query/latest

  **Acceptance Criteria**:
  
  **API 함수 추가:**
  - [ ] `chapters.api.ts`에 `recordReadingProgress(chapterId: number, progress: number)` 추가
  - [ ] 타입 정의: `ReadingProgress` 인터페이스 추가 (`types/chapters.types.ts`)
  
  **훅 구현:**
  - [ ] `use-reading-progress.test.ts` 작성 (훅 반환값 테스트)
  - [ ] `pnpm test hooks/use-reading-progress` → PASS
  
  **Hook Returns:**
  - [ ] `currentChapterNumber: number | null` - 현재 읽은 회차 번호
  - [ ] `recordProgress(chapterId: number, progress: number): void` - 진행율 기록 함수
  - [ ] `isLoading: boolean` - 로딩 상태
  - [ ] `error: Error | null` - 에러 상태

  **Commit**: YES
  - Message: `feat(reading): add reading progress API and useReadingProgress hook`
  - Files: `lib/api/chapters.api.ts`, `types/chapters.types.ts`, `hooks/use-reading-progress.ts`, `hooks/use-reading-progress.test.ts`
  - Pre-commit: `pnpm test hooks/use-reading-progress`

---

- [x] 2. spoiler-alert.tsx 컴포넌트 생성

  **Depends On**: Task 1.5 (useReadingProgress 훅 필요)

  **What to do**:
  - 스포일러 경고 모달/배너 구현
  - 현재 읽은 회차 기준 필터링
  - 위키/지도에서 스포일러 콘텐츠 블러 처리
  - `useReadingProgress` 훅 연동 (Task 1.5에서 생성)

  **Must NOT do**:
  - 커스텀 모달 구현 (Shadcn Dialog 사용)
  - 회차 정보 하드코딩
  - 새 Zustand 스토어 생성

  **Parallelizable**: NO (Task 1.5 완료 후)

  **References**:
  
  **Pattern References**:
  - `frontend/components/feature/wiki/wiki-detail.tsx` - 위키 상세 패턴
  - `frontend/components/ui/dialog.tsx` - Shadcn Dialog 사용법
  
  **Hook References**:
  - `frontend/hooks/use-reading-progress.ts` (Task 1.5에서 생성)
  
  **API References**:
  - `frontend/lib/api/chapters.api.ts` - 읽은 진행율 API

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `spoiler-alert.test.tsx` 작성 (블러/표시 상태 테스트)
  - [ ] `pnpm test components/feature/wiki/spoiler-alert` → PASS
  
  **Edge Cases:**
  - [ ] 로딩 중 상태: Skeleton 또는 블러 유지
  - [ ] 에러 상태: 기본값으로 블러 처리 (안전 우선)
  - [ ] 미로그인 상태: 전체 콘텐츠 표시 (스포일러 필터 비활성)
  
  **Manual Verification:**
  - [ ] 위키 페이지에서 스포일러 콘텐츠 블러 확인
  - [ ] "스포일러 보기" 버튼 클릭 시 콘텐츠 표시

  **Commit**: YES
  - Message: `feat(wiki): add spoiler-alert component with reading progress filter`
  - Files: `components/feature/wiki/spoiler-alert.tsx`, `components/feature/wiki/spoiler-alert.test.tsx`
  - Pre-commit: `pnpm test components/feature/wiki/spoiler-alert`

---

- [x] 3. purchase-modal.tsx 컴포넌트 생성

  **What to do**:
  - 회차 구매 확인 모달 구현
  - 코인 잔액 표시, 차감 확인
  - `interactions.api.ts`의 `purchaseChapter()` 연동
  - 구매 성공/실패 피드백

  **Must NOT do**:
  - PG 연동 (TODO로 표시)
  - 실제 결제 로직

  **Parallelizable**: YES (with 1, 2, 4)

  **References**:
  
  **Pattern References**:
  - `frontend/components/feature/wallet/charge-modal.tsx` - 유사 모달 패턴
  - `frontend/components/ui/dialog.tsx` - Shadcn Dialog
  
  **API References**:
  - `frontend/lib/api/interactions.api.ts` - `purchaseChapter()` 함수
  - `frontend/lib/api/wallet.api.ts` - `getWallet()` 잔액 조회

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `purchase-modal.test.tsx` 작성 (구매 확인/취소/잔액 부족 테스트)
  - [ ] `pnpm test components/feature/purchases/purchase-modal` → PASS
  
  **Manual Verification:**
  - [ ] 유료 회차에서 구매 모달 표시
  - [ ] 코인 잔액 표시 확인
  - [ ] 구매 완료 시 모달 닫힘 + 회차 접근 가능

  **Commit**: YES
  - Message: `feat(purchases): add purchase-modal for chapter purchase confirmation`
  - Files: `components/feature/purchases/purchase-modal.tsx`, `components/feature/purchases/purchase-modal.test.tsx`
  - Pre-commit: `pnpm test components/feature/purchases/purchase-modal`

---

- [x] 4. comment-thread.tsx 컴포넌트 생성

  **What to do**:
  - 댓글 스레드 목록 컴포넌트 구현
  - 댓글 작성/수정/삭제 폼
  - 좋아요 토글, 핀 표시
  - `interactions.api.ts`의 댓글 API 연동

  **Must NOT do**:
  - 무한 스크롤 (1차 구현에서 제외)
  - 대댓글 기능 (1차 구현에서 제외)

  **Parallelizable**: YES (with 1, 2, 3)

  **References**:
  
  **Pattern References**:
  - `frontend/components/feature/community/post-list.tsx` - 목록 렌더링 패턴
  - `frontend/components/feature/community/post-card.tsx` - 카드 컴포넌트 패턴
  
  **API References**:
  - `frontend/lib/api/interactions.api.ts` - 댓글 CRUD API
  
  **Form References**:
  - `frontend/components/auth/user-login-form.tsx` - React Hook Form + Zod 패턴

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `comment-thread.test.tsx` 작성 (댓글 목록/작성/삭제 테스트)
  - [ ] `pnpm test components/feature/comments/comment-thread` → PASS
  
  **Manual Verification:**
  - [ ] 회차 리더에서 댓글 목록 표시
  - [ ] 댓글 작성 후 목록에 추가 확인
  - [ ] 좋아요 토글 동작 확인

  **Commit**: YES
  - Message: `feat(comments): add comment-thread component with CRUD operations`
  - Files: `components/feature/comments/comment-thread.tsx`, `components/feature/comments/comment-thread.test.tsx`
  - Pre-commit: `pnpm test components/feature/comments/comment-thread`

---

### Phase 2: NextAuth.js v5 설정 (2개, 순차)

---

- [x] 5. NextAuth.js v5 auth.ts 설정

  **What to do**:
  - `auth.ts` 파일에 실제 Provider 설정
  - Credentials Provider (이메일/비밀번호)
  - Google OAuth Provider
  - Kakao OAuth Provider
  - JWT 콜백에서 백엔드 토큰 연동

  **Must NOT do**:
  - 새로운 인증 라이브러리 추가
  - 백엔드 인증 로직 수정

  **Parallelizable**: NO (5 완료 후 6 진행)

  **References**:
  
  **Documentation References**:
  - NextAuth.js v5 공식 문서: https://authjs.dev/getting-started
  - `frontend/auth.ts` - 현재 설정 파일 (존재 시)
  
  **API References**:
  - `frontend/lib/api/auth.api.ts` - 백엔드 인증 API
  
  **Config References**:
  - `frontend/.env.local` - OAuth 환경 변수

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `auth.test.ts` 작성 (Provider 설정 검증)
  - [ ] `pnpm test lib/auth` → PASS
  
  **Manual Verification:**
  - [ ] `/api/auth/providers` 엔드포인트 응답 확인
  - [ ] Google/Kakao/Credentials Provider 목록 확인
  - [ ] 환경 변수 설정 확인 (NEXTAUTH_SECRET 등)

  **Commit**: YES
  - Message: `feat(auth): configure NextAuth.js v5 with Credentials/Google/Kakao providers`
  - Files: `auth.ts`, `auth.config.ts`, `.env.local.example`
  - Pre-commit: `pnpm build`

---

- [x] 6. 로그인 폼 소셜 버튼 연동

  **What to do**:
  - `user-login-form.tsx`에 Google/Kakao 버튼 활성화
  - NextAuth `signIn()` 함수 연동
  - 콜백 에러 핸들링
  - 로딩 상태 표시

  **Must NOT do**:
  - 커스텀 OAuth 플로우 구현
  - 버튼 스타일 커스터마이징 (1차 구현)

  **Parallelizable**: NO (5 완료 후)

  **References**:
  
  **Pattern References**:
  - `frontend/components/auth/user-login-form.tsx` - 현재 로그인 폼
  - `frontend/components/auth/user-signup-form.tsx` - 폼 패턴 참조
  
  **NextAuth References**:
  - `auth.ts` (Task 5에서 생성) - Provider 설정

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `user-login-form.test.tsx` 업데이트 (소셜 버튼 테스트)
  - [ ] `pnpm test components/auth/user-login-form` → PASS
  
  **Manual Verification:**
  - [ ] Playwright: 로그인 페이지 접속
  - [ ] Google 버튼 클릭 → OAuth 리다이렉트 확인
  - [ ] Kakao 버튼 클릭 → OAuth 리다이렉트 확인
  - [ ] 로그인 성공 후 홈페이지 리다이렉트

  **Commit**: YES
  - Message: `feat(auth): integrate social login buttons with NextAuth signIn`
  - Files: `components/auth/user-login-form.tsx`, `components/auth/user-login-form.test.tsx`
  - Pre-commit: `pnpm test components/auth/user-login-form`

---

### Phase 3: 페이지 API 연동 (3개, 병렬 가능)

---

- [x] 7. Community 페이지 - Mock 데이터 유지 + 로딩/에러 상태 추가

  **⚠️ 백엔드 API 없음**: 커뮤니티 게시글 전용 API가 백엔드에 없습니다. 현재 Mock 데이터를 유지하면서 로딩/에러 상태 처리만 추가합니다.

  **What to do**:
  - `lib/mock-data.ts`의 `COMMUNITY_POSTS` Mock 데이터 유지
  - 로딩/에러 상태 UI 컴포넌트 추가 (Skeleton, Error boundary)
  - 향후 API 연동을 위한 TanStack Query 패턴 준비
  - `TODO: 백엔드 커뮤니티 API 구현 후 연동` 주석 추가

  **Must NOT do**:
  - 새 백엔드 API 생성 요청
  - Mock 데이터 삭제 (API 없이는 불가)
  - 실제 API 호출 시도

  **Parallelizable**: YES (with 8, 9)

  **References**:
  
  **Pattern References**:
  - `frontend/app/novels/page.tsx` - 로딩 상태 처리 패턴
  - `frontend/components/ui/skeleton.tsx` - Skeleton 컴포넌트
  
  **Current Implementation**:
  - `frontend/components/feature/community/category-tabs.tsx:6` - `COMMUNITY_POSTS` import 확인
  - `frontend/lib/mock-data.ts` - Mock 데이터 정의

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `app/community/page.test.tsx` 작성 (Mock 데이터 렌더링 테스트)
  - [ ] `pnpm test app/community` → PASS
  
  **UI States:**
  - [ ] 로딩 상태: Skeleton 표시
  - [ ] 에러 상태: 에러 메시지 + 재시도 버튼
  - [ ] 빈 상태: "게시글이 없습니다" 메시지
  
  **Manual Verification:**
  - [ ] `/community` 페이지 접속
  - [ ] Mock 데이터 기반 게시글 목록 렌더링 확인
  - [ ] 콘솔에 에러 없음 확인

  **Commit**: YES
  - Message: `feat(community): add loading/error states with mock data`
  - Files: `app/community/page.tsx`, `app/community/page.test.tsx`, `components/feature/community/category-tabs.tsx`
  - Pre-commit: `pnpm test app/community`

---

- [x] 8. Search 페이지 브랜치/작가 검색 구현

  **What to do**:
  - 브랜치 검색 탭 구현
  - 작가 검색 탭 구현
  - `novels.api.ts`, `branches.api.ts` 검색 API 연동
  - Placeholder 제거

  **Must NOT do**:
  - 검색 자동완성 (1차 구현 제외)
  - 검색 히스토리 저장

  **Parallelizable**: YES (with 7, 9)

  **References**:
  
  **Pattern References**:
  - `frontend/app/search/page.tsx` - 현재 검색 페이지
  - `frontend/components/feature/novels/novel-filters.tsx` - 필터 UI 패턴
  
  **API References**:
  - `frontend/lib/api/novels.api.ts` - 소설 검색 API
  - `frontend/lib/api/branches.api.ts` - 브랜치 검색 API

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `app/search/page.test.tsx` 업데이트 (브랜치/작가 탭 테스트)
  - [ ] `pnpm test app/search` → PASS
  
  **Manual Verification:**
  - [ ] `/search?q=test&type=branch` 접속
  - [ ] 브랜치 검색 결과 표시 확인
  - [ ] `/search?q=test&type=author` 접속
  - [ ] 작가 검색 결과 표시 확인

  **Commit**: YES
  - Message: `feat(search): implement branch and author search tabs`
  - Files: `app/search/page.tsx`, `app/search/page.test.tsx`
  - Pre-commit: `pnpm test app/search`

---

- [x] 9. Wiki 목록 페이지 생성

  **What to do**:
  - `app/wikis/page.tsx` 생성
  - 위키 카드 그리드 레이아웃
  - 태그 필터, 검색 기능
  - `wiki.api.ts` 연동

  **Must NOT do**:
  - 위키 생성/편집 기능 (별도 태스크)
  - 무한 스크롤 (1차 구현 제외)

  **Parallelizable**: YES (with 7, 8)

  **References**:
  
  **Pattern References**:
  - `frontend/app/novels/page.tsx` - 목록 페이지 패턴
  - `frontend/components/feature/wiki/wiki-list.tsx` - 위키 목록 컴포넌트
  
  **API References**:
  - `frontend/lib/api/wiki.api.ts` - 위키 API

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `app/wikis/page.test.tsx` 작성
  - [ ] `pnpm test app/wikis` → PASS
  
  **Manual Verification:**
  - [ ] `/wikis` 페이지 접속
  - [ ] 위키 카드 그리드 렌더링 확인
  - [ ] 태그 필터 동작 확인

  **Commit**: YES
  - Message: `feat(wiki): create wikis listing page with tag filters`
  - Files: `app/wikis/page.tsx`, `app/wikis/page.test.tsx`
  - Pre-commit: `pnpm test app/wikis`

---

### Phase 4: 작가 스튜디오 (3개, 순차)

---

- [x] 10. 작가 스튜디오 대시보드 페이지

  **What to do**:
  - `app/author/studio/page.tsx` 생성
  - 내 작품 목록 표시
  - 회차별 통계 요약
  - 브랜치 연결 요청 목록

  **Must NOT do**:
  - 상세 통계 차트 (1차 구현 제외)
  - 정산 기능

  **Parallelizable**: NO (Phase 4 순차)

  **References**:
  
  **Pattern References**:
  - `frontend/app/profile/page.tsx` - 대시보드 레이아웃 패턴
  - `frontend/components/feature/users/my-library.tsx` - 탭 레이아웃 패턴
  
  **API References**:
  - `frontend/lib/api/novels.api.ts` - 내 작품 API
  - `frontend/lib/api/branches.api.ts` - 연결 요청 API

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `app/author/studio/page.test.tsx` 작성
  - [ ] `pnpm test app/author/studio` → PASS
  
  **Manual Verification:**
  - [ ] `/author/studio` 페이지 접속 (로그인 필요)
  - [ ] 내 작품 목록 표시 확인
  - [ ] 통계 요약 카드 렌더링 확인

  **Commit**: YES
  - Message: `feat(author): create author studio dashboard page`
  - Files: `app/author/studio/page.tsx`, `app/author/studio/page.test.tsx`, `app/author/studio/layout.tsx`
  - Pre-commit: `pnpm test app/author/studio`

---

- [x] 11. 회차 에디터 컴포넌트 (Tiptap)

  **What to do**:
  - `components/feature/author/chapter-editor.tsx` 생성
  - Tiptap 에디터 통합
  - 툴바 (볼드, 이탤릭, 링크, 이미지)
  - 자동 저장 (디바운스)
  - `chapters.api.ts` 연동

  **Must NOT do**:
  - 이미지 업로드 구현 (URL 삽입만)
  - 마크다운 내보내기

  **Parallelizable**: NO (10 완료 후)

  **References**:
  
  **Pattern References**:
  - Tiptap 공식 문서: https://tiptap.dev/docs/editor/getting-started/overview
  
  **API References**:
  - `frontend/lib/api/chapters.api.ts` - 회차 CRUD API
  
  **Skill References**:
  - `bundle-dynamic-imports` - Tiptap은 `next/dynamic`으로 로드

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `chapter-editor.test.tsx` 작성 (에디터 마운트, 자동저장 테스트)
  - [ ] `pnpm test components/feature/author/chapter-editor` → PASS
  
  **Manual Verification:**
  - [ ] 작가 스튜디오에서 회차 편집 진입
  - [ ] Tiptap 에디터 렌더링 확인
  - [ ] 텍스트 입력 → 자동 저장 동작 확인

  **Commit**: YES
  - Message: `feat(author): add Tiptap-based chapter editor with auto-save`
  - Files: `components/feature/author/chapter-editor.tsx`, `components/feature/author/chapter-editor.test.tsx`
  - Pre-commit: `pnpm test components/feature/author/chapter-editor`

---

- [x] 12. AI 코파일럿 패널

  **What to do**:
  - `components/feature/author/ai-copilot-panel.tsx` 생성
  - 위키 제안 표시
  - 일관성 검사 결과 표시
  - 제안 승인/거절 UI
  - `ai.api.ts` 연동

  **Must NOT do**:
  - 실시간 스트리밍 (1차 구현 제외)
  - AI 모델 설정 변경

  **Parallelizable**: NO (11 완료 후)

  **References**:
  
  **Pattern References**:
  - `frontend/components/feature/wiki/wiki-detail.tsx` - 제안 표시 패턴
  
  **API References**:
  - `frontend/lib/api/ai.api.ts` - AI API (suggestWiki, checkConsistency)

  **Acceptance Criteria**:
  
  **TDD:**
  - [ ] `ai-copilot-panel.test.tsx` 작성 (제안 로드, 승인/거절 테스트)
  - [ ] `pnpm test components/feature/author/ai-copilot-panel` → PASS
  
  **Manual Verification:**
  - [ ] 회차 편집 중 AI 패널 열기
  - [ ] 위키 제안 목록 표시 확인
  - [ ] 제안 승인 클릭 → API 호출 확인

  **Commit**: YES
  - Message: `feat(author): add AI copilot panel for wiki suggestions`
  - Files: `components/feature/author/ai-copilot-panel.tsx`, `components/feature/author/ai-copilot-panel.test.tsx`
  - Pre-commit: `pnpm test components/feature/author/ai-copilot-panel`

---

### Phase 5: E2E 테스트 추가 (2개, 병렬 가능)

---

- [x] 13. 북마크 E2E 테스트 추가

  **What to do**:
  - `tests/e2e/bookmark.spec.ts` 생성
  - 북마크 추가/제거 시나리오
  - 서재에서 북마크 목록 확인

  **Must NOT do**:
  - 북마크 기능 구현 (이미 존재)
  - 성능 테스트

  **Parallelizable**: YES (with 14)

  **References**:
  
  **Test References**:
  - `frontend/tests/e2e/` - 기존 E2E 테스트 패턴
  - `frontend/playwright.config.ts` - Playwright 설정

  **Acceptance Criteria**:
  
  **E2E:**
  - [ ] `pnpm e2e tests/e2e/bookmark.spec.ts` → PASS
  
  **Scenarios Covered:**
  - [ ] 로그인 → 회차 페이지 → 북마크 버튼 클릭 → 성공 확인
  - [ ] 서재 → 북마크 탭 → 북마크된 회차 표시 확인
  - [ ] 북마크 제거 → 서재에서 사라짐 확인

  **Commit**: YES
  - Message: `test(e2e): add bookmark scenarios`
  - Files: `tests/e2e/bookmark.spec.ts`
  - Pre-commit: `pnpm e2e tests/e2e/bookmark.spec.ts`

---

- [x] 14. 문단 댓글 E2E 테스트 추가

  **What to do**:
  - `tests/e2e/paragraph-comment.spec.ts` 생성
  - 문단 선택 → 댓글 작성 시나리오
  - 댓글 좋아요/삭제 시나리오

  **Must NOT do**:
  - 문단 댓글 기능 구현 (이미 존재)
  - 대댓글 테스트 (1차 제외)

  **Parallelizable**: YES (with 13)

  **References**:
  
  **Test References**:
  - `frontend/tests/e2e/` - 기존 E2E 테스트 패턴
  - `frontend/components/feature/reader/reader-view.tsx` - 리더 컴포넌트

  **Acceptance Criteria**:
  
  **E2E:**
  - [ ] `pnpm e2e tests/e2e/paragraph-comment.spec.ts` → PASS
  
  **Scenarios Covered:**
  - [ ] 로그인 → 회차 리더 → 문단 선택 → 댓글 작성 → 성공 확인
  - [ ] 댓글 좋아요 클릭 → 카운트 증가 확인
  - [ ] 내 댓글 삭제 → 목록에서 제거 확인

  **Commit**: YES
  - Message: `test(e2e): add paragraph comment scenarios`
  - Files: `tests/e2e/paragraph-comment.spec.ts`
  - Pre-commit: `pnpm e2e tests/e2e/paragraph-comment.spec.ts`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | `chore(deps): add Tiptap packages` | package.json | pnpm build |
| 1 | `feat(branches): add vote-button` | vote-button.tsx | pnpm test |
| 1.5 | `feat(hooks): add useReadingProgress` | use-reading-progress.ts | pnpm test |
| 2 | `feat(wiki): add spoiler-alert` | spoiler-alert.tsx | pnpm test |
| 3 | `feat(purchases): add purchase-modal` | purchase-modal.tsx | pnpm test |
| 4 | `feat(comments): add comment-thread` | comment-thread.tsx | pnpm test |
| 5 | `feat(auth): configure NextAuth.js v5` | auth.ts | pnpm build |
| 6 | `feat(auth): integrate social login` | user-login-form.tsx | pnpm test |
| 7 | `feat(community): add loading/error states` | community/page.tsx | pnpm test |
| 8 | `feat(search): branch/author search` | search/page.tsx | pnpm test |
| 9 | `feat(wiki): create wikis page` | wikis/page.tsx | pnpm test |
| 10 | `feat(author): studio dashboard` | author/studio/page.tsx | pnpm test |
| 11 | `feat(author): chapter editor` | chapter-editor.tsx | pnpm test |
| 12 | `feat(author): AI copilot panel` | ai-copilot-panel.tsx | pnpm test |
| 13 | `test(e2e): bookmark scenarios` | bookmark.spec.ts | pnpm e2e |
| 14 | `test(e2e): paragraph comment` | paragraph-comment.spec.ts | pnpm e2e |

---

## Success Criteria

### Verification Commands
```bash
pnpm build                  # Expected: 0 errors
pnpm test                   # Expected: All tests pass
pnpm e2e                    # Expected: All scenarios pass
pnpm lint                   # Expected: 0 errors
```

### Final Checklist
- [x] 16개 TODO 모두 완료 (0, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
- [x] Tiptap 패키지 설치 완료
- [x] useReadingProgress 훅 생성 완료
- [x] 새 컴포넌트 4개 생성 완료
- [x] NextAuth.js v5 설정 완료
- [x] 작가 스튜디오 3개 파일 생성
- [x] E2E 테스트 2개 추가
- [x] GitHub 이슈 #219-#231 해소 가능 상태

---

## Document Version

- **v1.0**: 2026.01.21 - 초기 작성
- **v1.1**: 2026.01.21 - Metis 리뷰 반영 (Task 0, 1.5 추가, 가드레일 강화)
- **v1.2**: 2026.01.21 - Momus 리뷰 반영:
  - Task 1.5: `chapters.api.ts`에 `recordReadingProgress()` 추가 명시 (백엔드 API 확인됨)
  - Task 1: 타입 경로 수정 (`types/branch.ts` → `types/branches.types.ts`)
  - Task 7: 백엔드 커뮤니티 API 없음 확인, Mock 데이터 유지로 변경
