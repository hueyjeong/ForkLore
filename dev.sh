#!/bin/bash

# dev.sh - ForkLore 통합 개발 환경 실행 스크립트
# 백엔드(Django:8080) + 프론트엔드(Next.js:3000) 병렬 실행

set -euo pipefail

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로세스 PID 저장
BACKEND_PID=""
FRONTEND_PID=""

# 유틸리티 함수
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 ForkLore 개발 환경 시작${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 종료 핸들러
cleanup() {
    echo ""
    print_info "개발 서버 종료 중..."

    # 프로세스 그룹 전체 종료 (자식 프로세스 포함)
    if [ -n "$BACKEND_PID" ]; then
        kill -- -$BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi

    if [ -n "$FRONTEND_PID" ]; then
        kill -- -$FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi

    print_success "종료 완료"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 필수 도구 확인
check_requirements() {
    print_info "필수 도구 확인 중..."

    local missing=()

    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v poetry >/dev/null 2>&1 || missing+=("poetry")
    command -v pnpm >/dev/null 2>&1 || missing+=("pnpm")

    # lsof 또는 ss 중 하나는 있어야 함
    if ! command -v lsof >/dev/null 2>&1 && ! command -v ss >/dev/null 2>&1; then
        missing+=("lsof or ss")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        print_error "다음 도구가 설치되지 않았습니다: ${missing[*]}"
        exit 1
    fi

    print_success "필수 도구 확인 완료"
}

# 포트 충돌 확인
check_port_conflict() {
    local port=$1

    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_error "포트 $port이 이미 사용 중입니다."
            echo "   실행 중인 프로세스: $(lsof -Pi :$port -sTCP:LISTEN | tail -n 1)"
            return 1
        fi
    else
        # fallback to ss
        if ss -tlnp 2>/dev/null | grep -q ":$port "; then
            print_error "포트 $port이 이미 사용 중입니다."
            echo "   실행 중인 프로세스: $(ss -tlnp | grep ":$port ")"
            return 1
        fi
    fi

    return 0
}

check_ports() {
    print_info "포트 충돌 확인 중..."

    check_port_conflict 8080 || exit 1
    check_port_conflict 3000 || exit 1

    print_success "포트 충돌 없음"
}

# Docker 서비스 상태 확인 및 시작
wait_for_healthy() {
    local service_name=$1
    local max_wait=30
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if [ "$service_name" = "db" ]; then
            if docker exec forklore-db pg_isready -U postgres >/dev/null 2>&1; then
                return 0
            fi
        elif [ "$service_name" = "redis" ]; then
            if docker exec forklore-redis redis-cli ping >/dev/null 2>&1; then
                return 0
            fi
        fi

        sleep 1
        waited=$((waited + 1))
    done

    print_error "${service_name} 서비스가 준비되지 않았습니다 (${max_wait}초 타임아웃)"
    exit 1
}

check_docker_service() {
    local service_name=$1

    # 컨테이너가 실행 중인지 확인 (정확한 이름 매칭)
    if docker ps --filter "name=^forklore-${service_name}$" --format '{{.Names}}' | grep -q .; then
        print_success "${service_name} 이미 실행 중"
        return 0
    fi

    # 컨테이너가 존재하지만 중지된 상태인지 확인
    if docker ps -a --filter "name=^forklore-${service_name}$" --format '{{.Names}}' | grep -q .; then
        print_info "${service_name} 시작 중..."
        docker compose start ${service_name} >/dev/null 2>&1
    else
        # 처음 실행 - docker compose up으로 생성
        print_info "${service_name} 생성 및 시작 중..."
        docker compose up -d ${service_name} >/dev/null 2>&1
    fi

    # health check 대기
    wait_for_healthy ${service_name}
    print_success "${service_name} 준비 완료"
}

# Migration 확인
check_migrations() {
    print_info "마이그레이션 확인 중..."

    cd backend
    if poetry run python manage.py showmigrations 2>/dev/null | grep -q '\[ \]'; then
        print_warning "적용되지 않은 migration이 있습니다."

        # TTY 확인 (비대화형 환경 대응)
        if [ -t 0 ]; then
            read -p "migration을 실행하시겠습니까? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                poetry run python manage.py migrate
                print_success "마이그레이션 완료"
            fi
        else
            print_warning "비대화형 환경입니다. 마이그레이션을 수동으로 실행하세요."
        fi
    else
        print_success "마이그레이션 확인 완료"
    fi
    cd ..
}

# 프론트엔드 의존성 확인
check_node_modules() {
    if [ ! -d "frontend/node_modules" ]; then
        print_info "프론트엔드 의존성 설치 중..."
        cd frontend
        pnpm install
        cd ..
        print_success "의존성 설치 완료"
    fi
}

# 메인 실행
main() {
    print_header
    echo ""

    # 사전 체크
    check_requirements
    check_ports

    echo ""
    print_info "인프라 서비스 확인 중..."
    check_docker_service "db"
    check_docker_service "redis"

    echo ""
    check_migrations
    check_node_modules

    echo ""
    print_info "개발 서버 시작 중..."

    # 백엔드 실행 (8080 포트, 프로세스 그룹으로 시작)
    cd backend
    set -m  # job control 활성화
    poetry run python manage.py runserver 8080 2>&1 | sed "s/^/$(echo -e "${GREEN}[BACKEND] ${NC}") /" &
    BACKEND_PID=$!
    set +m  # job control 비활성화
    cd ..

    # 백엔드 준비 대기 (포트 폴링)
    local waited=0
    local max_wait=30
    while [ $waited -lt $max_wait ]; do
        if command -v curl >/dev/null 2>&1; then
            if curl -s http://localhost:8080 >/dev/null 2>&1; then
                break
            fi
        else
            # curl 없으면 단순 대기
            if [ $waited -ge 5 ]; then
                break
            fi
        fi

        # 백엔드 프로세스가 죽었는지 확인
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            print_error "백엔드 시작 실패"
            exit 1
        fi

        sleep 1
        waited=$((waited + 1))
    done

    # 프론트엔드 실행 (3000 포트, 프로세스 그룹으로 시작)
    cd frontend
    set -m  # job control 활성화
    pnpm dev 2>&1 | sed "s/^/$(echo -e "${BLUE}[FRONTEND]${NC}") /" &
    FRONTEND_PID=$!
    set +m  # job control 비활성화
    cd ..

    # 프론트엔드 준비 대기
    sleep 3

    # 실행 완료 메시지
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ 개발 서버 실행 중${NC}"
    echo -e "   Backend:  ${BLUE}http://localhost:8080${NC}"
    echo -e "   Frontend: ${BLUE}http://localhost:3000${NC}"
    echo -e "   종료: ${YELLOW}Ctrl+C${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # 프로세스 모니터링 (하나가 죽으면 전체 종료)
    while true; do
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            print_error "백엔드가 예기치 않게 종료되었습니다"
            cleanup
        fi
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            print_error "프론트엔드가 예기치 않게 종료되었습니다"
            cleanup
        fi
        sleep 2
    done
}

# 스크립트 실행
main
