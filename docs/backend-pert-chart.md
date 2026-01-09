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
        Init[패키지 구조 생성]:::setup --> BaseEntity[BaseEntity]:::setup
        Init --> Configs[GlobalException / Swagger / YML]:::setup
    end

    %% 2. 인증 & 사용자
    subgraph Auth [2. 인증 & 사용자]
        direction TB
        UserEnt[User 엔티티]:::auth --> UserRepo[User Repository]:::auth
        UserRepo --> UserSvc[User Service]:::auth
        UserRepo --> SecConfig[Security Config]:::auth
        SecConfig --> Jwt[JWT Provider/Filter]:::auth
        Jwt --> AuthService[Auth Service]:::auth
        AuthService --> AuthCtrl[Auth Controller]:::auth
    end

    %% 3. 소설 관리
    subgraph Novel [3. 소설 관리]
        direction TB
        NovelEnt[Novel 엔티티]:::novel --> NovelRepo[Novel Repository]:::novel
        NovelRepo --> NovelSvc[Novel Service]:::novel
        NovelSvc --> NovelCtrl[Novel Controller]:::novel
    end

    %% 4. 브랜치 시스템
    subgraph Branch [4. 브랜치 시스템]
        direction TB
        BranchEnt[Branch 엔티티]:::branch --> BranchRepo[Branch Repository]:::branch
        BranchRepo --> BranchSvc[Branch Service]:::branch
        BranchSvc --> BranchCtrl[Branch Controller]:::branch
    end

    %% 5. 회차 관리
    subgraph Chapter [5. 회차 관리]
        direction TB
        ChapEnt[Chapter 엔티티]:::chapter --> ChapRepo[Chapter Repository]:::chapter
        ChapRepo --> ChapSvc[Chapter Service]:::chapter
        ChapSvc --> ChapCtrl[Chapter Controller]:::chapter
    end

    %% 6. 구독 & 결제
    subgraph Subscription [6. 구독 & 결제]
        direction TB
        SubEnt[Subscription 엔티티]:::sub --> SubRepo[Subscription Repository]:::sub
        SubRepo --> SubSvc[Subscription Service]:::sub
        
        PurEnt[Purchase 엔티티]:::sub --> PurRepo[Purchase Repository]:::sub
        PurRepo --> PurSvc[Purchase Service]:::sub

        SubSvc & PurSvc --> AccessSvc[Access Service]:::sub
        AccessSvc --> AccessAOP[구독/권한 AOP]:::sub
    end

    %% 메인 종속성 연결
    BaseEntity --> UserEnt
    BaseEntity --> NovelEnt
    BaseEntity --> BranchEnt
    BaseEntity --> ChapEnt
    BaseEntity --> SubEnt

    UserEnt --> NovelEnt
    NovelEnt --> BranchEnt
    BranchEnt --> ChapEnt
    
    UserEnt --> SubEnt
    ChapEnt --> PurEnt
```

## 📋 작업 순서 가이드

1. **Setup 단계**: `패키지 구조` -> `BaseEntity` 및 설정 파일들
2. **Auth 단계**: `User Entity` -> `Repository` -> `Security/JWT` -> `Auth Service`
3. **Novel 단계**: `Novel Entity` -> `Repository` -> `Service`
4. **Branch 단계**: `Branch Entity` -> `Repository` -> `Service`
5. **Chapter 단계**: `Chapter Entity` -> `Repository` -> `Service`
6. **Sub/Pay 단계**: `Entity` -> `Repo` -> `Service` -> `Access Control`
