# Playwright E2E Runbook (ForkLore)

이 문서는 ForkLore에서 Playwright E2E를 **팀이 직접 설계/작성/운영**하기 위한 지침입니다.

> 핵심 철학: “스크린샷 픽셀 비교”가 아니라 **런타임 에러(Next.js) 없음 + 실제 DB 데이터 렌더링**을 성공 조건으로 둡니다.

> 중요: 과거의 “Ralph 전용 스위트/루프 자동화”는 코드에서 제거되었습니다.
> 이 문서는 특정 스위트에 종속되지 않도록, **실제 라우트 트리(frontend/app)** 기준으로 작성됩니다.
> vercel-react-best-practices, web-design-guidelines 스킬을 적극 활용하세요.
---

## 1) 성공 조건 (Stop Condition)

스위트가 아래 조건을 만족하며 통과하면(또는 목표 범위가 모두 충족되면) 사이클을 종료합니다.

- **Next.js 런타임 에러 없음**
  - `pageerror` 이벤트가 0개
  - `console.error`가 0개 (Ralph 스위트는 엄격 모드)
- **백엔드(DB) 데이터가 화면에 실제 렌더링됨**
  - 각 화면에서 “리스트/카드/항목 1개 이상”이 렌더링됨
  - Suspense/스켈레톤/플레이스홀더에 머무르지 않음
- **로그인 플로우는 실제 폼 로그인만 사용**
  - 소셜 로그인(NextAuth 등)은 테스트에서 클릭/사용하지 않음
- (선택) **스크린샷 정책**
  - 실패 분석용: `trace`/`screenshot`은 Playwright 설정에 따름
  - 성공 산출물용: 파일명 규칙(고정/누적)을 팀이 결정

---

## 2) Seed Contract (E2E DB 시드 계약)

현재 E2E seed 데이터는 아래 규모를 전제로 합니다.

| 모델 | 개수 | 용도 |
|------|------|------|
| Users | 21 | 1 reader + 20 authors |
| Novels | 50 | 무한 스크롤 테스트 |
| Branches | 70 | 50 main + 20 fork |
| Chapters | 350+ | 무한 스크롤 테스트 (첫 10개 소설 각 20회차) |
| Wallets | 21 | 결제 테스트 |
| Subscriptions | 1 | 구독 테스트 |
| Purchases | 1 | 소장 테스트 |
| Likes | 1 | 좋아요 테스트 |
| WikiEntries | 1 | 위키 테스트 |
| Maps | 1 | 맵 테스트 |
| AIUsageLogs | 1 | AI 사용량 테스트 |

Ralph 스위트의 기본 데이터 검증 기준은 **“1개 이상”**입니다.
(카운트가 고정돼야 하는 테스트는 별도 고정 계약을 추가로 명시합니다.)

---

## 3) 실행 준비

### 필수 설치

```bash
cd frontend
pnpm install
pnpm exec playwright install chromium
```

### 로컬 실행 (권장)

Playwright 설정이 dual webServer로 백엔드(8001) + 프론트(3000)를 자동 기동합니다.

```bash
cd frontend
pnpm e2e
```

리포트를 보고 싶을 때만 아래를 실행합니다(자동으로 뜨지 않음).

```bash
cd frontend
pnpm e2e:report
```

- 백엔드: `DJANGO_SETTINGS_MODULE=config.settings.e2e ... runserver 8001`
- 프론트: `NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1 pnpm dev`

DB 초기화/시드는 테스트에서 `POST /api/e2e/reset` 호출로 수행합니다.

---

## 4) Ralph Loop 절차

### 4.1 한 사이클

1. `pnpm e2e` 실행
2. 실패하면 실패 원인을 아래로 분류
   - (A) 라우트/페이지 미구현(404)
   - (B) 인증/리다이렉트 문제(쿠키, 미들웨어)
   - (C) API/백엔드 오류(500/serializer/permission)
   - (D) UI 렌더 실패(데이터 0, 로딩 지속)
   - (E) Next 런타임 에러(console error/pageerror)
3. 해당 범주를 구현/수정
4. 다시 1로 반복

### 4.2 멈춤

- Ralph 스위트 전체가 통과하면 종료
- 통과 시 고정 스크린샷 파일들이 최신 상태로 덮어써짐

---

## 5) (권장) 스크린샷/산출물 정책

이 레포는 기본적으로 Playwright `outputDir`을 `frontend/e2e-screenshots/`로 사용합니다.

권장:
- 실패 분석은 `trace: on-first-retry`, `screenshot: only-on-failure`로 충분한 경우가 많습니다.
- 성공 산출물이 필요하면, 팀 룰로 “고정 파일명 덮어쓰기” 또는 “빌드 번호 포함 누적” 중 하나를 선택하세요.

