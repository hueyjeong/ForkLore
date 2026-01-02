# 🏗️ ForkLore 백엔드 아키텍처 설계

**작성일**: 2026.01.02  
**작성자**: HueyJeong (with Gemini)  
**문서 버전**: v2.0 (피드백 반영)

---

## 1. 개요 (Overview)

ForkLore 백엔드는 **Spring Boot 4.0.1 + Java 23** 기반의 모놀리식 아키텍처로 시작하며, 확장성을 고려한 **레이어드 아키텍처**를 채택합니다.

### 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Layered Architecture** | Presentation → Service → Repository → Domain 분리 |
| **Domain-Driven Design** | 핵심 도메인(소설, 위키, 브랜치) 중심 설계 |
| **SOLID Principles** | 단일 책임, 개방-폐쇄, 의존성 역전 원칙 준수 |
| **RESTful API** | 자원 중심의 일관된 API 설계 |
| **Security by Default** | Spring Security 기반 인증/인가 |

---

## 2. 기술 스택

### 2.1 핵심 기술

| 구분 | 기술 | 버전 |
|------|------|------|
| **언어** | Java | 23 |
| **프레임워크** | Spring Boot | 4.0.1 |
| **빌드** | Gradle | 8.x (Wrapper) |
| **ORM** | Spring Data JPA + Hibernate | - |
| **보안** | Spring Security | - |
| **API 문서** | Springdoc OpenAPI | 3.0.0 |
| **유틸리티** | Lombok | - |

### 2.2 데이터베이스

| 환경 | DB | 용도 |
|------|-----|------|
| 개발/테스트 | H2 | 인메모리 DB, 빠른 테스트 |
| 운영 | PostgreSQL 18 | Core Data 저장 |
| 운영 | PostgreSQL + pgvector | 벡터 검색 (RAG용) |

### 2.3 인프라

| 구분 | 기술 |
|------|------|
| **컨테이너** | Docker Compose V2 |
| **개발 환경** | Dev Container (VS Code) |
| **CI/CD** | GitHub Actions (예정) |

---

## 3. 패키지 구조

```
backend/src/main/java/io/forklore/
├── ForkloreApplication.java          # Spring Boot 메인 클래스
├── config/                            # 설정 클래스
│   ├── SecurityConfig.java
│   ├── OpenApiConfig.java
│   ├── JpaConfig.java
│   └── WebConfig.java
│
├── domain/                            # 도메인 모델 (Entity)
│   ├── user/
│   │   ├── User.java
│   │   └── UserRole.java
│   ├── novel/
│   │   ├── Novel.java
│   │   ├── AgeRating.java            # ALL, 12, 15, 19
│   │   ├── Genre.java
│   │   └── NovelStatus.java
│   ├── branch/
│   │   ├── Branch.java               # 메인 + 파생 브랜치 통합
│   │   ├── Chapter.java              # 브랜치에 귀속
│   │   ├── BranchStatus.java
│   │   └── MergeRequest.java
│   ├── wiki/
│   │   ├── WikiEntry.java            # 브랜치별 위키
│   │   ├── WikiSnapshot.java
│   │   ├── WikiTagDefinition.java    # 사용자 정의 태그
│   │   └── WikiTag.java
│   ├── map/
│   │   ├── Map.java                  # 브랜치별 지도
│   │   ├── MapSnapshot.java          # 회차별 지도 스냅샷
│   │   ├── MapLayer.java
│   │   └── MapObject.java
│   ├── reading/
│   │   ├── ReadingLog.java           # 읽은 기록 (삭제 가능)
│   │   └── Bookmark.java
│   └── common/
│       ├── BaseEntity.java           # 공통 엔티티 (생성일, 수정일)
│       └── SoftDeletable.java        # 소프트 삭제 인터페이스
│
├── repository/                        # JPA 리포지토리
│   ├── user/
│   │   └── UserRepository.java
│   ├── novel/
│   │   ├── NovelRepository.java
│   │   └── ChapterRepository.java
│   ├── wiki/
│   │   └── WikiEntryRepository.java
│   └── branch/
│       └── BranchRepository.java
│
├── service/                           # 비즈니스 로직
│   ├── user/
│   │   ├── UserService.java
│   │   └── AuthService.java
│   ├── novel/
│   │   ├── NovelService.java
│   │   └── ChapterService.java
│   ├── wiki/
│   │   └── WikiService.java
│   ├── branch/
│   │   ├── BranchService.java
│   │   └── MergeService.java
│   └── ai/
│       ├── AIService.java
│       └── EmbeddingService.java
│
├── controller/                        # REST API 컨트롤러
│   ├── user/
│   │   ├── AuthController.java
│   │   └── UserController.java
│   ├── novel/
│   │   ├── NovelController.java
│   │   └── ChapterController.java
│   ├── wiki/
│   │   └── WikiController.java
│   └── branch/
│       └── BranchController.java
│
├── dto/                               # Data Transfer Objects
│   ├── request/
│   │   ├── SignUpRequest.java
│   │   ├── LoginRequest.java
│   │   ├── NovelCreateRequest.java
│   │   └── ChapterCreateRequest.java
│   ├── response/
│   │   ├── UserResponse.java
│   │   ├── NovelResponse.java
│   │   ├── ChapterResponse.java
│   │   └── ApiResponse.java          # 공통 응답 래퍼
│   └── mapper/
│       └── NovelMapper.java          # Entity ↔ DTO 변환
│
├── exception/                         # 예외 처리
│   ├── GlobalExceptionHandler.java   # @ControllerAdvice
│   ├── BusinessException.java        # 비즈니스 예외 기본 클래스
│   ├── NotFoundException.java
│   ├── UnauthorizedException.java
│   └── ValidationException.java
│
├── security/                          # 보안 관련
│   ├── jwt/
│   │   ├── JwtTokenProvider.java
│   │   ├── JwtAuthenticationFilter.java
│   │   └── JwtProperties.java
│   ├── oauth2/
│   │   ├── OAuth2SuccessHandler.java
│   │   └── CustomOAuth2UserService.java
│   └── UserPrincipal.java
│
└── util/                              # 유틸리티
    ├── MarkdownParser.java
    └── SlugGenerator.java
```

