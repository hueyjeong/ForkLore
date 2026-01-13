# ForkLore 백엔드 PERT 차트 (P0 태스크)

이 문서는 백엔드 P0 (MVP 필수) 태스크들 간의 종속성을 시각화한 PERT 차트입니다.  
AI 에이전트는 이 차트를 참조하여 **선행 작업이 완료된 태스크**를 다음 작업으로 선정해야 합니다.

```mermaid
graph LR
    subgraph Setup["1. 프로젝트 초기 설정"]
        direction TB
        Init["Poetry/Django 프로젝트 생성"] --> Settings["settings 분리 + 환경변수"]
        Settings --> BaseModel["common BaseModel"]
        Settings --> DRF["DRF 설정"]
        DRF --> Swagger["drf-spectacular"]
        DRF --> TestInfra["pytest-django"]
    end

    subgraph Auth["2. 인증 및 사용자"]
        direction TB
        UserModel["User 모델"] --> AuthSerial["Auth Serializer"]
        AuthSerial --> AuthViews["Auth API"]
        UserModel --> JWT["SimpleJWT 설정"]
        JWT --> AuthViews
    end

    subgraph Novel["3. 소설 관리"]
        direction TB
        NovelModel["Novel 모델"] --> NovelSerial["Novel Serializer"]
        NovelSerial --> NovelSvc["Novel Service"]
        NovelSvc --> NovelViews["Novel ViewSet"]
    end

    subgraph Branch["4. 브랜치 시스템"]
        direction TB
        BranchModel["Branch 모델"] --> BranchSerial["Branch Serializer"]
        BranchSerial --> BranchSvc["Branch Service"]
        BranchSvc --> BranchViews["Branch ViewSet"]
        BranchModel --> LinkReq["BranchLinkRequest 모델"]
        LinkReq --> BranchViews
    end

    subgraph Chapter["5. 회차 관리"]
        direction TB
        ChapterModel["Chapter 모델"] --> ChapterSerial["Chapter Serializer"]
        ChapterSerial --> ChapterSvc["Chapter Service"]
        ChapterSvc --> ChapterViews["Chapter ViewSet"]
        ChapterSvc --> Markdown["Markdown to HTML 변환"]
        ChapterSvc --> Scheduler["Celery 예약발행"]
    end

    subgraph Subscription["6. 구독 및 권한"]
        direction TB
        SubModel["Subscription 모델"] --> SubSvc["Subscription Service"]
        PurchaseModel["Purchase 모델"] --> PurchaseSvc["Purchase Service"]
        SubSvc --> AccessSvc["AccessService"]
        PurchaseSvc --> AccessSvc
        AccessSvc --> SubViews["Subscription API"]
    end

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

## 작업 순서 가이드

1. **Setup 단계**: 프로젝트 생성 → 설정/공통 모듈/DRF/테스트 인프라
2. **Auth 단계**: User/JWT → Auth API
3. **Novel 단계**: Novel → Service → ViewSet
4. **Branch 단계**: Branch/LinkRequest → Service → ViewSet
5. **Chapter 단계**: Chapter → 렌더링/예약발행 → ViewSet
6. **Sub 단계**: Subscription/Purchase → AccessService → API
