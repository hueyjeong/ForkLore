# 🔧 ForkLore 백엔드 태스크

**작성일**: 2026.01.02  
**문서 버전**: v1.0

---

## 범례

| 항목 | 설명 |
|------|------|
| **우선순위** | P0 (MVP 필수), P1 (MVP 권장), P2 (후속) |
| **난이도** | 🟢 Easy, 🟡 Medium, 🔴 Hard |
| **공수** | 예상 시간 (hours) |
| **상태** | ⬜ 미착수, 🔲 진행중, ✅ 완료 |

---

## 1. 프로젝트 초기 설정 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | 패키지 구조 생성 (domain, repository, service, controller, dto, exception) | 🟢 | 1h |
| ⬜ | BaseEntity 구현 (createdAt, updatedAt) | 🟢 | 0.5h |
| ⬜ | SoftDeletable 인터페이스 구현 | 🟢 | 0.5h |
| ⬜ | ApiResponse 공통 응답 클래스 구현 | 🟢 | 0.5h |
| ⬜ | GlobalExceptionHandler 구현 | 🟡 | 2h |
| ⬜ | OpenAPI/Swagger 설정 (OpenApiConfig) | 🟢 | 1h |
| ⬜ | JPA Auditing 설정 (JpaConfig) | 🟢 | 0.5h |
| ⬜ | application.yml 환경별 분리 (local, dev, prod) | 🟡 | 1h |

---

