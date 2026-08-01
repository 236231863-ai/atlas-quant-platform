# ============================================================
# Atlas Quant Platform - Packaging Script
# 打包 Atlas.exe / Atlas_CLI.exe / Atlas_Worker.exe 到 dist/
# Usage: powershell -ExecutionPolicy Bypass -File packaging/package.ps1 [-Desktop] [-CLI] [-Worker]
# ============================================================
param(
    [switch]$Desktop,
    [switch]$CLI,
    [switch]$Worker,
    [switch]$All
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$Dist = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $Dist | Out-Null

function Invoke-Spec {
    param([string]$Name)
    Write-Host "`n=== Packaging $Name ===" -ForegroundColor Cyan
    Push-Location (Join-Path $Root "packaging")
    & $Python -m PyInstaller --noconfirm --clean "$Name.spec" --distpath $Dist --workpath (Join-Path $Root "build")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed for $Name" }
    Pop-Location
    Write-Host "OK: $Dist\$Name"
}

$runDesktop = $Desktop -or $All
$runCLI = $CLI -or $All
$runWorker = $Worker -or $All
if (-not ($runDesktop -or $runCLI -or $runWorker)) {
    $runDesktop = $true; $runCLI = $true; $runWorker = $true
}

if ($runDesktop) { Invoke-Spec "atlas_desktop" }
if ($runCLI) { Invoke-Spec "atlas_cli" }
if ($runWorker) { Invoke-Spec "atlas_worker" }

Write-Host "`nPackaging complete. Artifacts in $Dist" -ForegroundColor Green
