# 🔌 ForkLore API 설계 명세 (v2.1)

**작성일**: 2026.01.13  
**작성자**: HueyJeong (with AI)  
**문서 버전**: v2.1 (응답 규약/페이징 정합성 + 댓글/신고 보강)  
**API 버전**: v1

---

## 1. 개요

### 1.1 기본 정보

| 항목 | 값 |
|------|-----|
| **Base URL** | `https://api.forklore.io/api/v1` |
| **인증 방식** | Bearer Token (JWT) |
| **Content-Type** | `application/json` |

### 1.2 JSON Naming 정책 (camelCase)
- 외부 API(JSON Request/Response)는 **camelCase**
- 서버 내부(Django 모델/Serializer 필드)는 **snake_case**
- 변환은 DRF Parser/Renderer로 통일한다. (구체 설정은 `docs/backend-architecture.md` 참고)

### 1.3 공통 응답 형식 (필수)

**중요**: 모든 API 응답은 `StandardJSONRenderer`에 의해 자동으로 감싸집니다.

#### Success Response
```json
{
  "success": true,
  "message": null,
  "data": { /* 실제 응답 데이터 */ },
  "timestamp": "2026-01-13T12:00:00+09:00"
}
```

#### Error Response
```json
{
  "success": false,
  "message": "에러 메시지",
  "data": null,
  "timestamp": "2026-01-13T12:00:00+09:00"
}
```

#### Validation Error Response
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "fieldName": ["Error message 1", "Error message 2"]
  },
  "timestamp": "2026-01-13T12:00:00+09:00"
}
```

**구현 상세**:
- Success responses (status < 400): `StandardJSONRenderer`가 자동으로 wrapping
- Error responses (status >= 400): `custom_exception_handler`가 처리
- DRF exceptions (`NotFound`, `PermissionDenied`, `ValidationError` 등) 사용
- View에서는 직접 wrapping하지 않고 데이터만 반환

**예시**:
```python
# View code (권장)
return Response(serializer.data)  # Renderer가 자동으로 wrapping

# 실제 클라이언트가 받는 응답
{
  "success": true,
  "data": <serializer.data>,
  "message": null,
  "timestamp": "2026-01-14T16:17:00+09:00"
}
```

### 1.4 Pagination 규약 (1-indexed)
- `page=1`이 첫 페이지
- `size`는 페이지 크기
- 예: `GET /novels?page=1&size=20`

---

## 2. 인증 API

### 2.1 회원가입

```
POST /auth/signup
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123!",
  "nickname": "독서왕",
  "birthDate": "1990-01-15"
}
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "독서왕"
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 2.2 로그인

```
POST /auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "expiresIn": 3600
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 2.3 토큰 갱신

```
POST /auth/refresh
```

### 2.4 소셜 로그인

```
GET /auth/oauth2/{provider}
```

---

## 3. 소설 API

### 3.1 소설 목록 조회

```
GET /novels?page=1&size=20&genre=FANTASY&sort=popular
```

### 3.2 소설 상세 조회

```
GET /novels/{novelId}
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "id": 1,
    "title": "흑마법사의 회귀",
    "author": { "id": 1, "nickname": "작가닉네임" },
    "genre": "FANTASY",
    "ageRating": "15",
    "status": "ONGOING",
    "allowBranching": true,
    "totalChapterCount": 245,
    "branchCount": 12,
    "linkedBranchCount": 3
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 3.3 소설 생성 (작가)

```
POST /novels
```

### 3.4 소설 수정/삭제

```
PATCH /novels/{novelId}
DELETE /novels/{novelId}
```

---

## 4. 브랜치 API

### 4.1 브랜치 목록 조회

```
GET /novels/{novelId}/branches?visibility=LINKED&page=1&size=20
```

**Query Parameters:**
| 파라미터 | 설명 |
|----------|------|
| `visibility` | PRIVATE, PUBLIC, LINKED (기본: 작가는 all, 일반은 LINKED) |
| `canonStatus` | NON_CANON, CANDIDATE, MERGED |
| `sort` | votes, latest, views |

### 4.2 메인 브랜치 조회

```
GET /novels/{novelId}/branches/main
```

