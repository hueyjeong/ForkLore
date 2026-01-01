# ForkLore 프로젝트 - AI 에이전트 가이드

## 프로젝트 개요

**ForkLore**는 Spring Boot 기반의 백엔드 애플리케이션입니다.

- **그룹**: `io.forklore`
- **버전**: `0.0.1-SNAPSHOT`
- **설명**: Spring Boot 데모 프로젝트

---

## 기술 스택

### 백엔드 (Backend)
- **언어**: Java 23
- **프레임워크**: Spring Boot 4.0.1
- **빌드 도구**: Gradle (Wrapper 포함)
- **패키지명**: `io.forklore`

### 주요 의존성
- **Spring Boot Starters**:
  - `spring-boot-starter-web` (WebMVC 포함)
  - `spring-boot-starter-data-jpa`
  - `spring-boot-starter-security`
  - `spring-boot-starter-actuator`
  - `spring-boot-starter-validation`
  - `spring-boot-devtools` (개발 환경)
  
- **데이터베이스**:
  - PostgreSQL (운영 환경)
  - H2 Database (개발/테스트 환경)
  - H2 Console 활성화
  
- **유틸리티**:
  - Lombok (코드 간소화)
  - Springdoc OpenAPI 3.0.0 (Swagger UI)

### 인프라
- **컨테이너**: Docker Compose (V2 문법 사용)
- **개발 환경**: Dev Container (VS Code)
- **데이터베이스**: PostgreSQL 18
- **베이스 이미지**: `mcr.microsoft.com/devcontainers/base:bookworm`

---

## 프로젝트 구조

```
/workspaces/ForkLore/
├── .devcontainer/              # Dev Container 설정
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── docker-compose.override.yml
├── .vscode/                    # VS Code 설정
├── backend/                    # Spring Boot 백엔드
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/io/forklore/
│   │   │   └── resources/
│   │   └── test/
│   ├── build.gradle           # Gradle 빌드 설정
│   ├── settings.gradle
│   ├── gradlew                # Gradle Wrapper (Unix)
│   └── gradlew.bat            # Gradle Wrapper (Windows)
└── AGENTS.md                  # 이 파일
```

---

## 개발 규칙 및 가이드라인

### 1. 코드 작성 규칙
- **Java 버전**: Java 23 사용 (최신 LTS 기준)
- **코딩 스타일**: 
  - Lombok 어노테이션 적극 활용 (`@Getter`, `@Setter`, `@Builder`, `@Data` 등)
  - Spring Boot 모범 사례 준수
  - RESTful API 설계 원칙 준수
- **패키지 구조**:
  - `io.forklore.domain` - 도메인 모델
  - `io.forklore.controller` - REST 컨트롤러
  - `io.forklore.service` - 비즈니스 로직
  - `io.forklore.repository` - JPA 리포지토리
  - `io.forklore.config` - 설정 클래스
  - `io.forklore.security` - 보안 관련 클래스
  - `io.forklore.dto` - DTO (Data Transfer Object)
  - `io.forklore.exception` - 예외 처리

### 2. 빌드 및 실행
- **빌드**: `./gradlew build`
- **테스트**: `./gradlew test`
- **실행**: `./gradlew bootRun`
- **클린**: `./gradlew clean`

### 3. 데이터베이스 규칙
- **운영 환경**: PostgreSQL 사용
- **개발 환경**: H2 또는 Docker Compose의 PostgreSQL 사용
- **마이그레이션**: JPA Auto DDL 또는 Flyway/Liquibase 사용 검토 필요
- **연결 정보**:
  - Host: `db` (Docker Compose 서비스명)
  - Port: `5432`
  - Database: `app_db`
  - Username: `postgres`
  - Password: `postgres`

### 4. API 문서화
- **Swagger UI**: Springdoc OpenAPI 사용
- **엔드포인트**: `/swagger-ui.html` 또는 `/v3/api-docs`
- **모든 API**는 OpenAPI 3.0 스펙에 맞게 문서화할 것
- Controller에 `@Tag`, `@Operation`, `@ApiResponse` 등 어노테이션 추가 권장

