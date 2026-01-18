# 🎨 ForkLore 프론트엔드 태스크

**작성일**: 2026.01.18  
**문서 버전**: v2.0

---

## 범례

| 항목 | 설명 |
|------|------|
| **우선순위** | P0 (MVP 필수), P1 (MVP 권장), P2 (후속) |
| **난이도** | 🟢 Easy, 🟡 Medium, 🔴 Hard |
| **공수** | 예상 시간 (hours) |
| **상태** | ⬜ 미착수, 🔲 진행중, ✅ 완료 |

---

## 🚨 백엔드-프론트엔드 갭 분석

### 백엔드 API 구현 상태 (완료 ✅)

#### 인증/사용자
- ✅ 회원가입: POST /api/v1/auth/signup
- ✅ 로그인: POST /api/v1/auth/login
- ✅ 소셜 로그인: POST /api/v1/auth/google/, POST /api/v1/auth/kakao/
- ✅ 로그아웃: POST /api/v1/auth/logout
- ✅ 프로필 조회/수정: GET/PATCH /api/v1/users/me
- ✅ 비밀번호 변경: POST /api/v1/users/me/password
- ✅ 읽은 기록: GET /api/v1/users/me/reading-history
- ✅ 북마크: GET /api/v1/users/me/bookmarks

#### 작품/브랜치
- ✅ 작품 목록: GET /api/v1/novels/ (필터, 정렬 지원)
- ✅ 작품 상세: GET /api/v1/novels/{id}/
- ✅ 작품 생성/수정/삭제: POST/PATCH/DELETE
- ✅ 브랜치 목록: GET /api/v1/novels/{id}/branches/
- ✅ 브랜치 포크(생성): POST /api/v1/novels/{id}/branches/
- ✅ 브랜치 상세: GET /api/v1/branches/{id}/
- ✅ 브랜치 공개 상태 변경: PATCH /api/v1/branches/{id}/visibility/
- ✅ 브랜치 투표: POST/DELETE /api/v1/branches/{id}/vote/
- ✅ 브랜치 연결 요청: POST /api/v1/branches/{id}/link-request/
- ✅ 연결 요청 검토: PATCH /api/v1/link-requests/{id}/
- ✅ 이어 읽기: GET /api/v1/branches/{id}/continue-reading/

#### 회차/컨텐츠
- ✅ 회차 목록: GET /api/v1/branches/{branch_pk}/chapters/
- ✅ 회차 생성: POST /api/v1/branches/{branch_pk}/chapters/
- ✅ 회차 상세: GET /api/v1/chapters/{id}/
- ✅ 회차 수정/삭제: PATCH/DELETE /api/v1/chapters/{id}/
- ✅ 회차 발행: POST /api/v1/chapters/{id}/publish/
- ✅ 예약 발행: POST /api/v1/chapters/{id}/schedule/
- ✅ 회차 북마크: POST/DELETE /api/v1/chapters/{id}/bookmark/
- ✅ 읽은 진행율: POST /api/v1/chapters/{id}/reading-progress/

#### 위키
- ✅ 위키 목록: GET /api/v1/branches/{branch_pk}/wikis/ (태그 필터)
- ✅ 위키 생성: POST /api/v1/branches/{branch_pk}/wikis/
- ✅ 위키 상세: GET /api/v1/wikis/{id}/ (?chapter=N 문맥 인식)
- ✅ 위키 수정/삭제: PATCH/DELETE /api/v1/wikis/{id}/
- ✅ 위키 태그 관리: PUT /api/v1/wikis/{id}/tags/
- ✅ 위키 태그 목록/생성: GET/POST /api/v1/branches/{branch_pk}/wiki-tags/
- ✅ 위키 스냅샷: GET/POST /api/v1/wikis/{wiki_pk}/snapshots/

