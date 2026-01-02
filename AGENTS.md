# ForkLore 프로젝트 - AI 에이전트 가이드

## 프로젝트 개요

**ForkLore**는 인터랙티브 웹소설 플랫폼입니다.

- **그룹**: `io.forklore`
- **버전**: `0.0.1-SNAPSHOT`

---

## 기술 스택

### 백엔드 (Backend)
| 카테고리 | 기술 | 버전 |
|----------|------|------|
| **언어** | Java | 23 |
| **프레임워크** | Spring Boot | 4.0.1 |
| **빌드** | Gradle | Wrapper |
| **ORM** | Spring Data JPA | - |
| **보안** | Spring Security + JWT | - |
| **API 문서** | Springdoc OpenAPI | 3.0.0 |
| **데이터베이스** | PostgreSQL + pgvector | 18 |
| **AI** | Gemini API | text-embedding-001 (3072차원) |

### 프론트엔드 (Frontend)
| 카테고리 | 기술 | 버전/스타일 |
|----------|------|-------------|
| **프레임워크** | Next.js (App Router) | 16 |
| **언어** | TypeScript | 5.x |
| **패키지 매니저** | pnpm | - |
| **CSS** | Tailwind CSS | 4.x |
| **컴포넌트** | shadcn/ui | New York 스타일 |
| **색상 시스템** | OKLCH | - |
| **아이콘** | Lucide Icons | - |
| **폰트** | Geist Sans/Mono | - |
| **서버 상태** | TanStack Query | v5 |
| **클라이언트 상태** | Zustand | - |
| **폼** | React Hook Form + Zod | - |
| **에디터** | Tiptap | - |
| **지도** | Leaflet + React Leaflet | - |
| **인증** | NextAuth.js | v5 |
| **테스트** | Vitest + Playwright | - |

### 인프라
| 카테고리 | 기술 |
|----------|------|
| **컨테이너** | Docker Compose V2 |
| **개발 환경** | Dev Container (VS Code) |
| **CI/CD** | GitHub Actions (예정) |

---

## 핵심 도메인 모델 (v4)

```
Novel (소설)
  └── Branch (브랜치)
        ├── is_main=true: 메인 스토리
        ├── is_main=false: 외전/팬픽/IF
        │
        ├── Chapter (회차)
        │     ├── content: 마크다운 원본
        │     ├── content_html: 렌더링 캐시
        │     └── access_type: FREE | SUBSCRIPTION
        │
        ├── WikiEntry (위키)
        │     └── WikiSnapshot (회차별 스냅샷)
        │
        └── Map (지도)
              └── MapSnapshot (회차별 스냅샷)
```

### 브랜치 시스템
- **branch_type**: SIDE_STORY, FAN_FIC, IF_STORY
- **visibility**: PRIVATE, PUBLIC, LINKED
- **canon_status**: NON_CANON, CANDIDATE, MERGED

### 구독 시스템
- **FREE**: 무료 열람
- **SUBSCRIPTION**: 구독 중 or 소장 시 열람

---

## 프로젝트 구조

```
/workspaces/ForkLore/
├── .devcontainer/              # Dev Container 설정
├── backend/                    # Spring Boot 백엔드
│   ├── src/main/java/io/forklore/
│   │   ├── domain/            # Entity
│   │   ├── repository/
│   │   ├── service/
│   │   ├── controller/
│   │   ├── dto/
│   │   ├── exception/
│   │   └── security/
│   └── build.gradle
├── frontend/                   # Next.js 프론트엔드 (예정)
│   ├── app/                   # App Router 라우트
│   ├── components/            # UI 컴포넌트
│   ├── lib/                   # 유틸, API 클라이언트
│   ├── hooks/                 # 커스텀 훅
│   ├── stores/                # Zustand 스토어
│   └── types/                 # TypeScript 타입
├── docs/                       # 설계 문서
│   ├── PRD.md
│   ├── database-schema.md
│   ├── backend-architecture.md
│   ├── api-specification.md
│   ├── design-system.md
│   ├── backend-tasks.md       # 백엔드 태스크
│   └── frontend-tasks.md      # 프론트엔드 태스크
└── AGENTS.md
```

---

## 개발 규칙

### 1. TDD (Test-Driven Development) ⚠️ 필수

> **AI 에이전트가 코드를 작성할 때 반드시 TDD 원칙을 따라야 합니다.**

```
1. RED    → 실패하는 테스트 먼저 작성
2. GREEN  → 테스트를 통과하는 최소 코드 작성
3. REFACTOR → 코드 정리 (테스트는 통과 유지)
```

**필수 사항:**
- 기능 구현 전 **테스트 먼저 작성**
- 테스트 없이 프로덕션 코드 작성 금지
- 테스트 커버리지 **70% 이상** 유지

### 2. 백엔드 명령어
```bash
./gradlew build
./gradlew bootRun
./gradlew test
```

### 3. 프론트엔드 명령어
```bash
pnpm install
pnpm dev
pnpm test
pnpm build
```

### 4. 데이터베이스
- **Host**: `db` (Docker Compose)
- **Port**: `5432`
- **Database**: `app_db`
- **Extension**: pgvector

### 5. API 문서화
- **Swagger UI**: `/swagger-ui.html`
- **OpenAPI**: `/v3/api-docs`

### 6. 보안
- **JWT 인증** (Access + Refresh Token)
- **BCrypt** 비밀번호 암호화
- **@PreAuthorize** 권한 검사

---

## GitHub 템플릿 사용법

### Issue 템플릿

프로젝트에는 백엔드와 프론트엔드를 위한 Issue 템플릿이 준비되어 있습니다:

