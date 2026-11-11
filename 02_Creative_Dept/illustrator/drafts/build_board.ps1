Add-Type -AssemblyName System.Drawing
$finalDir = Join-Path (Split-Path $PSScriptRoot -Parent) "final_outputs"
$outBoard = Join-Path $finalDir "logo_6proposals_board.png"

$W = 1800
$H = 1280
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(244, 248, 246))
$primaryColor = [System.Drawing.Color]::FromArgb(0, 162, 115)
$primaryBrush = New-Object System.Drawing.SolidBrush($primaryColor)
$slateColor = [System.Drawing.Color]::FromArgb(20, 46, 40)
$slateBrush = New-Object System.Drawing.SolidBrush($slateColor)
$subBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(74, 102, 94))
$whiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$linePen = New-Object System.Drawing.Pen($primaryColor, 3)

$g.FillRectangle($bgBrush, 0, 0, $W, $H)

$titleFont = New-Object System.Drawing.Font("Segoe UI", 21, [System.Drawing.FontStyle]::Bold)
$metaFont  = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$cardTitleFont = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
$cardSubFont   = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Regular)

$g.DrawString("cvn Plus Mobile - 6 Logo Design Proposals Overview (3 Patterns x 2 Proposals)", $titleFont, $slateBrush, 40, 22)
$g.DrawString("Primary Color: CMYK C:90% M:0% Y:70% K:0% (Web HEX: #00a273)  |  Design Policy: Modern, Minimal & Geometric Round", $metaFont, $primaryBrush, 42, 62)
$g.DrawLine($linePen, 40, 92, ($W - 40), 92)

$cards = @(
    @{ id="1A"; col=0; row=0; title="Proposal 1-A  |  Pattern 1 (Katakana 1-Line): Horizontal Minimal"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273)  |  Web Header, TVCM, Newspaper Flyer, Storefront Sign" },
    @{ id="1B"; col=1; row=0; title="Proposal 1-B  |  Pattern 1 (Katakana 2-Tier): Architectural 2-Tier Stack"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273)  |  Brochure, Price Plan Table, Business Card, Shop Sign" },
    @{ id="2A"; col=0; row=1; title="Proposal 2-A  |  Pattern 2 (English 2-Tier): Origin Grid 2-Tier Stack"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273)  |  Exact Inheritance of Corporate Tagline Grid & Spurless Arch DNA" },
    @{ id="2B"; col=1; row=1; title="Proposal 2-B  |  Pattern 2 (English 1-Line): Modern Weight Contrast"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273)  |  Medium 'plus' + Bold 'mobile' Contrast for Digital UI & eSIM" },
    @{ id="3A"; col=0; row=2; title="Proposal 3-A  |  Pattern 3 (Symbol + English): Geometric Capsule Plus Lockup"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273)  |  Iconic Round-Terminal Cross '+' for Bundle Promo & SIM Package" },
    @{ id="3B"; col=1; row=2; title="Proposal 3-B  |  Pattern 3 (Symbol + English + Kana): Compact Pill Unit"; sub="100% Primary Color CMYK C90 M0 Y70 K0 (#00a273 + White Knockout)  |  App Icon, SIM Card & All-Generation Media" }
)

$cardW = 840
$cardH = 360
$startX = 40
$startY = 112
$gapX = 40
$gapY = 24

foreach ($c in $cards) {
    $cx = $startX + $c.col * ($cardW + $gapX)
    $cy = $startY + $c.row * ($cardH + $gapY)
    
    $g.FillRectangle($whiteBrush, $cx, $cy, $cardW, $cardH)
    $borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(210, 230, 222), 2)
    $g.DrawRectangle($borderPen, $cx, $cy, $cardW, $cardH)
    
    $pngPath = Join-Path $finalDir ("logo_" + $c.id + ".png")
    $subImg = New-Object System.Drawing.Bitmap($pngPath)
    $srcRect = New-Object System.Drawing.Rectangle(140, 82, 1320, 260)
    # Preserve aspect ratio (1320 : 260 = 5.077 : 1) inside 800 x 158
    $dstRect = New-Object System.Drawing.Rectangle(($cx + 20), ($cy + 98), 800, 158)
    $g.DrawImage($subImg, $dstRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
    $subImg.Dispose()
    
    $g.FillRectangle($primaryBrush, $cx, $cy, $cardW, 42)
    $g.DrawString($c.title, $cardTitleFont, $whiteBrush, ($cx + 16), ($cy + 10))
    $g.DrawString($c.sub, $cardSubFont, $subBrush, ($cx + 16), ($cy + 322))
}

$g.Dispose()
$bmp.Save($outBoard, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Host "Saved clean composite board to $outBoard"