#### 지도
- ✅ 지도 목록: GET /api/v1/branches/{branch_pk}/maps/
- ✅ 지도 생성: POST /api/v1/branches/{branch_pk}/maps/
- ✅ 지도 상세: GET /api/v1/maps/{id}/ (?currentChapter=N 문맥 인식)
- ✅ 지도 수정/삭제: PATCH/DELETE /api/v1/maps/{id}/
- ✅ 지도 스냅샷: GET/POST /api/v1/maps/{map_pk}/snapshots/
- ✅ 레이어: GET/POST /api/v1/snapshots/{snapshot_pk}/layers/
- ✅ 오브젝트: GET/POST /api/v1/layers/{layer_pk}/objects/

#### 상호작용
- ✅ 구독 상태: GET /api/v1/subscriptions/status
- ✅ 구독 가입: POST /api/v1/subscriptions/
- ✅ 구독 취소: DELETE /api/v1/subscriptions/current/
- ✅ 소장 목록: GET /api/v1/purchases/
- ✅ 회차 구매: POST /api/v1/chapters/{chapter_pk}/purchase/
- ✅ 댓글: GET/POST /api/v1/chapters/{chapter_pk}/comments/ (문단 레벨)
- ✅ 댓글 수정/삭제/핀: PATCH/DELETE/POST/DELETE /api/v1/comments/{id}/
- ✅ 댓글 좋아요: POST/DELETE /api/v1/comments/{id}/like/
- ✅ 회차 좋아요: POST/DELETE /api/v1/chapters/{chapter_pk}/like/
- ✅ 신고: POST /api/v1/reports/
- ✅ 신고 관리자: GET/PATCH /api/v1/admin/reports/
- ✅ 코인 충전: POST /api/v1/wallet/charge/
- ✅ 지갑 조회: GET /api/v1/users/me/wallet/
- ✅ 거래 내역: GET /api/v1/users/me/wallet/transactions/
- ✅ AI 사용량: GET /api/v1/users/me/ai-usage/
- ✅ AI 한도 체크/기록: POST /api/v1/ai/check-limit/, POST /api/v1/ai/record-usage/

#### AI 기능
- ✅ 위키 제안: POST /api/v1/branches/{id}/ai/wiki-suggestions/
- ✅ 일관성 검사: POST /api/v1/branches/{id}/ai/consistency-check/
- ✅ RAG 질문응답: POST /api/v1/branches/{id}/ai/ask/
- ✅ 청킹 태스크: POST /api/v1/branches/{id}/ai/create-chunks/

### 프론트엔드 구현 상태

#### ✅ 완료된 부분
1. **프로젝트 초기 설정** (완료 ✅)
   - Next.js 16 프로젝트 구조
   - Tailwind CSS 4.x 설정
   - shadcn/ui 초기화 (New York 스타일)
   - Geist 폰트 설정
   - ESLint + Prettier 설정
   - 환경 변수 설정

2. **공통 컴포넌트** (완료 ✅)
   - Header (로고, 네비게이션, 검색바, 테마 토글)
   - Footer
   - 모바일 네비게이션 (Sheet)
   - RootLayout (메타데이터, 프로바이더들)

3. **인증 시스템** (부분 완료 🔲)
   - ✅ 로그인 페이지 (UI + Zod 유효성 검사)
   - ✅ 회원가입 페이지 (생년월일 포함)
   - ⏳ 소셜 로그인 연동 (TODO: NextAuth.js v5)
   - ✅ 인증 상태 관리 (AuthProvider + AuthStore)
   - ✅ 토큰 인터셉터 (Bearer 자동 주입)
   - ✅ 리프레시 토큰 로직 (401 에러 시 자동 갱신)

4. **API 클라이언트** (부분 완료 🔲)
   - ✅ Axios 인스턴스 설정
   - ✅ 응답 래퍼 언래핑
   - ✅ 토큰 자동 갱신
   - ✅ Auth API 모듈 (lib/api/auth.api.ts)
   - ❌ Novel API 모듈 - **미구현**
   - ❌ Branch API 모듈 - **미구현**
   - ❌ Chapter API 모듈 - **미구현**
   - ❌ Wiki API 모듈 - **미구현**
   - ❌ Map API 모듈 - **미구현**
   - ❌ Interaction API 모듈 - **미구현**
   - ❌ Subscription API 모듈 - **미구현**
   - ❌ Wallet API 모듈 - **미구현**
   - ❌ AI API 모듈 - **미구현**

