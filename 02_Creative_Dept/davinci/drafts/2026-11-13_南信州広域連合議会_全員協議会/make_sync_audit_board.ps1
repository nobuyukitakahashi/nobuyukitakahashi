Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
$finalDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"
$lines = Get-Content "$draftDir\plot_data.csv"

$W = 1920
$H = 1280
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(18, 22, 30))

$fontTitle = New-Object System.Drawing.Font("Meiryo", 20, [System.Drawing.FontStyle]::Bold)
$fontSub = New-Object System.Drawing.Font("Meiryo", 13, [System.Drawing.FontStyle]::Bold)
$fontBody = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Regular)
$fontSmall = New-Object System.Drawing.Font("Meiryo", 10, [System.Drawing.FontStyle]::Bold)

$brushWhite = [System.Drawing.Brushes]::White
$brushCyan = [System.Drawing.Brushes]::Cyan
$brushYellow = [System.Drawing.Brushes]::Yellow
$brushOrange = [System.Drawing.Brushes]::Orange
$brushLime = [System.Drawing.Brushes]::Lime
$brushPanel = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(30, 36, 48))
$penGrid = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(60, 70, 90), 1)
$penRed = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 80, 80), 2)
$penCyan = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(60, 210, 255), 1.5)
$penLime = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(80, 255, 120), 1.5)
$penYellow = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 220, 60), 2)

# Header
$g.DrawString("2026-11-13 南信州広域連合議会 全員協議会 — 映像(MOV)×音声(MP3) 同期解析・波形＆視覚監査シート", $fontTitle, $brushWhite, 30, 20)
$g.DrawString("Project: 2026-11-13 南信州広域連合議会 全員協議会 | DaVinci Resolve Studio 21.2.0.6 | Full-HD (1920x1080 @ 29.97fps)", $fontBody, $brushCyan, 34, 58)

# Helper to draw dB waveform (-80 dB to 0 dB)
function Draw-Waveform($gx, $gy, $gw, $gh, $colIdxMov, $colIdxMp3, $title, $subtitle) {
    $g.FillRectangle($brushPanel, $gx, $gy, $gw, $gh)
    $g.DrawRectangle($penGrid, $gx, $gy, $gw, $gh)
    $g.DrawString($title, $fontSub, $brushYellow, ($gx + 12), ($gy + 8))
    $g.DrawString($subtitle, $fontBody, $brushWhite, ($gx + 12), ($gy + 34))
    
    $plotY = $gy + 60
    $plotH = $gh - 75
    $plotX = $gx + 60
    $plotW = $gw - 80
    $g.DrawRectangle($penGrid, $plotX, $plotY, $plotW, $plotH)
    
    foreach ($db in @(-20, -40, -60)) {
        $yy = $plotY + $plotH * (0 - $db) / 80.0
        $g.DrawLine($penGrid, $plotX, $yy, ($plotX + $plotW), $yy)
        $g.DrawString("$($db)dB", $fontBody, $brushWhite, ($gx + 8), ($yy - 8))
    }
    
    for ($i = 0; $i -lt 999; $i++) {
        $p1 = $lines[$i].Split(",")
        $p2 = $lines[$i+1].Split(",")
        $x1 = $plotX + ($i / 1000.0) * $plotW
        $x2 = $plotX + (($i + 1) / 1000.0) * $plotW
        
        # MP3 (Cyan)
        $vMp3_1 = [math]::Max(-80.0, [math]::Min(0.0, [double]$p1[$colIdxMp3]))
        $vMp3_2 = [math]::Max(-80.0, [math]::Min(0.0, [double]$p2[$colIdxMp3]))
        $yMp3_1 = $plotY + $plotH * (0 - $vMp3_1) / 80.0
        $yMp3_2 = $plotY + $plotH * (0 - $vMp3_2) / 80.0
        $g.DrawLine($penCyan, $x1, $yMp3_1, $x2, $yMp3_2)
        
        # MOV (Red/Lime)
        $vMov_1 = [math]::Max(-80.0, [math]::Min(0.0, [double]$p1[$colIdxMov]))
        $vMov_2 = [math]::Max(-80.0, [math]::Min(0.0, [double]$p2[$colIdxMov]))
        $yMov_1 = $plotY + $plotH * (0 - $vMov_1) / 80.0
        $yMov_2 = $plotY + $plotH * (0 - $vMov_2) / 80.0
        $penUse = if ($vMov_1 -gt -55.0) { $penLime } else { $penRed }
        $g.DrawLine($penUse, $x1, $yMov_1, $x2, $yMov_2)
    }
}

