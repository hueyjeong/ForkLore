# Novelpia-Style UI Redesign (Full Stack)

## Context

### Original Request
ForkLore의 프론트엔드 페이지들(/novels, /ranking, /community)을 Novelpia 스타일로 리디자인. 백엔드 필드 추가 포함.

### Interview Summary
**Key Discussions**:
- Phase 1 완료: 8 commits, 45 tests passing, basic pages working
- Novelpia 디자인: PLUS/독점 badges, stats row, hashtag pills, category tabs
- TDD 방식 확정
- "Inspired By" 스코프 (1:1 클론 아님)
- 우선순위: /novels → /ranking → /community

**Research Findings**:
- Novelpia: 가로 스크롤 장르 필터, 최대 8개 해시태그, compact stats (1.52M)
- Category tabs: 전체/베테랑/독점/신작/완결
- Two layouts: mobile (compact) vs desktop (expanded)

### Metis Review
**Identified Gaps** (addressed):
- 백엔드에 isExclusive/isPremium 필드 없음 → 백엔드 수정 포함으로 해결
- Novel vs RankingNovel 타입 불일치 → 공통 Base 타입으로 해결
- /community 레퍼런스 없음 → 최소 변경으로 해결

---

## Work Objectives

### Core Objective
ForkLore의 /novels, /ranking, /community 페이지를 Novelpia 스타일로 리디자인하고, 필요한 백엔드 필드를 추가한다.

### Concrete Deliverables
- `backend/apps/novels/models.py`: `is_exclusive`, `is_premium` 필드 추가
- `backend/apps/novels/serializers.py`: 새 필드 직렬화
- `frontend/lib/types.ts`: `NovelBase`, `Novel`, `RankingNovel` 타입 정의
- `frontend/lib/mock-data.ts`: 새 필드로 mock 데이터 업데이트
- `frontend/components/feature/novels/novelpia-card.tsx`: Novelpia 스타일 카드
- `frontend/components/feature/novels/novel-badge.tsx`: PLUS/독점 배지
- `frontend/components/feature/novels/stats-row.tsx`: 조회수/회차/추천 통계
- `frontend/components/feature/novels/hashtag-pills.tsx`: 해시태그 필
- `frontend/components/feature/novels/category-tabs.tsx`: 카테고리 탭
- `frontend/app/novels/page.tsx`: Novelpia 스타일로 업데이트
- `frontend/app/ranking/page.tsx`: Novelpia 스타일로 업데이트
- `frontend/app/community/page.tsx`: 카드 스타일만 통일

### Definition of Done
- [ ] `cd backend && poetry run pytest` → All tests pass
- [ ] `cd frontend && pnpm test` → All tests pass (기존 45개 + 새 테스트)
- [ ] `cd frontend && pnpm build` → No errors
- [ ] 모든 3개 페이지가 Novelpia 스타일로 렌더링

### Must Have
- TDD: 테스트 먼저 작성
- TypeScript strict 유지 (no `any`)
- 기존 45개 테스트 모두 통과
- 백엔드 마이그레이션 포함
- PLUS/독점 배지 표시
- Stats row (조회수, 회차수, 추천수)

### Must NOT Have (Guardrails)
- ❌ `/novels/[id]` 상세 페이지 수정 (스코프 외)
- ❌ 새로운 상태관리 라이브러리 추가
- ❌ 기존 테스트 삭제 (업데이트만 허용)
- ❌ 복잡한 애니메이션 추가
- ❌ i18n/다국어 작업
- ❌ 실제 API 연동 (mock 데이터 사용)

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (pnpm test, pytest)
- **User wants tests**: TDD
- **Framework**: Vitest (frontend), Pytest (backend)

### TDD Workflow
각 TODO는 RED-GREEN-REFACTOR 패턴 따름:
1. **RED**: 실패하는 테스트 먼저 작성
2. **GREEN**: 테스트 통과하는 최소 구현
3. **REFACTOR**: 코드 정리 (테스트 유지)

---

## Task Flow