5. **상태 관리** (부분 완료 🔲)
   - ✅ Zustand 스토어 설정
   - ✅ Auth Store (사용자, 로그인/로그아웃)
   - ✅ Theme Store (다크/라이트 모드)
   - ✅ Reader Settings Store (글자 크기, 줄 간격)
   - ❌ Novel/Branch Store - **미구현**

6. **페이지 구현** (부분 완료 🔲)
   - ✅ 홈페이지 (/) - 히로, 랭킹, 추천, 장르 필터
   - ✅ 작품 목록 (/novels) - 카테고리 탭, 필터, 무한 스크롤
   - ⏳ 작품 상세 (/novels/[id]) - 페이지만 존재, 데이터 연동 필요
   - ⏳ 소설 리더 (/novels/[id]/reader/[chapterId]) - 페이지만 존재, 데이터 연동 필요
   - ✅ 로그인 페이지 (/login)
   - ✅ 회원가입 페이지 (/signup)
   - ✅ 랭킹 페이지 (/ranking)
   - ⏳ 커뮤니티 페이지 (/community) - 페이지만 존재, 데이터 연동 필요

7. **컴포넌트 구현** (부분 완료 🔲)
   - ✅ UI 프리미티브 (shadcn/ui)
   - ✅ Home: HeroSection, RankingCarousel, RecommendationList, GenreFilter
   - ✅ Ranking: RankingHeader, RankingTabs, RankingList
   - ✅ Novels: NovelCard, NovelGrid, CategoryTabs, NovelFilters, InfiniteNovelList
   - ✅ Community: CategoryTabs, PostList, PostCard
   - ✅ Auth: UserLoginForm, UserSignupForm
   - ❌ 작품 상세 컴포넌트들 - **미구현**
   - ❌ 브랜치 관련 컴포넌트 - **미구현**
   - ❌ 회차 리스트/상세 컴포넌트 - **미구현**
   - ❌ 위키 관련 컴포넌트 - **미구현**
   - ❌ 지도 뷰어 컴포넌트 - **미구현**
   - ❌ 댓글/좋아요 UI - **미구현**
   - ❌ 구독/결제 UI - **미구현**
   - ❌ 지갑 UI - **미구현**

8. **테스트** (미구현 ⬜)
   - Vitest 설정 - **미완료**
   - Playwright 설정 - **미완료**
   - 테스트 파일 - **부재**

---

## 📋 업데이트된 작업 목록

### P0: 백엔드 API 연동 (최우선)

