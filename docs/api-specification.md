# 🔌 ForkLore API 설계 명세 (v2)

**작성일**: 2026.01.02  
**작성자**: HueyJeong (with Gemini)  
**문서 버전**: v2.0 (브랜치/구독 시스템 반영)  
**API 버전**: v1

---

## 1. 개요

### 1.1 기본 정보

| 항목 | 값 |
|------|-----|
| **Base URL** | `https://api.forklore.io/api/v1` |
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

### 2.2 로그인

```
POST /auth/login
```

**Response:**
```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresIn": 3600
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
GET /novels?page=0&size=20&genre=FANTASY&sort=popular
```

### 3.2 소설 상세 조회

```
GET /novels/{novelId}
```

**Response:**
```json
{
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
GET /novels/{novelId}/branches?visibility=LINKED
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
GET /branches/{branchId}/chapters
```

### 5.2 회차 상세 조회

```
GET /branches/{branchId}/chapters/{chapterNumber}
```

**Response:**
```json
{
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

## 6. 구독 & 소장 API

### 6.1 구독 상태 조회

```
GET /users/me/subscription
```

**Response:**
```json
{
  "hasActiveSubscription": true,
  "planType": "PREMIUM",
  "expiresAt": "2026-02-01T00:00:00Z",
  "autoRenew": true
}
```

### 6.2 구독 신청

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

### 6.3 구독 취소

```
DELETE /subscriptions/current
```

### 6.4 회차 소장 (구매)

```
POST /chapters/{chapterId}/purchase
```

**Request:**
```json
{
  "useCoins": true
}
```

### 6.5 소장 목록 조회

```
GET /users/me/purchases
```

---

## 7. 위키 API

### 7.1 위키 목록 조회 (문맥 인식)

```
GET /branches/{branchId}/wiki?currentChapter=10&tag=인물
```

### 7.2 위키 상세 조회

```
GET /branches/{branchId}/wiki/{wikiId}?currentChapter=10
```

### 7.3 위키 생성/수정 (작가)

```
POST /branches/{branchId}/wiki
PATCH /branches/{branchId}/wiki/{wikiId}
```

### 7.4 위키 태그 관리

```
GET /branches/{branchId}/wiki-tags
POST /branches/{branchId}/wiki-tags
```

---

## 8. 지도 API

### 8.1 지도 목록 조회

```
GET /branches/{branchId}/maps
```

### 8.2 지도 상세 조회 (스냅샷)

```
GET /branches/{branchId}/maps/{mapId}?currentChapter=10
```

---

## 9. 읽은 기록 & 서재 API

### 9.1 최근 읽은 작품

```
GET /users/me/reading-logs?limit=10
```

**Response:**
```json
{
  "data": [
    {
      "novel": { "id": 1, "title": "흑마법사의 회귀" },
      "branch": { "id": 1, "isMain": true },
      "lastChapter": { "number": 15, "title": "..." },
      "progress": 0.75,
      "lastReadAt": "2026-01-02T10:00:00Z",
      "nextChapter": { "number": 16, "title": "..." }
    }
  ]
}
```

### 9.2 읽은 기록 삭제

```
DELETE /users/me/reading-logs/{logId}
```

### 9.3 책갈피 관리

```
POST /chapters/{chapterId}/bookmark
GET /users/me/bookmarks
DELETE /bookmarks/{bookmarkId}
```

---

## 10. AI API

### 10.1 위키 자동 생성 제안

```
POST /branches/{branchId}/ai/wiki-suggestions
```

### 10.2 일관성 검사

```
POST /branches/{branchId}/ai/consistency-check
```

### 10.3 AI 질문 (문맥 인식)

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

---

## 11. 접근 제어 요약

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