---

## 4. 레이어별 역할

### 4.1 Controller Layer (Presentation)

```
┌─────────────────────────────────────────────────────┐
│                  REST API 엔드포인트                 │
│  - HTTP 요청 수신 및 응답 반환                       │
│  - 입력 유효성 검증 (@Validated)                     │
│  - Swagger 문서화 (@Operation, @ApiResponse)        │
│  - 인증/인가 처리 (@PreAuthorize)                   │
└─────────────────────────────────────────────────────┘
```

**책임**:
- HTTP 요청/응답 처리
- DTO 변환 위임
- Swagger 어노테이션

**금지 사항**:
- 비즈니스 로직 포함 ❌
- Repository 직접 호출 ❌

### 4.2 Service Layer (Business)

```
┌─────────────────────────────────────────────────────┐
│                   비즈니스 로직                      │
│  - 도메인 규칙 적용                                  │
│  - 트랜잭션 관리 (@Transactional)                   │
│  - 여러 Repository 조합                             │
│  - 외부 서비스 연동 (AI API 등)                     │
└─────────────────────────────────────────────────────┘
```

**책임**:
- 핵심 비즈니스 로직
- 도메인 간 조율
- 트랜잭션 경계 설정

**금지 사항**:
- HTTP 관련 로직 ❌
- DTO 직접 반환 (선택적) ❌

### 4.3 Repository Layer (Persistence)

```
┌─────────────────────────────────────────────────────┐
│                  데이터 접근 계층                    │
│  - JPA Repository 인터페이스                         │
│  - 커스텀 쿼리 메서드                                │
│  - QueryDSL / Native Query (복잡한 경우)            │
└─────────────────────────────────────────────────────┘
```

**책임**:
- CRUD 연산
- 페이징, 정렬
- 복잡한 조회 쿼리

### 4.4 Domain Layer (Entity)

```
┌─────────────────────────────────────────────────────┐
│                    도메인 모델                       │
│  - JPA Entity (@Entity, @Table)                     │
│  - 도메인 로직 캡슐화 (Rich Domain Model)            │
│  - 불변 규칙 (Invariants) 보장                      │
└─────────────────────────────────────────────────────┘
```

**책임**:
- 엔티티 정의
- 도메인 규칙 캡슐화
- 연관관계 관리

---

## 5. 핵심 도메인 모델

### 5.1 핵심 설계 변경 (v2)