#### 1. API 모듈 구현

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **Novel API 모듈 생성** | 🟡 | 3h |
|   | ├─ ⬜ GET /api/v1/novels/ (목록, 필터, 정렬) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/novels/{id}/ (상세) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/novels/ (생성) | 🟢 | 0.5h |
|   | ├─ ⬜ PATCH /api/v1/novels/{id}/ (수정) | 🟢 | 0.5h |
|   | ├─ ⬜ DELETE /api/v1/novels/{id}/ (삭제) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 1h |
| ⬜ | **Branch API 모듈 생성** | 🟡 | 3h |
|   | ├─ ⬜ GET /api/v1/novels/{id}/branches/ (목록) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/novels/{id}/branches/ (포크/생성) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/branches/{id}/ (상세) | 🟢 | 0.5h |
|   | ├─ ⬜ PATCH /api/v1/branches/{id}/visibility/ (공개 상태) | 🟢 | 0.5h |
|   | ├─ ⬜ POST/DELETE /api/v1/branches/{id}/vote/ (투표) | 🟢 | 1h |
|   | ├─ ⬜ GET /api/v1/branches/{id}/continue-reading/ (이어 읽기) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 1h |
| ⬜ | **Chapter API 모듈 생성** | 🟡 | 4h |
|   | ├─ ⬜ GET /api/v1/branches/{branch_pk}/chapters/ (목록) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/chapters/{id}/ (상세) | 🟢 | 0.5h |
|   | ├─ ⬜ PATCH /api/v1/chapters/{id}/ (수정) | 🟢 | 0.5h |
|   | ├─ ⬜ DELETE /api/v1/chapters/{id}/ (삭제) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/chapters/{id}/publish/ (발행) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/chapters/{id}/schedule/ (예약) | 🟢 | 0.5h |
|   | ├─ ⬜ POST/DELETE /api/v1/chapters/{id}/bookmark/ (북마크) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/chapters/{id}/reading-progress/ (진행율) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 1h |
| ⬜ | **Wiki API 모듈 생성** | 🟡 | 3h |
|   | ├─ ⬜ GET /api/v1/branches/{branch_pk}/wikis/ (목록) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/branches/{branch_pk}/wikis/ (생성) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/wikis/{id}/ (상세, 문맥 인식) | 🟢 | 0.5h |
|   | ├─ ⬜ PATCH/DELETE /api/v1/wikis/{id}/ (수정/삭제) | 🟢 | 0.5h |
|   | ├─ ⬜ PUT /api/v1/wikis/{id}/tags/ (태그) | 🟢 | 0.5h |
|   | ├─ ⬜ GET/POST /api/v1/branches/{branch_pk}/wiki-tags/ (태그 CRUD) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 1h |
| ⬜ | **Interaction API 모듈 생성** | 🟡 | 4h |
|   | ├─ ⬜ GET /api/v1/purchases/ (소장 목록) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/chapters/{id}/purchase/ (구매) | 🟢 | 0.5h |
|   | ├─ ⬜ GET/POST /api/v1/chapters/{id}/comments/ (댓글) | 🟢 | 1h |
|   | ├─ ⬜ GET /api/v1/subscriptions/status (구독 상태) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/subscriptions/ (구독) | 🟢 | 0.5h |
|   | ├─ ⬜ DELETE /api/v1/subscriptions/current/ (취소) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 1h |
| ⬜ | **Wallet API 모듈 생성** | 🟡 | 2h |
|   | ├─ ⬜ POST /api/v1/wallet/charge/ (충전) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/users/me/wallet/ (지갑 조회) | 🟢 | 0.5h |
|   | ├─ ⬜ GET /api/v1/users/me/wallet/transactions/ (거래 내역) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 0.5h |
| ⬜ | **AI API 모듈 생성** | 🟡 | 2h |
|   | ├─ ⬜ POST /api/v1/branches/{id}/ai/wiki-suggestions (제안) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/branches/{id}/ai/consistency-check (검사) | 🟢 | 0.5h |
|   | ├─ ⬜ POST /api/v1/branches/{id}/ai/ask (RAG) | 🟢 | 0.5h |
|   | └─ ⬜ TypeScript 타입 정의 | 🟢 | 0.5h |

#### 2. 페이지 API 연동 (Mock → 실제 데이터)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **홈페이지 실제 API 연동** | 🟡 | 4h |
|   | ├─ ⬜ TanStack Query로 데이터 페칭 변경 | 🟡 | 2h |
|   | ├─ ⬜ 로딩/에러 상태 처리 | 🟢 | 1h |
|   | ├─ ⬜ Mock 데이터 제거 | 🟢 | 0.5h |
|   | └─ ⬜ 수동 테스트 | 🟢 | 0.5h |
| ⬜ | **작품 목록 페이지 API 연동** | 🟡 | 2h |
|   | ├─ ⬜ Novel API 모듈 사용하여 데이터 페칭 | 🟢 | 1h |
|   | ├─ ⬜ 무한 스크롤 최적화 | 🟢 | 0.5h |
|   | └─ ⬜ 필터 기능 실제 API 연동 | 🟢 | 0.5h |
| ⬜ | **랭킹 페이지 API 연동** | 🟡 | 2h |
|   | ├─ ⬜ 랭킹 데이터 API 페칭 | 🟢 | 1.5h |
|   | └─ ⬜ 탭별 필터링 구현 | 🟢 | 0.5h |
| ⬜ | **커뮤니티 페이지 API 연동** | 🟡 | 2h |
|   | ├─ ⬜ 댓글 API 연동 | 🟢 | 1h |
|   | ├─ ⬜ 게시글 리스트 구현 | 🟢 | 0.5h |
|   | └─ ⬜ 댓글/좋아요 UI 추가 | 🟢 | 0.5h |

