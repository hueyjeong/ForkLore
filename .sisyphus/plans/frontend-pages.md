# Frontend Pages Implementation

## Context

### Original Request
프론트엔드 페이지 구현: Novels 페이지 (작품 목록), Ranking 페이지 (랭킹), Community 페이지 (커뮤니티) 구현 및 네비게이션 메뉴 연결.

### Interview Summary
**Key Discussions**:
- **데이터 소스**: Mock 데이터 사용 (기존 패턴 유지)
- **테스트 전략**: TDD 적용 (Vitest)
- **구현 순서**: 3개 페이지 병렬 구현
- **UI 스타일**: 홈페이지 스타일 유지 (glass, premium 폰트)

**Research Findings**:
- 기존 페이지는 Server Components + Mock 데이터 사용
- Container 패턴: `container mx-auto max-w-6xl`
- 테스트 예시: `frontend/components/ui/input.test.tsx`
- Header에 `/novels`, `/ranking`, `/community` 링크 존재 (페이지 미구현)
- `Select` 컴포넌트 미설치 → shadcn select 설치 필요
- 무한 스크롤 라이브러리 없음 → react-virtuoso 설치 필요

### Metis Review
**Identified Gaps** (addressed):
- 무한 스크롤 방식 결정 → react-virtuoso 라이브러리 사용
- Select 컴포넌트 부재 → shadcn select 설치
- 필터 상태 저장 위치 → URL params (공유 가능)
- 랭킹 데이터 구조 → 단일 데이터셋 (탭별 정렬만 다름)
- Empty states → 한글 메시지 표시

---

## Work Objectives

### Core Objective
ForkLore 플랫폼에 Novels, Ranking, Community 3개 페이지를 구현하여 완전한 네비게이션 경험을 제공한다.

### Concrete Deliverables
- `frontend/app/novels/page.tsx` - 작품 목록 페이지
- `frontend/app/ranking/page.tsx` - 랭킹 페이지
- `frontend/app/community/page.tsx` - 커뮤니티 페이지
- `frontend/lib/mock-data.ts` - 추가 Mock 데이터
- `frontend/components/feature/novels/` - Novels 페이지 컴포넌트들
- `frontend/components/feature/ranking/` - Ranking 페이지 컴포넌트들
- `frontend/components/feature/community/` - Community 페이지 컴포넌트들
- 각 컴포넌트별 Vitest 테스트 파일