### 4.3 브랜치 생성 (포크)

```
POST /novels/{novelId}/branches
```

**Request:**
```json
{
  "name": "IF: 어둠의 길",
  "description": "만약 주인공이 다른 선택을 했다면...",
  "branchType": "IF_STORY",
  "forkPointChapter": 15
}
```

### 4.4 브랜치 상세 조회

```
GET /branches/{branchId}
```

### 4.5 브랜치 연결 요청 (작품 페이지 노출)

> 문서/DB/코드 용어를 **Link Request(연결 요청)** 로 통일한다.

```
POST /branches/{branchId}/link-request
```

**Request:**
```json
{
  "requestMessage": "작품 페이지에 연결을 요청드립니다."
}
```

### 4.6 연결 요청 검토 (원작 작가)

```
PATCH /branches/{branchId}/link-request/{requestId}
```

**Request:**
```json
{
  "status": "APPROVED",
  "reviewComment": "좋은 스토리네요!"
}
```

### 4.7 브랜치 투표

```
POST /branches/{branchId}/vote
DELETE /branches/{branchId}/vote
```

---

## 5. 회차 API

### 5.1 회차 목록 조회

```
GET /branches/{branchId}/chapters?page=1&size=20
```

### 5.2 회차 상세 조회

```
GET /branches/{branchId}/chapters/{chapterNumber}
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "id": 1,
    "chapterNumber": 1,
    "title": "어둠의 심연에서",
    "contentHtml": "<p>...</p>",
    "accessType": "FREE",
    "canAccess": true,
    "viewCount": 1234,
    "likeCount": 89,
    "prevChapter": null,
    "nextChapter": { "chapterNumber": 2, "title": "..." },
    "wikiTerms": ["에스테반", "아카데미아"]
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 5.3 회차 생성 (작가)

```
POST /branches/{branchId}/chapters
```

**Request:**
```json
{
  "title": "새 회차",
  "content": "마크다운 본문...",
  "status": "DRAFT",
  "accessType": "FREE",
  "price": 0
}
```

### 5.4 회차 발행

```
POST /branches/{branchId}/chapters/{chapterNumber}/publish
```

### 5.5 회차 좋아요

```
POST /chapters/{chapterId}/like
DELETE /chapters/{chapterId}/like
```

---

## 6. 댓글 API (Paragraph Comment)

### 6.1 회차 댓글 목록 조회
- 회차 전체 댓글
- 문단 댓글만 필터링: `paragraphIndex` 사용

```
GET /chapters/{chapterId}/comments?page=1&size=20
GET /chapters/{chapterId}/comments?page=1&size=20&paragraphIndex=3
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 10,
        "user": { "id": 1, "nickname": "독서왕" },
        "content": "이 부분 복선인가요?",
        "isSpoiler": false,
        "isPinned": false,
        "likeCount": 3,
        "paragraphIndex": 3,
        "selectionStart": 12,
        "selectionEnd": 24,
        "quotedText": "그는 다시 눈을 떴다",
        "parentId": null,
        "createdAt": "2026-01-13T12:00:00Z"
      }
    ]
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 6.2 댓글 작성

```
POST /chapters/{chapterId}/comments
```

**Request (회차 단위 댓글):**
```json
{
  "content": "재밌어요!",
  "isSpoiler": false
}
```

**Request (문단/선택영역 댓글):**
```json
{
  "content": "여기 표현이 멋지네요.",
  "isSpoiler": false,
  "paragraphIndex": 3,
  "selectionStart": 12,
  "selectionEnd": 24,
  "quotedText": "그는 다시 눈을 떴다"
}
```

### 6.3 댓글 수정/삭제

```
PATCH /comments/{commentId}
DELETE /comments/{commentId}
```

### 6.4 댓글 고정 (작가/권한자)

```
POST /comments/{commentId}/pin
DELETE /comments/{commentId}/pin
```

---

## 7. 신고(Report) API

### 7.1 신고 생성 (사용자)

```
POST /reports
```