## 2. 인증 & 사용자 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | User 엔티티 구현 (birthDate, role, authProvider) | 🟢 | 1h |
| ⬜ | UserRole enum 구현 | 🟢 | 0.5h |
| ⬜ | UserRepository 구현 | 🟢 | 0.5h |
| ⬜ | SecurityConfig 기본 설정 | 🟡 | 2h |
| ⬜ | JwtTokenProvider 구현 | 🔴 | 4h |
| ⬜ | JwtAuthenticationFilter 구현 | 🔴 | 3h |
| ⬜ | AuthService 구현 (회원가입, 로그인, 토큰 갱신) | 🔴 | 4h |
| ⬜ | AuthController 구현 (/auth/*) | 🟡 | 2h |
| ⬜ | OAuth2 설정 (Google, Kakao) | 🔴 | 6h |
| ⬜ | UserService 구현 (프로필 조회/수정) | 🟡 | 2h |
| ⬜ | UserController 구현 (/users/*) | 🟢 | 1h |

---

## 3. 소설 관리 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Novel 엔티티 구현 (ageRating, allowBranching) | 🟢 | 1h |
| ⬜ | AgeRating, Genre, NovelStatus enum 구현 | 🟢 | 0.5h |
| ⬜ | NovelRepository 구현 (페이징, 필터링 쿼리) | 🟡 | 2h |
| ⬜ | NovelService 구현 (CRUD + 통계) | 🟡 | 3h |
| ⬜ | NovelController 구현 (/novels/*) | 🟡 | 2h |
| ⬜ | NovelMapper (Entity ↔ DTO 변환) | 🟢 | 1h |

---

## 4. 브랜치 시스템 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Branch 엔티티 구현 (isMain, visibility, canonStatus) | 🟡 | 2h |
| ⬜ | BranchType, BranchVisibility, CanonStatus enum 구현 | 🟢 | 0.5h |
| ⬜ | BranchLinkRequest 엔티티 구현 | 🟢 | 1h |
| ⬜ | BranchRepository 구현 | 🟡 | 2h |
| ⬜ | BranchService 구현 (생성, 공개 상태 변경) | 🔴 | 4h |
| ⬜ | BranchLinkService 구현 (연결 요청/승인) | 🟡 | 3h |
| ⬜ | BranchController 구현 (/novels/{id}/branches/*) | 🟡 | 2h |
| ⬜ | 메인 브랜치 자동 생성 로직 (소설 생성 시) | 🟡 | 1h |
| ⬜ | 브랜치 투표 기능 (BranchVoteRepository) | 🟡 | 2h |

---

## 5. 회차 관리 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Chapter 엔티티 구현 (accessType, content/contentHtml) | 🟡 | 2h |
| ⬜ | ChapterStatus, AccessType enum 구현 | 🟢 | 0.5h |
| ⬜ | ChapterRepository 구현 | 🟡 | 2h |
| ⬜ | ChapterService 구현 (CRUD, 발행, 예약) | 🔴 | 4h |
| ⬜ | ChapterController 구현 (/branches/{id}/chapters/*) | 🟡 | 2h |
| ⬜ | 마크다운 → HTML 변환 유틸 (MarkdownParser) | 🟡 | 2h |
| ⬜ | 회차 발행 스케줄러 (예약 발행) | 🔴 | 3h |

---

## 6. 구독 & 결제 (P0)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Subscription 엔티티 구현 | 🟢 | 1h |
| ⬜ | Purchase 엔티티 구현 | 🟢 | 1h |
| ⬜ | SubscriptionRepository 구현 | 🟢 | 1h |
| ⬜ | PurchaseRepository 구현 | 🟢 | 1h |
| ⬜ | AccessService 구현 (열람 권한 확인) | 🟡 | 2h |
| ⬜ | SubscriptionService 구현 (구독 가입/해지) | 🟡 | 3h |
| ⬜ | PurchaseService 구현 (회차 소장) | 🟡 | 2h |
| ⬜ | SubscriptionController 구현 | 🟡 | 2h |
| ⬜ | 회차 열람 시 권한 검사 AOP/Interceptor | 🔴 | 3h |

---

## 7. 위키 시스템 (P1)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | WikiEntry 엔티티 구현 | 🟡 | 2h |
| ⬜ | WikiSnapshot 엔티티 구현 | 🟡 | 1h |
| ⬜ | WikiTagDefinition 엔티티 구현 | 🟢 | 1h |
| ⬜ | WikiEntryRepository 구현 | 🟡 | 2h |
| ⬜ | WikiService 구현 (CRUD, 스냅샷 관리) | 🔴 | 4h |
| ⬜ | 문맥 인식 위키 조회 (currentChapter 기준) | 🔴 | 4h |
| ⬜ | WikiController 구현 | 🟡 | 2h |
| ⬜ | 위키 포크 로직 (브랜치 생성 시) | 🔴 | 3h |

---

## 8. 지도 시스템 (P2)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Map 엔티티 구현 | 🟢 | 1h |
| ⬜ | MapSnapshot 엔티티 구현 | 🟡 | 1h |
| ⬜ | MapLayer, MapObject 엔티티 구현 | 🟡 | 2h |
| ⬜ | MapRepository 구현 | 🟡 | 2h |
| ⬜ | MapService 구현 (CRUD, 스냅샷) | 🔴 | 4h |
| ⬜ | MapController 구현 | 🟡 | 2h |

---

## 9. 읽은 기록 & 서재 (P1)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | ReadingLog 엔티티 구현 | 🟢 | 1h |
| ⬜ | Bookmark 엔티티 구현 | 🟢 | 1h |
| ⬜ | ReadingLogRepository 구현 | 🟡 | 2h |
| ⬜ | ReadingService 구현 (최근 읽은, 이어보기) | 🟡 | 3h |
| ⬜ | BookmarkService 구현 | 🟢 | 1h |
| ⬜ | 읽은 기록 삭제 기능 | 🟢 | 1h |

---

## 10. 커뮤니티 (P1)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | Comment 엔티티 구현 (대댓글, 스포일러) | 🟡 | 2h |
| ⬜ | Like 엔티티 구현 (polymorphic) | 🟡 | 1h |
| ⬜ | CommentRepository 구현 | 🟡 | 2h |
| ⬜ | CommentService 구현 (CRUD + 페이징) | 🟡 | 3h |
| ⬜ | CommentController 구현 | 🟡 | 2h |
| ⬜ | 좋아요 기능 (LikeService) | 🟢 | 2h |

---

## 11. AI 연동 (P2)

| 상태 | 태스크 | 난이도 | 공수 |
|------|--------|--------|------|
| ⬜ | ChapterChunk 엔티티 구현 (embedding) | 🟡 | 2h |
| ⬜ | EmbeddingService 구현 (Gemini API 연동) | 🔴 | 4h |
| ⬜ | 청크 분할 로직 (회차 저장 시) | 🔴 | 3h |
| ⬜ | pgvector 유사도 검색 쿼리 | 🔴 | 3h |
| ⬜ | AIService 구현 (위키 제안, 일관성 검사) | 🔴 | 6h |
| ⬜ | AIController 구현 (/ai/*) | 🟡 | 2h |

---

## 요약

| 우선순위 | 태스크 수 | 예상 총 공수 |
|----------|----------|--------------|
| P0 | 53개 | ~90h |
| P1 | 20개 | ~35h |
| P2 | 14개 | ~30h |

---

## 문서 끝
