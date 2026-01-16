# Draft: MCP, Skills, Hooks 설정

## 요구사항 (확정)
- [x] MCP 서버 설정: PostgreSQL, Playwright
- [x] Skills 정의: TDD Flow, PR Reviewer, API Pattern, Frontend Pattern
- [x] Hooks 구성: Python Lint, TypeScript Lint, Test Enforcement, Bash Validation

## 기존 상태
- 문서: docs/frontend/{mcp,skills,hooks}-guide.md 완비
- 설정: .claude/, .mcp.json, SKILL.md 파일 모두 없음
- 빈 디렉토리: .agent/ 존재 (사용 안 함)

## 사용자 결정사항

### MCP 서버
| 서버 | 용도 | 비고 |
|------|------|------|
| PostgreSQL | DB 스키마 조회, 쿼리 실행 | docker-compose의 DB 연결 |
| Playwright | 브라우저 자동화, E2E 테스트 | 이미 Opencode+Oh-My-Opencode에서 실행 중 |

### Skills (4개)
| 스킬 | 용도 |
|------|------|
| TDD Flow | RED-GREEN-REFACTOR 워크플로우 강제 |
| PR Reviewer | 코드 리뷰 체크리스트 적용 |
| API Pattern | ForkLore API 규칙 준수 검증 |
| Frontend Pattern | React 19/Next.js 16 패턴 적용 |

### Hooks (4개)
| 훅 | 트리거 | 용도 |
|------|--------|------|
| Python Lint | PostToolUse (Write) | ruff check 자동 실행 |
| TypeScript Lint | PostToolUse (Write) | eslint 자동 실행 |
| Test Enforcement | PreToolUse (Bash git commit) | 테스트 없이 커밋 방지 |
| Bash Validation | PreToolUse (Bash) | 위험한 명령어 차단 |

## 기술적 결정
- MCP 설정: .mcp.json (프로젝트 루트)
- Hooks 설정: .claude/settings.json
- Skills 위치: .claude/skills/{name}/SKILL.md

## 범위
- INCLUDE: 
  - .mcp.json 생성 (PostgreSQL, Playwright)
  - .claude/settings.json (4개 Hooks)
  - .claude/skills/ (4개 Skills)
  - 헬퍼 스크립트 (scripts/)
- EXCLUDE:
  - Git MCP (기본 제공)
  - Filesystem MCP (기본 제공)
  - Context7 MCP (외부 서비스)

## 열린 질문
- [ ] PostgreSQL 연결 정보: docker-compose.yml에서 가져올 것인가?
- [ ] Playwright MCP: 이미 실행 중이면 설정만 추가?
