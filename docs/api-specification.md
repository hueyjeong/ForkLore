# 🔌 ForkLore API 설계 명세

**작성일**: 2026.01.02  
**작성자**: HueyJeong (with Gemini)  
**문서 버전**: v1.0  
**API 버전**: v1

---

## 1. 개요

### 1.1 기본 정보

| 항목 | 값 |
|------|-----|
| **Base URL** | `https://api.forklore.io/api/v1` (운영) |
| **Base URL** | `http://localhost:8080/api/v1` (로컬) |
| **인증 방식** | Bearer Token (JWT) |
| **Content-Type** | `application/json` |

### 1.2 공통 응답 형식

```json
{
  "success": true,
  "message": null,
  "data": { ... },
  "timestamp": "2026-01-02T12:00:00Z"
}
```

### 1.3 에러 응답 형식

```json
{
  "success": false,
  "message": "리소스를 찾을 수 없습니다.",
  "data": null,
  "timestamp": "2026-01-02T12:00:00Z",
  "errorCode": "NOT_FOUND"
}
```

### 1.4 HTTP 상태 코드

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성됨 |
| 204 | 삭제 성공 (No Content) |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 충돌 (중복 등) |
| 500 | 서버 오류 |

---

## 2. 인증 API (Auth)

### 2.1 회원가입

```
POST /auth/signup
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "nickname": "독서왕",
  "agreeTerms": true
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "독서왕",
    "role": "READER"
  }
}
```

### 2.2 로그인

```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiJ9...",
    "tokenType": "Bearer",
    "expiresIn": 3600
  }
}
```

### 2.3 토큰 갱신

```
POST /auth/refresh
```

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9..."
}
```

### 2.4 소셜 로그인

```
GET /auth/oauth2/{provider}
```

**Path Parameters:**
- `provider`: `google`, `kakao`

**Response:** OAuth2 인증 페이지로 리다이렉트

### 2.5 로그아웃

```
POST /auth/logout
Authorization: Bearer {accessToken}
```

---

## 3. 사용자 API (Users)

### 3.1 내 프로필 조회

```
GET /users/me
Authorization: Bearer {accessToken}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "독서왕",
    "profileImageUrl": "https://...",
    "bio": "판타지 덕후입니다",
    "role": "AUTHOR",
    "mileage": 1250,
    "coin": 500,
    "createdAt": "2026-01-01T00:00:00Z"
  }
}
```

### 3.2 프로필 수정

```
PATCH /users/me
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "nickname": "새닉네임",
  "bio": "새로운 자기소개",
  "profileImageUrl": "https://..."
}
```

### 3.3 작가 등록

```
POST /users/me/author
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "penName": "작가필명",
  "introduction": "작가 소개글"
}
```

---

## 4. 소설 API (Novels)

### 4.1 소설 목록 조회

```
GET /novels
```

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `page` | int | N | 페이지 번호 (0부터) |
| `size` | int | N | 페이지 크기 (기본 20) |
| `sort` | string | N | 정렬 (latest, popular, views) |
| `genre` | string | N | 장르 필터 |
| `status` | string | N | 연재 상태 (ONGOING, COMPLETED) |
| `keyword` | string | N | 검색어 |

**Response:**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "title": "흑마법사의 회귀",
        "author": { "id": 1, "nickname": "마법작가" },
        "genre": "FANTASY",
        "status": "ONGOING",
        "coverImageUrl": "https://...",
        "description": "세계를 구한 흑마법사가...",
        "chapterCount": 245,
        "viewCount": 125000,
        "likeCount": 2300,
        "tags": ["회귀", "마법", "복수"]
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 150,
    "totalPages": 8
  }
}
```

### 4.2 소설 상세 조회

```
GET /novels/{novelId}
```

### 4.3 소설 생성 (작가 전용)

```
POST /novels
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "title": "새로운 소설",
  "description": "소설 설명...",
  "genre": "FANTASY",
  "tags": ["태그1", "태그2"],
  "coverImageUrl": "https://..."
}
```

### 4.4 소설 수정

```
PATCH /novels/{novelId}
Authorization: Bearer {accessToken}
```

### 4.5 소설 삭제

```
DELETE /novels/{novelId}
Authorization: Bearer {accessToken}
```

---

## 5. 회차 API (Chapters)

### 5.1 회차 목록 조회

