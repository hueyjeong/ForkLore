# 소설 페이지 UI 버그 수정

## Context

### Original Request
/novels 페이지의 여러 UI 문제 수정:
1. 독점/Plus 태그가 없으면 다른 작품들과 높이가 안 맞음
2. 인기순/최신순 정렬 배경이 투명해서 작품 아웃라인과 겹쳐보임
3. 컬럼 2개로 제한해서 작품 제목이 잘리지 않게
4. 베테랑 → 멤버십으로 이름 변경
5. 스크롤 시 padding-top이 늘어나서 작품이 밀려서 안 보임

### Interview Summary
**Key Discussions**:
- 베테랑 탭 제거 대신 "멤버십"으로 이름 변경 (PLUS 필터 유지)
- 스크롤 문제: 일정 수준 이상 스크롤 시 발생
- Select 배경색: `bg-background` 사용

**Research Findings**:
- `NovelBadge`가 배지 없으면 `null` 반환 → 높이 불일치
- `SelectTrigger`가 `bg-transparent` 사용 (shadcn 기본값)
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Virtuoso `useWindowScroll` + sticky 헤더 충돌 가능성

### Metis Review
**Identified Gaps** (addressed):
- 베테랑 제거 시 PLUS 필터 불가 → 멤버십으로 이름 변경
- 정확한 min-height 값 → 24px (배지 높이 기준)
- `?category=베테랑` URL → 멤버십으로 fallback 불필요 (이름만 변경)

---

## Work Objectives

### Core Objective
/novels 페이지의 5가지 UI 버그를 수정하여 일관된 레이아웃과 가독성 제공

### Concrete Deliverables
- `frontend/components/feature/novels/novelpia-card.tsx` - 배지 영역 min-height
- `frontend/components/feature/novels/novel-filters.tsx` - Select 배경색
- `frontend/components/feature/novels/infinite-novel-list.tsx` - 2컬럼 고정
- `frontend/components/feature/novels/category-tabs.tsx` - 베테랑→멤버십, grid-cols-4

### Definition of Done
- [x] `cd frontend && pnpm test` → All tests pass
- [x] `cd frontend && pnpm build` → No errors
- [x] 모든 카드 높이 일관성 확인
- [x] Select가 카드와 겹치지 않음

### Must Have
- 배지 없는 카드도 동일 높이
- Select 배경 불투명
- 2컬럼 레이아웃
- 멤버십 탭 (PLUS 필터 유지)

### Must NOT Have (Guardrails)
- ❌ `components/ui/select.tsx` 수정 (shadcn 베이스 컴포넌트)
- ❌ `novel-badge.tsx` 수정 (공유 컴포넌트)
- ❌ Virtuoso 핵심 설정 변경 (`useWindowScroll`, `overscan`)
- ❌ 새로운 상태 관리 추가
- ❌ 헤더 높이 리팩토링

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pnpm test)
- **User wants tests**: Tests-after (기존 테스트 유지)
- **Framework**: Vitest

### Manual QA Required
- 브라우저에서 /novels 페이지 시각적 확인
- 스크롤 동작 테스트

---

## Task Flow

