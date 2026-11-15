Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
$jsonPath = Join-Path $draftDir "council_telops_meta.json"
$items = Get-Content -Raw -Encoding UTF8 $jsonPath | ConvertFrom-Json

$fontAgenda = New-Object System.Drawing.Font("Meiryo", 17, [System.Drawing.FontStyle]::Bold)
$fontBadge  = New-Object System.Drawing.Font("Meiryo", 15, [System.Drawing.FontStyle]::Bold)
$fontTitle  = New-Object System.Drawing.Font("Meiryo", 20, [System.Drawing.FontStyle]::Bold)
$fontName   = New-Object System.Drawing.Font("Meiryo", 36, [System.Drawing.FontStyle]::Bold)
$fontTopic  = New-Object System.Drawing.Font("Meiryo", 20, [System.Drawing.FontStyle]::Bold)

$bgTopBar   = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220, 12, 22, 42))
$bgPlate    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(234, 10, 20, 38))
$brWhite    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 255, 255))
$brShadow   = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(180, 0, 0, 0))
$brTitle    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 175, 228, 245))
$brTopic    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 218, 110))
$brDivider  = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(90, 255, 255, 255))

$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center

$sfTopic = New-Object System.Drawing.StringFormat
$sfTopic.Alignment = [System.Drawing.StringAlignment]::Near
$sfTopic.LineAlignment = [System.Drawing.StringAlignment]::Center

foreach ($it in $items) {
    $bmp = New-Object System.Drawing.Bitmap(1920, 1080, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))

    # Role colors
    if ($it.role -eq "chair") {
        $accentColor = [System.Drawing.Color]::FromArgb(255, 230, 145, 56)
        $badgeText = "議事進行"
    } elseif ($it.role -eq "exec") {
        $accentColor = [System.Drawing.Color]::FromArgb(255, 0, 168, 204)
        $badgeText = "説明・答弁"
    } else {
        $accentColor = [System.Drawing.Color]::FromArgb(255, 224, 86, 70)
        $badgeText = "質疑・意見"
    }
    $brAccent = New-Object System.Drawing.SolidBrush($accentColor)

    # 1. Top-Left Agenda Banner
    $g.FillRectangle($bgTopBar, 44, 30, 1260, 52)
    $g.FillRectangle($brAccent, 44, 30, 10, 52)
    $g.DrawString($it.agenda, $fontAgenda, $brShadow, 70, 42)
    $g.DrawString($it.agenda, $fontAgenda, $brWhite, 68, 40)

    # 2. Lower-Third Speaker Nameplate
    $plateX = 44
    $plateY = 874
    $plateW = 1832
    $plateH = 158
    $g.FillRectangle($bgPlate, $plateX, $plateY, $plateW, $plateH)
    $g.FillRectangle($brAccent, $plateX, $plateY, 16, $plateH)
    $g.FillRectangle($brAccent, $plateX, $plateY, $plateW, 4)

    # Role Badge Pill
    $badgeRect = New-Object System.Drawing.RectangleF(78, 890, 142, 38)
    $g.FillRectangle($brAccent, $badgeRect)
    $g.DrawString($badgeText, $fontBadge, $brWhite, $badgeRect, $sfCenter)

    # Official Title (肩書き)
    $g.DrawString($it.title, $fontTitle, $brShadow, 236, 892)
    $g.DrawString($it.title, $fontTitle, $brTitle, 234, 890)

    # Speaker Name (氏名)
    $g.DrawString($it.name, $fontName, $brShadow, 80, 940)
    $g.DrawString($it.name, $fontName, $brWhite, 78, 938)

    # Vertical Divider
    $g.FillRectangle($brDivider, 685, 936, 3, 80)

    # Topic / Summary on the right
    $topicRect = New-Object System.Drawing.RectangleF(708, 928, 1148, 94)
    $topicShadowRect = New-Object System.Drawing.RectangleF(710, 930, 1148, 94)
    $g.DrawString($it.topic, $fontTopic, $brShadow, $topicShadowRect, $sfTopic)
    $g.DrawString($it.topic, $fontTopic, $brTopic, $topicRect, $sfTopic)

    $bmp.Save($it.path, [System.Drawing.Imaging.ImageFormat]::Png)
    $brAccent.Dispose()
    $g.Dispose()
    $bmp.Dispose()
}

Write-Output "Successfully rendered $($items.Count) broadcast speaker telop PNGs."