### 5. 보안 규칙
- **Spring Security** 기본 설정 활성화
- **비밀번호**: 반드시 BCrypt 등으로 암호화
- **JWT 또는 세션**: 인증 방식은 요구사항에 따라 결정
- **CORS 설정**: 필요시 명시적으로 설정
- **민감 정보**: `application.properties` 또는 환경 변수로 관리

### 6. 테스트 규칙
- **단위 테스트**: JUnit 5 사용
- **통합 테스트**: `@SpringBootTest` 사용
- **보안 테스트**: `@WithMockUser` 등 활용
- **테스트 커버리지**: 최소 70% 이상 유지 권장

### 7. Docker Compose 규칙
- **명령어**: `docker compose` (V2 문법) 사용
- **네트워크**: 기본 브리지 네트워크 사용
- **볼륨**: `postgres-data` 볼륨으로 데이터 영속성 보장
- **환경 변수**: `.env` 파일 사용 권장 (현재는 하드코딩)

---

## 개발 워크플로우

### 새로운 기능 추가 시
1. **도메인 모델 정의** (`@Entity`, `@Table`)
2. **리포지토리 인터페이스 작성** (`JpaRepository` 상속)
3. **서비스 레이어 작성** (비즈니스 로직)
4. **DTO 클래스 작성** (요청/응답 객체)
5. **컨트롤러 작성** (REST API 엔드포인트)
6. **Swagger 문서화** (어노테이션 추가)
7. **테스트 코드 작성** (단위 테스트 + 통합 테스트)
8. **빌드 및 검증** (`./gradlew build`)

### 디버깅
- **VS Code**: `.vscode/launch.json` 설정 활용
- **포트**: 기본 Spring Boot 포트는 `8080`
- **로그**: `application.properties`에서 로그 레벨 조정 가능

---

## 주의사항

### AI 에이전트가 지켜야 할 사항
1. **최신 버전 사용**: 
   - Java 23, Spring Boot 4.x 등 최신 버전 우선
   - Docker 이미지도 `latest` 또는 최신 LTS 태그 사용
   
2. **타입 안전성**:
   - Java의 강타입 시스템 활용
   - Generic, Optional 적극 사용
   - Null 체크 철저히
   
3. **에러 핸들링**:
   - `@ControllerAdvice`로 전역 예외 처리
   - 커스텀 예외 클래스 정의
   - 사용자 친화적인 에러 메시지
   
4. **코드 품질**:
   - SOLID 원칙 준수
   - DRY (Don't Repeat Yourself)
   - 의미 있는 변수/메서드명 사용
   
5. **문서화**:
   - JavaDoc 주석 작성
   - README 업데이트
   - API 변경 시 Swagger 문서 갱신

---

## 환경 변수 (권장)

향후 프로젝트 확장 시 다음 환경 변수 사용 권장:

```properties
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Spring Boot
SPRING_PROFILES_ACTIVE=dev
SERVER_PORT=8080

# Security
JWT_SECRET=your-secret-key
JWT_EXPIRATION=86400000
```

---

## 추가 고려사항

### 향후 도입 검토 사항
- **Flyway/Liquibase**: 데이터베이스 마이그레이션 관리
- **Spring Cloud**: 마이크로서비스 아키텍처 전환 시
- **Redis**: 캐싱 및 세션 관리
- **Kafka/RabbitMQ**: 비동기 메시징
- **Elasticsearch**: 검색 기능 강화
- **Docker Hub/ECR**: 컨테이너 이미지 레지스트리
- **CI/CD**: GitHub Actions, Jenkins 등

---

## 버전 히스토리
- **v0.0.1-SNAPSHOT**: 초기 프로젝트 구조 생성
  - Spring Boot 4.0.1
  - Java 23
  - PostgreSQL 18
  - Springdoc OpenAPI 3.0.0