```
Task 1 (Badge height) ─┬─ Task 2 (Select bg) ─┬─ Task 3 (Grid cols)
                       │                      │
                       └──────────────────────┴─→ Task 4 (Tab rename)
                                                          ↓
                                                  Task 5 (Scroll fix)
                                                          ↓
                                                  Task 6 (Verification)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 1, 2, 3, 4 | 독립적인 CSS/텍스트 변경 |

| Task | Depends On | Reason |
|------|------------|--------|
| 5 | 1-4 | 다른 수정 후 스크롤 테스트 |
| 6 | 1-5 | 최종 검증 |

---

## TODOs

- [x] 1. 배지 영역 min-height 추가

  **What to do**:
  - `frontend/components/feature/novels/novelpia-card.tsx` line 52 수정
  - 배지+제목 wrapper에 `min-h-6` (24px) 추가

  **Must NOT do**:
  - `novel-badge.tsx` 수정
  - 다른 카드 영역 수정

  **Parallelizable**: YES (Task 2, 3, 4와 병렬)

  **References**:
  - `frontend/components/feature/novels/novelpia-card.tsx:52` - 수정 대상
  - `frontend/components/feature/novels/novel-badge.tsx:9` - null 반환 확인

  **Acceptance Criteria**:
  - [ ] 배지 없는 카드와 있는 카드의 높이가 동일
  - [ ] `pnpm test` → Pass
  - [ ] 수정된 라인에 `min-h-6` 포함

  **Commit**: YES
  - Message: `fix(novels): add min-height to badge area for consistent card height`
  - Files: `frontend/components/feature/novels/novelpia-card.tsx`

---

- [x] 2. Select 배경색 추가

  **What to do**:
  - `frontend/components/feature/novels/novel-filters.tsx` line 108 수정
  - `SelectTrigger`에 `bg-background` 클래스 추가

  **Must NOT do**:
  - `components/ui/select.tsx` 수정
  - 다른 Select 인스턴스 수정

  **Parallelizable**: YES (Task 1, 3, 4와 병렬)

  **References**:
  - `frontend/components/feature/novels/novel-filters.tsx:108` - 수정 대상
  - `frontend/components/ui/select.tsx:40` - bg-transparent 기본값 확인

  **Acceptance Criteria**:
  - [ ] Select가 카드 위에서 겹치지 않음 (배경 불투명)
  - [ ] `pnpm test` → Pass
  - [ ] 수정된 라인에 `bg-background` 포함

  **Commit**: YES
  - Message: `fix(novels): add background to sort select for visibility`
  - Files: `frontend/components/feature/novels/novel-filters.tsx`

---

- [x] 3. 그리드 2컬럼으로 제한

  **What to do**:
  - `frontend/components/feature/novels/infinite-novel-list.tsx` line 112 수정
  - `lg:grid-cols-3` 제거하여 최대 2컬럼 유지

  **Must NOT do**:
  - Virtuoso 컴포넌트 구조 변경
  - 모바일 1컬럼 변경

  **Parallelizable**: YES (Task 1, 2, 4와 병렬)

  **References**:
  - `frontend/components/feature/novels/infinite-novel-list.tsx:112` - 수정 대상

  **Acceptance Criteria**:
  - [ ] 데스크탑에서 최대 2컬럼 표시
  - [ ] 제목이 잘리지 않음
  - [ ] `pnpm test` → Pass

  **Commit**: YES
  - Message: `fix(novels): limit grid to 2 columns for better title visibility`
  - Files: `frontend/components/feature/novels/infinite-novel-list.tsx`

---

- [x] 4. 베테랑 → 멤버십 이름 변경

  **What to do**:
  - `frontend/components/feature/novels/category-tabs.tsx` line 10 수정
  - `'베테랑'` → `'멤버십'` 변경
  - `frontend/components/feature/novels/infinite-novel-list.tsx` line 47 수정
  - case 문의 `'베테랑'` → `'멤버십'` 변경

  **Must NOT do**:
  - 필터 로직 변경 (`isPremium` 유지)
  - 탭 개수 변경 (5개 유지)

  **Parallelizable**: YES (Task 1, 2, 3과 병렬)

  **References**:
  - `frontend/components/feature/novels/category-tabs.tsx:10` - CATEGORIES 배열
  - `frontend/components/feature/novels/infinite-novel-list.tsx:47-48` - case 문

  **Acceptance Criteria**:
  - [ ] 탭에 "멤버십" 표시
  - [ ] 멤버십 클릭 시 PLUS(isPremium) 작품 필터링
  - [ ] `pnpm test` → Pass

  **Commit**: YES
  - Message: `fix(novels): rename 베테랑 tab to 멤버십`
  - Files: `frontend/components/feature/novels/category-tabs.tsx`, `frontend/components/feature/novels/infinite-novel-list.tsx`

---

- [x] 5. 스크롤 padding 문제 조사 및 수정

  **What to do**:
  - 스크롤 시 padding-top 증가 원인 조사
  - Virtuoso `useWindowScroll`과 sticky 헤더 상호작용 확인
  - 필요시 수정 적용

  **가능한 수정 방향**:
  - `infinite-novel-list.tsx`에서 Virtuoso 컨테이너에 고정 스타일 추가
  - 또는 부모 컨테이너에 `overflow` 속성 조정

  **Must NOT do**:
  - Virtuoso 핵심 prop 변경 (`useWindowScroll` 제거 금지)
  - 헤더 컴포넌트 수정
  - 전역 스타일 변경

  **Parallelizable**: NO (Task 1-4 완료 후)

  **References**:
  - `frontend/components/feature/novels/infinite-novel-list.tsx:100-121` - Virtuoso 설정
  - `frontend/components/common/header.tsx` - sticky 헤더 (읽기만)
  - `frontend/app/novels/page.tsx` - 페이지 구조

  **Acceptance Criteria**:
  - [ ] 스크롤 시 카드가 밀려서 안 보이는 현상 해결
  - [ ] 다른 스크롤 동작에 영향 없음
  - [ ] `pnpm test` → Pass

  **Commit**: YES (수정이 필요한 경우)
  - Message: `fix(novels): resolve scroll padding issue with Virtuoso`
  - Files: TBD

---

- [x] 6. 최종 검증

  **What to do**:
  - 모든 테스트 실행
  - 빌드 확인
  - 브라우저에서 수동 검증

  **Parallelizable**: NO (모든 태스크 완료 후)

  **References**:
  - 모든 이전 태스크

  **Acceptance Criteria**:
  - [ ] `cd frontend && pnpm test` → All PASS
  - [ ] `cd frontend && pnpm build` → Success
  - [ ] 브라우저에서 /novels 페이지 확인:
    - 카드 높이 일관성
    - Select 배경 불투명
    - 2컬럼 레이아웃
    - 멤버십 탭 동작
    - 스크롤 정상

  **Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(novels): add min-height to badge area` | novelpia-card.tsx | `pnpm test` |
| 2 | `fix(novels): add background to sort select` | novel-filters.tsx | `pnpm test` |
| 3 | `fix(novels): limit grid to 2 columns` | infinite-novel-list.tsx | `pnpm test` |
| 4 | `fix(novels): rename 베테랑 to 멤버십` | category-tabs.tsx, infinite-novel-list.tsx | `pnpm test` |
| 5 | `fix(novels): resolve scroll padding issue` | TBD | `pnpm test` |

---

## Success Criteria

### Verification Commands
```bash
cd /WorkSpace/ForkLore/frontend && pnpm test   # Expected: All pass
cd /WorkSpace/ForkLore/frontend && pnpm build  # Expected: Success
```

### Final Checklist
- [ ] 배지 없는 카드 높이 일관성
- [ ] Select 배경 불투명
- [ ] 최대 2컬럼 레이아웃
- [ ] 멤버십 탭 표시 및 동작
- [ ] 스크롤 정상 동작
- [ ] 모든 기존 테스트 통과