```
Task 0 (Backend) → Task 1 (Types) → Task 2 (Mock Data)
                                          ↓
Task 3 (Badge) ─┬─ Task 4 (StatsRow) ─┬─ Task 5 (Hashtags)
                │                      │
                └──────────────────────┴─→ Task 6 (NovelpiaCard)
                                                    ↓
                                          Task 7 (CategoryTabs)
                                                    ↓
                                          Task 8 (/novels page)
                                                    ↓
                                          Task 9 (/ranking page)
                                                    ↓
                                          Task 10 (/community page)
                                                    ↓
                                          Task 11 (Final verification)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 3, 4, 5 | 독립적인 UI 컴포넌트들 |

| Task | Depends On | Reason |
|------|------------|--------|
| 1 | 0 | 백엔드 스키마 확정 후 타입 정의 |
| 2 | 1 | 타입 정의 후 mock 데이터 |
| 6 | 3, 4, 5 | 하위 컴포넌트 완성 후 조합 |
| 8 | 6, 7 | 카드와 탭 완성 후 페이지 조립 |

---

## TODOs

- [x] 0. Backend: Novel 모델에 is_exclusive, is_premium 필드 추가

  **What to do**:
  - `backend/apps/novels/models.py`에 `is_exclusive = models.BooleanField(default=False)` 추가
  - `backend/apps/novels/models.py`에 `is_premium = models.BooleanField(default=False)` 추가
  - 마이그레이션 생성: `python manage.py makemigrations`
  - 마이그레이션 적용: `python manage.py migrate`
  - `backend/apps/novels/serializers.py`에 새 필드 추가
  - 테스트 작성: 필드 존재 및 기본값 확인

  **Must NOT do**:
  - 다른 모델 수정
  - 기존 필드 변경
  - Chapter의 access_type 수정 (별개 개념)

  **Parallelizable**: NO (첫 번째 태스크)

  **References**:
  - `backend/apps/novels/models.py` - Novel 모델 정의
  - `backend/apps/novels/serializers.py` - NovelSerializer 정의
  - `backend/apps/novels/tests/` - 기존 테스트 패턴
  - `backend/apps/contents/models.py:13-15` - AccessType enum 패턴 참조 (FREE/SUBSCRIPTION)
  - `backend/apps/contents/models.py:30-32` - access_type 필드 구현 패턴 참조
  
  **Context Note**:
  > Chapter에는 이미 `access_type` (FREE/SUBSCRIPTION)이 있음.
  > Novel 레벨의 `is_exclusive`/`is_premium`은 작품 전체 속성 (독점 계약, 프리미엄 서비스).
  > Chapter의 access_type은 개별 회차의 유료/무료 여부. 별개 개념임.

  **Acceptance Criteria**:
  - [ ] 테스트 작성: `test_novel_has_is_exclusive_field`, `test_novel_has_is_premium_field`
  - [ ] `cd backend && poetry run pytest apps/novels/tests/` → PASS
  - [ ] 마이그레이션 파일 생성됨
  - [ ] Serializer에서 새 필드 반환 확인

  **Commit**: YES
  - Message: `feat(novels): add is_exclusive and is_premium fields to Novel model`
  - Files: `backend/apps/novels/models.py`, `backend/apps/novels/serializers.py`, `backend/apps/novels/migrations/`

---

- [x] 1. Frontend: NovelBase 공통 타입 및 확장 타입 정의

  **What to do**:
  - `frontend/lib/types.ts` 생성 (또는 기존 파일 확장)
  - `NovelBase` 인터페이스 정의 (공통 필드)
  - `Novel extends NovelBase` 정의
  - `RankingNovel extends NovelBase` 정의
  - 새 필드 포함: `episodeCount`, `recommendCount`, `isExclusive`, `isPremium`, `updatedAt`, `description`

  **Must NOT do**:
  - 기존 mock-data.ts의 인터페이스 직접 수정 (types.ts로 이동)
  - `any` 타입 사용

  **Parallelizable**: NO (Task 0 완료 후)

  **References**:
  - `frontend/lib/mock-data.ts:1-30` - 기존 Novel, RankingNovel 인터페이스
  - `backend/apps/novels/serializers.py` - 백엔드 필드명 참조

  **Acceptance Criteria**:
  - [ ] `frontend/lib/types.ts` 파일 존재
  - [ ] `NovelBase` 타입 정의됨
  - [ ] `Novel`, `RankingNovel` 타입이 `NovelBase` 확장
  - [ ] `pnpm tsc --noEmit` → No errors

  **Commit**: YES
  - Message: `refactor(types): create NovelBase shared type with Novel and RankingNovel extensions`
  - Files: `frontend/lib/types.ts`

---

- [x] 2. Frontend: Mock 데이터에 새 필드 추가

  **What to do**:
  - `frontend/lib/mock-data.ts`의 인터페이스를 `types.ts`에서 import하도록 변경
  - `NOVELS_LIST`에 새 필드 추가: `episodeCount`, `recommendCount`, `isExclusive`, `isPremium`, `updatedAt`, `description`
  - `RANKING_NOVELS`에 새 필드 추가
  - 기존 테스트 mock 데이터 업데이트

  **Must NOT do**:
  - 기존 테스트 삭제
  - 기존 필드 제거

  **Parallelizable**: NO (Task 1 완료 후)

  **References**:
  - `frontend/lib/mock-data.ts` - 기존 mock 데이터
  - `frontend/lib/types.ts` - 새 타입 정의
  - `frontend/components/feature/novels/__tests__/` - 기존 테스트 파일들

  **Acceptance Criteria**:
  - [ ] 모든 mock 소설에 새 필드 존재
  - [ ] `pnpm test` → 기존 45개 테스트 통과
  - [ ] `pnpm tsc --noEmit` → No errors

  **Commit**: YES
  - Message: `feat(mock): extend mock data with Novelpia-style fields`
  - Files: `frontend/lib/mock-data.ts`

---

- [x] 3. Frontend: NovelBadge 컴포넌트 (PLUS/독점 배지)

  **What to do**:
  - TDD: `frontend/components/feature/novels/__tests__/novel-badge.test.tsx` 먼저 작성
  - `frontend/components/feature/novels/novel-badge.tsx` 구현
  - Props: `isPremium?: boolean`, `isExclusive?: boolean`
  - PLUS 배지: 골드 배경, 흰 텍스트
  - 독점 배지: 파란 배경, 흰 텍스트
  - 기존 `frontend/components/ui/badge.tsx` 활용

  **Must NOT do**:
  - 기존 Badge 컴포넌트 수정
  - 애니메이션 추가

  **Parallelizable**: YES (Task 4, 5와 병렬 가능)

  **References**:
  - `frontend/components/ui/badge.tsx` - 기존 Badge 컴포넌트
  - Novelpia 디자인: PLUS는 골드(#FFD700), 독점은 파란색(#3B82F6)

  **Acceptance Criteria**:
  - [ ] RED: `novel-badge.test.tsx` 작성, 테스트 실패 확인
  - [ ] GREEN: 컴포넌트 구현, `pnpm test novel-badge` → PASS
  - [ ] `isPremium=true` → "PLUS" 배지 렌더링
  - [ ] `isExclusive=true` → "독점" 배지 렌더링
  - [ ] 둘 다 true → 두 배지 모두 렌더링

  **Commit**: YES
  - Message: `feat(novels): add NovelBadge component for PLUS and exclusive badges`
  - Files: `frontend/components/feature/novels/novel-badge.tsx`, `frontend/components/feature/novels/__tests__/novel-badge.test.tsx`

---

- [x] 4. Frontend: StatsRow 컴포넌트 (조회수/회차/추천)

  **What to do**:
  - TDD: `frontend/components/feature/novels/__tests__/stats-row.test.tsx` 먼저 작성
  - `frontend/components/feature/novels/stats-row.tsx` 구현
  - Props: `views: number`, `episodeCount: number`, `recommendCount: number`
  - 숫자 포맷팅: 1000 → 1K, 1000000 → 1M
  - 아이콘: Eye (조회), Book (회차), ThumbsUp (추천)
  - lucide-react 아이콘 사용

  **Must NOT do**:
  - 새 아이콘 라이브러리 추가
  - 클릭 핸들러 추가 (표시 전용)

  **Parallelizable**: YES (Task 3, 5와 병렬 가능)

  **References**:
  - `frontend/components/feature/ranking/ranking-list.tsx` - 기존 통계 표시 패턴
  - Novelpia 포맷: "1.52M명", "242회차", "42.5K회"

  **Acceptance Criteria**:
  - [ ] RED: `stats-row.test.tsx` 작성, 테스트 실패 확인
  - [ ] GREEN: 컴포넌트 구현, `pnpm test stats-row` → PASS
  - [ ] 1520000 → "1.52M" 포맷팅 테스트
  - [ ] 42500 → "42.5K" 포맷팅 테스트
  - [ ] 3개 통계 모두 아이콘과 함께 렌더링

  **Commit**: YES
  - Message: `feat(novels): add StatsRow component with formatted view/episode/recommendation counts`
  - Files: `frontend/components/feature/novels/stats-row.tsx`, `frontend/components/feature/novels/__tests__/stats-row.test.tsx`

---

- [x] 5. Frontend: HashtagPills 컴포넌트

  **What to do**:
  - TDD: `frontend/components/feature/novels/__tests__/hashtag-pills.test.tsx` 먼저 작성
  - `frontend/components/feature/novels/hashtag-pills.tsx` 구현
  - Props: `tags: string[]`, `maxDisplay?: number` (기본값 8)
  - 각 태그를 "#태그명" 형식의 pill로 렌더링
  - 최대 개수 초과 시 "+N more" 표시

  **Must NOT do**:
  - 클릭 시 필터링 기능 (표시 전용)
  - 태그 수정/삭제 기능

  **Parallelizable**: YES (Task 3, 4와 병렬 가능)

  **References**:
  - `frontend/components/ui/badge.tsx` - pill 스타일링 참조
  - Novelpia 디자인: "#판타지 #하렘 #일상" 형식

  **Acceptance Criteria**:
  - [ ] RED: `hashtag-pills.test.tsx` 작성, 테스트 실패 확인
  - [ ] GREEN: 컴포넌트 구현, `pnpm test hashtag-pills` → PASS
  - [ ] 8개 이하 태그 → 모두 표시
  - [ ] 10개 태그, maxDisplay=8 → 8개 + "+2 more" 표시
  - [ ] 빈 배열 → 아무것도 렌더링하지 않음

  **Commit**: YES
  - Message: `feat(novels): add HashtagPills component with max display limit`
  - Files: `frontend/components/feature/novels/hashtag-pills.tsx`, `frontend/components/feature/novels/__tests__/hashtag-pills.test.tsx`

---

- [x] 6. Frontend: NovelpiaCard 컴포넌트 (통합 카드)

  **What to do**:
  - TDD: `frontend/components/feature/novels/__tests__/novelpia-card.test.tsx` 먼저 작성
  - `frontend/components/feature/novels/novelpia-card.tsx` 구현
  - NovelBadge, StatsRow, HashtagPills 조합
  - Props: `novel: Novel | RankingNovel`
  - 레이아웃: 커버 이미지 (좌), 정보 (우)
  - 상대 시간 표시: "3분전 UP" 형식

  **Must NOT do**:
  - 기존 novel-card.tsx 삭제 (공존)
  - 복잡한 호버 애니메이션

  **Parallelizable**: NO (Task 3, 4, 5 완료 후)

  **References**:
  - `frontend/components/feature/novels/novel-badge.tsx` - 배지 컴포넌트
  - `frontend/components/feature/novels/stats-row.tsx` - 통계 컴포넌트
  - `frontend/components/feature/novels/hashtag-pills.tsx` - 해시태그 컴포넌트
  - Novelpia 카드 레이아웃 참조

  **Acceptance Criteria**:
  - [ ] RED: `novelpia-card.test.tsx` 작성, 테스트 실패 확인
  - [ ] GREEN: 컴포넌트 구현, `pnpm test novelpia-card` → PASS
  - [ ] Novel 타입과 RankingNovel 타입 모두 렌더링 가능
  - [ ] 배지, 통계, 해시태그 모두 표시
  - [ ] "3분전 UP" 상대 시간 표시 (updatedAt 기준)

  **Commit**: YES
  - Message: `feat(novels): add NovelpiaCard component combining badge, stats, and hashtags`
  - Files: `frontend/components/feature/novels/novelpia-card.tsx`, `frontend/components/feature/novels/__tests__/novelpia-card.test.tsx`

---

- [x] 7. Frontend: CategoryTabs 컴포넌트

  **What to do**:
  - TDD: `frontend/components/feature/novels/__tests__/category-tabs.test.tsx` 먼저 작성
  - `frontend/components/feature/novels/category-tabs.tsx` 구현
  - 탭 목록: 전체, 베테랑, 독점, 신작, 완결
  - Props: `activeCategory: string`, `onCategoryChange: (category: string) => void`
  - 기존 `frontend/components/ui/tabs.tsx` 활용

  **Must NOT do**:
  - 실제 필터링 로직 구현 (UI만)
  - URL 파라미터 연동

  **Parallelizable**: YES (Task 6과 병렬 가능)

  **References**:
  - `frontend/components/ui/tabs.tsx` - 기존 Tabs 컴포넌트
  - `frontend/components/feature/ranking/ranking-tabs.tsx` - 유사 패턴

  **Acceptance Criteria**:
  - [ ] RED: `category-tabs.test.tsx` 작성, 테스트 실패 확인
  - [ ] GREEN: 컴포넌트 구현, `pnpm test category-tabs` → PASS
  - [ ] 5개 탭 모두 렌더링
  - [ ] 탭 클릭 시 onCategoryChange 호출
  - [ ] activeCategory에 따른 활성 상태 표시

  **Commit**: YES
  - Message: `feat(novels): add CategoryTabs component for novel filtering`
  - Files: `frontend/components/feature/novels/category-tabs.tsx`, `frontend/components/feature/novels/__tests__/category-tabs.test.tsx`

---

- [ ] 8. Frontend: /novels 페이지 Novelpia 스타일로 업데이트

  **What to do**:
  - 기존 `frontend/app/novels/page.tsx` 수정
  - CategoryTabs 추가 (상단)
  - NovelGrid를 NovelpiaCard 기반으로 교체
  - 기존 NovelFilters 유지 (장르, 정렬)
  - InfiniteNovelList는 유지하되 NovelpiaCard 사용

  **Must NOT do**:
  - 기존 컴포넌트 삭제 (새 컴포넌트와 공존)
  - 라우팅 구조 변경

  **Parallelizable**: NO (Task 6, 7 완료 후)

  **References**:
  - `frontend/app/novels/page.tsx` - 기존 페이지 구조
  - `frontend/components/feature/novels/infinite-novel-list.tsx` - 기존 무한 스크롤
  - `frontend/components/feature/novels/novelpia-card.tsx` - 새 카드 컴포넌트

  **Acceptance Criteria**:
  - [ ] `pnpm test` → 모든 테스트 통과
  - [ ] CategoryTabs가 페이지 상단에 렌더링
  - [ ] NovelpiaCard로 소설 목록 표시
  - [ ] 기존 필터/정렬 기능 유지
  - [ ] 무한 스크롤 기능 유지
  - [ ] Playwright: `http://localhost:3000/novels` 접속 → Novelpia 스타일 확인

  **Commit**: YES
  - Message: `feat(novels): update /novels page with Novelpia-style components`
  - Files: `frontend/app/novels/page.tsx`

