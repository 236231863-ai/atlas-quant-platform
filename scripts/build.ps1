# ============================================================
# Atlas Quant Platform - Unified Build Pipeline
# Usage:  powershell -ExecutionPolicy Bypass -File scripts/build.ps1 [-Target clean|install|lint|test|desktop|package|publish|all]
# ============================================================
param(
    [ValidateSet("clean", "install", "lint", "test", "desktop", "package", "publish", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }

function Step { param([string]$Msg) Write-Host "`n=== $Msg ===" -ForegroundColor Cyan }

function Invoke-Clean {
    Step "Clean"
    Remove-Item -Recurse -Force (Join-Path $Root "dist"), (Join-Path $Root "build"), (Join-Path $Root "*.spec") -ErrorAction SilentlyContinue
    Write-Host "Cleaned dist/ build/ *.spec"
}

function Invoke-Install {
    Step "Install Dependencies"
    & $Python -m pip install -r (Join-Path $Root "requirements-dev.txt") -c (Join-Path $Root "constraints.txt")
}

function Invoke-Lint {
    Step "Lint (Ruff)"
    & $Python -m ruff check $Root --exclude ".venv" --exclude "tests" 2>$null
    Write-Host "Lint complete (skip if ruff not installed)"
}

function Invoke-Test {
    Step "Run Tests"
    Push-Location $Root
    & $Python -m pytest tests/ -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
    Pop-Location
}

function Invoke-Desktop {
    Step "Build Desktop (PyInstaller)"
    Push-Location $Root
    & $Python -m PyInstaller --noconfirm --clean desktop/main.py --name Atlas --windowed
    if ($LASTEXITCODE -ne 0) { throw "Desktop build failed" }
    Pop-Location
    Write-Host "Atlas.exe generated at dist/Atlas.exe"
}

function Invoke-Package {
    Step "Package Release Artifacts"
    if (Test-Path (Join-Path $Root "packaging\package.ps1")) {
        & (Join-Path $Root "packaging\package.ps1")
    } else {
        Write-Host "packaging/package.ps1 not found - run Phase 5 first"
    }
}

function Invoke-Publish {
    Step "Publish (placeholder)"
    Write-Host "Publish stage: upload dist artifacts to GitHub Release"
}

switch ($Target) {
    "clean"    { Invoke-Clean }
    "install"  { Invoke-Install }
    "lint"     { Invoke-Lint }
    "test"     { Invoke-Test }
    "desktop"  { Invoke-Desktop }
    "package"  { Invoke-Package }
    "publish"  { Invoke-Publish }
    "all"      { Invoke-Clean; Invoke-Install; Invoke-Lint; Invoke-Test; Invoke-Desktop; Invoke-Package }
}

Write-Host "`nBuild pipeline complete. Target: $Target" -ForegroundColor Green
