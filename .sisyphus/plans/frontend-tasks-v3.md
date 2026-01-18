# 🎨 ForkLore 프론트엔드 태스크 v3.0 (최종)

**작성일**: 2026.01.18
**문서 버전**: v3.0
**기반**: v2.0에 Metis 검토 및 ULTRATHINK 분석 반영

---

## 📊 수정된 작업 계획

### 총 작업량 요약

| 우선순위 | 카테고리 | 작업 수 | 수정된 시간 | 비고 |
|----------|----------|----------|------------|-----------|
| **P0** | 인프라 구축 | 1개 | 8h → 8h | Metis 검토 후 삭제 (이미 완료됨) |
| **P0** | 백엔드 API 병렬 연동 | 1개 | 13개 → 병렬 | 23h | 13명 병렬 실행 가능 |
| **P0** | 페이지 API 연동 | 1개 | 4개 → 병렬 | 10h | API 모듈 완료 후 페이지 통합 작업 |
| **P0** | 소셜 로그인 | 1개 | 2개 → P1 재배치 | 4h → 6h | P0으로 재배치 |
| **P1** | 핵심 페이지 | 1개 | 10개 → 병렬 | 17h | 15개 컴포넌트 동시 개발 가능 |
| **P1** | 브랜치/위키 시스템 | 1개 | 6개 → 병렬 | 10h | 도메인별 병렬 실행 가능 |
| **P1** | 구독/결제/댓글 | 1개 | 7개 → 병렬 | 12h | 상호작용 컴포넌트 동시 개발 |
| **P1** | 지갑/작가 AI | 1개 | 6개 → 병렬 | 11h | AI 코파일럿 병렬 |
| **P1** | NextAuth.js v5 | 1개 | 4h → 5h | 소셜 로그인 병렬 |
| **P1** | 위키/지도 | 1개 | 5개 → 병렬 | 9h | 지도 컴포넌트는 P2로 격상 |
| **P1** | 검색 | 1개 | 2개 → 병렬 | 4h | 작가 스튜디오 병렬 |
| **P0** | E2E 테스트 | 1개 | 8h → 8h | E2E 단위 테스트만 추가 (인프라는 P0에) |
| **P2** | 지도 뷰어 | 1개 | 4개 → 병렬 | 4h | 작가 스튜디오 P2로 재배치 |

**총계**: 14개 카테고리 / **~105시간** (v2.0의 118시간에서 13시간 절감)

---

## 🚨 Phase 0: 인프라 구축 (8시간, 완료 ✅)

| 작업 | 상태 | 설명 | 시간 |
|------|------|------|------|
| Vitest 설정 | ✅ 완료 | vitest.config.ts + vitest.setup.ts 생성, 유틸리 설정 |
| Playwright 설정 | ✅ 완료 | playwright.config.ts + base URL 설정 |
| 테스트 유틸리 | ✅ 완료 | render.ts, providers.ts 생성 |
| 환경 변수 | ✅ 완료 | PLAYWRIGHT_HEADLESS 등 추가 |
| 공통 에러 핸들링 | ✅ 완료 | API 래퍼 + 토큰 관리 유틸리티 |

**수락 확인 기준**:
- [ ] vitest.config.ts 존재
- [ ] playwright.config.ts 존재
- [ ] 테스트 유틸리 파일 생성
- [ ] 환경 변수 설정 완료
- [ ] 공통 에러 핸들링 구현

---

## 🚨 Phase 1: 백엔드 API 병렬 연동 (23시간)

### 병렬 작업 배치 1 (13명 병렬, 8h)

