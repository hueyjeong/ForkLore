# 🏗️ ForkLore 백엔드 아키텍처 설계 (Django)

**작성일**: 2026.01.13  
**작성자**: HueyJeong (with AI)  
**문서 버전**: v5.0 (Django 전환)

---

## 1. 개요 (Overview)

ForkLore 백엔드는 **Django 5.1+ / Python 3.12+** 기반의 모놀리식 아키텍처로, **Django REST Framework (DRF)**를 사용하여 RESTful API를 제공합니다.

### 설계 원칙

| 원칙 | 설명 |
|------|------|
| **App-based Architecture** | 기능 도메인별 Django App 분리 |
| **Fat Models, Thin Views** | 비즈니스 로직은 Model 또는 Service 레이어에 캡슐화 |
| **Service Layer** | 복잡한 비즈니스 로직은 `services/` 모듈로 분리 |
| **DRF Conventions** | Serializer, ViewSet, Router 패턴 준수 |
| **TDD** | pytest-django 기반 테스트 우선 개발 |

---

## 2. 기술 스택

### 2.1 핵심 기술

| 구분 | 기술 | 버전 |
|------|------|------|
| **언어** | Python | 3.12+ |
| **프레임워크** | Django | 5.1+ |
| **API 프레임워크** | Django REST Framework | 3.15+ |
| **패키지 관리** | Poetry | latest |
| **인증** | SimpleJWT + dj-rest-auth | - |
| **API 문서** | drf-spectacular | 0.27+ |

### 2.2 데이터베이스

| 환경 | DB | 용도 |
|------|-----|------|
| 개발/테스트 | SQLite / PostgreSQL | 로컬 개발 |
| 운영 | PostgreSQL 18 | Core Data |
| 운영 | PostgreSQL + pgvector | 벡터 검색 (Gemini Embedding 3072차원) |

### 2.3 인프라

| 구분 | 기술 |
|------|------|
| **컨테이너** | Docker Compose (루트 디렉토리) |
| **비동기 태스크** | Celery + Redis |
| **CI/CD** | GitHub Actions (예정) |

---

## 3. 프로젝트 구조

```
backend/
├── pyproject.toml           # Poetry 의존성 정의
├── poetry.lock
├── manage.py
├── pytest.ini               # pytest 설정
│
├── config/                  # 프로젝트 설정 (settings, urls, wsgi, asgi)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # 공통 설정
│   │   ├── local.py         # 로컬 개발
│   │   ├── production.py    # 운영
│   │   └── test.py          # 테스트
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                    # 기능별 Django 앱
│   ├── __init__.py
│   ├── users/               # 사용자 및 인증
│   │   ├── __init__.py
│   │   ├── models.py        # User, UserRole
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py      # AuthService, UserService
│   │   ├── permissions.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       └── test_views.py
│   │
│   ├── novels/              # 소설 및 브랜치 관리
│   │   ├── models.py        # Novel, Branch, BranchVote, BranchLinkRequest
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py      # NovelService, BranchService
│   │   └── tests/
│   │
│   ├── contents/            # 회차, 위키, 지도
│   │   ├── models.py        # Chapter, WikiEntry, WikiSnapshot, Map, MapSnapshot
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py      # ChapterService, WikiService, MapService
│   │   └── tests/
│   │
│   ├── interactions/        # 댓글, 좋아요, 구독, 결제
│   │   ├── models.py        # Comment, Like, Subscription, Purchase, ReadingLog, Bookmark
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py      # SubscriptionService, PurchaseService, AccessService
│   │   └── tests/
│   │
│   └── ai/                  # AI 연동
│       ├── models.py        # ChapterChunk (벡터 임베딩)
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services.py      # EmbeddingService, AIService
│       └── tests/
│
├── common/                  # 공통 유틸리티
│   ├── __init__.py
│   ├── models.py            # BaseModel (created_at, updated_at)
│   ├── pagination.py        # 커스텀 페이지네이션
│   ├── exceptions.py        # 커스텀 예외
│   ├── permissions.py       # 공통 권한 클래스
│   └── utils.py             # 유틸리티 함수
│
└── tests/                   # 통합 테스트
    ├── __init__.py
    ├── conftest.py          # pytest fixtures
    └── e2e/
        └── test_novel_flow.py
```

---

## 4. 레이어별 역할

### 4.1 Views (Presentation Layer)

