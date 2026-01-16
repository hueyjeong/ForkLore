# 🧠 Skills 가이드 (Claude Code)

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> Claude Code에 프로젝트 특화 기능을 가르치는 Skills 작성 가이드

## 1. 개요 (Overview)

**Skills**는 Claude Code 에이전트에게 특정 워크플로우, 코딩 표준 또는 프로젝트 특화 지식을 가르치는 프롬프트 및 명령어의 집합입니다. 이는 단순한 문서를 넘어, 에이전트가 특정 상황에서 어떤 도구를 사용하고 어떤 절차를 따라야 하는지 정의하는 '실행 가능한 지침서' 역할을 합니다.

- **핵심 역할**: 모델이 복잡한 작업을 자율적으로 수행할 수 있도록 가이드라인 제공.
- **차별점**: 일반적인 React Hook이나 라이브러리와는 무관하며, Claude 에이전트의 행동 방식을 정의하는 설정 파일입니다.

## 2. 스킬 파일 구조 (File Structure)

스킬은 프로젝트 루트의 `.claude/skills` 디렉토리 아래에 위치합니다. 각 스킬은 고유한 이름을 가진 하위 디렉토리를 가집니다.

```text
ForkLore/
└── .claude/
    └── skills/
        └── [skill-name]/
            ├── SKILL.md       # (필수) 스킬의 메타데이터와 지침
            ├── docs/          # (옵션) 추가 참고 문서
            └── scripts/       # (옵션) 스킬 실행에 필요한 보조 스크립트
```

## 3. SKILL.md 작성법 (Writing Skills)

`SKILL.md` 파일은 YAML 형식의 Frontmatter와 Markdown 형식의 지침으로 구성됩니다.

### Frontmatter 필드 설명

| 필드 | 필수 여부 | 설명 |
| :--- | :---: | :--- |
| `name` | 필수 | 스킬의 고유 식별자 (예: `pr-reviewer`) |
| `description` | 필수 | 스킬의 용도에 대한 짧은 설명 |
| `allowed-tools` | 옵션 | 이 스킬이 사용할 수 있는 도구 목록 (예: `bash`, `read`, `edit`) |
| `context` | 옵션 | 스킬이 활성화될 조건이나 프로젝트 컨텍스트 |
| `model` | 옵션 | 최적화된 모델 지정 (기본값은 현재 사용 중인 모델) |

### SKILL.md 예시

```markdown
---
name: tdd-flow
description: ForkLore 프로젝트의 TDD (Red-Green-Refactor) 사이클 준수 가이드
allowed-tools: [bash, read, edit, write]
---

# TDD Flow Skill

ForkLore 프로젝트에서는 모든 기능 개발 시 TDD 원칙을 엄격히 준수합니다.

## 실행 절차
1. **Red**: 실패하는 테스트 코드를 먼저 작성합니다.
2. **Green**: 테스트를 통과하기 위한 최소한의 프로덕션 코드를 작성합니다.
3. **Refactor**: 코드를 정리하고 중복을 제거합니다.

## 주의 사항
- `backend/` 폴더 작업 시 `pytest`를 사용합니다.
- `frontend/` 폴더 작업 시 `vitest`를 사용합니다.
- 테스트 커버리지는 항상 95% 이상을 유지해야 합니다.
```

## 4. 프론트엔드 개발용 스킬 예시

ForkLore 프론트엔드 개발에 유용한 스킬 구성 예시입니다.

### 1) PR Reviewer Skill
- **용도**: `gh pr diff` 결과를 분석하여 스타일 가이드 준수 여부 확인.
- **주요 지침**: `Naming Convention` (camelCase vs PascalCase), `No any` 원칙 등 체크.

### 2) API Pattern Skill
- **용도**: 신규 API 호출 함수 작성 시 `StandardJSONRenderer` 규격 준수 확인.
- **주요 지침**: `lib/api/` 경로 내에 파일을 생성하고, `Response` 인터페이스 타입을 정의하도록 유도.

### 3) Shadcn/UI Component Skill
- **용도**: 컴포넌트 생성 시 프로젝트의 UI 일관성 유지.
- **주요 지침**: `components/ui/`에 있는 기존 아토믹 컴포넌트를 우선적으로 활용하도록 안내.

## 5. 스킬 활성화 및 사용 (Activation)

Claude Code는 다음 과정을 통해 스킬을 인식하고 실행합니다.

1. **Discovery (발견)**: 사용자가 명령을 내리면 Claude는 `.claude/skills` 폴더를 검색하여 관련 있는 스킬이 있는지 확인합니다.
2. **User Confirmation (사용자 확인)**: 특정 스킬이 필요하다고 판단되면 사용자에게 "이 스킬을 사용하여 작업을 진행할까요?"라고 묻습니다.
3. **Execution (실행)**: 사용자가 승인하면 `SKILL.md`에 정의된 지침에 따라 도구를 호출하고 코드를 작성/수정합니다.

---

## 문서 끝
