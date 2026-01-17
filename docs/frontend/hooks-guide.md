# 🪝 Hooks 가이드 (Claude Code)

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> Claude Code 작업 흐름을 자동화하는 Hooks 설정 가이드

## 1. 개요 (Overview)

Claude Code의 **Hooks**는 특정 생명주기 이벤트(Lifecycle events) 발생 시 실행되는 결정론적인 셸 명령(Deterministic shell commands)입니다. 이를 통해 개발자는 AI 에이전트의 동작을 제어하거나, 특정 도구 사용 전후에 자동화된 작업을 수행할 수 있습니다.

**주요 특징:**
- **자동화**: 반복적인 작업(포맷팅, 테스트) 자동 실행
- **제어**: 위험한 명령 실행 차단 또는 경고
- **컨텍스트 강화**: 세션 시작 시 필요한 정보 자동 주입
- **일관성**: 프로젝트 표준 준수 강제 (Lint, Style)

## 2. 훅 종류 (Hook Types)

Claude Code는 다음과 같은 이벤트 시점에서 훅 실행을 지원합니다.

| 훅 이름 | 실행 시점 | 주요 용도 |
| :--- | :--- | :--- |
| `PreToolUse` | 도구(Tool)가 호출되기 직전 | 가드레일(Guardrails), 명령 검증, 권한 체크 |
| `PostToolUse` | 도구 실행이 완료된 직후 | 자동 포맷팅(ruff/prettier), 상태 확인 |
| `UserPromptSubmit` | 사용자가 프롬프트를 제출한 직후 | 입력 필터링, 컨텍스트 추가 |
| `SessionStart` | Claude Code 세션이 시작될 때 | 환경 변수 설정, 초기 브리핑 제공 |
| `SessionStop` | 세션이 종료될 때 | 리소스 정리, 작업 요약 저장 |
| `Notification` | 시스템 알림 발생 시 | 외부 시스템 연동 (Slack, Webhook 등) |

## 3. 설정 방법 (Configuration)

Hooks는 프로젝트 루트의 `.claude/settings.json` 파일에서 설정합니다.

### 설정 예시 (`.claude/settings.json`)

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "write_file",
      "command": "poetry run ruff format $FILE_PATH"
    },
    {
      "event": "PreToolUse",
      "matcher": "bash",
      "command": "sh scripts/validate_bash.sh",
      "type": "filter"
    }
  ]
}
```

### 주요 설정 필드
- `event`: 훅이 실행될 이벤트 타입
- `matcher`: 특정 도구 이름이나 패턴 (예: `bash`, `write_file`, `*`)
- `command`: 실행할 셸 명령
- `type`: 
    - `filter`: 명령 실행 여부를 결정 (종료 코드 사용)
    - `modifier`: 입출력을 수정 (JSON 출력 필요)

### 종료 코드 (Exit Codes)
- **0**: 성공 (작업 계속 진행)
- **2**: 차단 (에러 메시지와 함께 작업 중단)
- **기타**: 오류로 간주

## 4. 일반적인 사용 사례 (Use Cases)

1. **자동 코드 포맷팅**: 파일을 저장할 때마다 `ruff`나 `prettier`를 실행하여 코드 스타일 유지
2. **보안 가이드라인**: `rm -rf`와 같은 위험한 명령이 포함된 `bash` 실행 시 경고 또는 차단
3. **환경 검사**: 세션 시작 시 필요한 의존성(Docker, Database)이 실행 중인지 확인
4. **테스트 강제**: 중요 파일 수정 후 자동으로 관련 테스트 실행

## 5. ForkLore 프로젝트 훅 설정

ForkLore 프로젝트의 품질 유지를 위해 권장되는 설정입니다.

### 5.1. Backend 자동 포맷팅 (Ruff)
파일 수정 후 자동으로 Ruff 포맷터를 실행합니다.

```json
{
  "event": "PostToolUse",
  "matcher": "write_file",
  "command": "cd backend && poetry run ruff format $FILE_PATH"
}
```

### 5.2. Frontend 테스트 실행 및 린트
프론트엔드 파일 수정 시 린트 체크를 강제합니다.

```json
{
  "event": "PostToolUse",
  "matcher": "write_file",
  "command": "cd frontend && pnpm lint --fix"
}
```

### 5.3. 실행 방지 가드레일 (Bash Validation)
의도치 않은 파괴적인 명령 실행을 방지합니다.

```json
{
  "event": "PreToolUse",
  "matcher": "bash",
  "command": "if [[ \"$COMMAND\" == *\"rm -rf /\"* ]]; then echo \"Critical protection: rm -rf / is blocked\"; exit 2; fi",
  "type": "filter"
}
```

---

## 문서 끝
