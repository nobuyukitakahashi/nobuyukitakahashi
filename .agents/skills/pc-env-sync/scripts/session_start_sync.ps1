param(
    [int]$CooldownHours = 6
)

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Drain stdin JSON required by Antigravity hook contract
try {
    $null = [Console]::In.ReadToEnd()
} catch {}

$StateDir = Join-Path $env:LOCALAPPDATA "agy"
if (-not (Test-Path $StateDir)) {
    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
}
$StampFile = Join-Path $StateDir "last_auto_sync.txt"
$LogFile = Join-Path $StateDir "auto_sync.log"

$ShouldRun = $true
if (Test-Path $StampFile) {
    try {
        $raw = (Get-Content -Path $StampFile -Raw -Encoding UTF8).Trim()
        $last = [DateTimeOffset]::Parse($raw)
        if (((Get-Date) - $last.LocalDateTime).TotalHours -lt $CooldownHours) {
            $ShouldRun = $false
        }
    } catch {
        $ShouldRun = $true
    }
}

if ($ShouldRun) {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($StampFile, (Get-Date).ToString("o"), $utf8NoBom)

    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $SyncScript = Join-Path $ScriptDir "sync_pc_env.ps1"

    $workerCmd = @"
`$ErrorActionPreference = 'Continue'
Start-Transcript -Path '$LogFile' -Force | Out-Null
try {
    foreach (`$bin in @("`$env:USERPROFILE\.gemini\bin\agy.exe", "`$env:LOCALAPPDATA\agy\bin\agy.exe")) {
        if (Test-Path `$bin) { & `$bin update 2>&1 | Out-Host }
    }
    if (Test-Path '$SyncScript') {
        & '$SyncScript' | Out-Host
    }
} finally {
    Stop-Transcript | Out-Null
}
"@
    $encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($workerCmd))
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded -WindowStyle Hidden | Out-Null
}

# Return valid empty hook JSON immediately without blocking session startup
Write-Output "{}"
