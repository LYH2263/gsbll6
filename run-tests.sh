#!/usr/bin/env bash
# 一条命令运行前后端全部测试（Linux / macOS / CI）。
#
# 用法：
#   ./run-tests.sh              # 前后端全部
#   ./run-tests.sh backend      # 仅后端
#   ./run-tests.sh frontend     # 仅前端
#   COVERAGE=1 ./run-tests.sh   # 前端附带覆盖率
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-all}"
FAILED=0

run_backend() {
  echo "==> 运行后端测试 (docker compose backend-test)"
  docker compose -f "$ROOT/docker-compose.yml" run --rm backend-test || FAILED=1
}

run_frontend() {
  echo "==> 运行前端测试 (vitest)"
  cd "$ROOT/frontend"
  [ -d node_modules ] || npm install
  if [ "${COVERAGE:-0}" = "1" ]; then
    npm run test:coverage || FAILED=1
  else
    npm run test || FAILED=1
  fi
}

case "$TARGET" in
  backend) run_backend ;;
  frontend) run_frontend ;;
  all) run_backend; run_frontend ;;
  *) echo "未知参数: $TARGET (可选 backend|frontend|all)"; exit 2 ;;
esac

if [ "$FAILED" -ne 0 ]; then
  echo "==> 存在失败用例"; exit 1
fi
echo "==> 全部测试通过"