#### 백엔드
- **🔧 기능 개발**: `.github/ISSUE_TEMPLATE/backend-feature.md`
  - 신규 기능 개발 또는 개선
  - TDD 체크리스트 포함
  - Entity, Service, Controller, Repository 구조
  
- **🐛 버그 수정**: `.github/ISSUE_TEMPLATE/backend-bug.md`
  - 버그 리포트 및 수정
  - 재현 단계 명시
  - 우선순위별 분류

#### 프론트엔드
- **🎨 기능 개발**: `.github/ISSUE_TEMPLATE/frontend-feature.md`
  - 신규 기능 개발 또는 개선
  - 디자인 시스템 체크리스트
  - 반응형 및 접근성 체크
  
- **🎨 버그 수정**: `.github/ISSUE_TEMPLATE/frontend-bug.md`
  - UI/UX 버그 리포트
  - 브라우저 호환성 체크

**사용 방법**: GitHub Issues → New Issue → 템플릿 선택

### Pull Request 템플릿

PR 생성 시 백엔드/프론트엔드 템플릿을 선택할 수 있습니다:

#### 방법 1: URL 쿼리 파라미터 사용
```
# 백엔드 PR
https://github.com/[owner]/ForkLore/compare/[branch]?template=pull_request_template_backend.md

# 프론트엔드 PR
https://github.com/[owner]/ForkLore/compare/[branch]?template=pull_request_template_frontend.md
```

#### 방법 2: PR 생성 후 수동 선택
1. PR 생성 페이지 접속
2. 우측 "Preview template" 드롭다운에서 템플릿 선택
3. 또는 템플릿 파일 내용을 복사하여 붙여넣기

#### 백엔드 PR 체크리스트
- ✅ TDD 원칙 준수 (RED-GREEN-REFACTOR)
- ✅ 테스트 커버리지 70% 이상
- ✅ Swagger API 문서 업데이트
- ✅ 보안 체크 (SQL Injection, XSS 등)
- ✅ 성능 체크 (N+1 쿼리 등)

#### 프론트엔드 PR 체크리스트
- ✅ 디자인 시스템 준수 (shadcn/ui, Tailwind CSS)
- ✅ 반응형 디자인 (모바일/태블릿/데스크톱)
- ✅ 접근성 (a11y) 확인
- ✅ 브라우저 호환성 확인
- ✅ 성능 최적화 체크

---

## AI 에이전트 작업 절차 (Workflow)

프로젝트 작업을 수행할 때 AI 에이전트는 반드시 다음 절차를 준수해야 합니다.

### 1. 최신 기술 스택 확인 (Context7)
- **원칙**: 모든 코드는 현재 사용 중인 라이브러리/프레임워크의 **최신 버전 사용법**을 따릅니다.
- **실행**: 구현 전 `Context7` 도구를 사용하여 최신 공식 문서와 예제를 확인합니다. (예: Next.js 16, Spring Boot 4.x)

### 2. 이슈 확인 및 선정
- `GitHub MCP`를 사용하여 열려있는 이슈 목록을 확인합니다.
- **선정 기준**:
  - `docs/backend-pert-chart.md` (백엔드) 또는 관련 로직 흐름도를 참조하여 선행 작업(종속성)이 완료되었는지 확인
  - 선행 작업이 완료되어 `develop` 브랜치에 반영된 이슈
  - 병렬 처리가 가능한 독립적인 이슈
  - 우선순위(P0 > P1)가 높은 이슈

### 3. 브랜치 전략
- **Base Branch**: `develop`
- **Naming**: `feat/#<이슈번호>-<간단요약-영어>`
  - 예: `feat/#42-auth-login`, `fix/#15-user-entity`

### 4. 작업 수행 (TDD)
1. 브랜치 생성 (`create_branch`)
2. 이슈 체크리스트 업데이트 (`update_issue`)
3. **TDD 사이클** 수행 (Red → Green → Refactor)
4. 완료 시 이슈 체크리스트 최종 완료 표시

### 5. Pull Request 생성
- 작업이 완료되면 `GitHub MCP`를 사용하여 PR을 생성합니다.
- **Target**: `develop`
- **내용**: 작업 요약, 테스트 결과, 관련 이슈 번호 (`Closes #이슈번호`)
- **보고**: PR 생성 후 사용자에게 링크와 함께 보고합니다.

### 6. 승인 및 반복
- 사용자의 PR 검토 및 승인을 대기합니다.
- 사용자의 지시에 따라 다음 "진행 가능한 이슈"를 선정하여 프로세스를 반복합니다.

---

## 설계 문서 참조

| 문서 | 설명 |
|------|------|
| `docs/PRD.md` | 제품 요구사항 정의 |
| `docs/backlog.md` | 제품 백로그 (v2) |
| `docs/database-schema.md` | DB 스키마 (v4) |
| `docs/backend-architecture.md` | 백엔드 아키텍처 (v4) |
| `docs/api-specification.md` | REST API 명세 (v2) |
| `docs/ui-ux-specification.md` | UI/UX 명세서 |
| `docs/wireframes.md` | 와이어프레임 |
| `docs/design-system.md` | 디자인 시스템 |
| `docs/backend-tasks.md` | 백엔드 태스크 목록 |
| `docs/frontend-tasks.md` | 프론트엔드 태스크 목록 |

---

## 버전 히스토리
- **v0.0.1-SNAPSHOT**: 초기 프로젝트 구조 및 설계 문서 완성
  - Spring Boot 4.0.1 / Java 23
  - Next.js 16 / TypeScript / TanStack Query / Zustand
  - PostgreSQL 18 + pgvector
  - Gemini Embedding 001 (3072차원)
  - 브랜치 통합 스키마 (v4)