> **브랜치 통합**: 메인 스토리도 브랜치로 관리. 모든 챕터는 브랜치에 귀속.
> **브랜치별 위키/지도**: 각 브랜치가 독립적인 위키와 지도를 가질 수 있음.
> **지도 스냅샷**: 위키처럼 지도도 회차별 스냅샷 지원.

### 5.2 도메인 관계도

```mermaid
erDiagram
    USER ||--o{ NOVEL : writes
    USER ||--o{ BRANCH : creates
    USER ||--o{ READING_LOG : has
    USER ||--o{ BOOKMARK : has
    USER ||--o{ LIKE : gives
    USER ||--o{ COMMENT : writes
    
    NOVEL ||--o{ BRANCH : contains
    NOVEL ||--o{ NOVEL_TAG : tagged_with
    
    BRANCH ||--o{ CHAPTER : contains
    BRANCH ||--o{ WIKI_ENTRY : has
    BRANCH ||--o{ MAP : has
    BRANCH ||--o{ MERGE_REQUEST : submits
    BRANCH ||--o{ BRANCH_VOTE : receives
    BRANCH }o--|| BRANCH : "forked from (parent)"
    
    CHAPTER ||--o{ CHAPTER_CHUNK : contains
    CHAPTER ||--o{ COMMENT : receives
    CHAPTER ||--o{ LIKE : receives
    
    WIKI_ENTRY ||--o{ WIKI_SNAPSHOT : versions
    WIKI_ENTRY ||--o{ WIKI_TAG : tagged_with
    WIKI_ENTRY ||--o{ WIKI_APPEARANCE : appears_in
    
    MAP ||--o{ MAP_SNAPSHOT : versions
    MAP_SNAPSHOT ||--o{ MAP_LAYER : contains
    MAP_LAYER ||--o{ MAP_OBJECT : contains
```

### 5.3 주요 엔티티 설계

#### User (사용자)

```java
@Entity
@Table(name = "users")
public class User extends BaseEntity implements SoftDeletable {
    @Id @GeneratedValue
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    private String passwordHash;  // BCrypt 암호화
    
    @Column(unique = true, nullable = false)
    private String nickname;
    
    private String profileImageUrl;
    private String bio;
    
    // 연령 확인용 생년월일
    private LocalDate birthDate;
    
    @Enumerated(EnumType.STRING)
    private UserRole role;  // READER, AUTHOR, ADMIN
    
    @Enumerated(EnumType.STRING)
    private AuthProvider authProvider;  // LOCAL, GOOGLE, KAKAO
    private String providerId;
    
    private Integer mileage = 0;
    private Integer coin = 0;
    
    private boolean emailVerified = false;
    
    private LocalDateTime deletedAt;  // 소프트 삭제
}
```

#### Novel (소설 - 메타 정보 컨테이너)

```java
@Entity
@Table(name = "novels")
public class Novel extends BaseEntity implements SoftDeletable {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private User author;
    
    @Column(nullable = false)
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    private String coverImageUrl;
    
    @Enumerated(EnumType.STRING)
    private Genre genre;
    
    // 연령 등급 (ALL, 12, 15, 19)
    @Enumerated(EnumType.STRING)
    private AgeRating ageRating = AgeRating.ALL;
    
    @Enumerated(EnumType.STRING)
    private NovelStatus status;  // ONGOING, COMPLETED, HIATUS
    
    // 브랜치 목록 (메인 + 파생)
    @OneToMany(mappedBy = "novel", cascade = CascadeType.ALL)
    private List<Branch> branches = new ArrayList<>();
    
    // 집계 (캐시)
    private Long totalViewCount = 0L;
    private Long totalLikeCount = 0L;
    private Integer totalChapterCount = 0;
    private Integer branchCount = 1;  // 최소 1 (메인 브랜치)
    
    private LocalDateTime deletedAt;
}
```

#### Branch (브랜치 - 메인 & 파생 통합)

