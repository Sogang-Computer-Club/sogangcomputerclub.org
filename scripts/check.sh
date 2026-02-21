#!/bin/bash
# 로컬 검증 스크립트 - CI와 동일한 검사를 로컬에서 실행
# 사용법: ./scripts/check.sh [backend|frontend|all]

set -e

# 프로젝트 루트 디렉토리 (스크립트 위치 기준)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 카운터
TOTAL=0
PASSED=0
FAILED=0
FAILED_CHECKS=()

# 체크 실행 함수
run_check() {
    local name=$1
    local cmd=$2
    ((TOTAL++))

    printf "[%d] %s... " "$TOTAL" "$name"

    # 임시 파일에 출력 저장
    local output_file=$(mktemp)

    if eval "$cmd" > "$output_file" 2>&1; then
        echo -e "${GREEN}OK${NC}"
        ((PASSED++))
        rm -f "$output_file"
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
        FAILED_CHECKS+=("$name")
        echo -e "${YELLOW}--- 에러 출력 ---${NC}"
        cat "$output_file"
        echo -e "${YELLOW}--- 에러 끝 ---${NC}"
        rm -f "$output_file"
        return 1
    fi
}

# 백엔드 검사
run_backend_checks() {
    echo ""
    echo "=== 백엔드 검사 ==="

    run_check "백엔드 린트 검사 (ruff check)" "uv run ruff check app/ tests/" || true
    run_check "백엔드 포맷 검사 (ruff format)" "uv run ruff format --check app/ tests/" || true
    run_check "백엔드 테스트 (pytest)" "uv run pytest tests/ -v --ignore=tests/integration --ignore=tests/load -q" || true
}

# 프론트엔드 검사
run_frontend_checks() {
    echo ""
    echo "=== 프론트엔드 검사 ==="

    run_check "프론트엔드 타입 체크 (svelte-check)" "cd $PROJECT_ROOT/frontend && npm run check" || true
    run_check "프론트엔드 테스트 (vitest)" "cd $PROJECT_ROOT/frontend && npm run test" || true
    run_check "프론트엔드 빌드" "cd $PROJECT_ROOT/frontend && npm run build" || true
}

# 결과 출력
print_summary() {
    echo ""
    echo "========================================"
    echo "결과: ${PASSED}/${TOTAL} 통과"

    if [ $FAILED -gt 0 ]; then
        echo ""
        echo -e "${RED}실패한 검사:${NC}"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
        echo ""
        echo "위 오류를 수정 후 다시 실행하세요."
        exit 1
    else
        echo ""
        echo -e "${GREEN}모든 검사를 통과했습니다.${NC}"
        exit 0
    fi
}

# 메인 로직
case "${1:-all}" in
    backend)
        run_backend_checks
        ;;
    frontend)
        run_frontend_checks
        ;;
    all|"")
        run_backend_checks
        run_frontend_checks
        ;;
    *)
        echo "사용법: $0 [backend|frontend|all]"
        echo ""
        echo "  backend   - 백엔드 검사만 실행"
        echo "  frontend  - 프론트엔드 검사만 실행"
        echo "  all       - 전체 검사 실행 (기본값)"
        exit 1
        ;;
esac

print_summary