| 작업 | 파일 | 세부 설명 | 비고 |
|------|------|---------|--------|
| novels.api.ts 생성 | frontend/lib/api/novels.api.ts | GET 목록/필터/정렬, GET 상세, POST 생성, PATCH 수정, DELETE 삭제 |
| branches.api.ts 생성 | frontend/lib/api/branches.api.ts | GET 목록, POST 포크/생성, GET 상세, PATCH 공개상태, POST/DELETE 투표, GET 이어 읽기 |
| chapters.api.ts 생성 | frontend/lib/api/chapters.api.ts | GET 목록, GET 상세, PATCH 수정, DELETE 삭제, POST 발행/예약, POST/DELETE 북마크, POST 진행율 |
| wiki.api.ts 생성 | frontend/lib/api/wiki.api.ts | GET 목록, POST 생성, GET 상세(?chapter=N), PATCH/DELETE 수정, PUT 태그, GET/POST 태그 CRUD, GET/POST 스냅샷 |
| maps.api.ts 생성 | frontend/lib/api/maps.api.ts | GET 목록, POST 생성, GET 상세(?currentChapter=N), PATCH/DELETE 수정, GET/POST 스냅샷, GET/POST 레이어, GET/POST 오브젝트 |
| interactions.api.ts 생성 | frontend/lib/api/interactions.api.ts | GET 소장, POST 회차 구매, GET/POST 댓글(문단 레벨), PATCH/DELETE 댓글, POST/DELETE 댓글 핀/좋아요, POST/DELETE 회차 좋아요, POST 신고, GET 구독상태, POST 구독, DELETE 구독취소 |
| subscription.api.ts 생성 | frontend/lib/api/subscription.api.ts | GET 상태, POST 구독, DELETE 취소 |
| wallet.api.ts 생성 | frontend/lib/api/wallet.api.ts | POST 충전, GET 지갑, GET 거래내역 |
| ai.api.ts 생성 | frontend/lib/api/ai.api.ts | POST 위키 제안, POST 일관성 검사, POST RAG 질문응답, POST 청킹 태스크 |

### 공통 타입 정의 (2명 병렬, 2h)

| 작업 | 설명 | 비고 |
|------|------|---------|--------|
| 공통 타입 인터페이스 생성 | frontend/types/common.ts | ApiResponse<T>, PaginatedResponse<T>, Error types |

---

## 🚨 Phase 2: 페이지 API 연동 (10시간)

### 작업 배치 (4개 작업 병렬)

| 작업 | 파일 | 세부 설명 | 비고 |
|------|------|---------|--------|
| 홈페이지 API 연동 | frontend/app/page.ts | TanStack Query로 Novel/랭킹/추천 데이터 페칭, Mock 데이터 제거, 로딩/에러 상태 처리 |
| 작품 목록 API 연동 | frontend/app/novels/page.ts | Novel API 사용하여 목록 페칭, 필터 기능 실제 API 연동, 무한 스크롤 최적화 |
| 랭킹 페이지 API 연동 | frontend/app/ranking/page.ts | Ranking API 사용하여 데이터 페칭, 탭별 필터링 구현 |
| 커뮤니티 페이지 API 연동 | frontend/app/community/page.ts | 댓글/게시글 API 연동, 게시글 작성 폼 |

---

## 🚨 Phase 3: 핵심 페이지 구현 (17시간)

### 작업 배치 (10개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| NovelDetail 컴포넌트 | components/novels/novel-detail.tsx | 통계/배지/장르 태그 표시, 회차 목록 탭, 브랜치 목록 탭, 위키 프리뷰 탭 |
| 회차 목록 컴포넌트 | components/novels/chapter-list.tsx | 회차 카드 그리드, 무료/읽음 표시, 정렬 옵션 |
| 브랜치 관련 컴포넌트 | components/novels/branch-*.tsx | BranchCard(투표, 작가, 통계), BranchList(필터, 정렬), ForkModal, LinkRequestModal |
| 소설 리더 실제 API 연동 | app/novels/[id]/reader/[chapterId]/page.tsx | Chapter API 사용하여 회차 페칭, 마크다운 렌더링, 위키 키워드 자동 링크, 읽은 진행율 API 연동, 리더 설정 패널 |
| 사용자 프로필 | components/users/user-profile.tsx | 프로필 정보 표시, 프로필 수정 폼, 이미지 업로드 |
| 서재 페이지 | components/users/my-library.tsx | 최근 읽은/북마크/좋아요 탭, Reading History API 연동, 북마크/좋아요 API 연동 |

---

## 🚨 Phase 4: 브랜치 & 위키 시스템 (10시간)