```java
@Entity
@Table(name = "branches")
public class Branch extends BaseEntity implements SoftDeletable {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Novel novel;
    
    // 메인 브랜치 여부 (소설당 하나만 true)
    private boolean isMain = false;
    
    // 파생 브랜치인 경우: 부모 브랜치 + 분기점
    @ManyToOne(fetch = FetchType.LAZY)
    private Branch parentBranch;
    private Integer forkPointChapter;
    
    // 파생 브랜치 작성자 (메인은 novel.author와 동일)
    @ManyToOne(fetch = FetchType.LAZY)
    private User author;
    
    private String title;  // 메인: null (소설 제목 사용), 파생: "IF: ..."
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    private String coverImageUrl;
    
    // 정사 편입 관련
    @Enumerated(EnumType.STRING)
    private BranchStatus status = BranchStatus.ACTIVE;
    private Integer mergedAtChapter;  // 정사 편입 시 본편 연결 회차
    private Integer voteThreshold = 1000;
    
    // 회차, 위키, 지도 (브랜치별 독립)
    @OneToMany(mappedBy = "branch", cascade = CascadeType.ALL)
    private List<Chapter> chapters = new ArrayList<>();
    
    @OneToMany(mappedBy = "branch", cascade = CascadeType.ALL)
    private List<WikiEntry> wikiEntries = new ArrayList<>();
    
    @OneToMany(mappedBy = "branch", cascade = CascadeType.ALL)
    private List<Map> maps = new ArrayList<>();
    
    // 집계
    private Long voteCount = 0L;
    private Long viewCount = 0L;
    private Integer chapterCount = 0;
    
    private LocalDateTime deletedAt;
}
```

#### Chapter (회차 - 브랜치에 귀속)

```java
@Entity
@Table(name = "chapters")
public class Chapter extends BaseEntity {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Branch branch;  // Novel이 아닌 Branch에 귀속
    
    private Integer chapterNumber;
    
    @Column(nullable = false)
    private String title;
    
    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;  // Markdown 원본
    
    @Column(columnDefinition = "TEXT")
    private String contentHtml;  // 렌더링 캐시
    
    private Integer wordCount = 0;
    
    @Enumerated(EnumType.STRING)
    private ChapterStatus status = ChapterStatus.DRAFT;
    
    private boolean isPaid = false;
    private Integer price = 0;
    
    private LocalDateTime scheduledAt;
    private LocalDateTime publishedAt;
    
    private Long viewCount = 0L;
    private Long likeCount = 0L;
    private Integer commentCount = 0;
}
```

#### WikiEntry (위키 항목 - 브랜치별)

```java
@Entity
@Table(name = "wiki_entries")
public class WikiEntry extends BaseEntity {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Branch branch;  // Novel이 아닌 Branch에 귀속
    
    @Column(nullable = false)
    private String name;
    
    private String imageUrl;
    private Integer firstAppearance;
    
    // 작가 전용 비공개 메모
    @Column(columnDefinition = "TEXT")
    private String hiddenNote;
    
    // AI 분석 메타데이터 (JSONB)
    @Type(JsonBinaryType.class)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> aiMetadata;
    
    // 스냅샷 버전 관리 (문맥 인식 위키)
    @OneToMany(mappedBy = "wikiEntry", cascade = CascadeType.ALL)
    @OrderBy("validFromChapter DESC")
    private List<WikiSnapshot> snapshots = new ArrayList<>();
    
    // 사용자 정의 태그 (나무위키 스타일)
    @ManyToMany
    @JoinTable(name = "wiki_tags")
    private Set<WikiTagDefinition> tags = new HashSet<>();
}
```

#### WikiTagDefinition (위키 사용자 정의 태그)

```java
@Entity
@Table(name = "wiki_tag_definitions")
public class WikiTagDefinition extends BaseEntity {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Branch branch;
    
    @Column(nullable = false)
    private String name;  // "인물", "지역", "마법 체계", ...
    
    private String color;  // Hex color
    private String icon;   // Lucide icon name
    private String description;
    private Integer displayOrder = 0;
}
```

#### MapSnapshot (지도 스냅샷 - 회차별)

```java
@Entity
@Table(name = "map_snapshots")
public class MapSnapshot extends BaseEntity {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Map map;
    
    // 이 스냅샷이 유효한 시작 회차 (위키와 동일 로직)
    private Integer validFromChapter;
    
    private String baseImageUrl;
    
    @OneToMany(mappedBy = "snapshot", cascade = CascadeType.ALL)
    @OrderBy("zIndex ASC")
    private List<MapLayer> layers = new ArrayList<>();
}
```

#### ReadingLog (읽은 기록 - 삭제 가능)

```java
@Entity
@Table(name = "reading_logs")
public class ReadingLog extends BaseEntity {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private User user;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Chapter chapter;
    
    private BigDecimal progress = BigDecimal.ZERO;  // 0.0 ~ 1.0
    private boolean isCompleted = false;
    
    private LocalDateTime readAt;
    private LocalDateTime deletedAt;  // 사용자가 삭제 가능
}
```