#### 3. 소셜 로그인 연동

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **NextAuth.js v5 설정** | 🔴 | 4h |
|   | ├─ ⬜ auth.ts 설정 파일 | 🟡 | 1h |
|   | ├─ ⬜ Credentials Provider (이메일/비밀번호) | 🟢 | 0.5h |
|   | ├─ ⬜ Google OAuth Provider | 🟡 | 1h |
|   | ├─ ⬜ Kakao OAuth Provider | 🟡 | 1h |
|   | └─ ⬜ 콜백 URL 환경 변수 설정 | 🟡 | 0.5h |
| ⬜ | **소셜 로그인 버튼 연동** | 🟡 | 2h |
|   | ├─ ⬜ 로그인 페이지 Google/Kakao 버튼 활성화 | 🟢 | 1h |
|   | ├─ ⬜ OAuth 콜백 핸들링 | 🟢 | 1h |

---

### P1: 핵심 페이지 구현

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **작품 상세 페이지 구현** | 🔴 | 6h |
|   | ├─ ⬜ NovelDetail 컴포넌트 | 🟡 | 2h |
|   | ├─ ⬜ 통계/배지/장르 표시 | 🟢 | 1.5h |
|   | ├─ ⬜ 회차 목록 탭 구현 | 🟡 | 2h |
|   | ├─ ⬜ 브랜치 목록 탭 구현 | 🟡 | 2h |
|   | └─ ⬜ 위키 프리뷰 탭 | 🟢 | 0.5h |
| ⬜ | **소설 리더 실제 데이터 연동** | 🔴 | 4h |
|   | ├─ ⬜ Chapter API 사용하여 회차 페칭 | 🟢 | 1h |
|   | ├─ ⬜ 마크다운 렌더링 구현 | 🟡 | 2h |
|   | ├─ ⬜ 위키 키워드 자동 링크 | 🟡 | 1.5h |
|   | ├─ ⬜ 리더 설정 패널 | 🟢 | 0.5h |
|   | └─ ⬜ 읽은 진행율 API 연동 | 🟢 | 0.5h |
| ⬜ | **사용자 프로필 페이지** | 🟡 | 3h |
|   | ├─ ⬜ 프로필 페이지 레이아웃 | 🟡 | 0.5h |
|   | ├─ ⬜ 프로필 정보 표시 컴포넌트 | 🟡 | 1h |
|   | ├─ ⬜ 프로필 수정 폼 | 🟡 | 1h |
|   | └─ ⬜ 이미지 업로드 | 🟢 | 0.5h |
| ⬜ | **서재 페이지** | 🟡 | 4h |
|   | ├─ ⬜ 서재 페이지 레이아웃 | 🟡 | 0.5h |
|   | ├─ ⬜ 최근 읽은 작품 탭 | 🟡 | 1.5h |
|   | ├─ ⬜ 북마크 탭 | 🟢 | 0.5h |
|   | ├─ ⬜ 좋아요한 작품 탭 | 🟢 | 0.5h |
|   | └─ ⬜ Reading History API 연동 | 🟢 | 1.5h |

---