### 작업 배치 (6개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| 브랜치 상세 페이지 | app/branches/[id]/page.tsx | 브랜치 정보, 회차 목록, 연결 요청 목록(작가용) |
| 브랜치 포크 모달 | components/branches/fork-modal.tsx | 부모 브랜치 선택, 포크 설명 폼, Branch API 연동 |
| 브랜치 투표 UI | components/branches/vote-button.tsx | 투표 버튼, 카운트 표시, Optimistic Update 구현, Branch 투표 API 연동 |
| 연결 요청 UI | components/branches/link-request-modal.tsx | 요청 버튼, 요청 폼, 요청 목록 표시(작가용) |
| 위키 목록 페이지 | app/wiki/page.tsx | 위키 카드 그리드, 태그 필터, 검색 기능 |
| 위키 상세 컴포넌트 | components/wiki/wiki-detail.tsx | 위키 내용, 문맥 인식 스냅샷 전환, 태그 관리 |
| 스포일러 방지 UI | components/wiki/spoiler-alert.tsx | 현재 읽은 회차 기준 필터, 경고 모달 |

---

## 🚨 Phase 5: 구독 & 결제 & 댓글 (12시간)

### 작업 배치 (7개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| 구독 상태 페이지 | app/subscriptions/page.tsx | 현재 구독 정보 표시, 구독 플랜 선택 UI, 구독 취소 버튼, Subscription API 연동 |
| 구독 가입 페이지 | app/subscriptions/checkout/page.tsx | 플랜 선택(BASIC/PREMIUM), 결제 연동(TODO: PG 연동), Subscription API 연동 |
| 회차 구매 모달 | components/purchases/purchase-modal.tsx | 코인 차감 확인, 구매 버튼, Purchase API 연동 |
| 지갑 페이지 | app/wallet/page.tsx | 잔액/최근 거래 표시, 충전 버튼(TODO: PG 연동), Wallet API 연동 |
| 댓글 스레드 컴포넌트 | components/comments/comment-thread.tsx | 댓글 목록, 댓글 작성 폼, Comment API 연동, 좋아요 토글 |

---

## 🚨 Phase 6: 작가 스튜디오 & AI 코파일럿 (11시간)

### 작업 배치 (3개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| 작가 스튜디오 대시보드 | app/author/studio/page.tsx | 내 작품 목록, 회차별 통계, 브랜치 연결 요청 관리 |
| 회차 에디터 | components/author/chapter-editor.tsx | Tiptap 에디터, 툴바(볼드/이탤릭/링크/이미지), 이미지 업로드, 자동 저장(디바운스), Chapter API 연동 |
| 발행 설정 패널 | components/author/publish-panel.tsx | 즉시 발행/예약 발행 선택, 유료/무료 설정, 발행/예약 API 연동 |
| AI 코파일럿 패널 | components/author/ai-copilot-panel.tsx | 위키 제안 표시, 일관성 검사 결과 표시, 제안 승인/거절 UI, AI API 연동 |

---

## 🚨 Phase 7: 위키 & 지도 (9시간)

### 작업 배치 (2개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| 지도 뷰어 페이지 | app/map-viewer/page.tsx | Leaflet 지도 컴포넌트, 현재 회차 기준 레이어/객체 전환, 회차별 스냅샷 탭 |
| 지도 컴포넌트 | components/map/map-viewer.tsx, map-layers.tsx | Leaflet 설정, 커스텀 이미지 오버레이, 마커/레이어 렌더링, 레이어/객체 관리 |

---

## 🚨 Phase 8: NextAuth.js v5 & 소셜 로그인 (6시간)

### 작업 배치 (2개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| NextAuth.js v5 설정 | auth.config.ts | auth.ts 설정 파일, Credentials Provider(이메일/비밀번호), Google OAuth Provider, Kakao OAuth Provider, 콜백 URL 환경 변수 |
| 로그인 페이지 소셜 버튼 연동 | components/auth/user-login-form.tsx | Google/Kakao 버튼 활성화, NextAuth signIn() 연동, 콜백 에러 핸들링 |

---

## 🚨 Phase 9: 검색 (4시간)