---

## 6. 횡단 관심사 (Cross-Cutting Concerns)

### 6.1 인증/인가

```
┌─────────────────────────────────────────────────────┐
│                   JWT 기반 인증                      │
│                                                     │
│  1. 로그인 → Access Token + Refresh Token 발급      │
│  2. API 요청 → Bearer Token 검증                    │
│  3. Token 만료 → Refresh Token으로 갱신             │
│  4. 인가 → @PreAuthorize("hasRole('AUTHOR')")       │
└─────────────────────────────────────────────────────┘
```

### 6.2 예외 처리

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotFound(NotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(ApiResponse.error(e.getMessage()));
    }
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(ValidationException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(e.getMessage()));
    }
    
    // ...
}
```

### 6.3 공통 응답 형식

```java
@Data
@Builder
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private LocalDateTime timestamp;
    
    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
            .success(true)
            .data(data)
            .timestamp(LocalDateTime.now())
            .build();
    }
    
    public static <T> ApiResponse<T> error(String message) {
        return ApiResponse.<T>builder()
            .success(false)
            .message(message)
            .timestamp(LocalDateTime.now())
            .build();
    }
}
```

### 6.4 감사 (Auditing)

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {
    
    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    @CreatedBy
    @Column(updatable = false)
    private String createdBy;
    
    @LastModifiedBy
    private String updatedBy;
}
```

---

## 7. 외부 서비스 연동

### 7.1 AI 서비스 (OpenAI API)

```
┌─────────────────────────────────────────────────────┐
│                 AI Service Layer                    │
│                                                     │
│  AIService                                          │
│  ├── generateWikiSuggestion(chapterContent)         │
│  ├── checkConsistency(novelId, newContent)          │
│  └── answerQuestion(novelId, currentChapter, query) │
│                                                     │
│  EmbeddingService                                   │
│  ├── embed(text) → float[]                          │
│  └── search(embedding, limit) → List<ChunkResult>   │
└─────────────────────────────────────────────────────┘
```

### 7.2 벡터 DB (pgvector + Gemini Embedding)

```sql
-- 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 청크 테이블
CREATE TABLE chapter_chunks (
    id SERIAL PRIMARY KEY,
    chapter_id BIGINT REFERENCES chapters(id),
    chunk_index INTEGER,
    content TEXT,
    embedding vector(768)  -- Gemini Embedding 001 차원
);

-- 인덱스
CREATE INDEX ON chapter_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 8. 환경 설정 전략

### 8.1 프로파일 구조

```
application.yml              # 공통 설정
application-local.yml        # 로컬 개발 (H2)
application-dev.yml          # Docker 개발 환경 (PostgreSQL)
application-prod.yml         # 운영 환경
```

### 8.2 주요 설정 항목

```yaml
# application.yml
spring:
  application:
    name: forklore
  
  jpa:
    hibernate:
      ddl-auto: validate  # 운영: validate, 개발: update
    open-in-view: false
    properties:
      hibernate:
        format_sql: true
        
  data:
    web:
      pageable:
        default-page-size: 20
        max-page-size: 100

# JWT 설정
jwt:
  secret: ${JWT_SECRET}
  access-token-expiration: 3600000   # 1시간
  refresh-token-expiration: 604800000 # 7일

# AI 설정  
ai:
  gemini:
    api-key: ${GEMINI_API_KEY}
    model: gemini-1.5-pro
    embedding-model: text-embedding-001  # 768차원
```

---

## 9. 테스트 전략

### 9.1 테스트 피라미드

```
        ┌─────────┐
        │  E2E   │  ← 최소화 (API 통합 테스트)
       ┌───────────┐
       │Integration│  ← 서비스 + Repository
     ┌───────────────┐
     │    Unit      │  ← Service, Domain 로직
   └─────────────────┘
```

### 9.2 테스트 구성

| 레벨 | 도구 | 대상 |
|------|------|------|
| Unit | JUnit 5 + Mockito | Service, Domain |
| Integration | @DataJpaTest | Repository |
| Integration | @WebMvcTest | Controller |
| E2E | @SpringBootTest + TestRestTemplate | 전체 플로우 |
| Security | @WithMockUser | 인증/인가 |

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
    │ (Spring)│        │ (Spring)│        │ (Spring)│
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
