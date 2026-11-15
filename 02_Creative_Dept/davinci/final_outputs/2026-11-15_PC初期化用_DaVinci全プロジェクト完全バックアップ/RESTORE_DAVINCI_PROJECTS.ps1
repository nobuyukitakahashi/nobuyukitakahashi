# ==============================================================================
# DaVinci Resolve Studio 全プロジェクト＆設定 1クリック完全復元スクリプト
# 作成日: 2026-11-15
# 使い方: PC初期化＆DaVinci Resolve再インストール後（DaVinciを閉じた状態で）
#         このスクリプトを右クリック ➔「PowerShellで実行」してください。
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  DaVinci Resolve 全15プロジェクト＆設定 自動復元ツール" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# DaVinci Resolve が起動中なら警告して終了
$proc = Get-Process Resolve -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[!] DaVinci Resolve が起動中です。終了してから再実行してください。" -ForegroundColor Red
    Read-Host "Enterキーで終了します"
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SupportDst = "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support"

if (-not (Test-Path $SupportDst)) {
    New-Item -ItemType Directory -Path $SupportDst -Force | Out-Null
}

# 1. Resolve Project Library の復元
$LibSrc = Join-Path $ScriptDir "02_Resolve_Project_Library_丸ごとバックアップ\Resolve Project Library"
$LibDst = Join-Path $SupportDst "Resolve Project Library"

if (Test-Path $LibSrc) {
    Write-Host "[1/3] プロジェクトライブラリ (全15プロジェクト) を復元中..." -ForegroundColor Yellow
    if (Test-Path $LibDst) {
        $BackupOld = "${LibDst}_old_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Rename-Item -Path $LibDst -NewName $BackupOld -Force
        Write-Host "  -> 既存の初期ライブラリを $BackupOld に退避しました。" -ForegroundColor Gray
    }
    Copy-Item -Path $LibSrc -Destination $LibDst -Recurse -Force
    Write-Host "  -> 完了: $LibDst" -ForegroundColor Green
} else {
    Write-Host "[!] $LibSrc が見つかりません。ZIPファイルから展開します..." -ForegroundColor Yellow
    $ZipSrc = Join-Path $ScriptDir "02_Resolve_Project_Library_丸ごとバックアップ\Resolve_Project_Library_FullBackup_20261115.zip"
    if (Test-Path $ZipSrc) {
        Expand-Archive -Path $ZipSrc -DestinationPath $SupportDst -Force
        Write-Host "  -> ZIPから復元完了: $LibDst" -ForegroundColor Green
    }
}

# 2. カスタム設定 (Fusion / .LUT / Fairlight) の復元
Write-Host "[2/3] カスタム設定 (Fusion / LUT / Fairlight) を復元中..." -ForegroundColor Yellow
$SettingsSrc = Join-Path $ScriptDir "03_Custom_Settings_LUT_Templates"
foreach ($folder in @("Fusion", ".LUT", "Fairlight")) {
    $s = Join-Path $SettingsSrc $folder
    $d = Join-Path $SupportDst $folder
    if (Test-Path $s) {
        Copy-Item -Path $s -Destination $SupportDst -Recurse -Force
        Write-Host "  -> $folder 復元完了" -ForegroundColor Green
    }
}

# 3. D:\DvinchiProject\.gallery が消えている場合の復元
$GallerySrc = Join-Path $SettingsSrc "Gallery_Stills_D_Drive"
$GalleryDst = "D:\DvinchiProject\.gallery"
if ((Test-Path $GallerySrc) -and (-not (Test-Path $GalleryDst))) {
    if (Test-Path "D:\") {
        Write-Host "[3/3] D:\DvinchiProject\.gallery (スチルデータ) を復元中..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path "D:\DvinchiProject" -Force | Out-Null
        Copy-Item -Path $GallerySrc -Destination $GalleryDst -Recurse -Force
        Write-Host "  -> ギャラリースチル復元完了: $GalleryDst" -ForegroundColor Green
    }
} else {
    Write-Host "[3/3] D:\DvinchiProject\.gallery は既に存在するためスキップしました。" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  すべての復元が完了しました！DaVinci Resolve を起動してください。" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Read-Host "Enterキーで画面を閉じます"
