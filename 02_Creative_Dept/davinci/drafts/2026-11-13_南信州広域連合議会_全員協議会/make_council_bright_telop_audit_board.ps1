Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
$finalDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"

function Get-MeanLuma($imgPath) {
    $b = New-Object System.Drawing.Bitmap($imgPath)
    $sumY = 0.0
    $count = 0
    for ($y = 0; $y -lt $b.Height; $y += 8) {
        for ($x = 0; $x -lt $b.Width; $x += 8) {
            $c = $b.GetPixel($x, $y)
            $luma = 0.2126 * $c.R + 0.7152 * $c.G + 0.0722 * $c.B
            $sumY += $luma
            $count++
        }
    }
    $b.Dispose()
    return [math]::Round($sumY / $count, 1)
}

$y17Before = Get-MeanLuma (Join-Path $draftDir "audit_pb17_before.png")
$y17After  = Get-MeanLuma (Join-Path $draftDir "audit_pb17_after_sato.png")
$y19Before = Get-MeanLuma (Join-Path $draftDir "audit_pb19_before.png")
$y19After  = Get-MeanLuma (Join-Path $draftDir "audit_pb19_after_kobayashi.png")

Write-Output "PB130017 Mean Luma Y: Before = $y17Before -> After = $y17After (+$([math]::Round(($y17After - $y17Before)/$y17Before*100, 1))%)"
Write-Output "PB130019 Mean Luma Y: Before = $y19Before -> After = $y19After (+$([math]::Round(($y19After - $y19Before)/$y19Before*100, 1))%)"

$W = 2400
$H = 1920
$canvas = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($canvas)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::FromArgb(255, 16, 20, 28))

$fontHeader = New-Object System.Drawing.Font("Meiryo", 22, [System.Drawing.FontStyle]::Bold)
$fontSub    = New-Object System.Drawing.Font("Meiryo", 14, [System.Drawing.FontStyle]::Bold)
$fontLabel  = New-Object System.Drawing.Font("Meiryo", 13, [System.Drawing.FontStyle]::Bold)
$brWhite    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$brCyan     = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 100, 220, 255))
$brGold     = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 210, 100))
$brCardBg   = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 26, 34, 48))

$g.DrawString("南信州広域連合議会 令和8年第2回全員協議会 ｜ 明るさ大幅改善（CDL）＆ 全発言者肩書き・氏名テロップ 視覚監査シート", $fontHeader, $brWhite, 36, 22)
$g.DrawString("CDL: Slope(1.38, 1.36, 1.32) Offset(0.04, 0.04, 0.05) Power(0.65, 0.65, 0.65) Sat(1.14) ｜ PB17平均輝度Y: $y17Before → $y17After / PB19平均輝度Y: $y19Before → $y19After", $fontSub, $brCyan, 38, 66)

$panels = @(
    @{ file="audit_pb17_before.png";          title="① [Before] PB130017 補正前（04:30 広域連合長挨拶・平均輝度 Y=$y17Before）" },
    @{ file="audit_pb17_after_sato.png";      title="② [After] PB130017 明るさ補正＋テロップ（佐藤 健 広域連合長・平均輝度 Y=$y17After）" },
    @{ file="audit_pb17_after_takemura.png";  title="③ [After] PB130017 次第2 議長挨拶（竹村 圭史 議長）" },
    @{ file="audit_pb17_after_takada.png";    title="④ [After] PB130017 次第4-(1) 資料No.1 説明（髙田 修 副管理者［飯田市副市長］）" },
    @{ file="audit_pb19_before.png";          title="⑤ [Before] PB130019 補正前（27:15 資料No.3 質疑・平均輝度 Y=$y19Before）" },
    @{ file="audit_pb19_after_kobayashi.png"; title="⑥ [After] PB130019 明るさ補正＋テロップ（小林 真一 議員 質疑・平均輝度 Y=$y19After）" },
    @{ file="audit_pb19_after_sekijima.png";  title="⑦ [After] PB130019 執行部答弁テロップ（関島 徹信 飯田環境センター所長）" },
    @{ file="audit_pb19_after_ichinose.png";  title="⑧ [After] PB130019 後半質疑テロップ（市瀬 芳明 議員 質疑）" }
)

$colW = 1140
$rowH = 435
$imgW = 704
$imgH = 396

for ($i = 0; $i -lt $panels.Count; $i++) {
    $col = $i % 2
    $row = [math]::Floor($i / 2)
    $px = 36 + $col * ($colW + 48)
    $py = 112 + $row * ($rowH + 14)

    $g.FillRectangle($brCardBg, $px, $py, $colW, $rowH)
    $g.DrawString($panels[$i].title, $fontLabel, $brGold, ($px + 14), ($py + 8))

    $imgPath = Join-Path $draftDir $panels[$i].file
    if (Test-Path $imgPath) {
        $src = New-Object System.Drawing.Bitmap($imgPath)
        # Left side: full 16:9 frame
        $g.DrawImage($src, ($px + 12), ($py + 34), $imgW, $imgH)
        # Right side top: 2x zoom on speaker / room center
        $crop1 = New-Object System.Drawing.Rectangle(360, 220, 720, 345)
        $dest1 = New-Object System.Drawing.Rectangle(($px + $imgW + 24), ($py + 34), 400, 192)
        $g.DrawImage($src, $dest1, $crop1, [System.Drawing.GraphicsUnit]::Pixel)
        # Right side bottom: 1:1 natural aspect zoom on lower-third speaker nameplate
        $crop2 = New-Object System.Drawing.Rectangle(40, 868, 600, 174)
        $dest2 = New-Object System.Drawing.Rectangle(($px + $imgW + 24), ($py + 236), 400, 194)
        $g.DrawImage($src, $dest2, $crop2, [System.Drawing.GraphicsUnit]::Pixel)
        $src.Dispose()
    }
}

$outBoard = Join-Path $finalDir "council_bright_telop_audit_board.png"
$canvas.Save($outBoard, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$canvas.Dispose()
Write-Output "Saved visual audit board to $outBoard"