---

- [ ] 9. Frontend: /ranking 페이지 Novelpia 스타일로 업데이트

  **What to do**:
  - 기존 `frontend/app/ranking/page.tsx` 수정
  - RankingList를 NovelpiaCard 기반으로 업데이트
  - 순위 표시 유지 (금/은/동 배지)
  - 기존 period tabs 유지 (daily/weekly/monthly)

  **Must NOT do**:
  - 기존 ranking-tabs.tsx 삭제
  - 순위 배지 스타일 변경

  **Parallelizable**: NO (Task 8 완료 후)

  **References**:
  - `frontend/app/ranking/page.tsx` - 기존 페이지 구조
  - `frontend/components/feature/ranking/ranking-list.tsx` - 기존 랭킹 리스트
  - `frontend/components/feature/novels/novelpia-card.tsx` - 새 카드 컴포넌트

  **Acceptance Criteria**:
  - [ ] `pnpm test` → 모든 테스트 통과
  - [ ] NovelpiaCard로 랭킹 목록 표시
  - [ ] 순위 배지 (1, 2, 3위) 유지
  - [ ] Period tabs 기능 유지
  - [ ] Playwright: `http://localhost:3000/ranking` 접속 → 스타일 확인

  **Commit**: YES
  - Message: `feat(ranking): update /ranking page with Novelpia-style cards`
  - Files: `frontend/app/ranking/page.tsx`, `frontend/components/feature/ranking/ranking-list.tsx`