### P1: 브랜치 시스템 구현

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **브랜치 상세 페이지** | 🟡 | 3h |
|   | ├─ ⬜ 브랜치 상세 컴포넌트 | 🟢 | 1.5h |
|   | ├─ ⬜ 브랜치 정보 헤더 | 🟢 | 0.5h |
|   | ├─ ⬜ 브랜치 회차 목록 | 🟢 | 1h |
|   | └─ ⬜ 이어 읽기 버튼 | 🟢 | 0.5h |
| ⬜ | **브랜치 포크 모달** | 🟡 | 2h |
|   | ├─ ⬜ 포크 폼 구현 | 🟢 | 1h |
|   | ├─ ⬜ 부모 브랜치 선택 | 🟢 | 1h |
|   | └─ ⬜ Branch API 연동 | 🟢 | 0.5h |
| ⬜ | **브랜치 투표 UI** | 🟡 | 2h |
|   | ├─ ⬜ 투표 버튼 + 카운트 표시 | 🟢 | 1h |
|   | ├─ ⬜ Optimistic Update 구현 | 🟡 | 1h |
|   | └─ ⬜ Branch API 투표 엔드포인트 연동 | 🟢 | 0.5h |
| ⬜ | **브랜치 연결 요청 UI** | 🟡 | 2h |
|   | ├─ ⬜ 연결 요청 버튼/폼 | 🟢 | 1h |
|   | ├─ ⬜ 연결 요청 목록 표시 (작가용) | 🟢 | 1h |
|   | └─ ⬜ LinkRequest API 연동 | 🟢 | 0.5h |

---

### P1: 위키 시스템 구현

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **위키 목록 페이지** | 🟡 | 3h |
|   | ├─ ⬜ 위키 목록 페이지 레이아웃 | 🟡 | 0.5h |
|   | ├─ ⬜ 태그별 필터 탭 | 🟡 | 1h |
|   | ├─ ⬜ 검색 기능 | 🟢 | 0.5h |
|   | └─ ⬜ 위키 카드 그리드 | 🟢 | 1h |
| ⬜ | **위키 상세 페이지** | 🟡 | 3h |
|   | ├─ ⬜ 위키 상세 컴포넌트 | 🟡 | 2h |
|   | ├─ ⬜ 문맥 인식 슬라이더 | 🟡 | 1.5h |
|   | └─ ⬜ 스냅샷 목록 표시 | 🟢 | 0.5h |
| ⬜ | **스포일러 방지 UI** | 🟡 | 2h |
|   | ├─ ⬜ 현재 읽은 회차 기준 필터 | 🟡 | 1.5h |
|   | └─ ⬜ 스포일러 경고 모달 | 🟢 | 0.5h |

---

### P1: 구독 & 결제

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **구독 상태 페이지** | 🟡 | 2h |
|   | ├─ ⬜ 구독 상태 페이지 레이아웃 | 🟢 | 0.5h |
|   | ├─ ⬜ 현재 구독 정보 표시 | 🟢 | 0.5h |
|   | ├─ ⬜ 구독 취소 버튼 | 🟢 | 0.5h |
|   | └─ ⬜ Subscription API 연동 | 🟢 | 0.5h |
| ⬜ | **구독 가입 페이지** | 🟡 | 3h |
|   | ├─ ⬜ 구독 가입 페이지 레이아웃 | 🟡 | 0.5h |
|   | ├─ ⬜ 플랜 선택 UI | 🟡 | 1.5h |
|   | └─ ⬜ 결제 연동 (TODO: PG 연동) | 🟡 | 1h |
| ⬜ | **회차 구매 모달** | 🟡 | 2h |
|   | ├─ ⬜ 구매 모달 컴포넌트 | 🟡 | 1.5h |
|   | ├─ ⬜ 코인 차감 확인 | 🟢 | 0.5h |
|   | └─ ⬜ Purchase API 연동 | 🟢 | 0.5h |
| ⬜ | **지갑 페이지** | 🟡 | 2h |
|   | ├─ ⬜ 지갑 페이지 레이아웃 | 🟡 | 0.5h |
|   | ├─ ⬜ 잔액/최근 거래 표시 | 🟡 | 1h |
|   | └─ ⬜ Wallet API 연동 | 🟢 | 0.5h |

---

