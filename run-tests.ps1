<#
.SYNOPSIS
  一条命令运行前后端全部测试（Windows / PowerShell）。

.DESCRIPTION
  默认通过 Docker 运行后端测试（SQLite 内存库，无需 Postgres），
  并运行前端 Vitest 测试。

.PARAMETER Backend
  仅运行后端测试。

.PARAMETER Frontend
  仅运行前端测试。

.PARAMETER Coverage
  运行时输出覆盖率报告（后端始终输出；前端加 --coverage）。

.EXAMPLE
  ./run-tests.ps1
  ./run-tests.ps1 -Backend
  ./run-tests.ps1 -Frontend -Coverage
#>
param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Coverage
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$runBoth = -not ($Backend -or $Frontend)
$failed = $false

if ($Backend -or $runBoth) {
    Write-Host "==> 运行后端测试 (docker compose backend-test)" -ForegroundColor Cyan
    docker compose -f "$root/docker-compose.yml" run --rm backend-test
    if ($LASTEXITCODE -ne 0) { $failed = $true }
}

if ($Frontend -or $runBoth) {
    Write-Host "==> 运行前端测试 (vitest)" -ForegroundColor Cyan
    Push-Location "$root/frontend"
    try {
        if (-not (Test-Path "node_modules")) { npm install }
        if ($Coverage) { npm run test:coverage } else { npm run test }
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    }
    finally { Pop-Location }
}

if ($failed) {
    Write-Host "==> 存在失败用例" -ForegroundColor Red
    exit 1
}
Write-Host "==> 全部测试通过" -ForegroundColor Green
