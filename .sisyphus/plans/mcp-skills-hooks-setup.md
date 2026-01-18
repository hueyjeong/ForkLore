# MCP, Skills, Hooks 설정 작업 계획

**이슈**: #204 (생성 예정)
**브랜치**: `feat/#204-mcp-skills-hooks-setup`
**작성일**: 2026.01.16

---

## 개요

ForkLore 프로젝트에 Claude Code 스타일의 MCP 서버, Skills, Hooks를 실제로 설정합니다.

## 작업 목록

### Phase 1: 디렉토리 구조 생성

- [ ] **Task 1.1**: `.claude/` 디렉토리 구조 생성
  - `.claude/settings.json` (Hooks 설정)
  - `.claude/skills/` (Skills 디렉토리)
  - **Parallelizable**: NO (기반 작업)

### Phase 2: MCP 서버 설정

- [ ] **Task 2.1**: `.mcp.json` 생성 - PostgreSQL MCP
  - 서버: `@anthropic-ai/mcp-server-postgres`
  - 연결: `postgresql://postgres:password@localhost:5432/app_db`
  - **Parallelizable**: YES (with Task 2.2)

- [ ] **Task 2.2**: `.mcp.json` 업데이트 - Playwright MCP
  - 서버: `@anthropic-ai/mcp-server-playwright`
  - 브라우저 자동화 및 E2E 테스트
  - **Parallelizable**: YES (with Task 2.1)

### Phase 3: Skills 생성 (5개)

- [ ] **Task 3.1**: TDD Flow 스킬 생성
  - 경로: `.claude/skills/tdd-flow/SKILL.md`
  - 용도: RED-GREEN-REFACTOR 워크플로우 강제
  - **Parallelizable**: YES (with 3.2, 3.3, 3.4, 3.5)

- [ ] **Task 3.2**: PR Reviewer 스킬 생성
  - 경로: `.claude/skills/pr-reviewer/SKILL.md`
  - 용도: 코드 리뷰 체크리스트 적용
  - **Parallelizable**: YES (with 3.1, 3.3, 3.4, 3.5)

- [ ] **Task 3.3**: API Pattern 스킬 생성
  - 경로: `.claude/skills/api-pattern/SKILL.md`
  - 용도: ForkLore API 규칙 준수 검증
  - **Parallelizable**: YES (with 3.1, 3.2, 3.4, 3.5)

- [ ] **Task 3.4**: Frontend Pattern 스킬 생성
  - 경로: `.claude/skills/frontend-pattern/SKILL.md`
  - 용도: React 19/Next.js 16 패턴 적용
  - **Parallelizable**: YES (with 3.1, 3.2, 3.3, 3.5)

- [ ] **Task 3.5**: Commit Push PR 스킬 생성
  - 경로: `.claude/skills/commit-push-pr/SKILL.md`
  - 용도: Git 커밋 → Push → PR 생성 워크플로우 표준화
  - **Parallelizable**: YES (with 3.1, 3.2, 3.3, 3.4)

### Phase 4: Hooks 설정 (4개)

- [ ] **Task 4.1**: `.claude/settings.json` - Python Lint Hook
  - 트리거: PostToolUse (Write on *.py)
  - 명령: `cd backend && poetry run ruff check --fix $FILE`
  - **Parallelizable**: NO (같은 파일 수정)

- [ ] **Task 4.2**: `.claude/settings.json` - TypeScript Lint Hook
  - 트리거: PostToolUse (Write on *.ts, *.tsx)
  - 명령: `cd frontend && pnpm eslint --fix $FILE`
  - **Parallelizable**: NO (같은 파일 수정)

- [ ] **Task 4.3**: `.claude/settings.json` - Test Enforcement Hook
  - 트리거: PreToolUse (Bash with git commit)
  - 용도: 테스트 없이 커밋 방지
  - **Parallelizable**: NO (같은 파일 수정)

- [ ] **Task 4.4**: `.claude/settings.json` - Bash Validation Hook
  - 트리거: PreToolUse (Bash)
  - 용도: 위험한 명령어 차단 (rm -rf /, git push -f 등)
  - **Parallelizable**: NO (같은 파일 수정)

### Phase 5: 헬퍼 스크립트

- [ ] **Task 5.1**: `scripts/validate_bash.sh` 생성
  - 위험한 bash 명령어 검증 스크립트
  - **Parallelizable**: YES (with 5.2)

- [ ] **Task 5.2**: `scripts/check_tests_exist.sh` 생성
  - 커밋 전 테스트 존재 여부 확인 스크립트
  - **Parallelizable**: YES (with 5.1)

### Phase 6: 검증 및 문서화

- [ ] **Task 6.1**: 설정 검증
  - MCP 서버 연결 테스트
  - Hooks 동작 확인
  - Skills 로드 확인
  - **Parallelizable**: NO (모든 작업 완료 후)

- [ ] **Task 6.2**: AGENTS.md 업데이트
  - MCP, Skills, Hooks 설정 참조 추가
  - **Parallelizable**: NO (6.1 이후)

---

## 파일 구조 (예상)

```
.claude/
├── settings.json           # Hooks 설정
└── skills/
    ├── tdd-flow/
    │   └── SKILL.md
    ├── pr-reviewer/
    │   └── SKILL.md
    ├── api-pattern/
    │   └── SKILL.md
    ├── frontend-pattern/
    │   └── SKILL.md
    └── commit-push-pr/
        └── SKILL.md

.mcp.json                   # MCP 서버 설정

scripts/
├── validate_bash.sh
└── check_tests_exist.sh
```

---

## 기술 참조

### PostgreSQL 연결 정보 (docker-compose.yml)
- Host: `localhost`
- Port: `5432`
- Database: `app_db`
- User: `postgres`
- Password: `${DB_PASSWORD:-password}`

### 프로젝트 명령어
- Backend lint: `cd backend && poetry run ruff check --fix`
- Frontend lint: `cd frontend && pnpm eslint --fix`
- Backend test: `cd backend && poetry run pytest`
- Frontend test: `cd frontend && pnpm test`

---

## 의존성

```
Phase 1 → Phase 2, 3, 4, 5 (병렬 가능)
Phase 2, 3, 4, 5 → Phase 6
```

## 예상 소요 시간

| Phase | 예상 시간 |
|-------|----------|
| Phase 1 | 2분 |
| Phase 2 | 5분 |
| Phase 3 | 15분 |
| Phase 4 | 10분 |
| Phase 5 | 5분 |
| Phase 6 | 5분 |
| **총계** | **~42분** |
