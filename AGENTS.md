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

## 설계 문서 참조

| 문서 | 설명 |
|------|------|
| `docs/PRD.md` | 제품 요구사항 정의 |
| `docs/database-schema.md` | DB 스키마 (v4) |
| `docs/backend-architecture.md` | 백엔드 아키텍처 (v4) |
| `docs/api-specification.md` | REST API 명세 (v2) |
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
