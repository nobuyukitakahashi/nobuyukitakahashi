param(
    [ValidateSet("ide", "app", "auto")]
    [string]$Target = "ide",
    [switch]$SkipUpdate,
    [switch]$SkipSync
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$StateDir = Join-Path $env:LOCALAPPDATA "agy"
if (-not (Test-Path $StateDir)) {
    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
}
$StampFile = Join-Path $StateDir "last_auto_sync.txt"

if (-not $SkipUpdate) {
    Write-Host "=== [1/3] Checking agy CLI updates ==="
    $agyBins = @(
        (Join-Path $env:USERPROFILE ".gemini\bin\agy.exe"),
        (Join-Path $env:LOCALAPPDATA "agy\bin\agy.exe")
    ) | Where-Object { Test-Path $_ }

    foreach ($bin in $agyBins) {
        Write-Host "  Checking: $bin"
        & $bin update 2>&1 | ForEach-Object { Write-Host "  $_" }
    }
}

if (-not $SkipSync) {
    Write-Host "`n=== [2/3] Running pc-env-sync ==="
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $SyncScript = Join-Path $ScriptDir "sync_pc_env.ps1"
    if (Test-Path $SyncScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $SyncScript
    } else {
        Write-Warning "sync_pc_env.ps1 not found at $SyncScript"
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($StampFile, (Get-Date).ToString("o"), $utf8NoBom)

Write-Host "`n=== [3/3] Launching Antigravity ($Target) ==="
$IdeExe = Join-Path $env:LOCALAPPDATA "Programs\Antigravity IDE\Antigravity IDE.exe"
$AppExe = Join-Path $env:LOCALAPPDATA "Programs\antigravity\Antigravity.exe"

$ExeToRun = $null
if ($Target -eq "ide") {
    $ExeToRun = if (Test-Path $IdeExe) { $IdeExe } elseif (Test-Path $AppExe) { $AppExe } else { $null }
} elseif ($Target -eq "app") {
    $ExeToRun = if (Test-Path $AppExe) { $AppExe } elseif (Test-Path $IdeExe) { $IdeExe } else { $null }
} else {
    $ExeToRun = if (Test-Path $IdeExe) { $IdeExe } elseif (Test-Path $AppExe) { $AppExe } else { $null }
}

if (-not $ExeToRun) {
    Write-Error "Antigravity executable not found."
    exit 1
}

Write-Host "  Starting: $ExeToRun"
Start-Process -FilePath $ExeToRun