**Request:**
```json
{
  "targetType": "COMMENT",
  "targetId": 10,
  "reportType": "SPOILER",
  "message": "스포일러가 포함되어 있습니다."
}
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "id": 100,
    "status": "PENDING",
    "createdAt": "2026-01-13T12:00:00Z"
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 7.2 신고 목록 조회 (관리자)

```
GET /admin/reports?status=PENDING&page=1&size=20
```

### 7.3 신고 처리 (관리자)

```
PATCH /admin/reports/{reportId}
```

**Request:**
```json
{
  "status": "RESOLVED",
  "resolutionNote": "해당 댓글을 블라인드 처리했습니다."
}
```

---

## 8. 구독 & 소장 API

### 8.1 구독 상태 조회

```
GET /users/me/subscription
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": {
    "hasActiveSubscription": true,
    "planType": "PREMIUM",
    "expiresAt": "2026-02-01T00:00:00Z",
    "autoRenew": true
  },
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 8.2 구독 신청

```
POST /subscriptions
```

**Request:**
```json
{
  "planType": "PREMIUM",
  "paymentMethod": "CARD"
}
```

### 8.3 구독 취소

```
DELETE /subscriptions/current
```

### 8.4 회차 소장 (구매)

```
POST /chapters/{chapterId}/purchase
```

**Request:**
```json
{
  "useCoins": true
}
```

### 8.5 소장 목록 조회

```
GET /users/me/purchases
```

---

## 9. 위키 API

### 9.1 위키 목록 조회 (문맥 인식)

```
GET /branches/{branchId}/wiki?currentChapter=10&tag=인물
```

### 9.2 위키 상세 조회

```
GET /branches/{branchId}/wiki/{wikiId}?currentChapter=10
```

### 9.3 위키 생성/수정 (작가)

```
POST /branches/{branchId}/wiki
PATCH /branches/{branchId}/wiki/{wikiId}
```

### 9.4 위키 태그 관리

```
GET /branches/{branchId}/wiki-tags
POST /branches/{branchId}/wiki-tags
```

---

## 10. 지도 API

### 10.1 지도 목록 조회

```
GET /branches/{branchId}/maps
```

### 10.2 지도 상세 조회 (스냅샷)

```
GET /branches/{branchId}/maps/{mapId}?currentChapter=10
```

---

## 11. 읽은 기록 & 서재 API

### 11.1 최근 읽은 작품

```
GET /users/me/reading-logs?limit=10
```

**Response:**
```json
{
  "success": true,
  "message": null,
  "data": [
    {
      "novel": { "id": 1, "title": "흑마법사의 회귀" },
      "branch": { "id": 1, "isMain": true },
      "lastChapter": { "number": 15, "title": "..." },
      "progress": 0.75,
      "lastReadAt": "2026-01-02T10:00:00Z",
      "nextChapter": { "number": 16, "title": "..." }
    }
  ],
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### 11.2 읽은 기록 삭제

```
DELETE /users/me/reading-logs/{logId}
```

### 11.3 책갈피 관리

```
POST /chapters/{chapterId}/bookmark
GET /users/me/bookmarks
DELETE /bookmarks/{bookmarkId}
```

---

## 12. AI API

### 12.1 위키 자동 생성 제안

```
POST /branches/{branchId}/ai/wiki-suggestions
```

### 12.2 일관성 검사

```
POST /branches/{branchId}/ai/consistency-check
```

### 12.3 AI 질문 (문맥 인식)

```
POST /branches/{branchId}/ai/ask
```

**Request:**
```json
{
  "question": "에스테반은 왜 회귀했나요?",
  "currentChapter": 10
}
```

> **추가 규칙**: AI 요청은 서버에서 `ai_usage_logs` 기반 일일 한도 검증을 수행한다. (상세는 `docs/backend-architecture.md`)

---

## 13. 접근 제어 요약

| 리소스 | 조건 | 접근 |
|--------|------|------|
| FREE 회차 | - | ✅ |
| SUBSCRIPTION 회차 | 구독 중 or 소장 | ✅ |
| SUBSCRIPTION 회차 | 미구독 & 미소장 | ❌ |
| PRIVATE 브랜치 | 작성자 | ✅ |
| PUBLIC 브랜치 | 모두 (검색/URL) | ✅ |
| LINKED 브랜치 | 모두 (작품 페이지) | ✅ |

---

## 문서 끝
