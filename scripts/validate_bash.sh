#!/bin/bash
# validate_bash.sh - 위험한 bash 명령어 검증

# 입력: 실행하려는 명령어 (stdin 또는 $1)
CMD="${1:-$(cat)}"

# 위험한 패턴 목록
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "rm -rf ~"
    "rm -rf \$HOME"
    "git push.*--force.*main"
    "git push.*--force.*master"
    "git push.*--force.*develop"
    "git push -f.*main"
    "git push -f.*master"
    "git push -f.*develop"
    "git reset --hard.*origin"
    "> /dev/sda"
    "mkfs\\."
    "dd if=.*/dev/"
    ":(){:|:&};:"
    "chmod -R 777 /"
    "chown -R.*/"
)

# 각 패턴 확인
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$CMD" | grep -qE "$pattern"; then
        echo "❌ 위험한 명령어 감지: $pattern" >&2
        echo "명령어: $CMD" >&2
        exit 2  # exit 2 = 블록
    fi
done

# 안전한 명령어
exit 0