### 작업 배치 (1개 작업)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| 검색 결과 페이지 | app/search/page.tsx | 검색어 하이라이팅, 검색 결과 목록, 필터(작품/작가/회차), 무한 스크롤 |

---

## 🚨 Phase 10: E2E 테스트 & 배포 (8시간)

### 작업 배치 (2개 작업 병렬)

| 작업 | 세부 설명 | 비고 |
|------|---------|--------|
| E2E 통합 테스트 | tests/e2e/ | 주요 사용자 시나리오 작성, 로그인/작품 조회/회차 댓글/좋아요/북마크 경로 테스트 |
| API 단위 테스트 추가 | tests/api/ | 각 API 모듈(novels, branches, chapters 등) 단위 테스트 추가 |

---

## 📋 GitHub 이슈 생성 가이드

### 이슈 생성 순서

**Phase 0 → Phase 1 → Phase 2 → ... → Phase 10**

각 Phase에서 작업이 완료되면 해당 Phase의 이슈를 한 번에 생성하여 배포합니다.

### 이슈 명명 규칙

```bash
# P0: 백엔드 API 연동
feat/p0-api-modules

# P0: 소셜 로그인
feat/p0-social-login

# P0: 페이지 API 연동  
feat/p0-page-api-integration

# P0: E2E 테스트
feat/p0-e2e-integration

# P1: 핵심 페이지
feat/p1-core-pages

# P1: 브랜치 & 위키 시스템
feat/p1-branch-wiki-system

# P1: 구독 & 결제
feat/p1-subscription-payment

# P1: 지갑/작가 AI
feat/p1-wallet-author-ai

# P1: NextAuth.js v5
feat/p1-nextauth-v5

# P1: 위키 & 지도
feat/p1-wiki-map-system

# P1: 검색
feat/p1-search

# P1: 작가 스튜디오
feat/p1-author-studio

# P2: 지도 뷰어
feat/p2-map-viewer

# P2: E2E 테스트
feat/p2-e2e-testing

# P2: 배포
feat/p2-deployment
```

### 브랜치 생성 명령어

```bash
# develop 브랜치에서 시작
git checkout develop

# P0 백엔드 API 연동 시작 전
git checkout -b feat/p0-api-modules

# 작업 완료 후 develop으로 병합
git checkout develop
git merge feat/p0-api-modules --no-ff

# 브랜치 삭제
git branch -d feat/p0-api-modules
```

---

## 🚫 아웃 오브 스코프 (강제)

### 제외할 항목

**백엔드 관련**:
- ❌ 백엔드 코드 수정 (전용 읽기)
- ❌ 데이터베이스 스키마 변경
- ❌ 백엔드 API 버전 관리 (콜백 등 수정)
- ❌ CI/CD 파이프라인 변경

**프론트엔드 관련**:
- ❌ 새로운 라이브러리 추가 (사전 승인 없이)
- ❌ 반응형 디자인 개선 (별도 P1 트랙)
- ❌ 접근성 개선 (별도 P1 트랙)
- ❌ 모바일 반응형 최적화 (별도 P1 트랙)

**테스트 관련**:
- ❌ 테스트 커버리지 80% 목표 (별도 P1 트랙)
- ❌ 성능 벤치마크 추가 (별도 P2 트랙)

### 각 이슈는 하나의 도메인만 다룸어야 함

예시:
- ✅ 좋음: "Novel API 모듈 생성" (API만, UI 포함 X)
- ✅ 나쁨: "랭킹 페이지 API 연동" (페이지만, 새로운 컴포넌트 X)
- ❌ 나쁨: "회차 에디터 + 랭킹 API 연동" (여러 도메인 섞임)

---

## 📝 참고 자료

### 백엔드 API 문서
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

### 프론트엔드 개발 가이드

**타입스크립트**:
- TypeScript: 5.7
- React: 19.x
- Node.js: 22.x

**코드베이스 규칙**:
- API 모듈: auth.api.ts 패턴 따르기
- 컴포넌트: shadcn/ui 프리미티브 사용, 복사 금지
- 폼 관리: React Hook Form + Zod
- 상태 관리: Zustand 스토어 사용

---

## 문서 끝
