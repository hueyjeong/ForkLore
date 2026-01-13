# 📊 ForkLore 백엔드 PERT 차트 (P0 태스크)

이 문서는 백엔드 P0 (MVP 필수) 태스크들 간의 종속성을 시각화한 PERT 차트입니다.  
AI 에이전트는 이 차트를 참조하여 **선행 작업이 완료된 태스크**를 다음 작업으로 선정해야 합니다.

```mermaid
graph LR
    %% 스타일 정의
    classDef setup fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef auth fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef novel fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef branch fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef chapter fill:#ffebee,stroke:#b71c1c,stroke-width:2px;
    classDef sub fill:#f9fbe7,stroke:#827717,stroke-width:2px;

    %% 1. 프로젝트 초기 설정
    subgraph Setup [1. 프로젝트 초기 설정]
        direction TB
        Init[Poetry/Django 프로젝트 생성]:::setup --> Settings[settings 분리 + 환경변수]:::setup
        Settings --> BaseModel[common BaseModel]:::setup
        Settings --> DRF[DRF 설정(인증/페이징/예외/응답규약)]:::setup
        DRF --> Swagger[drf-spectacular(OpenAPI)]:::setup
        DRF --> TestInfra[pytest-django 기본 세팅]:::setup
    end

    %% 2. 인증 & 사용자
    subgraph Auth [2. 인증 & 사용자]
        direction TB
        UserModel[User 모델]:::auth --> AuthSerial[Auth Serializer]:::auth
        AuthSerial --> AuthViews[Auth API(ViewSet/APIView)]:::auth
        UserModel --> JWT[SimpleJWT 설정]:::auth
        JWT --> AuthViews
    end

    %% 3. 소설 관리
    subgraph Novel [3. 소설 관리]
        direction TB
        NovelModel[Novel 모델]:::novel --> NovelSerial[Novel Serializer]:::novel
        NovelSerial --> NovelSvc[Novel Service]:::novel
        NovelSvc --> NovelViews[Novel ViewSet]:::novel
    end

    %% 4. 브랜치 시스템
    subgraph Branch [4. 브랜치 시스템]
        direction TB
        BranchModel[Branch 모델]:::branch --> BranchSerial[Branch Serializer]:::branch
        BranchSerial --> BranchSvc[Branch Service]:::branch
        BranchSvc --> BranchViews[Branch ViewSet]:::branch
        BranchModel --> LinkReq[BranchLinkRequest 모델]:::branch
        LinkReq --> BranchViews
    end

    %% 5. 회차 관리
    subgraph Chapter [5. 회차 관리]
        direction TB
        ChapterModel[Chapter 모델]:::chapter --> ChapterSerial[Chapter Serializer]:::chapter
        ChapterSerial --> ChapterSvc[Chapter Service]:::chapter
        ChapterSvc --> ChapterViews[Chapter ViewSet]:::chapter
        ChapterSvc --> Markdown[Markdown→HTML 변환]:::chapter
        ChapterSvc --> Scheduler[Celery 예약발행]:::chapter
    end

    %% 6. 구독 & 권한
    subgraph Subscription [6. 구독 & 권한]
        direction TB
        SubModel[Subscription 모델]:::sub --> SubSvc[Subscription Service]:::sub
        PurchaseModel[Purchase 모델]:::sub --> PurchaseSvc[Purchase Service]:::sub
        SubSvc & PurchaseSvc --> AccessSvc[AccessService(열람권한)]:::sub
        AccessSvc --> SubViews[Subscription API]:::sub
    end

    %% 메인 종속성 연결
    BaseModel --> UserModel
    BaseModel --> NovelModel
    BaseModel --> BranchModel
    BaseModel --> ChapterModel
    BaseModel --> SubModel

    UserModel --> NovelModel
    NovelModel --> BranchModel
    BranchModel --> ChapterModel
    ChapterModel --> PurchaseModel
```

## 📋 작업 순서 가이드

1. **Setup 단계**: 프로젝트 생성 → 설정/공통 모듈/DRF/테스트 인프라
2. **Auth 단계**: User/JWT → Auth API
3. **Novel 단계**: Novel → Service → ViewSet
4. **Branch 단계**: Branch/LinkRequest → Service → ViewSet
5. **Chapter 단계**: Chapter → 렌더링/예약발행 → ViewSet
6. **Sub 단계**: Subscription/Purchase → AccessService → API

---
## 문서 끝
