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

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-01-02 | 초기 문서 작성 |