```
GET /novels/{novelId}/chapters
```

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `page` | int | N | 페이지 번호 |
| `size` | int | N | 페이지 크기 |
| `order` | string | N | 정렬 (asc, desc) |

**Response:**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "chapterNumber": 1,
        "title": "어둠의 심연에서",
        "status": "PUBLISHED",
        "publishedAt": "2026-01-01T12:00:00Z",
        "viewCount": 1234,
        "likeCount": 89,
        "commentCount": 45,
        "isPaid": false
      }
    ],
    "totalElements": 245
  }
}
```

### 5.2 회차 본문 조회

```
GET /novels/{novelId}/chapters/{chapterNumber}
Authorization: Bearer {accessToken} (선택: 유료 회차/읽은 기록)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chapterNumber": 1,
    "title": "어둠의 심연에서",
    "content": "마탑의 최상층, 에스테반은...",
    "contentHtml": "<p>마탑의 최상층...</p>",
    "publishedAt": "2026-01-01T12:00:00Z",
    "viewCount": 1234,
    "likeCount": 89,
    "isLiked": false,
    "isBookmarked": true,
    "wikiTerms": ["아카데미아", "흑마법", "에스테반"],
    "prevChapter": null,
    "nextChapter": { "chapterNumber": 2, "title": "..." }
  }
}
```

### 5.3 회차 생성 (작가 전용)

```
POST /novels/{novelId}/chapters
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "title": "새 회차 제목",
  "content": "회차 본문 (마크다운)...",
  "status": "DRAFT",
  "scheduledAt": null
}
```

### 5.4 회차 수정

```
PATCH /novels/{novelId}/chapters/{chapterNumber}
Authorization: Bearer {accessToken}
```

### 5.5 회차 발행

```
POST /novels/{novelId}/chapters/{chapterNumber}/publish
Authorization: Bearer {accessToken}
```

### 5.6 회차 좋아요

```
POST /novels/{novelId}/chapters/{chapterNumber}/like
Authorization: Bearer {accessToken}
```

### 5.7 회차 좋아요 취소

```
DELETE /novels/{novelId}/chapters/{chapterNumber}/like
Authorization: Bearer {accessToken}
```

---

## 6. 위키 API (Wiki)

### 6.1 위키 항목 목록 조회

```
GET /novels/{novelId}/wiki
```

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `currentChapter` | int | N | 문맥 인식 (해당 회차까지만) |
| `category` | string | N | CHARACTER, LOCATION, ITEM, CONCEPT |
| `keyword` | string | N | 검색어 |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "에스테반",
      "category": "CHARACTER",
      "summary": "흑마법사. 회귀자.",
      "imageUrl": "https://...",
      "firstAppearanceChapter": 1,
      "lastUpdatedChapter": 245
    }
  ]
}
```

### 6.2 위키 항목 상세 조회 (문맥 인식)

```
GET /novels/{novelId}/wiki/{wikiId}?currentChapter=10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "에스테반",
    "category": "CHARACTER",
    "imageUrl": "https://...",
    "snapshot": {
      "summary": "회귀자. 아카데미아 입학생.",
      "fullDescription": "에스테반은 20년 전으로 회귀한...",
      "validFromChapter": 1
    },
    "appearsInChapters": [1, 2, 3, 5, 8],
    "relatedEntries": [
      { "id": 2, "name": "아카데미아" }
    ]
  }
}
```

### 6.3 위키 항목 생성 (작가 전용)

```
POST /novels/{novelId}/wiki
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "name": "새 위키 항목",
  "category": "CHARACTER",
  "summary": "요약...",
  "fullDescription": "상세 설명...",
  "imageUrl": "https://...",
  "validFromChapter": 15,
  "hiddenNote": "작가 전용 메모 (비공개)"
}
```

### 6.4 위키 스냅샷 추가 (업데이트)

```
POST /novels/{novelId}/wiki/{wikiId}/snapshots
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "summary": "업데이트된 요약",
  "fullDescription": "업데이트된 설명",
  "validFromChapter": 50
}
```

---

## 7. 브랜치 API (Branches)

### 7.1 브랜치 목록 조회

```
GET /branches
```

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `novelId` | long | N | 특정 원작 필터 |
| `status` | string | N | ACTIVE, CANDIDATE, MERGED |
| `sort` | string | N | votes, latest, views |

### 7.2 브랜치 생성 (포크)

