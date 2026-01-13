# ForkLore 백엔드 개발 가이드라인 (Django)

> **ForkLore 백엔드(Django) 개발자 및 AI 에이전트가 반드시 준수해야 하는 핵심 규칙 모음**

---

## 1. 기술 스택 버전 (필수)

| 카테고리 | 기술 | 버전 | 비고 |
|---|---|---:|---|
| 언어 | Python | 3.12+ | |
| 프레임워크 | Django | 5.1+ | |
| API | Django REST Framework | 3.15+ | |
| 인증 | SimpleJWT + dj-rest-auth | - | |
| 문서화 | drf-spectacular | 0.27+ | OpenAPI 3.1 |
| DB | PostgreSQL | 18 | dev/test/prod 모두 동일 |
| 벡터 | pgvector | - | `vector(3072)` |
| 비동기 | Celery + Redis | - | |
| 패키지 관리 | Poetry | latest | |

---

## 2. TDD (Test-Driven Development) ⚠️ 필수

```
1. RED      → 실패하는 테스트 먼저 작성
2. GREEN   → 테스트를 통과하는 최소 코드 작성
3. REFACTOR → 코드 정리 (테스트는 통과 유지)
```

- 기능 구현 전 **테스트 먼저 작성**
- 테스트 없이 프로덕션 코드 작성 금지
- 테스트 커버리지 **70% 이상** 유지 (가능한 범위 내에서 지속적으로 유지/개선)

---

## 3. 프로젝트 실행/개발 워크플로우

### 3.1 로컬 개발 (Poetry)
```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### 3.2 Docker Compose (권장: DB/Redis 포함)
```bash
docker compose up -d
docker compose exec backend poetry run python manage.py migrate
docker compose exec backend poetry run python manage.py runserver 0.0.0.0:8000
```

### 3.3 마이그레이션 규칙
- 모델 변경 시 반드시 마이그레이션 생성/적용
```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```
- 스키마 변경이 PRD/문서와 충돌하면 **문서/스키마/코드 중 하나가 틀린 것**이므로 먼저 정합성을 맞춘다.

---

## 4. Django/DRF 개발 규칙 (권장 패턴)

### 4.1 App-based Architecture (도메인별 앱 분리)
- `apps/users`, `apps/novels`, `apps/contents`, `apps/interactions`, `apps/ai`
- "기능 단위"로 응집도를 높이고, 앱 간 결합은 Service 레이어에서 조정한다.

### 4.2 Fat Models, Thin Views + Service Layer
- View/ViewSet: 요청/응답, Serializer 검증, 권한/인증, Swagger 문서화
- Service: 트랜잭션/도메인 규칙/여러 모델 조합/외부 연동(Gemini 등)
- Model: 관계/제약/단순 도메인 메서드

---

## 5. 테스트 전략 (표준) ⚠️ 필수

### 5.1 테스트 도구
- `pytest` + `pytest-django`
- `model_bakery` (또는 `factory_boy`)
- API 통합 테스트: `rest_framework.test.APIClient`

### 5.2 테스트 레이어
| 레벨 | 도구 | 대상 | 원칙 |
|---|---|---|---|
| Unit (Service/Domain) | pytest | 서비스/도메인 로직 | DB 의존 최소화, Mock 활용 |
| Unit (Serializer) | pytest | 입력 검증/출력 포맷 | 필수/옵션/에러 케이스 |
| Integration (ViewSet/APIView) | pytest + APIClient | 실제 HTTP 요청/응답 | 인증/권한/페이징 포함 |
| E2E (핵심 플로우) | pytest + APIClient | 큰 흐름 | 최소 개수로 유지 |

### 5.3 실행 명령어
```bash
cd backend
poetry run pytest
poetry run pytest --cov=apps
```

### 5.4 테스트 파일/네이밍 권장
- `apps/<app>/tests/test_models.py`
- `apps/<app>/tests/test_serializers.py`
- `apps/<app>/tests/test_views.py`
- 통합 플로우: `backend/tests/e2e/`

---

## 6. API 규약 (필수)

### 6.1 공통 응답 래퍼 (Success/Failure 동일 규약)
- 모든 성공 응답은 아래 형태로 반환한다.
```json
{
  "success": true,
  "message": null,
  "data": { },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

- 모든 실패 응답은 아래 형태를 유지한다.
```json
{
  "success": false,
  "message": "에러 메시지",
  "data": null,
  "errors": { "field": ["..."] },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

> 구현은 "예외 핸들러"만으로 끝내지 않는다. 성공 응답도 일관되게 감싸도록 Renderer(또는 Response 래퍼 유틸)를 둔다.  
> 상세 구현은 `docs/backend-architecture.md`를 따른다.

### 6.2 Pagination: 1-indexed
- `page=1`이 첫 페이지 (DRF PageNumberPagination 표준)
- query param은 `page`, `size`를 기본으로 사용한다.
  - 예: `GET /novels?page=1&size=20`

### 6.3 JSON camelCase 정책 (API)
- API Request/Response JSON은 **camelCase**
- Python/Django 내부(모델/필드)는 **snake_case**
- camelCase 변환은 DRF 설정(파서/렌더러)으로 통일한다. (구체 설정은 `docs/backend-architecture.md` 참고)

---

## 7. 보안 - 민감 정보 관리 ⚠️ 필수

### 7.1 하드코딩 금지
- `SECRET_KEY`, DB 비밀번호, OAuth client secret, Gemini API Key 등은 코드에 직접 작성 금지
- `django-environ`으로 환경 변수를 통해 주입

### 7.2 .gitignore 필수
- `.env`, `.env.local`, `*.secret` 등 환경 파일은 커밋 금지

### 7.3 커밋 전 점검
```bash
git diff --cached
```
- 의심 문자열(예: `SECRET`, `PASSWORD`, `API_KEY`) 포함 여부 확인

---

## 8. Context7 MCP 활용 ⚠️ 필수
> deprecated 코드 사용 방지 목적

1. 구현 전 `resolve-library-id`로 라이브러리 ID 확인
2. `query-docs`로 최신 사용법/권장 패턴 확인
3. deprecated 경고 발견 시 즉시 대체 구현 적용

---

## 9. Git 운영 규칙 ⚠️ 필수

- **Base Branch**: `develop`
- **Naming**: `feat/#<이슈번호>-<간단요약-영어>`
- **금지**: 사용자 승인 없이 `main`/`develop` 강제 푸시/덮어쓰기
- 작업 완료 시 반드시 PR 생성 (Target: `develop`)

---

## 10. 문서/스키마 정합성 규칙
- PRD / API 명세 / DB 스키마 문서 / 코드 중 하나라도 불일치하면
  1) **PRD 요구사항** 우선 확인
  2) 문서와 코드 중 "단일 진실(SSOT)"을 정하고
  3) 나머지를 그에 맞게 업데이트한다.

---

## 문서 끝