---

## 6) 기능/페이지 매트릭스 (검증 대상)

아래는 **현재 `frontend/app` 기준으로 실제 존재하는 페이지 라우트**입니다.
(동적 라우트는 `{}` 표기)

### 6.1 주요 페이지 라우트

- 홈: `/`
- 로그인: `/login`
- 회원가입: `/signup`
- 소설 목록: `/novels`
- 소설 상세: `/novels/{id}`
- 리더: `/novels/{id}/reader/{chapterId}`
- 브랜치(챕터 목록): `/branches/{id}`
- 브랜치 위키(목록): `/branches/{id}/wikis`
- 위키(목록): `/wikis?branchId={branchId}` (branchId 쿼리 필수)
- 위키(상세): `/wikis/{id}`
- 랭킹: `/ranking`
- 커뮤니티: `/community`
- 검색: `/search`
- 프로필: `/profile`
- 서재: `/library`
- 지갑: `/wallet`
- 구독: `/subscriptions`
- 구독 결제: `/subscriptions/checkout`
- 맵 뷰어: `/map-viewer`
- 작가 스튜디오: `/author/studio`

### 6.2 작성(Authoring) 관련 주의

- 소설 작성/관리 화면으로 **실제 존재하는 경로는 `/author/studio`** 입니다.
- `/publish`는 현재 `frontend/app`에 페이지가 없습니다.
  - 하지만 UI/미들웨어에서 `/publish`가 참조되는 흔적이 있어(예: CTA 링크), 새 AI가 보면 “작성 페이지가 /publish”로 오해하기 쉽습니다.
  - 문서/테스트/플로우 설계 시에는 `/author/studio`를 기준으로 하세요.

- 메인 히어로 섹션: `/` (UI 존재)
- 맞춤 추천 섹션: `/` (DB 기반 작품 카드 1개 이상)
- 로그인(소셜 제외): `/login` (폼 로그인 성공)
- 회원가입: `/signup` (가입→/login 이동)
- 회원 패널: `/profile` (DB 기반 프로필/지갑 렌더)
- 소설 목록: `/novels` (DB 기반 카드 1개 이상 + 다음 페이지 요청 발생)
- 랭킹: `/ranking` (DB 기반 리스트 1개 이상)
- 소설 상세: `/novels/{id}` (DB 기반 title/author 렌더)
- 챕터 목록: `/branches/{branchId}` (DB 기반 챕터 row 1개 이상)
- 연관 브랜치 목록: `/novels/{id}/reader/{chapterId}` 하단 `AVAILABLE BRANCHES` (DB 기반 분기 노출)
- 소설 리더: `/novels/{id}/reader/{chapterId}` (DB 기반 chapter 렌더)
- 위키 섹션: `/wikis?branchId={branchId}` (DB 기반 위키 카드 1개 이상)
- 위키 페이지: `/wikis/{wikiId}` (DB 기반 위키 내용 렌더)
### 6.3 테스트 시나리오 예시(팀이 선택)

- 메인 히어로/추천 섹션: `/` (UI 존재 + DB 기반 카드 1개 이상)
- 로그인(소셜 제외): `/login` (폼 로그인 성공)
- 회원가입: `/signup` (가입 후 흐름)
- 회원 패널: `/profile` (DB 기반 프로필 노출)
- 소설 목록: `/novels` (DB 기반 카드 1개 이상 + 페이징/무한스크롤)
- 랭킹: `/ranking` (DB 기반 리스트 1개 이상)
- 소설 상세: `/novels/{id}` (DB 기반 title/author 렌더)
- 챕터 목록: `/branches/{id}` (DB 기반 챕터 row 1개 이상)
- 리더: `/novels/{id}/reader/{chapterId}` (DB 기반 chapter 렌더)
- 위키: `/branches/{id}/wikis` 또는 `/wikis?branchId={branchId}` (DB 기반 위키 카드 1개 이상)
- 작가 스튜디오: `/author/studio` (로그인 필요, 내 작품/요청 데이터 렌더)

---

## 7) 트러블슈팅

- 브라우저 설치 문제: `pnpm exec playwright install chromium`
- 백엔드가 안 뜸: `cd backend && poetry install` 확인
- E2E reset 실패: `http://localhost:8001/api/e2e/reset` 엔드포인트 확인
- Next 콘솔 에러로 실패: 해당 에러 로그가 Ralph 테스트 출력에 포함되므로 먼저 해결

---

## 부록) 라우트 트리 근거

이 문서의 라우트 목록은 `frontend/app/**/page.tsx`를 기준으로 합니다.