```
POST /novels/{novelId}/fork
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "title": "IF: 흑마법사가 백마법을 배웠다면",
  "description": "에스테반이 흑마법 대신...",
  "forkPointChapter": 5
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "IF: 흑마법사가...",
    "originalNovel": { "id": 1, "title": "흑마법사의 회귀" },
    "forkPointChapter": 5,
    "status": "ACTIVE",
    "inheritedWikiCount": 15,
    "inheritedMapLayers": 3
  }
}
```

### 7.3 브랜치 추천 (투표)

```
POST /branches/{branchId}/vote
Authorization: Bearer {accessToken}
```

### 7.4 브랜치 상세 조회

```
GET /branches/{branchId}
```

### 7.5 정사 편입 요청 (자동) - 내부 API

시스템이 투표 임계값 도달 시 자동 호출

```
POST /internal/branches/{branchId}/promote
```

### 7.6 편입 요청 검토 (작가 전용)

```
POST /branches/{branchId}/merge-requests/{requestId}/review
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "decision": "APPROVE",
  "comment": "좋은 스토리입니다. 승인합니다.",
  "contractAgreed": true
}
```

---

## 8. 댓글 API (Comments)

### 8.1 댓글 목록 조회

```
GET /novels/{novelId}/chapters/{chapterNumber}/comments
```

### 8.2 댓글 작성

```
POST /novels/{novelId}/chapters/{chapterNumber}/comments
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "content": "다음 화 기대됩니다!",
  "parentId": null
}
```

### 8.3 댓글 삭제

```
DELETE /comments/{commentId}
Authorization: Bearer {accessToken}
```

### 8.4 댓글 신고

```
POST /comments/{commentId}/report
Authorization: Bearer {accessToken}
```

---

## 9. AI API (AI Services)

### 9.1 위키 자동 생성 제안 (작가 전용)

```
POST /novels/{novelId}/ai/wiki-suggestions
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "chapterContent": "회차 본문...",
  "chapterNumber": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "term": "아카데미아",
        "action": "NEW",
        "confidence": 0.95,
        "suggestedSummary": "칼데론 왕국 최고의 마법학교...",
        "suggestedCategory": "LOCATION"
      },
      {
        "term": "흑마법",
        "action": "UPDATE",
        "confidence": 0.88,
        "suggestedChanges": "생명력을 대가로..."
      }
    ]
  }
}
```

### 9.2 일관성 검사 (작가 전용)

```
POST /novels/{novelId}/ai/consistency-check
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "newContent": "새로 작성한 본문...",
  "chapterNumber": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "checks": [
      {
        "type": "SUCCESS",
        "message": "캐릭터 성격 일관성 확인됨"
      },
      {
        "type": "WARNING",
        "message": "3화에서 마력 색깔이 붉은색으로 묘사됨",
        "reference": { "chapterNumber": 3, "excerpt": "..." }
      }
    ]
  }
}
```

### 9.3 AI 질문 (독자용, 문맥 인식)

```
POST /novels/{novelId}/ai/ask
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "question": "에스테반은 왜 회귀했나요?",
  "currentChapter": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "현재 10화까지의 정보에 따르면, 에스테반은...",
    "sources": [
      { "chapterNumber": 1, "excerpt": "..." },
      { "chapterNumber": 5, "excerpt": "..." }
    ],
    "remainingQuota": 4
  }
}
```

---

## 10. 북마크 & 서재 API

### 10.1 내 서재 조회

```
GET /users/me/library
Authorization: Bearer {accessToken}
```

**Query Parameters:**
- `tab`: `reading`, `completed`, `bookmarked`

### 10.2 책갈피 추가

```
POST /novels/{novelId}/bookmark
Authorization: Bearer {accessToken}
```

**Request Body:**
```json
{
  "chapterNumber": 15,
  "scrollPosition": 0.35
}
```

### 10.3 읽은 기록 동기화

```
POST /novels/{novelId}/reading-progress
Authorization: Bearer {accessToken}
```

---

## 11. 파일 업로드 API

### 11.1 이미지 업로드

```
POST /upload/image
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: 이미지 파일
- `type`: `cover`, `profile`, `wiki`, `map`

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://cdn.forklore.io/images/...",
    "thumbnailUrl": "https://cdn.forklore.io/images/thumb/..."
  }
}
```

---

## 문서 끝