# Panel 1: PB130017.MOV vs MP3_1328
Draw-Waveform 30 95 1860 220 0 1 `
    "1. PB130017.MOV (尺 10分15.12秒 / 18,435f) × 『11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3』" `
    "MOV内蔵音声: 全編無音 (-69.8 dBFS 赤線) | 同期オフセット: MP3の 00:00:36.63 (1,098f) 〜 00:10:51.75 (19,533f) を配置 (水色線)"

# Panel 2: Visual Sync Verification Frames for PB130017 (Union Head Sato standing/bowing/sitting)
$g.FillRectangle($brushPanel, 30, 330, 1860, 290)
$g.DrawRectangle($penGrid, 30, 330, 1860, 290)
$g.DrawString("2. PB130017.MOV × 13-28.mp3 視覚・動作同期検証（佐藤広域連合長の起立・一礼・着席タイミングとMP3音声の一致確認）", $fontSub, $brushYellow, 42, 338)

$keyFrames = @(
    @{f="pb17_s0030.png"; lbl="PB17 00:30.0 (MP3 01:06.6)`n開会起立・一礼 (無音区間)"},
    @{f="pb17_s0052.png"; lbl="PB17 00:52.0 (MP3 01:28.6)`n議長 起立・挨拶開始"},
    @{f="pb17_s0236.png"; lbl="PB17 03:56.0 (MP3 04:32.6)`n佐藤連合長 指名・起立"},
    @{f="pb17_s0239.png"; lbl="PB17 03:59.0 (MP3 04:35.6)`n『こんにちは』一礼の頂点"},
    @{f="pb17_s0360.png"; lbl="PB17 06:00.0 (MP3 06:36.6)`n挨拶終了・一礼"},
    @{f="pb17_s0361.png"; lbl="PB17 06:01.0 (MP3 06:37.6)`n佐藤連合長 着席完了"}
)

$srcCrop = New-Object System.Drawing.Rectangle(0, 180, 950, 420)
for ($k = 0; $k -lt $keyFrames.Count; $k++) {
    $kx = 45 + $k * 305
    $ky = 372
    $p = "$draftDir\pb17_sync_frames\$($keyFrames[$k].f)"
    if (Test-Path $p) {
        $im = [System.Drawing.Image]::FromFile($p)
        $dstR = New-Object System.Drawing.Rectangle($kx, $ky, 290, 185)
        $g.DrawImage($im, $dstR, $srcCrop, [System.Drawing.GraphicsUnit]::Pixel)
        $g.DrawRectangle($penYellow, $kx, $ky, 290, 185)
        $im.Dispose()
    }
    $g.DrawString($keyFrames[$k].lbl, $fontSmall, $brushWhite, $kx, ($ky + 190))
}

# Panel 3: PB130019.MOV vs MP3_1412 Full Duration
Draw-Waveform 30 635 1860 280 2 3 `
    "3. PB130019.MOV (尺 1時間17分15.13秒 / 138,915f) × 『11月13日（14-12）…資料3 桐林クリーンセンター解体について.mp3』" `
    "MOV内蔵音声: 00:00:00〜00:17:44.59 (0〜31,905f) 無音(赤線) ➔ 00:17:44.60 (1,064.6s) マイクON(緑線) | 同期位置: MP3 00:00:12.63 (379f)〜01:17:27.76 (水色線)"

# Draw vertical marker at 1064.6s / 4635.1s on Panel 3
$switchX = 90 + (1064.6 / 4635.13) * 1780
$g.DrawLine($penYellow, $switchX, 695, $switchX, 900)
$g.DrawString("◀ 17分44.6秒 (Frame 31,906) 外部マイク電源ON (これより前は無音)", $fontSmall, $brushYellow, ($switchX + 6), 875)

# Panel 4: Zoomed 100s correlation window around 1040s..1140s
Draw-Waveform 30 930 1860 320 4 5 `
    "4. PB130019.MOV [1040s〜1140s] × 14-12.mp3 [1052.63s〜1152.63s] 10ミリ秒精度 相互相関拡大波形 (相関係数 r = 0.9325)" `
    "水色=14-12.mp3 (+12.63s オフセット) / 赤色=MOV無音区間 / 緑色=MOV有音区間 (1,064.6s以降、発言波形・無音ギャップがミリ秒単位で完全一致)"

$g.Dispose()
$outBoard = "$finalDir\sync_audit_board.png"
$bmp.Save($outBoard, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "Saved $outBoard"
