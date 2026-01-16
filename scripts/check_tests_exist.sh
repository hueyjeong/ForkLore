#!/bin/bash
# check_tests_exist.sh - 커밋 전 테스트 존재 여부 확인

# 변경된 파일 목록 가져오기
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# 테스트가 필요한 파일 확인
NEEDS_TEST=false
MISSING_TESTS=()

for file in $CHANGED_FILES; do
    # Python 파일 (테스트 파일 제외)
    if [[ "$file" =~ ^backend/apps/.*/.*\.py$ ]] && [[ ! "$file" =~ test_ ]] && [[ ! "$file" =~ /tests/ ]]; then
        # 해당 앱의 테스트 디렉토리 확인
        APP_DIR=$(echo "$file" | sed 's|backend/apps/\([^/]*\)/.*|\1|')
        TEST_DIR="backend/apps/$APP_DIR/tests"
        
        if [[ ! -d "$TEST_DIR" ]] || [[ -z "$(ls -A $TEST_DIR 2>/dev/null)" ]]; then
            NEEDS_TEST=true
            MISSING_TESTS+=("$file -> $TEST_DIR 필요")
        fi
    fi
    
    # TypeScript/TSX 파일 (테스트 파일 제외)
    if [[ "$file" =~ ^frontend/.*(\.ts|\.tsx)$ ]] && [[ ! "$file" =~ \.test\. ]] && [[ ! "$file" =~ __tests__ ]]; then
        # 해당 파일의 테스트 파일 확인
        TEST_FILE="${file%.ts}.test.ts"
        TEST_FILE="${TEST_FILE%.tsx}.test.tsx"
        
        if [[ ! -f "$TEST_FILE" ]]; then
            # __tests__ 디렉토리도 확인
            DIR=$(dirname "$file")
            BASENAME=$(basename "$file" | sed 's/\.[^.]*$//')
            TEST_IN_DIR="$DIR/__tests__/$BASENAME.test.tsx"
            
            if [[ ! -f "$TEST_IN_DIR" ]]; then
                NEEDS_TEST=true
                MISSING_TESTS+=("$file -> 테스트 파일 필요")
            fi
        fi
    fi
done

# 결과 출력
if [[ "$NEEDS_TEST" == "true" ]]; then
    echo "⚠️ 다음 파일들에 대한 테스트가 없습니다:" >&2
    for missing in "${MISSING_TESTS[@]}"; do
        echo "  - $missing" >&2
    done
    echo "" >&2
    echo "TDD 원칙: 테스트를 먼저 작성하세요!" >&2
    echo "테스트 없이 커밋하려면: git commit --no-verify" >&2
    exit 1
fi

exit 0