### P2: 작가 스튜디오 (추후)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **작가 스튜디오 페이지** | 🔴 | 6h |
|   | ├─ ⬜ 스튜디오 페이지 레이아웃 | 🟢 | 0.5h |
|   | ├─ ⬜ 내 작품 목록 | 🟡 | 1h |
|   | ├─ ⬜ 회차별 통계 | 🟡 | 1h |
|   | └─ ⬜ 브랜치 연결 요청 관리 | 🟡 | 1h |
| ⬜ | **회차 에디터** | 🔴 | 6h |
|   | ├─ ⬜ Tiptap 에디터 설정 | 🔴 | 2h |
|   | ├─ ⬜ 툴바 (볼드, 이탤릭, 링크) | 🟡 | 1.5h |
|   | ├─ ⬜ 이미지 업로드 | 🟡 | 1h |
|   | └─ ⬜ 자동 저장 (디바운스) | 🟡 | 1.5h |
| ⬜ | **발행 설정 패널** | 🟡 | 2h |
|   | ├─ ⬜ 즉시 발행/예약 발행 선택 | 🟢 | 0.5h |
|   | ├─ ⬜ 유료/무료 설정 | 🟢 | 0.5h |
|   | └─ ⬜ 발행/예약 API 연동 | 🟢 | 1h |
| ⬜ | **AI 코파일럿 패널** | 🔴 | 4h |
|   | ├─ ⬜ 위키 제안 표시 | 🟡 | 1h |
|   | ├─ ⬜ 일관성 검사 결과 표시 | 🟡 | 1h |
|   | ├─ ⬜ 제안 승인/거절 UI | 🟡 | 1h |
|   | └─ ⬜ AI API 연동 | 🟢 | 1h |

---

### P2: 지도 뷰어 (추후)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **지도 뷰어 페이지** | 🔴 | 4h |
|   | ├─ ⬜ 지도 뷰어 페이지 레이아웃 | 🟢 | 0.5h |
|   | ├─ ⬜ Leaflet 컴포넌트 설정 | 🔴 | 2h |
|   | ├─ ⬜ 커스텀 이미지 오버레이 | 🟡 | 1h |
|   | └─ ⬜ 마커/레이어 렌더링 | 🟡 | 1h |
| ⬜ | **문맥 인식 타임라인 슬라이더** | 🟡 | 2h |
|   | ├─ ⬜ 회차별 스냅샷 전환 | 🟡 | 1h |
|   | ├─ ⬜ 애니메이션 전환 | 🟢 | 1h |
|   | └─ ⬜ 마커 클릭 → 위키 연동 | 🟢 | 0.5h |

---

### P0: 테스트 인프라 (필수)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | **Vitest 설정 완료** | 🟢 | 2h |
|   | ├─ ⬜ 테스트 유틸리 생성 (render, providers) | 🟢 | 1h |
|   | ├─ ⬜ 커버리지 설정 | 🟢 | 0.5h |
|   | └─ ⬜ 예시 테스트 생성 | 🟢 | 0.5h |
| ⬜ | **API 모듈 단위 테스트** | 🟡 | 8h |
|   | ├─ ⬜ novel.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ branch.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ chapter.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ wiki.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ interaction.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ subscription.api.ts 단위 테스트 | 🟢 | 1h |
|   | ├─ ⬜ wallet.api.ts 단위 테스트 | 🟢 | 1h |
|   | └─ ⬜ ai.api.ts 단위 테스트 | 🟢 | 1h |

---

## 📊 요약

| 우선순위 | 카테고리 | 태스크 수 | 예상 총 공수 |
|----------|----------|---------|--------------|
| P0 | API 연동 | 13개 | ~35h |
| P0 | 페이지 API 연동 | 4개 | ~10h |
| P0 | 소셜 로그인 | 2개 | ~6h |
| P0 | 테스트 인프라 | 2개 | ~10h |
| P1 | 핵심 페이지 | 3개 | ~13h |
| P1 | 브랜치 시스템 | 3개 | ~7h |
| P1 | 위키 시스템 | 3개 | ~8h |
| P1 | 구독 & 결제 | 3개 | ~7h |
| P2 | 작가 스튜디오 | 3개 | ~16h |
| P2 | 지도 뷰어 | 2개 | ~6h |
| **합계** | **39개** | **~118h** |