```
┌─────────────────────────────────────────────────────┐
│              DRF ViewSet / APIView                  │
│  - HTTP 요청 수신 및 응답 반환                       │
│  - 입력 유효성 검증 (Serializer)                    │
│  - Swagger 문서화 (@extend_schema)                  │
│  - 인증/인가 처리 (permission_classes)              │
└─────────────────────────────────────────────────────┘
```

**책임**:
- HTTP 요청/응답 처리
- Serializer를 통한 데이터 검증 및 변환
- drf-spectacular 데코레이터

**금지 사항**:
- 비즈니스 로직 포함 ❌
- 직접적인 ORM 쿼리 ❌ (단순 CRUD 제외)

### 4.2 Services (Business Layer)

```
┌─────────────────────────────────────────────────────┐
│                  비즈니스 로직                       │
│  - 도메인 규칙 적용                                  │
│  - 트랜잭션 관리 (@transaction.atomic)              │
│  - 여러 Model 조합                                  │
│  - 외부 서비스 연동 (AI API 등)                     │
└─────────────────────────────────────────────────────┘
```

**책임**:
- 핵심 비즈니스 로직
- 도메인 간 조율
- 트랜잭션 경계 설정

**예시**:
```python
# apps/novels/services.py
from django.db import transaction

class NovelService:
    @transaction.atomic
    def create_novel(self, author, data):
        """소설 생성 시 메인 브랜치도 함께 생성"""
        novel = Novel.objects.create(author=author, **data)
        Branch.objects.create(
            novel=novel,
            author=author,
            name=novel.title,
            is_main=True,
            branch_type=BranchType.MAIN
        )
        return novel
```

### 4.3 Serializers (Data Layer)

```
┌─────────────────────────────────────────────────────┐
│              DRF Serializer                          │
│  - 요청 데이터 유효성 검증                           │
│  - 객체 ↔ JSON 직렬화/역직렬화                      │
│  - 중첩 관계 처리                                   │
└─────────────────────────────────────────────────────┘
```

### 4.4 Models (Domain Layer)

```
┌─────────────────────────────────────────────────────┐
│                  Django Model                        │
│  - ORM 정의 (필드, 관계, 제약조건)                   │
│  - 도메인 로직 캡슐화 (property, method)             │
│  - Manager 커스터마이징                             │
└─────────────────────────────────────────────────────┘
```

---

## 5. 핵심 도메인 모델

### 5.1 도메인 관계도

```mermaid
erDiagram
    User ||--o{ Novel : writes
    User ||--o{ Branch : creates
    User ||--o{ Subscription : has
    User ||--o{ Purchase : owns
    
    Novel ||--o{ Branch : contains
    
    Branch ||--o{ Chapter : contains
    Branch ||--o{ WikiEntry : has
    Branch ||--o{ Map : has
    Branch }o--|| Branch : "forked from"
    
    Chapter ||--o{ ChapterChunk : contains
    WikiEntry ||--o{ WikiSnapshot : versions
    Map ||--o{ MapSnapshot : versions
```

### 5.2 주요 모델 설계

#### User (커스텀 유저)

```python
from django.contrib.auth.models import AbstractUser

class UserRole(models.TextChoices):
    READER = 'READER', 'Reader'
    AUTHOR = 'AUTHOR', 'Author'
    ADMIN = 'ADMIN', 'Admin'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    profile_image_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.READER
    )
    auth_provider = models.CharField(max_length=20, default='LOCAL')
    provider_id = models.CharField(max_length=255, blank=True)
    
    mileage = models.IntegerField(default=0)
    coin = models.IntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname']
```

#### Novel (소설)

```python
class Novel(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novels')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    
    genre = models.CharField(max_length=50, choices=Genre.choices)
    age_rating = models.CharField(max_length=10, choices=AgeRating.choices, default=AgeRating.ALL)
    status = models.CharField(max_length=20, choices=NovelStatus.choices, default=NovelStatus.ONGOING)
    
    allow_branching = models.BooleanField(default=True)
    
    # 집계 캐시
    total_view_count = models.BigIntegerField(default=0)
    total_like_count = models.BigIntegerField(default=0)
    total_chapter_count = models.IntegerField(default=0)
    branch_count = models.IntegerField(default=1)
    
    deleted_at = models.DateTimeField(null=True, blank=True)
```

#### Branch (브랜치)

