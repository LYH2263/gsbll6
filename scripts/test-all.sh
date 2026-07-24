#!/usr/bin/env bash
set -euo pipefail

COVERAGE=0
POSTGRES=0
SKIP_BACKEND=0
SKIP_FRONTEND=0

for arg in "$@"; do
  case "$arg" in
    --coverage) COVERAGE=1 ;;
    --postgres) POSTGRES=1 ;;
    --skip-backend) SKIP_BACKEND=1 ;;
    --skip-frontend) SKIP_FRONTEND=1 ;;
    -h|--help)
      echo "Usage: $0 [--coverage] [--postgres] [--skip-backend] [--skip-frontend]"
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

banner() {
  echo ""
  echo "================================================================"
  echo "  $1"
  echo "================================================================"
}

EXIT=0

if [ "$SKIP_BACKEND" -eq 0 ]; then
  banner "Backend tests (Django TestCase)"
  if [ "$POSTGRES" -eq 1 ]; then
    docker compose run --rm backend python manage.py test --settings=flight_booking.test_settings || { EXIT=1; echo "BACKEND TESTS FAILED"; }
  else
    docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend python manage.py test --settings=flight_booking.test_settings || { EXIT=1; echo "BACKEND TESTS FAILED"; }
  fi

  if [ "$COVERAGE" -eq 1 ]; then
    banner "Backend coverage (coverage.py, fail_under=80)"
    if [ "$POSTGRES" -eq 1 ]; then
      docker compose run --rm backend sh -c "coverage run --rcfile=.coveragerc manage.py test --settings=flight_booking.test_settings && coverage report -m" || { EXIT=1; echo "BACKEND COVERAGE FAILED"; }
    else
      docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend sh -c "coverage run --rcfile=.coveragerc manage.py test --settings=flight_booking.test_settings && coverage report -m" || { EXIT=1; echo "BACKEND COVERAGE FAILED"; }
    fi
  fi
fi

if [ "$SKIP_FRONTEND" -eq 0 ]; then
  banner "Frontend tests (Vitest + @vue/test-utils)"
  if [ "$COVERAGE" -eq 1 ]; then
    docker compose run --rm --no-deps frontend npx vitest run --coverage || { EXIT=1; echo "FRONTEND TESTS FAILED"; }
  else
    docker compose run --rm --no-deps frontend npx vitest run || { EXIT=1; echo "FRONTEND TESTS FAILED"; }
  fi
fi

banner "Summary"
if [ "$EXIT" -eq 0 ]; then
  echo "ALL TESTS PASSED"
else
  echo "SOME TESTS FAILED (see above)"
fi
exit $EXIT