---

## 🚫 아웃 오브 스코프 (이슈 생성 시 제외)

### 제외할 항목
- ❌ 백엔드 코드 수정 (읽기 전용)
- ❌ 데이터베이스 스키마 변경
- ❌ CI/CD 파이프라인 변경
- ❌ 새로운 라이브러리 추가 (사전 승인 없이)
- ❌ 성능 최적화 (별도 P1 트랙)
- ❌ 접근성 개선 (별도 P1 트랙)
- ❌ 반응형 디자인 개선 (별도 P1 트랙)

### 각 이슈는 하나의 도메인만 다루어야 함
예시:
- ✅ 좋음: "Novel API 모듈 생성" (API만, UI 포함 X)
- ✅ 좋음: "랭킹 페이지 API 연동" (페이지만, 새로운 컴포넌트 X)
- ❌ 나쁨: "회차 에디터 + 랭킹 API 연동" (여러 도메인 섞임)

---

## 📋 GitHub 이슈 생성 가이드

### 이슈 제목 규칙
```bash
# P0: 백엔드 API 연동
feat/#42-novels-api-module
feat/#43-branch-api-module
feat/#44-chapter-api-module

# P0: 소셜 로그인
feat/#45-nextauth-v5-setup
feat/#46-social-login-integration

# P1: 핵심 페이지
feat/#47-novel-detail-page
feat/#48-reader-api-integration
feat/#49-user-profile-page

# P1: 브랜치 시스템
feat/#50-branch-detail-page
feat/#51-branch-voting-ui
feat/#52-branch-fork-modal
```

### 브랜치 생성 명령어
```bash
# develop 브랜치에서 시작
git checkout develop

# 새로운 기능 브랜치 생성
git checkout -b feat/#42-novels-api-module

# 작업 완료 후 develop으로 병합
git checkout develop
git merge feat/#42-novels-api-module
git branch -d feat/#42-novels-api-module
```

### 이슈 템플릿 (GitHub Issue Body)

```markdown
## 📋 구현 내용

### 백엔드 API 엔드포인트
- [ ] GET /api/v1/novels/ (목록, 필터, 정렬)
- [ ] GET /api/v1/novels/{id}/ (상세)
- [ ] POST /api/v1/novels/ (생성)
- [ ] PATCH /api/v1/novels/{id}/ (수정)
- [ ] DELETE /api/v1/novels/{id}/ (삭제)

### 프론트엔드 파일
- 생성: `frontend/lib/api/novels.api.ts`
- 수정: 없음

### 타입 정의
- 생성: `frontend/types/novels.types.ts` (필요시)

### 테스트
- [ ] 단위 테스트 작성: `frontend/lib/api/novels.api.test.ts`
- [ ] 테스트 통과: `pnpm test -- novels.api.test.ts`
- [ ] TypeScript 에러 없음: `pnpm type-check`

## ✅ 수락 확인 기준
- [ ] API 모듈 생성 완료
- [ ] 모든 엔드포인트 구현
- [ ] 응답 래퍼 언래핑 확인
- [ ] 에러 핸들링 구현
- [ ] 단위 테스트 통과
- [ ] 수동 테스트 (실제 데이터 요청)

## 🚫 아웃 오브 스코프
- 백엔드 코드 수정 없음
- 새로운 라이브러리 추가 없음
- UI 컴포넌트 구현 없음 (API 연동만)
```

---

## 📝 참고 자료

### 백엔드 API 문서
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

### 프론트엔드 코드베이스 규칙
- 서비스 패턴: `apps/*/services.py` (백엔드 로직)
- 뷰 계층: 백엔드는 ViewSet이 얇은 래퍼
- 타입 힌트: 모든 함수/메서드에 타입 명시 (백엔드)
- API 응답: `{ success: true/false, message, data, timestamp }`
- JSON 네이밍: API Request/Response는 camelCase

---

## 문서 끝
