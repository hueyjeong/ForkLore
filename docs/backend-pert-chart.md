# ForkLore 백엔드 PERT 차트 (P0 태스크)

이 문서는 백엔드 P0 (MVP 필수) 태스크들 간의 종속성을 시각화한 PERT 차트입니다.  
AI 에이전트는 이 차트를 참조하여 **선행 작업이 완료된 태스크**를 다음 작업으로 선정해야 합니다.

```mermaid
graph LR
    subgraph Setup["1. 프로젝트 초기 설정"]
        direction TB
        Init["Poetry/Django 프로젝트 생성"] --> Settings["settings 분리 + 환경변수"]
        Settings --> Common["common 모듈(BaseModel/exceptions/pagination)"]
        Settings --> DRF["DRF 설정"]
        DRF --> Swagger["drf-spectacular"]
        Settings --> TestInfra["pytest-django"]
        Settings --> CeleryConfig["Celery/Redis 설정"]
    end

    subgraph Auth["2. 인증 및 사용자"]
        direction TB
        UsersApp["users 앱 생성"] --> UserModel["User 모델"]
        UserModel --> JWT["SimpleJWT 설정"]
        UserModel --> AuthSvc["AuthService"]
        JWT --> AuthSvc
        AuthSvc --> AuthSerial["Auth Serializer"]
        AuthSerial --> AuthViews["Auth API"]
        UserModel --> OAuth2["OAuth2 설정"]
        UserModel --> UserSvc["UserService"]
        UserSvc --> UserViews["User API"]
    end

    subgraph Novel["3. 소설 관리"]
        direction TB
        NovelsApp["novels 앱 생성"] --> NovelModel["Novel 모델"]
        NovelModel --> NovelSerial["Novel Serializer"]
        NovelSerial --> NovelSvc["NovelService"]
        NovelSvc --> NovelViews["Novel ViewSet"]
    end

    subgraph Branch["4. 브랜치 시스템"]
        direction TB
        BranchModel["Branch 모델"] --> BranchSerial["Branch Serializer"]
        BranchSerial --> BranchSvc["BranchService"]
        BranchSvc --> BranchViews["Branch ViewSet"]
        BranchModel --> LinkReq["BranchLinkRequest 모델"]
        LinkReq --> LinkSvc["BranchLinkService"]
        LinkSvc --> BranchViews
        BranchModel --> BranchVote["BranchVote 모델"]
        BranchVote --> BranchViews
    end

    subgraph Chapter["5. 회차 관리"]
        direction TB
        ContentsApp["contents 앱 생성"] --> ChapterModel["Chapter 모델"]
        ChapterModel --> ChapterSerial["Chapter Serializer"]
        ChapterSerial --> ChapterSvc["ChapterService"]
        ChapterSvc --> ChapterViews["Chapter ViewSet"]
        ChapterSvc --> Markdown["Markdown to HTML"]
        CeleryConfig --> Scheduler["Celery 예약발행 태스크"]
        ChapterSvc --> Scheduler
    end

    subgraph Subscription["6. 구독 및 결제"]
        direction TB
        InteractionsApp["interactions 앱 생성"] --> SubModel["Subscription 모델"]
        InteractionsApp --> PurchaseModel["Purchase 모델"]
        SubModel --> SubSvc["SubscriptionService"]
        PurchaseModel --> PurchaseSvc["PurchaseService"]
        SubSvc --> AccessSvc["AccessService"]
        PurchaseSvc --> AccessSvc
        AccessSvc --> SubViews["Subscription/Purchase API"]
    end

    %% Setup -> 모든 도메인 모델
    Common --> UserModel
    Common --> NovelModel
    Common --> BranchModel
    Common --> ChapterModel
    Common --> SubModel
    Common --> PurchaseModel

    %% DB FK 기반 종속성
    UserModel --> NovelModel
    NovelModel --> BranchModel
    BranchModel --> ChapterModel
    ChapterModel --> PurchaseModel
    UserModel --> SubModel
    UserModel --> PurchaseModel
    UserModel --> LinkReq
    UserModel --> BranchVote

    %% 비즈니스 로직 종속성
    NovelSvc --> BranchSvc
    AccessSvc --> ChapterSvc
```

## 작업 순서 가이드

1. **Setup**: 프로젝트 생성 → settings → common/DRF/pytest/Celery
2. **Auth**: users 앱 → User 모델 → JWT/AuthService/OAuth2 → Auth API
3. **Novel**: novels 앱 → Novel 모델 → Serializer → Service → ViewSet
4. **Branch**: Branch 모델 → LinkRequest/Vote → Service → ViewSet
5. **Chapter**: contents 앱 → Chapter 모델 → Service(+AccessService) → ViewSet
6. **Subscription**: interactions 앱 → Sub/Purchase 모델 → Service → AccessService → API

## 주요 종속성 설명

| 종속성 | 이유 |
|--------|------|
| `Common → 모든 모델` | BaseModel 상속 |
| `UserModel → NovelModel` | `novels.author_id` FK |
| `NovelModel → BranchModel` | `branches.novel_id` FK |
| `BranchModel → ChapterModel` | `chapters.branch_id` FK |
| `ChapterModel → PurchaseModel` | `purchases.chapter_id` FK |
| `UserModel → SubModel/PurchaseModel` | `user_id` FK |
| `NovelSvc → BranchSvc` | Novel 생성 시 메인 브랜치 자동 생성 |
| `AccessSvc → ChapterSvc` | Chapter.retrieve()가 열람 권한 검사 호출 |
| `CeleryConfig → Scheduler` | 예약 발행 태스크 선행 조건 |
