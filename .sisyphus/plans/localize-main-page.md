# 메인 페이지 한국어화 및 UI 개선

## Context

### Original Request
프론트엔드 메인 화면 개선:
1. 테마 메뉴 배경 투명 문제 수정
2. 히어로 섹션을 1/3 높이 배너 캐러셀로 변경
3. 랭킹 섹션 full width → container 너비로 변경
4. 전체 영어 텍스트 한국어로 번역
5. 장르 필터 container 내부로 이동

### Interview Summary
**Key Discussions**:
- 장르 버튼: 한국어로 번역 (전체, 판타지, 로맨스 등)
- 브랜드명: 영어 유지 (ForkLore)
- Git 전략: 기존 PR #209에 추가 (feat/#208-revamp-main-page-ui 브랜치)
- 배너 데이터: 새 BANNER_SLIDES 생성 (id, image, link)
- 히어로 높이: 300px 고정
- dot 인디케이터: 클릭 가능
- 태그 번역: 한국어로 번역 (SF, 미스터리 등)

### Metis Review
**Identified Gaps** (addressed):
- 배너 데이터 구조 → `{ id, image, link }` 확정
- 히어로 높이 → `h-[300px]` 확정
- 태그 번역 여부 → 한국어로 번역 확정

---

## Work Objectives

### Core Objective
메인 페이지의 모든 영어 UI 텍스트를 한국어로 번역하고, 히어로 섹션을 컴팩트한 배너 캐러셀로 리팩토링하며, 전체 레이아웃을 container 너비로 통일한다.

### Concrete Deliverables
- `frontend/components/common/header.tsx` - 한국어화
- `frontend/components/common/footer.tsx` - 한국어화
- `frontend/components/feature/home/genre-filter.tsx` - 한국어화
- `frontend/components/feature/home/ranking-carousel.tsx` - 한국어화
- `frontend/components/feature/home/recommendation-list.tsx` - 한국어화 (태그 포함)
- `frontend/components/feature/home/hero-section.tsx` - 배너 캐러셀로 리팩토링
- `frontend/lib/mock-data.ts` - BANNER_SLIDES 추가
- `frontend/app/page.tsx` - GenreFilter container 래핑

### Definition of Done
- [x] `pnpm build` 성공 (TypeScript 에러 없음)
- [x] 모든 UI 텍스트가 한국어로 표시됨 (ForkLore 브랜드명 제외)
- [x] 히어로 섹션이 300px 높이의 배너 캐러셀로 표시됨
- [x] 모든 섹션이 container 너비로 정렬됨

### Must Have
- 모든 네비게이션, 버튼, 레이블 텍스트 한국어화
- 히어로 섹션 300px 높이, container 너비
- dot 인디케이터 (클릭 가능)
- 자동 전환 (5초 간격)

### Must NOT Have (Guardrails)
- 새 npm 패키지 설치 금지 (framer-motion 재사용)
- RANKING_NOVELS, RECOMMENDATIONS 소설 제목/설명 번역 금지
- i18n 라이브러리 도입 금지 (하드코딩 직접 교체)
- 다른 페이지 수정 금지 (novels, login, signup 등)
- 컴포넌트 export 이름 변경 금지

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pnpm test 가능)
- **User wants tests**: Manual verification (이번 작업은 UI 텍스트/스타일 변경)
- **Framework**: Vitest 존재하나 UI 텍스트 변경에는 수동 검증 적합

### Manual QA Procedure
각 TODO 완료 후:
1. `pnpm build` 실행하여 TypeScript 에러 없음 확인
2. `pnpm dev` 실행 후 브라우저에서 시각적 확인
3. 필요시 playwright 스크린샷

---

## Task Flow

