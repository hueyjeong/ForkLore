# ForkLore 백엔드 개발 가이드라인

> **AI 에이전트 및 개발자가 반드시 준수해야 하는 핵심 규칙 모음**

---

## 1. 기술 스택 버전 (필수)

| 기술 | 버전 | 비고 |
|------|------|------|
| **Java** | 23 | OpenJDK 23 |
| **Spring Boot** | 4.0.1 | Spring 7.0 기반 |
| **Spring Security** | 7.0 | |
| **Gradle** | Wrapper | |
| **PostgreSQL** | 18 | + pgvector |
| **JWT** | java-jwt 4.5.0 | com.auth0 |

---

## 2. TDD (Test-Driven Development) ⚠️ 필수

```
1. RED    → 실패하는 테스트 먼저 작성
2. GREEN  → 테스트를 통과하는 최소 코드 작성
3. REFACTOR → 코드 정리 (테스트는 통과 유지)
```

- 기능 구현 전 **테스트 먼저 작성**
- 테스트 없이 프로덕션 코드 작성 금지
- 테스트 커버리지 **70% 이상** 유지

---

## 3. 테스트 프레임워크 (Spring Boot 4.x 변경사항) ⚠️ 필수

### @MockBean 대신 @MockitoBean 사용
```java
// ❌ Deprecated
@MockBean
private UserService userService;

// ✅ Spring Boot 3.4+ / 4.x
@MockitoBean
private UserService userService;
```

### 통합 테스트: @WebMvcTest 대신 RestTemplate 권장
```java
// ❌ WebMvcTest - 환경 설정 복잡, 의존성 충돌 가능
@WebMvcTest(UserController.class)

// ✅ SpringBootTest + RestTemplate
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserControllerTest {
    @LocalServerPort
    private int port;
    
    private RestTemplate restTemplate = new RestTemplate();
    
    @MockitoBean
    private UserService userService;
}
```

### PATCH 요청 지원 (JDK 11+)
```java
@BeforeEach
void setUp() {
    restTemplate.setRequestFactory(new JdkClientHttpRequestFactory());
}
```

---

## 4. Context7 MCP 활용 ⚠️ 필수

> **deprecated 코드 사용을 방지하기 위한 필수 절차**

1. **구현 전**: `resolve-library-id`로 라이브러리 ID 조회
2. **API 확인**: `query-docs`로 최신 사용법 검색
3. **즉시 대체**: deprecated 경고 발견 시 최신 API로 교체

**예시:**
```
// Spring Security 최신 API 확인
resolve-library-id("spring-security")
query-docs("/spring-projects/spring-security", "SecurityFilterChain 설정 방법")
```

---

## 5. 보안 - 민감 정보 관리 ⚠️ 필수

### 하드코딩 금지
```yaml
# ❌ 절대 금지
jwt:
  secret: my-secret-key-12345

# ✅ 환경 변수 참조
jwt:
  secret: ${JWT_SECRET}
```

### .gitignore 필수 항목
```gitignore
**/src/main/resources/application-local.yml
**/src/main/resources/application-dev.yml
**/src/main/resources/application-prod.yml
.env
.env.local
```

### 커밋 전 확인
```bash
git diff --cached | grep -E "(secret|password|key)"
```

---

## 6. Git 운영 규칙 ⚠️ 필수

### 브랜치 전략
- **Base Branch**: `develop`
- **Naming**: `feat/#<이슈번호>-<간단요약-영어>`
  - 예: `feat/#19-20-user-profile`

### 베이스 브랜치 보호
- **금지**: `main`, `develop` 브랜치를 사용자 승인 없이 강제 푸시/덮어쓰기
- **필수**: 기능 완료 후 반드시 Push와 PR 생성

---

## 7. 패키지 구조

```
io.forklore/
├── domain/           # Entity
│   ├── user/
│   └── refresh/
├── repository/       # JPA Repository
├── service/          # Business Logic
│   └── user/
├── controller/       # REST API
├── dto/              # Request/Response DTO
│   ├── request/
│   └── response/
├── security/         # Security 관련
│   ├── jwt/
│   └── oauth2/
└── global/           # Common
    ├── common/       # BaseEntity, ApiResponse
    ├── config/       # Configuration
    └── error/        # Exception Handling
```

---

## 8. 빌드 및 테스트 명령어

```bash
# 빌드
./gradlew build

# 테스트 실행
./gradlew test

# 특정 테스트만 실행
./gradlew test --tests io.forklore.controller.UserControllerTest

# 애플리케이션 실행
./gradlew bootRun
```

---

## 9. API 문서화

- **Swagger UI**: `http://localhost:8080/swagger-ui.html`
- **OpenAPI**: `http://localhost:8080/v3/api-docs`

---


---

## 10. 트러블슈팅 및 주의사항 (Lessons Learned)

### 10.1 Spring Boot 4.x 테스트 전략

#### 테스트 계층 구분
| 계층 | 어노테이션 | 용도 |
|------|-----------|------|
| **Unit Test** | `@ExtendWith(MockitoExtension.class)` | 단일 클래스 테스트 (Mock 사용) |
| **Slice Test** | `@DataJpaTest`, `@WebMvcTest` | 특정 레이어만 로드 |
| **Integration Test** | `@SpringBootTest` | 전체 컨텍스트 로드 |
| **E2E Test** | `@SpringBootTest(webEnvironment=RANDOM_PORT)` | 실제 HTTP 요청 |

#### Spring Boot 4 패키지 변경 (중요!)
```java
// ❌ Spring Boot 3 (구버전)
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

// ✅ Spring Boot 4 (신버전)
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jpa.test.autoconfigure.TestEntityManager;
```

#### Repository 테스트: @DataJpaTest 사용
```java
// ✅ 권장: 슬라이스 테스트 (자동 롤백, 빠른 실행)
@DataJpaTest
@ActiveProfiles("common")
class NovelRepositoryTest {
    @Autowired
    private TestEntityManager em;
    
    @BeforeEach
    void setUp() {
        // deleteAll() 불필요 - @DataJpaTest는 자동 롤백
        author = User.builder()...
        em.persist(author);
    }
}
```

#### 필요 의존성
```gradle
testImplementation 'org.springframework.boot:spring-boot-starter-data-jpa-test'
```

### 10.2 테스트 격리 문제 해결
*   **문제**: `@SpringBootTest`에서 테스트 간 데이터 간섭
*   **원인**: ApplicationContext 캐싱으로 DB 상태 공유
*   **해결책**:
    - **상책**: `@DataJpaTest` 사용 (자동 롤백)
    - **중책**: `@BeforeEach`에서 `deleteAll()` 호출
    - **하책**: 고유 이메일 사용 (비권장)

### 10.3 Git 작업 시작 시 Base Branch 확인 (치명적)
*   **이슈 상황**: `main` 브랜치에서 실수로 Feature 브랜치를 생성하여, `develop`에만 반영된 공통 코드(`BaseEntity`, `User` 등)가 누락되어 컴파일 에러 폭탄 발생.
*   **예방 가이드**:
    *   작업 시작 전 **반드시** 현재 로컬의 `develop`이 최신인지 확인 (`git pull origin develop`)
    *   브랜치 생성 시 명시적으로 base 지정: `git checkout -b feat/new-feature develop`

---

## 11. 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.2 | 2026-01-02 | Spring Boot 4 @DataJpaTest 테스트 전략 가이드 추가 |
| 1.1 | 2026-01-02 | 트러블슈팅(테스트 전략, Git Base) 섹션 추가 |
| 1.0 | 2026-01-02 | 초기 문서 작성 |