```python
class Branch(BaseModel):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='branches')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branches')
    
    is_main = models.BooleanField(default=False)
    parent_branch = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    fork_point_chapter = models.IntegerField(null=True, blank=True)
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    
    branch_type = models.CharField(max_length=20, choices=BranchType.choices, default=BranchType.FAN_FIC)
    visibility = models.CharField(max_length=20, choices=BranchVisibility.choices, default=BranchVisibility.PRIVATE)
    canon_status = models.CharField(max_length=20, choices=CanonStatus.choices, default=CanonStatus.NON_CANON)
    
    vote_count = models.BigIntegerField(default=0)
    vote_threshold = models.IntegerField(default=1000)
    view_count = models.BigIntegerField(default=0)
    chapter_count = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['novel'],
                condition=models.Q(is_main=True),
                name='unique_main_branch_per_novel'
            )
        ]
```

#### ChapterChunk (벡터 임베딩)

```python
from pgvector.django import VectorField

class ChapterChunk(BaseModel):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content = models.TextField()
    embedding = VectorField(dimensions=3072)  # Gemini Embedding 001
    
    class Meta:
        unique_together = ['chapter', 'chunk_index']
        indexes = [
            # IVFFlat 인덱스는 마이그레이션에서 Raw SQL로 생성
        ]
```

---

## 6. 횡단 관심사 (Cross-Cutting Concerns)

### 6.1 공통 모델 (BaseModel)

```python
# common/models.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

### 6.2 전역 예외 처리

```python
# common/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'message': response.data.get('detail', str(exc)),
            'errors': response.data if 'detail' not in response.data else None,
            'timestamp': timezone.now().isoformat()
        }
    
    return response
```

### 6.3 JWT 인증

```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### 6.4 열람 권한 검사

```python
# apps/interactions/services.py
class AccessService:
    def can_access_chapter(self, user, chapter) -> bool:
        # 1. FREE 회차
        if chapter.access_type == AccessType.FREE:
            return True
        
        # 2. 소장 중
        if Purchase.objects.filter(user=user, chapter=chapter).exists():
            return True
        
        # 3. 구독 중
        return Subscription.objects.filter(
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=timezone.now()
        ).exists()
```

---

## 7. AI 서비스 연동

### 7.1 Gemini API

```python
# apps/ai/services.py
import google.generativeai as genai

class EmbeddingService:
    EMBEDDING_DIMENSION = 3072
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = 'models/text-embedding-001'
    
    def embed(self, text: str) -> list[float]:
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def search_similar(self, embedding: list[float], branch_id: int, limit: int = 5):
        return ChapterChunk.objects.filter(
            chapter__branch_id=branch_id
        ).order_by(
            CosineDistance('embedding', embedding)
        )[:limit]
```

---

## 8. 환경 설정

```python
# config/settings/base.py
import environ

env = environ.Env()

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# JWT
JWT_SECRET = env('JWT_SECRET')

# AI
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'PAGE_SIZE': 20,
}
```

---

## 9. 테스트 전략

### 9.1 테스트 피라미드

```
        ┌─────────┐
        │  E2E   │  ← 최소화 (API 통합 테스트)
       ┌───────────┐
       │Integration│  ← Service + Repository
     ┌───────────────┐
     │    Unit      │  ← Service, Serializer, Model
   └─────────────────┘
```

### 9.2 테스트 도구

| 레벨 | 도구 | 대상 |
|------|------|------|
| Unit | pytest + pytest-django | Service, Serializer |
| Unit | pytest + model_bakery | Model |
| Integration | pytest + APIClient | ViewSet |
| E2E | pytest + APIClient | 전체 플로우 |

### 9.3 TDD 원칙

- **Red → Green → Refactor** 사이클 준수
- 기능 구현 전 테스트 먼저 작성
- 테스트 커버리지 70% 이상 유지

```python
# 예시: tests/conftest.py
import pytest
from model_bakery import baker

@pytest.fixture
def user(db):
    return baker.make('users.User')

@pytest.fixture
def novel(db, user):
    return baker.make('novels.Novel', author=user)
```

---

## 10. 배포 구조 (향후)

```
┌──────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
└──────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │  App 1  │        │  App 2  │        │  App 3  │
    │ (Gunicorn)│      │ (Gunicorn)│      │ (Gunicorn)│
    └─────────┘        └─────────┘        └─────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
            ┌───────────┐     ┌───────────┐
            │ PostgreSQL│     │   Redis   │
            │  Primary  │     │  (Cache)  │
            └───────────┘     └───────────┘
```

---

## 문서 끝
