param(
    [switch]$Coverage,
    [switch]$Postgres,
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Write-Banner($text) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
}

$exit = 0

if (-not $SkipBackend) {
    Write-Banner "Backend tests (Django TestCase)"
    if ($Postgres) {
        docker compose run --rm backend python manage.py test --settings=flight_booking.test_settings
    } else {
        docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend python manage.py test --settings=flight_booking.test_settings
    }
    if ($LASTEXITCODE -ne 0) { $exit = 1; Write-Host "BACKEND TESTS FAILED" -ForegroundColor Red }

    if ($Coverage) {
        Write-Banner "Backend coverage (coverage.py, fail_under=80)"
        if ($Postgres) {
            docker compose run --rm backend sh -c "coverage run --rcfile=.coveragerc manage.py test --settings=flight_booking.test_settings && coverage report -m"
        } else {
            docker compose run --rm --no-deps -e DB_ENGINE=sqlite3 backend sh -c "coverage run --rcfile=.coveragerc manage.py test --settings=flight_booking.test_settings && coverage report -m"
        }
        if ($LASTEXITCODE -ne 0) { $exit = 1; Write-Host "BACKEND COVERAGE FAILED" -ForegroundColor Red }
    }
}

if (-not $SkipFrontend) {
    Write-Banner "Frontend tests (Vitest + @vue/test-utils)"
    if ($Coverage) {
        docker compose run --rm --no-deps frontend npx vitest run --coverage
    } else {
        docker compose run --rm --no-deps frontend npx vitest run
    }
    if ($LASTEXITCODE -ne 0) { $exit = 1; Write-Host "FRONTEND TESTS FAILED" -ForegroundColor Red }
}

Write-Banner "Summary"
if ($exit -eq 0) {
    Write-Host "ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "SOME TESTS FAILED (see above)" -ForegroundColor Red
}
exit $exit