---

- [ ] 10. Frontend: /community 페이지 카드 스타일 통일

  **What to do**:
  - 기존 `frontend/app/community/page.tsx` 수정
  - PostCard 스타일을 Novelpia 카드와 유사하게 조정
  - 기존 구조 유지 (카테고리 탭, 포스트 리스트)

  **Must NOT do**:
  - 커뮤니티 기능 변경
  - 새 컴포넌트 추가

  **Parallelizable**: NO (Task 9 완료 후)

  **References**:
  - `frontend/app/community/page.tsx` - 기존 페이지 구조
  - `frontend/components/feature/community/post-card.tsx` - 기존 포스트 카드
  - `frontend/components/feature/novels/novelpia-card.tsx` - 스타일 참조

  **Acceptance Criteria**:
  - [ ] `pnpm test` → 모든 테스트 통과
  - [ ] PostCard 스타일이 NovelpiaCard와 유사
  - [ ] 기존 기능 모두 유지
  - [ ] Playwright: `http://localhost:3000/community` 접속 → 스타일 확인

  **Commit**: YES
  - Message: `style(community): align PostCard styling with Novelpia design`
  - Files: `frontend/components/feature/community/post-card.tsx`

---

- [ ] 11. Final Verification: 전체 테스트 및 빌드 확인

  **What to do**:
  - 모든 백엔드 테스트 실행
  - 모든 프론트엔드 테스트 실행
  - 프론트엔드 빌드 확인
  - 3개 페이지 모두 수동 확인

  **Must NOT do**:
  - 새 코드 작성
  - 테스트 스킵

  **Parallelizable**: NO (모든 태스크 완료 후)

  **References**:
  - 모든 이전 태스크

  **Acceptance Criteria**:
  - [ ] `cd backend && poetry run pytest` → All PASS
  - [ ] `cd frontend && pnpm test` → All PASS (기존 45개 + 새 테스트)
  - [ ] `cd frontend && pnpm build` → Success
  - [ ] Playwright로 3개 페이지 스크린샷 캡처
  - [ ] TypeScript 에러 0개

  **Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | `feat(novels): add is_exclusive and is_premium fields` | backend/apps/novels/* | `pytest` |
| 1 | `refactor(types): create NovelBase shared type` | frontend/lib/types.ts | `tsc --noEmit` |
| 2 | `feat(mock): extend mock data with Novelpia fields` | frontend/lib/mock-data.ts | `pnpm test` |
| 3 | `feat(novels): add NovelBadge component` | frontend/components/feature/novels/* | `pnpm test` |
| 4 | `feat(novels): add StatsRow component` | frontend/components/feature/novels/* | `pnpm test` |
| 5 | `feat(novels): add HashtagPills component` | frontend/components/feature/novels/* | `pnpm test` |
| 6 | `feat(novels): add NovelpiaCard component` | frontend/components/feature/novels/* | `pnpm test` |
| 7 | `feat(novels): add CategoryTabs component` | frontend/components/feature/novels/* | `pnpm test` |
| 8 | `feat(novels): update /novels page Novelpia style` | frontend/app/novels/page.tsx | `pnpm test && pnpm build` |
| 9 | `feat(ranking): update /ranking page Novelpia style` | frontend/app/ranking/* | `pnpm test && pnpm build` |
| 10 | `style(community): align PostCard with Novelpia` | frontend/components/feature/community/* | `pnpm test` |

---

## Success Criteria

### Verification Commands
```bash
# Backend
cd backend && poetry run pytest  # Expected: All tests pass

# Frontend
cd frontend && pnpm test         # Expected: 45+ tests pass
cd frontend && pnpm build        # Expected: Success, no errors
cd frontend && pnpm tsc --noEmit # Expected: No TypeScript errors
```

### Final Checklist
- [ ] 모든 "Must Have" 구현됨
- [ ] 모든 "Must NOT Have" 지켜짐
- [ ] 기존 45개 테스트 통과
- [ ] 새 컴포넌트 테스트 커버리지 ≥ 80%
- [ ] /novels, /ranking, /community 페이지 Novelpia 스타일 적용
- [ ] TypeScript strict 모드 에러 없음
