# PR #245 Review Fixes

## Context

### Original Request
PR #245 코드 리뷰 코멘트 해결

### Key Issues
1. **Genre enum 누락**: 6개 장르가 mappings.ts에서 삭제됨 (LIGHT_NOVEL, BL, GL, TS, SPORTS, ALTERNATIVE_HISTORY)
2. **Next.js params 패턴 오류**: params는 Promise가 아닌 일반 객체
3. **에러 처리 부족**: 모든 에러를 404로 처리
4. **하드코딩 값들**: rating 4.5, 플레이스홀더 챕터 데이터
5. **테스트 품질**: 미사용 변수, 오해 소지 테스트명, 타입 안전성

---

## Work Objectives

### Core Objective
PR 리뷰 코멘트를 해결하여 코드 품질 개선

### Definition of Done
- [x] 모든 Critical 이슈 해결
- [x] 모든 Medium 이슈 해결
- [x] 테스트 통과
- [x] 빌드 성공

---

## TODOs

- [x] 1. Genre enum 복원 (CRITICAL)

  **What to do**:
  - `novels.types.ts`에 누락된 Genre 추가:
    - LIGHT_NOVEL, BL, GL, TS, SPORTS, ALTERNATIVE_HISTORY
  - `mappings.ts`에 해당 라벨 추가:
    - 라이트노벨, BL, GL, TS, 스포츠, 대체역사

  **References**:
  - `frontend/types/novels.types.ts:7-18`
  - `frontend/lib/utils/mappings.ts:3-14`

  **Acceptance Criteria**:
  - [ ] Genre enum에 6개 항목 추가됨
  - [ ] GENRE_LABELS에 6개 라벨 추가됨
  - [ ] TypeScript 에러 없음

  **Commit**: YES
  - Message: `fix(mappings): restore missing genre types`

---

- [x] 2. Next.js params 패턴 수정 (CRITICAL)

  **What to do**:
  - `novels/[id]/page.tsx` 수정:
    - `params: Promise<{ id: string }>` → `params: { id: string }`
    - `await params` 제거

  **References**:
  - `frontend/app/novels/[id]/page.tsx:15`
  - Next.js App Router 공식 문서

  **Acceptance Criteria**:
  - [ ] params 타입이 일반 객체로 변경됨
  - [ ] await 제거됨
  - [ ] 빌드 성공

  **Commit**: YES (Task 3과 함께)

---

- [x] 3. 에러 처리 개선 (CRITICAL)

  **What to do**:
  - 404와 다른 에러 구분:
    ```typescript
    catch (error: unknown) {
      const status = (error as any)?.response?.status;
      if (status === 404) {
        notFound();
      }
      console.error('Failed to fetch novel:', error);
      throw error;
    }
    ```

  **References**:
  - `frontend/app/novels/[id]/page.tsx:21`

  **Acceptance Criteria**:
  - [ ] 404 에러만 notFound() 호출
  - [ ] 다른 에러는 console.error + rethrow

  **Commit**: YES
  - Message: `fix(novel-detail): improve error handling and fix params pattern`

---

- [x] 4. rating 하드코딩 제거 (MEDIUM)

  **What to do**:
  - `rating: 4.5` → `rating: novel.average_rating ?? 0`
  - Novel 타입에 average_rating 필드 확인/추가

  **References**:
  - `frontend/app/novels/[id]/page.tsx:38`
  - `frontend/types/novels.types.ts`

  **Acceptance Criteria**:
  - [ ] rating이 실제 데이터 사용
  - [ ] average_rating 없으면 0 표시

  **Commit**: YES (Task 5와 함께)

---

- [x] 5. CHAPTERS 데이터 개선 (MEDIUM)

  **What to do**:
  - 각 챕터에 다른 날짜 부여 (created_at + i일)
  - 처음 3개는 무료, 나머지는 유료 (coins: 10)
  - 또는 TODO 주석으로 "실제 API 연결 필요" 명시

  **References**:
  - `frontend/app/novels/[id]/page.tsx:49`

  **Acceptance Criteria**:
  - [ ] 챕터별 날짜 다름
  - [ ] 가격 정책 반영됨

  **Commit**: YES
  - Message: `fix(novel-detail): use real rating and improve chapter data`

---

- [x] 6. React.memo 비교 함수 수정 (MEDIUM)

  **What to do**:
  - `post-card.tsx`: commentCount, likeCount 비교에 포함
  - 주석 업데이트하여 의도 명확화

  **References**:
  - `frontend/components/feature/community/post-card.tsx:54`

  **Acceptance Criteria**:
  - [ ] count 변경 시 리렌더 됨
  - [ ] 테스트 통과

  **Commit**: YES
  - Message: `fix(post-card): include counts in memo comparison`

---

- [x] 7. branch-card 에러 로깅 추가 (MEDIUM)

  **What to do**:
  - `_error` → `error`
  - `console.error("Failed to update vote:", error)` 추가

  **References**:
  - `frontend/components/feature/branches/branch-card.tsx:42`

  **Acceptance Criteria**:
  - [ ] 에러 로깅됨
  - [ ] 테스트 통과

  **Commit**: YES
  - Message: `fix(branch-card): add error logging for vote failures`

---

- [x] 8. user-profile useQueries 타입 개선 (MEDIUM)

  **What to do**:
  - 타입 캐스팅 대신 proper 타입 가드 사용
  - 또는 UseQueryResult 타입 명시

  **References**:
  - `frontend/components/feature/users/user-profile.tsx:34`

  **Acceptance Criteria**:
  - [ ] 타입 안전성 개선
  - [ ] as 캐스팅 제거 또는 최소화

  **Commit**: YES
  - Message: `fix(user-profile): improve useQueries type safety`

---

- [x] 9. 테스트 품질 개선 (LOW - Batch)

  **What to do**:
  - `branch-choices.test.tsx`: 미사용 container 변수 4곳 제거
  - `user-profile.test.tsx`: 미사용 createMockResponse 제거
  - `infinite-novel-list.test.tsx`: render import 정리
  - `vitest.config.ts`: 중복 e2e 패턴 정리

  **References**:
  - 해당 테스트 파일들

  **Acceptance Criteria**:
  - [ ] 미사용 변수 없음
  - [ ] import 깔끔함
  - [ ] 테스트 통과

  **Commit**: YES
  - Message: `chore(tests): remove unused variables and clean imports`

---

- [x] 10. 최종 검증 및 푸시

  **What to do**:
  - `pnpm test --run`
  - `pnpm build`
  - `git push`

  **Acceptance Criteria**:
  - [ ] 테스트 통과
  - [ ] 빌드 성공
  - [ ] PR 업데이트됨

  **Commit**: NO (푸시만)

---

## Commit Strategy

| After Task | Message |
|------------|---------|
| 1 | `fix(mappings): restore missing genre types` |
| 2-3 | `fix(novel-detail): improve error handling and fix params pattern` |
| 4-5 | `fix(novel-detail): use real rating and improve chapter data` |
| 6 | `fix(post-card): include counts in memo comparison` |
| 7 | `fix(branch-card): add error logging for vote failures` |
| 8 | `fix(user-profile): improve useQueries type safety` |
| 9 | `chore(tests): remove unused variables and clean imports` |
| 10 | (push only) |

---

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 1 | 독립적 (types + mappings) |
| B | 2, 3, 4, 5 | 동일 파일 (novel-detail) |
| C | 6, 7, 8 | 독립적 컴포넌트 |
| D | 9 | 테스트 파일만 |

**Recommended Order**: 1 → B(2-5) → C(6-8 parallel) → 9 → 10
