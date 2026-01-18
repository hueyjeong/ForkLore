# StatsRow 별점 오버플로우 버그 수정

## Context

### Original Request
작품 페이지에서 별(rating)이 칸을 넘어감

### Interview Summary
- **문제**: `StatsRow` 컴포넌트가 좁은 화면에서 오버플로우
- **원인**: `flex-wrap` 누락
- **범위**: 한 줄 CSS 클래스 수정

---

## Work Objectives

### Core Objective
StatsRow 컴포넌트에 `flex-wrap` 추가하여 좁은 화면에서 통계 항목들이 자연스럽게 줄바꿈되도록 수정

### Concrete Deliverables
- `frontend/components/feature/novels/stats-row.tsx` line 32 수정

### Definition of Done
- [x] 수정 후 `pnpm test` 통과
- [x] 좁은 화면에서 별점이 컨테이너 내에 표시됨

### Must Have
- `flex-wrap` 추가
- 기존 gap을 `gap-x-4 gap-y-1`로 분리 (줄바꿈 시 세로 간격 조정)

### Must NOT Have (Guardrails)
- 다른 파일 수정 금지
- 로직 변경 금지 (CSS만 변경)

---

## TODOs

- [x] 1. StatsRow flex-wrap 추가

  **What to do**:
  - `frontend/components/feature/novels/stats-row.tsx` line 32 수정
  - FROM: `flex items-center gap-4`
  - TO: `flex flex-wrap items-center gap-x-4 gap-y-1`

  **Must NOT do**:
  - 다른 컴포넌트 수정
  - 로직 변경

  **Parallelizable**: NO (단일 작업)

  **References**:
  - `frontend/components/feature/novels/stats-row.tsx:32` - 수정 대상 라인

  **Acceptance Criteria**:
  - [x] `cd /WorkSpace/ForkLore/frontend && pnpm test` → 63 tests pass
  - [x] 수정된 라인에 `flex-wrap`과 `gap-x-4 gap-y-1` 포함 확인

  **Commit**: YES
  - Message: `fix(novels): add flex-wrap to StatsRow for narrow screen support`
  - Files: `frontend/components/feature/novels/stats-row.tsx`
  - Pre-commit: `pnpm test`

---

## Success Criteria

### Verification Commands
```bash
cd /WorkSpace/ForkLore/frontend && pnpm test  # Expected: 63 tests pass
grep "flex-wrap" frontend/components/feature/novels/stats-row.tsx  # Expected: 1 match
```

### Final Checklist
- [x] flex-wrap 추가됨
- [x] 테스트 통과
- [x] 커밋 완료

---

## Completion

**Completed**: 2026-01-17
**Commit**: `0ef6af0 fix(novels): add flex-wrap to StatsRow for narrow screen support`
