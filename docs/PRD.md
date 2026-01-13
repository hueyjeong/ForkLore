# 📄 [PRD] ForkLore: 인터랙티브 월드 웹소설 플랫폼

**작성일**: 2026.01.02  
**작성자**: HueyJeong (with Gemini)  
**문서 버전**: v1.1

---

## 1. 프로젝트 개요 (Overview)

### 제품명 (가칭): ForkLore (포크로어)

### 핵심 가치:

- **Dynamic Context**: 독자의 열람 시점에 맞춰 변화하는 위키와 지도 (스포일러 방지).
- **Interactive Writing**: 깃(Git)의 브랜치를 모방한 스핀오프(이하 팬픽)의 작성과 팬픽의 정사(Canon) 편입 및 협업 생태계.
- **AI Co-Pilot**: 작가의 세계관 관리(위키, 지도) 자동화 및 보조.

### 타겟 유저:

- 설정 덕후 성향의 판타지/대체역사 독자.
- 세계관 관리가 어려운 장편 소설 작가.
- 2차 창작 욕구가 강한 팬픽러.

---

## 2. 기술 스택 (Tech Stack)

### Backend
- **언어**: Python 3.12+
- **프레임워크**: Django 5.1+
- **API 프레임워크**: Django REST Framework (DRF)
- **패키지 관리**: Poetry
- **주요 의존성**:
  - djangorestframework (REST API)
  - djangorestframework-simplejwt (JWT 인증)
  - dj-rest-auth + django-allauth (소셜 로그인)
  - drf-spectacular (OpenAPI 3.1 문서화)
  - django-environ (환경 변수 관리)
  - celery + redis (비동기 태스크)
- **데이터베이스 드라이버**: psycopg[binary], django-pgvector

### Frontend
- **프레임워크**: Next.js 16 (App Router)
- **언어**: TypeScript
- **상태 관리**: Zustand, TanStack Query v5
- **스타일링**: Tailwind CSS 4.x, shadcn/ui (New York)
- **폼**: React Hook Form + Zod
- **에디터**: Tiptap
- **지도**: Leaflet + React Leaflet
- **인증**: NextAuth.js v5

### Database
- **Primary**: PostgreSQL 18 (Core Data)
- **Vector Extension**: pgvector + django-pgvector (Vector Search/RAG)
- **Embedding**: Gemini text-embedding-001 (3072차원)

### Infrastructure & AI
- **컨테이너**: Docker Compose (루트 디렉토리)
- **AI**: Gemini API
- **캐시/태스크 브로커**: Redis

---

## 3. 핵심 기능 명세 (Functional Specifications)

### A. 독자 시스템 (Reader Experience)

#### 1. 인터랙티브 뷰어

**마크다운/마크업 렌더링**: 텍스트 효과, 이미지, BGM 트리거 지원.

**문맥 인식 위키 (Context-Aware Wiki)**:
- **스냅샷 로직**: 독자가 N화를 읽을 때, `Valid_From <= N`인 위키 데이터 중 가장 최신 버전만 노출.
- **UX**: 키워드 하이라이팅 → 클릭 시 툴팁(요약) → '더 보기' 시 AI 채팅.
- **하이브리드 RAG**: AI 질문 시, 현재 회차까지의 줄거리 벡터만 검색 범위로 지정 (미래 정보 차단).

**댓글 시스템**:
- 회차별 댓글(Paragraph Comment) 지원.
- 스포일러 방지 필터 및 신고 기능.

#### 2. 다이내믹 지도 (Dynamic Map)

- **타임라인 연동**: 회차 진행에 따라 국경선, 부대 위치 등 레이어(Layer) 변경.
- **상호작용**: 지도 내 오브젝트 클릭 시 관련 위키 정보 팝업.

#### 3. 구독 및 AI 티어

- **BM**: 월 정액제 (플랫폼 부담 모델).
- **제한 정책**: AI 딥 검색(채팅)은 일일 횟수 제한(토큰 비용 방어), 프리미엄 티어는 한도 상향.

---

### B. 작가 스튜디오 (Author Studio)

#### 1. 에디터 및 발행

**Markdown 에디터**: AI 보조 도구 내장 (문장 다듬기, 설정 검사).

**예약 업로드 (Scheduled Publish)**:
- 상태값: `Draft → Scheduled (공개일 설정) → Published`.

**AI 코파일럿 (World Builder)**:
- **위키 자동 생성**: 본문 분석 → 인물/사건 정보 추출 → 위키 스냅샷 초안 생성 → 작가 승인.
- **Text-to-Map**: 텍스트("군대가 남하했다") → 지도 에디터에 경로 초안 표시 → 작가 수정/확정.

#### 2. 위키 관리 및 히스토리

- **미래 설정 메모**: 아직 공개되지 않은 설정을 '비공개(Hidden)' 상태로 저장 (AI 기억용).
- **기여 내역 (Wiki History)**: 위키 수정 시 Contributor, Diff, Timestamp 기록.

---

### C. 깃(Git)의 브랜치를 모방한 팬픽 시스템 (The "ForkLore" Core)

> **정사 편입이란 팬픽 브랜치가 정사 브랜치의 어느 지점과 논리적으로 연결(Link)되는 것으로 정사의 스토리와 팬픽이 합쳐지는 것이 아님.**  
> 즉 팬픽이 정사로 편입되면 외전이 되는 것임

#### 1. 브랜치(Branch) & 포크(Fork)

- **메인 브랜치**: 원작자의 정사(Canon) 스토리.
- **팬픽 포크**: 독자가 특정 회차(Commit)에서 Fork하여 IF 스토리 연재.
- **설정 상속**: 포크된 시점까지의 위키/지도 데이터를 그대로 물려받음.

#### 2. 정사 편입 요청 (Link Request) 및 투표

- **커뮤니티 검증**: 팬픽 브랜치의 추천 수(Votes)가 작가가 설정한 임계값(Threshold) 도달 시, 자동으로 '편입 후보'로 격상 및 작가에게 알림.
- **작가 검토**: 작가 전용 Diff 뷰어에서 내용 확인 후 승인/거절/수정 제안.
- **보상 정책**: 연결 승인 시, 저작권 매절 계약 팝업 → 동의 시 보상 지급 및 크레딧 표기 (`Co-authored by [User]`).

---

## 문서 끝
