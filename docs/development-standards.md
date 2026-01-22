# development-standards.md

ForkLore 개발 시 팀 단위로 합의된 **명명/구조/품질** 규칙을 정의합니다.

## 0. 문서 우선순위 (Source of Truth)

- 작업 규칙/명령어/브랜치/커밋: `AGENTS.md`
- API 규약(응답 래핑, camelCase JSON 등): `docs/api-specification.md`
- 백엔드 아키텍처(서비스 레이어, renderer/parser 등): `docs/backend-architecture.md`

## 1. Naming Conventions

### 1.1 공통

- **Python 코드**: `snake_case`
- **TypeScript 코드**: `camelCase` (변수/함수), `PascalCase` (컴포넌트/클래스)
- **상수**: `SCREAMING_SNAKE_CASE`
- **JSON(Request/Response) 필드**: `camelCase` (내부 Django 필드 `snake_case`와 분리)
- **약어/ID**:
  - TS/JSON: `userId`, `novelId` 처럼 `Id`로 통일 (`userID` 금지)
  - Python: `user_id`, `novel_id`

### 1.2 Backend (Django/DRF)

- **Django App/패키지 경로**: 도메인 단위 `apps/<domain>/...` (예: `apps/novels/`, `apps/interactions/`)
- **모듈/파일명**: `snake_case.py` (예: `services.py`, `test_views.py`)
- **Model**: `PascalCase` 단수 (예: `Novel`, `BranchLinkRequest`)
- **Model field**: `snake_case` (예: `created_at`, `is_main`)
- **Service**: `<Domain>Service` (예: `NovelService`, `AccessService`)
  - 메서드명은 동사로 시작: `create`, `publish`, `fork`, `can_access_chapter`
  - 트랜잭션 경계는 Service에서: `@transaction.atomic`
- **Serializer**:
  - 기본: `<Model>Serializer`
  - 목적이 다르면 접미사로 구분: `<Model>CreateSerializer`, `<Model>ListSerializer`, `<Model>DetailSerializer`
- **ViewSet/APIView**: `<Model>ViewSet`
- **URL path**: path segment는 `kebab-case` 권장 (예: `link-request`, `reading-logs`)
- **Path parameter / Query parameter / JSON field**: 외부로 노출되는 이름은 `camelCase` 기준(상세는 `docs/api-specification.md` 우선)

### 1.3 Frontend (Next.js/TypeScript)

- **경로(디렉토리/파일명)**: `kebab-case`
  - 예: `frontend/components/novel-card.tsx`, `frontend/hooks/use-novel.ts`, `frontend/lib/api/novels-api.ts`
- **React component 이름(심볼/export)**: `PascalCase`
  - 예: `NovelCard`, `ChapterEditor`
- **Hook**:
  - export: `useXxx` (`useNovel`)
  - 파일명: `use-xxx.ts` (`use-novel.ts`)
- **Zustand store**:
  - hook export: `useXxxStore` (`useAuthStore`, `useNovelStore`)
  - 파일명: `xxx-store.ts` (`auth-store.ts`)
- **API client 함수**:
  - 동사+리소스: `getNovel`, `createNovel`, `listNovels`
  - 파일명: `xxx-api.ts` (`novels-api.ts`)

## 2. Project Structure & Boundaries

### 2.1 Backend

- View는 **thin wrapper**만 담당한다.
  - 입력 검증(Serializer) → Service 호출 → Response 반환(래핑은 renderer가 수행)
- 비즈니스 로직은 **반드시** `services.py`에 둔다.
  - View/Serializer에 도메인 규칙/트랜잭션/외부 연동 로직을 넣지 않는다.

### 2.2 Frontend

- `app/`: Next.js App Router 라우트(기본은 Server Component)
- `components/`: 재사용 UI(필요 시 `use client`)
- `lib/`: API client, schema, shared utils
- `hooks/`: UI/상태 관련 hook
- `stores/`: Zustand store

## 3. Code Style

### 3.1 Python

- 모든 함수에 타입힌트 필수
- Docstring은 Google Style (Args/Returns/Raises)
- Ruff 준수 (line-length: 100)
- import 순서: stdlib → django → 3rd-party → local

### 3.2 TypeScript

- `as any`, `@ts-ignore`, `@ts-expect-error` 금지
- named export 선호
- Prettier 규칙 준수 (세미콜론 없음, single quote, tab width 2)

## 4. Testing (TDD)

- 기본 원칙: **RED → GREEN → REFACTOR**

### 4.1 Backend

- `pytest` 기반, 테스트는 `apps/<domain>/tests/`에 작성
- Service 레이어는 최소 unit test를 갖는다.
- View는 핵심 플로우에 대해 integration test를 갖는다.

### 4.2 Frontend

- `pnpm test` (Vitest)
- 순수 로직(validator, formatter, API client)은 unit test 우선

## 5. API Response & Errors

상세 규약은 `docs/api-specification.md`를 따른다.

- View는 wrapping 하지 않고 **raw data**만 반환한다.
- 성공 응답은 `StandardJSONRenderer`가 자동으로 wrapping 한다.

Success:
```json
{
  "success": true,
  "message": null,
  "data": {},
  "timestamp": "2026-01-13T12:00:00+09:00"
}
```

Validation Error:
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "fieldName": ["Error message 1"]
  },
  "timestamp": "2026-01-13T12:00:00+09:00"
}
```

## 6. Git Workflow

- Base branch: `develop`
- 브랜치명: `feat/#<issue>-<short-english-summary>`, `fix/#<issue>-<short-english-summary>`
- 커밋 메시지: `type(scope): message`
  - type: `feat | fix | refactor | docs | test | chore`
  - scope 예: `users`, `novels`, `api`, `ui`
- `main/develop`에 force push 금지

## 7. Environment & Secrets

- 실제 시크릿(`.env`, `.env.local` 등)은 커밋 금지
- 필요한 환경변수는 코드에서 조용히 기본값을 두지 말고(운영/테스트 포함) **명시적으로 실패**하도록 한다.
- Backend는 `DATABASE_URL` 등 주요 설정을 환경변수로 주입한다(상세는 `docs/backend-architecture.md`).