### Definition of Done
- [x] `pnpm test` 모든 테스트 통과
- [x] `pnpm build` 빌드 성공
- [x] 3개 페이지 모두 접근 가능 (http://localhost:3000/novels, /ranking, /community)
- [x] Header 네비게이션에서 각 페이지로 이동 가능
- [x] 반응형 디자인 동작 (모바일/데스크톱)

### Must Have
- Mock 데이터 기반 UI
- TDD (테스트 먼저 작성)
- 한글 라벨
- 반응형 디자인 (모바일: 2열 그리드, 데스크톱: 4열 그리드)
- URL params 기반 필터 상태 관리

### Must NOT Have (Guardrails)
- 실제 API 호출 또는 Server Actions ❌
- loading.tsx, error.tsx 파일 생성 ❌
- 새 Zustand 스토어 생성 ❌
- 쓰기 기능 (글쓰기, 댓글 작성) ❌
- 인증 체크 또는 보호된 라우트 ❌
- 다국어(i18n) 기능 ❌
- 승인되지 않은 의존성 설치 ❌ (react-virtuoso, shadcn select 제외)

---

## GitHub Issue & Branch Strategy

### Issue Creation (PRE-WORK)
Before starting implementation, create a GitHub issue:

**Issue Title**: `feat: Implement frontend pages (Novels, Ranking, Community)`

**Issue Body**:
```markdown
## Summary
Novels, Ranking, Community 3개 페이지를 구현하여 Header 네비게이션 완성

## Features
- [x] `/novels` - 작품 목록 페이지 (무한 스크롤, 필터, 검색)
- [x] `/ranking` - 랭킹 페이지 (일간/주간/월간 탭)
- [x] `/community` - 커뮤니티 페이지 (카테고리별 게시글)

## Technical Details
- Mock 데이터 사용 (API 연동 별도)
- TDD with Vitest
- react-virtuoso for infinite scroll
- URL params for filter state

## Acceptance Criteria
- [x] 모든 테스트 통과 (pnpm test)
- [x] 빌드 성공 (pnpm build)
- [x] 반응형 디자인 동작
```

**Command**:
```bash
gh issue create --title "feat: Implement frontend pages (Novels, Ranking, Community)" --body "..." --label "enhancement,frontend"
```

### Branch Strategy
- **Base branch**: `develop`
- **Feature branch**: `feat/#<issue-number>-frontend-pages`
- **Naming convention**: `feat/#<issue>-<description>`

**Commands**:
```bash
# After issue creation, note the issue number (e.g., #211)
git checkout develop
git pull origin develop
git checkout -b feat/#211-frontend-pages
```

### PR Strategy
After all tasks complete:
- PR target: `develop` (NOT main)
- PR title: `feat: Implement frontend pages (Novels, Ranking, Community) #<issue>`
- Link to issue with `Closes #<issue>` in PR body

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES
- **User wants tests**: TDD
- **Framework**: Vitest + @testing-library/react

### TDD Pattern
Each component task follows RED-GREEN-REFACTOR:

1. **RED**: Write failing test first
   - Test file: `{component}.test.tsx`
   - Test command: `pnpm test {file}`
   - Expected: FAIL (test exists, implementation doesn't)
2. **GREEN**: Implement minimum code to pass
   - Command: `pnpm test {file}`
   - Expected: PASS
3. **REFACTOR**: Clean up while keeping green
   - Command: `pnpm test`
   - Expected: PASS (still)

---

## Task Flow

```
PRE-WORK (Issue & Branch)
      ↓
Task 0 (Dependencies)
      ↓
Task 1 (Mock Data)
      ↓
┌─────┼─────┐
↓     ↓     ↓
Task 2  Task 6  Task 10
(Novels) (Ranking) (Community)
   ↓     ↓     ↓
Task 3  Task 7  Task 11
   ↓     ↓     ↓
Task 4  Task 8  Task 12
   ↓     ↓     ↓
Task 5  Task 9  Task 13
      ↓
Task 14 (Final Verification)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 2-5, 6-9, 10-13 | 독립적인 3개 페이지 |

| Task | Depends On | Reason |
|------|------------|--------|
| 1 | 0 | 의존성 설치 후 Mock 데이터 작성 |
| 2-13 | 1 | Mock 데이터 필요 |
| 14 | 2-13 | 모든 페이지 완료 후 검증 |

---

## TODOs

### PRE-WORK: Create GitHub Issue and Feature Branch

**What to do**:
- GitHub 이슈 생성
- develop 브랜치에서 feature 브랜치 생성
- 브랜치명: `feat/#<이슈번호>-frontend-pages`

**Must NOT do**:
- main 브랜치에서 직접 작업 ❌
- 이슈 없이 작업 시작 ❌

**Parallelizable**: NO (모든 태스크의 선행 조건)

**References**:
- 프로젝트 브랜치 컨벤션: `feat/#<issue>-<description>`
- Base branch: `develop`

**Commands**:
```bash
# 1. Create issue
gh issue create \
  --title "feat: Implement frontend pages (Novels, Ranking, Community)" \
  --body "## Summary
Novels, Ranking, Community 3개 페이지를 구현하여 Header 네비게이션 완성

## Features
- [x] \`/novels\` - 작품 목록 페이지 (무한 스크롤, 필터, 검색)
- [x] \`/ranking\` - 랭킹 페이지 (일간/주간/월간 탭)
- [x] \`/community\` - 커뮤니티 페이지 (카테고리별 게시글)

## Technical Details
- Mock 데이터 사용 (API 연동 별도)
- TDD with Vitest
- react-virtuoso for infinite scroll
- URL params for filter state

## Acceptance Criteria
- [x] 모든 테스트 통과 (pnpm test)
- [x] 빌드 성공 (pnpm build)
- [x] 반응형 디자인 동작" \
  --label "enhancement,frontend"

# 2. Note the issue number from output (e.g., #211)

# 3. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feat/#<ISSUE_NUMBER>-frontend-pages
```

**Acceptance Criteria**:
- [x] GitHub 이슈 생성됨 (이슈 번호 확인) → #211
- [x] `git branch` → `feat/#211-frontend-pages` 확인 ✓
- [x] `git log -1 --oneline` → develop의 최신 커밋 기반 확인 (55a9b6e)

**Commit**: NO (브랜치 생성만)

---

### Task 0: Install Dependencies

**What to do**:
- shadcn select 컴포넌트 설치: `npx shadcn@latest add select`
- react-virtuoso 설치: `pnpm add react-virtuoso`
- 설치 확인

**Must NOT do**:
- 다른 컴포넌트나 라이브러리 설치 ❌

**Parallelizable**: NO (모든 태스크의 선행 조건)

**References**:
- `frontend/package.json` - 현재 의존성 확인
- `frontend/components/ui/` - 기존 shadcn 컴포넌트 구조

**Acceptance Criteria**:
- [x] `npx shadcn@latest add select` 실행 완료 ✓
- [x] `frontend/components/ui/select.tsx` 파일 생성 확인 ✓
- [x] `pnpm add react-virtuoso` 실행 완료 ✓
- [x] `frontend/package.json`에 `react-virtuoso` 추가 확인 ✓
- [x] `pnpm test` → 기존 테스트 여전히 통과 ✓ (3 tests)

**Commit**: YES ✓ (633f642)
- Message: `chore: add select component and react-virtuoso for frontend pages`
- Files: `frontend/components/ui/select.tsx`, `frontend/package.json`, `frontend/pnpm-lock.yaml`
- Pre-commit: `pnpm test`

---

### Task 1: Add Mock Data for All Pages

**What to do**:
- `frontend/lib/mock-data.ts`에 TypeScript 인터페이스 정의
- Novels 페이지용 `NOVELS_LIST` (20개 작품)
- Community 페이지용 `COMMUNITY_POSTS` (15개 게시글)
- 기존 `RANKING_NOVELS` 확장 (status, tags 필드 추가)

**Must NOT do**:
- API 호출 로직 추가 ❌
- 다른 파일에 Mock 데이터 분산 ❌

**Parallelizable**: NO (모든 페이지 태스크의 선행 조건)

**References**:
**Pattern References**:
- `frontend/lib/mock-data.ts:1-50` - 기존 Mock 데이터 구조 (BANNER_SLIDES, RANKING_NOVELS)
- `frontend/app/novels/[id]/page.tsx:12-42` - Novel 객체 구조 참고

**Type References**:
```typescript
// 추가할 인터페이스
interface Novel {
  id: string;
  title: string;
  author: string;
  coverUrl: string;
  genre: string;
  rating: number;
  views: string;
  status: '연재중' | '완결';
  tags: string[];
  lastUpdated: string;
}

interface CommunityPost {
  id: string;
  title: string;
  author: string;
  category: '자유' | '작품토론' | '공지';
  commentCount: number;
  likeCount: number;
  createdAt: string;
  isPinned: boolean;
}
```

**Acceptance Criteria**:
- [x] `Novel` 인터페이스 export 확인 ✓
- [x] `CommunityPost` 인터페이스 export 확인 ✓
- [x] `NOVELS_LIST` 배열 20개 항목 확인 ✓
- [x] `COMMUNITY_POSTS` 배열 15개 항목 확인 ✓
- [x] 기존 `RANKING_NOVELS`에 `status`, `tags` 필드 추가 확인 ✓
- [x] TypeScript 컴파일 에러 없음: `pnpm build` 성공 ✓

**Commit**: YES ✓ (961266e)
- Message: `feat(mock): add novels list and community posts data`
- Files: `frontend/lib/mock-data.ts`
- Pre-commit: `pnpm build`

---

### Task 2: Create NovelGrid Component (TDD)

**What to do**:
- `frontend/components/feature/novels/novel-grid.tsx` 생성
- 테스트 먼저 작성: `novel-grid.test.tsx`
- NovelCard를 그리드로 배치
- 반응형: 모바일 2열, 데스크톱 4열

**Must NOT do**:
- NovelCard 컴포넌트 수정 ❌
- 필터링 로직 포함 ❌ (별도 컴포넌트)

**Parallelizable**: YES (Task 6, 10과 병렬)

**References**:
**Pattern References**:
- `frontend/components/feature/novel/novel-card.tsx` - 기존 NovelCard 컴포넌트 구조
- `frontend/components/ui/input.test.tsx` - 테스트 작성 패턴 (render, screen, expect)

**Test References**:
```typescript
// 테스트 케이스
describe('NovelGrid', () => {
  it('renders novel cards in a grid', () => {})
  it('displays 2 columns on mobile', () => {})
  it('displays 4 columns on desktop', () => {})
  it('shows empty state when no novels', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test novel-grid` → FAIL (테스트 존재, 구현 없음)
- [x] GREEN: `pnpm test novel-grid` → PASS (4개 테스트)
- [x] 그리드 클래스: `grid grid-cols-2 md:grid-cols-4 gap-4`
- [x] Empty state: "표시할 작품이 없습니다" 메시지

**Commit**: YES
- Message: `feat(novels): add NovelGrid component with tests`
- Files: `frontend/components/feature/novels/novel-grid.tsx`, `frontend/components/feature/novels/novel-grid.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 3: Create NovelFilters Component (TDD)

**What to do**:
- `frontend/components/feature/novels/novel-filters.tsx` 생성
- 테스트 먼저 작성: `novel-filters.test.tsx`
- 장르 필터 (GenreFilter 패턴 재사용)
- 상태 필터 (연재중/완결/전체)
- 정렬 Select (인기순/최신순)
- 검색바
- URL params로 상태 관리 (`useSearchParams`)

**Must NOT do**:
- 서버 사이드 필터링 ❌
- 외부 상태 관리 (Zustand) ❌

**Parallelizable**: YES (Task 2 완료 후)

**References**:
**Pattern References**:
- `frontend/components/feature/home/genre-filter.tsx` - 장르 필터 UI 패턴
- `frontend/components/ui/select.tsx` - Select 컴포넌트 사용법 (Task 0에서 설치)
- `frontend/components/ui/input.tsx` - 검색바 Input 사용

**API References**:
- Next.js `useSearchParams()` - URL 쿼리 파라미터 읽기/쓰기
- Next.js `useRouter()` - URL 업데이트

**Test References**:
```typescript
describe('NovelFilters', () => {
  it('renders genre filter buttons', () => {})
  it('renders status filter buttons', () => {})
  it('renders sort select', () => {})
  it('renders search input', () => {})
  it('updates URL params on filter change', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test novel-filters` → FAIL
- [x] GREEN: `pnpm test novel-filters` → PASS (5개 테스트)
- [x] 장르 필터: 전체, 판타지, 로맨스, 무협, SF, 미스터리 버튼
- [x] 상태 필터: 전체, 연재중, 완결 버튼
- [x] 정렬 Select: 인기순, 최신순 옵션
- [x] 검색바: placeholder "작품 검색..."
- [x] URL 변경 확인: `/novels?genre=판타지&status=연재중`

**Commit**: YES
- Message: `feat(novels): add NovelFilters component with URL params`
- Files: `frontend/components/feature/novels/novel-filters.tsx`, `frontend/components/feature/novels/novel-filters.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 4: Create InfiniteNovelList Component (TDD)

**What to do**:
- `frontend/components/feature/novels/infinite-novel-list.tsx` 생성
- 테스트 먼저 작성: `infinite-novel-list.test.tsx`
- react-virtuoso의 `Virtuoso` 컴포넌트 사용
- NovelGrid를 감싸서 무한 스크롤 구현
- 클라이언트 사이드 Mock 데이터 필터링/정렬

**Must NOT do**:
- 실제 API 페이지네이션 ❌
- 서버 컴포넌트로 구현 ❌

**Parallelizable**: YES (Task 3 완료 후)

**References**:
**Pattern References**:
- `frontend/components/feature/novels/novel-grid.tsx` - NovelGrid 사용 (Task 2)
- react-virtuoso 공식 문서: https://virtuoso.dev/

**Test References**:
```typescript
describe('InfiniteNovelList', () => {
  it('renders initial set of novels', () => {})
  it('loads more novels on scroll', () => {})
  it('filters novels by genre', () => {})
  it('filters novels by status', () => {})
  it('sorts novels by popularity', () => {})
  it('sorts novels by date', () => {})
  it('filters novels by search query', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test infinite-novel-list` → FAIL
- [x] GREEN: `pnpm test infinite-novel-list` → PASS (7개 테스트)
- [x] 초기 로드: 12개 작품 표시
- [x] 스크롤 시 12개씩 추가 로드
- [x] 필터 적용 시 결과 필터링
- [x] 검색 시 제목 기준 필터링

**Commit**: YES
- Message: `feat(novels): add InfiniteNovelList with virtualization`
- Files: `frontend/components/feature/novels/infinite-novel-list.tsx`, `frontend/components/feature/novels/infinite-novel-list.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 5: Create Novels Page

**What to do**:
- `frontend/app/novels/page.tsx` 생성
- Server Component로 페이지 구조 작성
- NovelFilters, InfiniteNovelList 조합
- 페이지 타이틀: "작품"

**Must NOT do**:
- 클라이언트 컴포넌트로 전체 페이지 작성 ❌
- API 호출 ❌

**Parallelizable**: NO (Task 2-4 완료 후)

**References**:
**Pattern References**:
- `frontend/app/page.tsx` - 홈페이지 구조 (Server Component + feature 컴포넌트 조합)
- `frontend/components/feature/novels/novel-filters.tsx` - 필터 컴포넌트 (Task 3)
- `frontend/components/feature/novels/infinite-novel-list.tsx` - 무한 스크롤 리스트 (Task 4)

**Acceptance Criteria**:
- [x] `http://localhost:3000/novels` 접근 가능
- [x] Header "작품" 링크 클릭 시 이동
- [x] 장르 필터 동작 확인
- [x] 상태 필터 동작 확인
- [x] 정렬 동작 확인
- [x] 검색 동작 확인
- [x] 무한 스크롤 동작 확인
- [x] `pnpm build` 성공

**Commit**: YES
- Message: `feat(novels): add novels list page`
- Files: `frontend/app/novels/page.tsx`
- Pre-commit: `pnpm build`

---

### Task 6: Create RankingList Component (TDD)

**What to do**:
- `frontend/components/feature/ranking/ranking-list.tsx` 생성
- 테스트 먼저 작성: `ranking-list.test.tsx`
- TOP 100 순위 리스트
- 순위 배지 (1-3위: 금/은/동)
- 각 항목: 순위, 커버, 제목, 작가, 조회수, 평점

**Must NOT do**:
- 순위 변동 애니메이션 ❌
- 페이지네이션 ❌

**Parallelizable**: YES (Task 2, 10과 병렬)

**References**:
**Pattern References**:
- `frontend/components/feature/home/ranking-carousel.tsx` - 기존 랭킹 UI 패턴
- `frontend/components/feature/novel/novel-card.tsx` - 작품 정보 표시 패턴

**Test References**:
```typescript
describe('RankingList', () => {
  it('renders ranking items with rank numbers', () => {})
  it('displays gold badge for rank 1', () => {})
  it('displays silver badge for rank 2', () => {})
  it('displays bronze badge for rank 3', () => {})
  it('displays regular number for rank 4+', () => {})
  it('shows novel info: cover, title, author, views, rating', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test ranking-list` → FAIL
- [x] GREEN: `pnpm test ranking-list` → PASS (6개 테스트)
- [x] 1위: 금색 배지 (`text-yellow-500`)
- [x] 2위: 은색 배지 (`text-gray-400`)
- [x] 3위: 동색 배지 (`text-orange-500`)
- [x] 4위 이상: 일반 숫자
- [x] 각 항목에 조회수, 평점 표시

**Commit**: YES
- Message: `feat(ranking): add RankingList component with badges`
- Files: `frontend/components/feature/ranking/ranking-list.tsx`, `frontend/components/feature/ranking/ranking-list.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 7: Create RankingTabs Component (TDD)

**What to do**:
- `frontend/components/feature/ranking/ranking-tabs.tsx` 생성
- 테스트 먼저 작성: `ranking-tabs.test.tsx`
- 3개 탭: 일간, 주간, 월간
- shadcn Tabs 컴포넌트 사용
- 탭 전환 시 정렬 기준만 변경 (같은 데이터)

**Must NOT do**:
- 별도 데이터 fetch ❌
- URL params 동기화 ❌ (로컬 상태만)

**Parallelizable**: YES (Task 6 완료 후)

**References**:
**Pattern References**:
- `frontend/components/ui/tabs.tsx` - shadcn Tabs 컴포넌트
- `frontend/app/novels/[id]/page.tsx:121-126` - Tabs 사용 예시

**Test References**:
```typescript
describe('RankingTabs', () => {
  it('renders three tabs: 일간, 주간, 월간', () => {})
  it('displays 일간 tab content by default', () => {})
  it('switches to 주간 tab on click', () => {})
  it('switches to 월간 tab on click', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test ranking-tabs` → FAIL
- [x] GREEN: `pnpm test ranking-tabs` → PASS (4개 테스트)
- [x] 탭 라벨: 일간, 주간, 월간
- [x] 기본 선택: 일간
- [x] 탭 전환 시 RankingList에 다른 정렬 전달

**Commit**: YES
- Message: `feat(ranking): add RankingTabs component`
- Files: `frontend/components/feature/ranking/ranking-tabs.tsx`, `frontend/components/feature/ranking/ranking-tabs.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 8: Create RankingPage Header Component (TDD)

**What to do**:
- `frontend/components/feature/ranking/ranking-header.tsx` 생성
- 테스트 먼저 작성: `ranking-header.test.tsx`
- 페이지 타이틀: "인기 랭킹"
- 부제목: "독자들이 사랑하는 작품"

**Must NOT do**:
- 복잡한 통계 표시 ❌

**Parallelizable**: YES (Task 6, 7과 병렬)

**References**:
**Pattern References**:
- `frontend/components/feature/home/hero-section.tsx` - 헤더 스타일링 패턴

**Test References**:
```typescript
describe('RankingHeader', () => {
  it('renders title "인기 랭킹"', () => {})
  it('renders subtitle', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test ranking-header` → FAIL
- [x] GREEN: `pnpm test ranking-header` → PASS (2개 테스트)
- [x] 타이틀: `text-3xl font-bold text-premium`
- [x] 부제목: `text-muted-foreground`

**Commit**: YES
- Message: `feat(ranking): add RankingHeader component`
- Files: `frontend/components/feature/ranking/ranking-header.tsx`, `frontend/components/feature/ranking/ranking-header.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 9: Create Ranking Page

**What to do**:
- `frontend/app/ranking/page.tsx` 생성
- Server Component로 페이지 구조 작성
- RankingHeader, RankingTabs 조합

**Must NOT do**:
- 클라이언트 컴포넌트로 전체 페이지 작성 ❌

**Parallelizable**: NO (Task 6-8 완료 후)

**References**:
**Pattern References**:
- `frontend/app/page.tsx` - 홈페이지 구조
- `frontend/components/feature/ranking/ranking-header.tsx` - 헤더 (Task 8)
- `frontend/components/feature/ranking/ranking-tabs.tsx` - 탭 (Task 7)

**Acceptance Criteria**:
- [x] `http://localhost:3000/ranking` 접근 가능
- [x] Header "랭킹" 링크 클릭 시 이동
- [x] 일간/주간/월간 탭 전환 동작
- [x] TOP 100 리스트 표시
- [x] 1-3위 배지 표시
- [x] `pnpm build` 성공

**Commit**: YES
- Message: `feat(ranking): add ranking page`
- Files: `frontend/app/ranking/page.tsx`
- Pre-commit: `pnpm build`

---

### Task 10: Create PostCard Component (TDD)

**What to do**:
- `frontend/components/feature/community/post-card.tsx` 생성
- 테스트 먼저 작성: `post-card.test.tsx`
- 게시글 카드: 제목, 작성자, 댓글수, 날짜
- 핀 아이콘 (공지용)

**Must NOT do**:
- 클릭 시 상세 페이지 이동 ❌ (페이지 미구현)

**Parallelizable**: YES (Task 2, 6과 병렬)

**References**:
**Pattern References**:
- `frontend/components/ui/card.tsx` - Card 컴포넌트
- `frontend/lib/mock-data.ts` - CommunityPost 인터페이스 (Task 1)

**Test References**:
```typescript
describe('PostCard', () => {
  it('renders post title', () => {})
  it('renders author name', () => {})
  it('renders comment count', () => {})
  it('renders created date', () => {})
  it('shows pin icon for pinned posts', () => {})
  it('does not show pin icon for regular posts', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test post-card` → FAIL
- [x] GREEN: `pnpm test post-card` → PASS (6개 테스트)
- [x] 핀 아이콘: lucide-react `Pin` 아이콘
- [x] 날짜 포맷: 상대 시간 또는 YYYY-MM-DD

**Commit**: YES
- Message: `feat(community): add PostCard component`
- Files: `frontend/components/feature/community/post-card.tsx`, `frontend/components/feature/community/post-card.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 11: Create PostList Component (TDD)

**What to do**:
- `frontend/components/feature/community/post-list.tsx` 생성
- 테스트 먼저 작성: `post-list.test.tsx`
- PostCard 리스트
- Empty state 처리

**Must NOT do**:
- 무한 스크롤 ❌ (Community는 단순 리스트)

**Parallelizable**: YES (Task 10 완료 후)

**References**:
**Pattern References**:
- `frontend/components/feature/community/post-card.tsx` - PostCard (Task 10)

**Test References**:
```typescript
describe('PostList', () => {
  it('renders list of post cards', () => {})
  it('shows empty state when no posts', () => {})
  it('displays pinned posts first', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test post-list` → FAIL
- [x] GREEN: `pnpm test post-list` → PASS (3개 테스트)
- [x] 핀 게시글 상단 정렬
- [x] Empty state: "게시글이 없습니다"

**Commit**: YES
- Message: `feat(community): add PostList component`
- Files: `frontend/components/feature/community/post-list.tsx`, `frontend/components/feature/community/post-list.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 12: Create CategoryTabs Component (TDD)

**What to do**:
- `frontend/components/feature/community/category-tabs.tsx` 생성
- 테스트 먼저 작성: `category-tabs.test.tsx`
- 4개 탭: 전체, 자유, 작품토론, 공지
- 정렬 토글: 인기글/최신글

**Must NOT do**:
- URL params 동기화 ❌

**Parallelizable**: YES (Task 10, 11과 병렬)

**References**:
**Pattern References**:
- `frontend/components/ui/tabs.tsx` - Tabs 컴포넌트
- `frontend/components/feature/ranking/ranking-tabs.tsx` - 탭 패턴 (Task 7)

**Test References**:
```typescript
describe('CategoryTabs', () => {
  it('renders category tabs: 전체, 자유, 작품토론, 공지', () => {})
  it('displays 전체 tab by default', () => {})
  it('renders sort toggle: 인기글/최신글', () => {})
  it('filters posts by category on tab change', () => {})
  it('sorts posts on toggle change', () => {})
})
```

**Acceptance Criteria**:
- [x] RED: `pnpm test category-tabs` → FAIL
- [x] GREEN: `pnpm test category-tabs` → PASS (5개 테스트)
- [x] 탭 라벨: 전체, 자유, 작품토론, 공지
- [x] 정렬 토글: 인기글(기본), 최신글

**Commit**: YES
- Message: `feat(community): add CategoryTabs component`
- Files: `frontend/components/feature/community/category-tabs.tsx`, `frontend/components/feature/community/category-tabs.test.tsx`
- Pre-commit: `pnpm test`

---

### Task 13: Create Community Page

**What to do**:
- `frontend/app/community/page.tsx` 생성
- Server Component로 페이지 구조 작성
- 페이지 헤더, CategoryTabs, PostList 조합

**Must NOT do**:
- 클라이언트 컴포넌트로 전체 페이지 작성 ❌

**Parallelizable**: NO (Task 10-12 완료 후)

**References**:
**Pattern References**:
- `frontend/app/page.tsx` - 홈페이지 구조
- `frontend/components/feature/community/category-tabs.tsx` - 카테고리 탭 (Task 12)
- `frontend/components/feature/community/post-list.tsx` - 게시글 리스트 (Task 11)

**Acceptance Criteria**:
- [x] `http://localhost:3000/community` 접근 가능
- [x] Header "커뮤니티" 링크 클릭 시 이동
- [x] 카테고리 탭 전환 동작
- [x] 정렬 토글 동작
- [x] 핀 게시글 상단 표시
- [x] `pnpm build` 성공

**Commit**: YES
- Message: `feat(community): add community page`
- Files: `frontend/app/community/page.tsx`
- Pre-commit: `pnpm build`

---

### Task 14: Final Verification and Build

**What to do**:
- 모든 테스트 실행
- 프로덕션 빌드 확인
- 각 페이지 수동 검증

**Must NOT do**:
- 새로운 기능 추가 ❌

**Parallelizable**: NO (모든 태스크 완료 후)

**References**:
- 모든 이전 태스크 결과물

**Acceptance Criteria**:
- [x] `pnpm test` → 모든 테스트 통과 (0 failures)
- [x] `pnpm build` → 빌드 성공
- [x] `pnpm dev` 실행 후:
  - [x] `/novels` 페이지 정상 렌더링
  - [x] `/ranking` 페이지 정상 렌더링
  - [x] `/community` 페이지 정상 렌더링
  - [x] Header 네비게이션 링크 동작 확인
  - [x] 모바일 뷰 (2열 그리드) 확인
  - [x] 데스크톱 뷰 (4열 그리드) 확인

**Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | `chore: add select component and react-virtuoso` | ui/select.tsx, package.json | pnpm test |
| 1 | `feat(mock): add novels list and community posts data` | lib/mock-data.ts | pnpm build |
| 2 | `feat(novels): add NovelGrid component with tests` | feature/novels/* | pnpm test |
| 3 | `feat(novels): add NovelFilters component with URL params` | feature/novels/* | pnpm test |
| 4 | `feat(novels): add InfiniteNovelList with virtualization` | feature/novels/* | pnpm test |
| 5 | `feat(novels): add novels list page` | app/novels/page.tsx | pnpm build |
| 6 | `feat(ranking): add RankingList component with badges` | feature/ranking/* | pnpm test |
| 7 | `feat(ranking): add RankingTabs component` | feature/ranking/* | pnpm test |
| 8 | `feat(ranking): add RankingHeader component` | feature/ranking/* | pnpm test |
| 9 | `feat(ranking): add ranking page` | app/ranking/page.tsx | pnpm build |
| 10 | `feat(community): add PostCard component` | feature/community/* | pnpm test |
| 11 | `feat(community): add PostList component` | feature/community/* | pnpm test |
| 12 | `feat(community): add CategoryTabs component` | feature/community/* | pnpm test |
| 13 | `feat(community): add community page` | app/community/page.tsx | pnpm build |

---

## Success Criteria

### Verification Commands
```bash
pnpm test              # Expected: All tests pass
pnpm build             # Expected: Build succeeds
pnpm dev               # Then manually check pages
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All tests pass (pnpm test)
- [x] Build succeeds (pnpm build)
- [x] 3 pages accessible and functional
- [x] Header navigation works
- [x] Responsive design works