```
Task 1 (BANNER_SLIDES) 
    ↓
Task 2 (HeroSection 리팩토링) 
    ↓
Task 3, 4, 5, 6, 7 (번역 - 병렬 가능)
    ↓
Task 8 (GenreFilter 레이아웃)
    ↓
Task 9 (빌드 검증 및 커밋)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 3, 4, 5, 6, 7 | 독립적인 파일 수정 (번역) |

| Task | Depends On | Reason |
|------|------------|--------|
| 2 | 1 | HeroSection이 BANNER_SLIDES 필요 |
| 9 | 1-8 | 모든 변경 완료 후 검증 |

---

## TODOs

- [x] 1. BANNER_SLIDES 데이터 생성

  **What to do**:
  - `frontend/lib/mock-data.ts`에 BANNER_SLIDES 배열 추가
  - 구조: `{ id: number, image: string, link: string }`
  - 5개 슬라이드 (기존 RANKING_NOVELS 이미지 활용 가능)

  **Must NOT do**:
  - 기존 RANKING_NOVELS 수정 금지

  **Parallelizable**: NO (Task 2가 의존)

  **References**:
  - `frontend/lib/mock-data.ts:1-7` - 기존 RANKING_NOVELS 구조 참고
  
  **Acceptance Criteria**:
  - [x] BANNER_SLIDES export 추가됨
  - [x] 5개 항목, 각각 id/image/link 필드 포함
  - [x] TypeScript 에러 없음

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 2. HeroSection 배너 캐러셀로 리팩토링

  **What to do**:
  - 높이: `h-[80vh] min-h-[600px]` → `h-[300px]`
  - 타이틀, 서브타이틀, 버튼 완전 삭제
  - RANKING_NOVELS → BANNER_SLIDES 로 import 변경
  - container 래핑 추가 (`container mx-auto max-w-6xl`)
  - dot 인디케이터 추가 (클릭 가능)
  - 자동 전환 유지 (5초)
  - 둥근 모서리 추가 (`rounded-xl overflow-hidden`)
  - 불필요한 import 제거 (Button, BookOpen, PenTool)

  **Must NOT do**:
  - framer-motion 외 새 라이브러리 사용 금지
  - 자동 전환 로직 삭제 금지

  **Parallelizable**: NO (Task 1 완료 필요)

  **References**:
  - `frontend/components/feature/home/hero-section.tsx:20` - 현재 높이 설정
  - `frontend/components/feature/home/hero-section.tsx:22-38` - AnimatePresence 패턴
  - `frontend/components/feature/home/hero-section.tsx:12-17` - setInterval 패턴

  **Acceptance Criteria**:
  - [x] 높이 300px로 변경됨
  - [x] 타이틀/버튼 완전 제거됨
  - [x] container 클래스 적용됨
  - [x] dot 인디케이터 표시됨 (클릭 시 슬라이드 전환)
  - [x] 자동 전환 동작함 (5초)
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 3. Header 한국어화

  **What to do**:
  - `frontend/components/common/header.tsx` 수정
  - 번역 목록:
    | 영어 | 한국어 | 위치 |
    |------|--------|------|
    | Novels | 작품 | L59, L82 |
    | Ranking | 랭킹 | L60, L83 |
    | Community | 커뮤니티 | L61, L84 |
    | Search stories... | 작품 검색... | L56 |
    | Search novels... | 작품 검색... | L99 |
    | My Account | 내 계정 | L119 |
    | Profile | 프로필 | L120 |
    | Library | 서재 | L121 |
    | Settings | 설정 | L122 |
    | Log out | 로그아웃 | L125 |
    | Toggle navigation menu | 메뉴 열기 | L48 (sr-only) |

  **Must NOT do**:
  - ForkLore 브랜드명 변경 금지

  **Parallelizable**: YES (with 4, 5, 6, 7)

  **References**:
  - `frontend/components/common/header.tsx:48` - sr-only 텍스트
  - `frontend/components/common/header.tsx:56-61` - 데스크탑 네비게이션
  - `frontend/components/common/header.tsx:119-125` - 드롭다운 메뉴

  **Acceptance Criteria**:
  - [x] 모든 네비게이션 텍스트 한국어로 변경됨
  - [x] ForkLore 브랜드명 영어 유지됨
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 4. Footer 한국어화

  **What to do**:
  - `frontend/components/common/footer.tsx` 수정
  - 번역 목록:
    | 영어 | 한국어 | 위치 |
    |------|--------|------|
    | Where stories fork... | 이야기가 갈라지는 곳, 전설이 시작됩니다. | L14 |
    | Platform | 플랫폼 | L20 |
    | Novels | 작품 | L22 |
    | Ranking | 랭킹 | L23 |
    | Community | 커뮤니티 | L24 |
    | Support | 지원 | L30 |
    | Help Center | 고객센터 | L32 |
    | Terms of Service | 이용약관 | L33 |
    | Privacy Policy | 개인정보처리방침 | L34 |
    | Follow Us | 팔로우 | L40 |
    | Terms | 이용약관 | L59 |
    | Privacy | 개인정보 | L60 |
    | Cookies | 쿠키 | L61 |

  **Must NOT do**:
  - ForkLore 브랜드명 변경 금지
  - 저작권 연도 변경 금지

  **Parallelizable**: YES (with 3, 5, 6, 7)

  **References**:
  - `frontend/components/common/footer.tsx:14` - 태그라인
  - `frontend/components/common/footer.tsx:20-40` - 섹션 헤더 및 링크
  - `frontend/components/common/footer.tsx:56-61` - 하단 링크

  **Acceptance Criteria**:
  - [x] 모든 UI 텍스트 한국어로 변경됨
  - [x] ForkLore 브랜드명 영어 유지됨
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 5. GenreFilter 한국어화

  **What to do**:
  - `frontend/components/feature/home/genre-filter.tsx` 수정
  - GENRES 배열 번역 (L7-20):
    | 영어 | 한국어 |
    |------|--------|
    | All | 전체 |
    | Fantasy | 판타지 |
    | Romance | 로맨스 |
    | Sci-Fi | SF |
    | Mystery | 미스터리 |
    | Horror | 호러 |
    | Thriller | 스릴러 |
    | Historical | 역사 |
    | Action | 액션 |
    | Adventure | 어드벤처 |
    | Comedy | 코미디 |
    | Drama | 드라마 |

  **Must NOT do**:
  - 컴포넌트 구조 변경 금지

  **Parallelizable**: YES (with 3, 4, 6, 7)

  **References**:
  - `frontend/components/feature/home/genre-filter.tsx:7-20` - GENRES 배열

  **Acceptance Criteria**:
  - [x] 12개 장르 모두 한국어로 변경됨
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 6. RankingCarousel 한국어화

  **What to do**:
  - `frontend/components/feature/home/ranking-carousel.tsx` 수정
  - 번역 목록:
    | 영어 | 한국어 | 위치 |
    |------|--------|------|
    | Top Rankings | 인기 랭킹 | L18 |
    | View All | 전체보기 | L21 |

  **Must NOT do**:
  - RANKING_NOVELS 소설 제목/설명 번역 금지

  **Parallelizable**: YES (with 3, 4, 5, 7)

  **References**:
  - `frontend/components/feature/home/ranking-carousel.tsx:18` - 제목
  - `frontend/components/feature/home/ranking-carousel.tsx:21` - 링크 텍스트

  **Acceptance Criteria**:
  - [x] 섹션 제목 한국어로 변경됨
  - [x] 소설 제목은 영어 유지됨
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 7. RecommendationList 한국어화 (태그 포함)

  **What to do**:
  - `frontend/components/feature/home/recommendation-list.tsx` 수정
  - UI 텍스트 번역:
    | 영어 | 한국어 | 위치 |
    |------|--------|------|
    | Picked for You | 맞춤 추천 | L45 |
    | Based on your reading history | 읽은 작품을 기반으로 추천합니다 | L46 |
    | by {author} | {author} 작가 | L90 |
  - 태그 번역 (RECOMMENDATIONS 배열 내):
    | 영어 | 한국어 |
    |------|--------|
    | Sci-Fi | SF |
    | Mystery | 미스터리 |
    | Fantasy | 판타지 |
    | Slice of Life | 일상 |
    | Action | 액션 |
    | LitRPG | 리트RPG |

  **Must NOT do**:
  - 소설 제목/설명 번역 금지

  **Parallelizable**: YES (with 3, 4, 5, 6)

  **References**:
  - `frontend/components/feature/home/recommendation-list.tsx:45-46` - 섹션 제목
  - `frontend/components/feature/home/recommendation-list.tsx:90` - 작가명 패턴
  - `frontend/components/feature/home/recommendation-list.tsx:17-18, 26-27, 35` - 태그 배열

  **Acceptance Criteria**:
  - [x] 섹션 제목/부제목 한국어로 변경됨
  - [x] 작가명 패턴 "by X" → "X 작가"로 변경됨
  - [x] 태그 한국어로 변경됨
  - [x] 소설 제목/설명은 영어 유지됨
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 8. GenreFilter 레이아웃 수정

  **What to do**:
  - `frontend/app/page.tsx` 수정
  - GenreFilter를 container로 래핑
  - 변경:
    ```tsx
    // Before (L17)
    <GenreFilter />
    
    // After
    <section className="container mx-auto max-w-6xl">
      <GenreFilter />
    </section>
    ```

  **Must NOT do**:
  - 다른 섹션 레이아웃 변경 금지

  **Parallelizable**: YES (독립적)

  **References**:
  - `frontend/app/page.tsx:17` - 현재 GenreFilter 위치
  - `frontend/app/page.tsx:19-22` - 다른 섹션 container 패턴

  **Acceptance Criteria**:
  - [x] GenreFilter가 container 너비로 표시됨
  - [x] 다른 섹션과 너비 동일함
  - [x] `pnpm build` 성공

  **Commit**: NO (Task 9에서 일괄)

---

- [x] 9. 빌드 검증 및 커밋

  **What to do**:
  - `pnpm build` 실행하여 전체 빌드 성공 확인
  - 변경 파일 스테이징 및 커밋
  - 기존 PR #209에 푸시

  **Must NOT do**:
  - 새 PR 생성 금지 (기존 PR에 추가)

  **Parallelizable**: NO (모든 Task 완료 후)

  **References**:
  - 기존 브랜치: `feat/#208-revamp-main-page-ui`
  - 기존 PR: #209

  **Acceptance Criteria**:
  - [x] `pnpm build` 성공
  - [x] 커밋 생성됨
  - [x] PR #209에 푸시됨

  **Commit**: YES
  - Message: `feat: localize main page to Korean and refactor hero section`
  - Files: 8개 파일 (mock-data.ts, hero-section.tsx, header.tsx, footer.tsx, genre-filter.tsx, ranking-carousel.tsx, recommendation-list.tsx, page.tsx)
  - Pre-commit: `pnpm build`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 9 | `feat: localize main page to Korean and refactor hero section` | 8 files | pnpm build |

---

## Success Criteria

### Verification Commands
```bash
cd frontend && pnpm build  # Expected: Build successful, no errors
```

### Final Checklist
- [x] 모든 UI 텍스트 한국어로 표시됨 (ForkLore 제외)
- [x] 히어로 섹션 300px 높이, container 너비
- [x] 장르 필터 container 너비
- [x] dot 인디케이터 클릭 가능
- [x] 빌드 성공
- [x] PR #209에 커밋됨
