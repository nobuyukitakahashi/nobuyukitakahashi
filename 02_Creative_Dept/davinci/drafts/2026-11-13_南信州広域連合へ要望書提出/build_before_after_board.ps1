Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
$baDir = Join-Path $draftDir "before_after"

$srcFrames = @(215, 300, 1200, 3600, 5000, 5080)
$labels = @(
    "In-Point (f=215 / 7.17s)",
    "Opening Bow (f=300 / 10.01s)",
    "Reading Petition (f=1200 / 40.04s)",
    "Handoff to Union Head (f=3600 / 120.12s)",
    "Closing Bow (f=5000 / 166.83s)",
    "Out-Point (f=5080 / 169.50s)"
)

$w = 640
$h = 360
$cols = 2
$rows = $srcFrames.Count
$board = New-Object System.Drawing.Bitmap(($cols * $w), ($rows * $h))
$g = [System.Drawing.Graphics]::FromImage($board)
$g.Clear([System.Drawing.Color]::FromArgb(20, 20, 20))

$font = New-Object System.Drawing.Font("Consolas", 13, [System.Drawing.FontStyle]::Bold)
$brushBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(210, 0, 0, 0))
$brushBefore = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 160, 80))
$brushAfter = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 100, 255, 140))

function Get-MeanLuma([System.Drawing.Bitmap]$bmp) {
    $sum = 0.0
    $cnt = 0
    for ($sy = 0; $sy -lt 24; $sy++) {
        $py = [int](($sy + 0.5) * $bmp.Height / 24)
        for ($sx = 0; $sx -lt 32; $sx++) {
            $px = [int](($sx + 0.5) * $bmp.Width / 32)
            $c = $bmp.GetPixel($px, $py)
            $sum += (0.299 * $c.R + 0.587 * $c.G + 0.114 * $c.B)
            $cnt++
        }
    }
    return [math]::Round($sum / $cnt, 1)
}

for ($r = 0; $r -lt $rows; $r++) {
    $sf = $srcFrames[$r]
    $lbl = $labels[$r]
    $bPath = Join-Path $baDir ("before_src_{0:D4}.png" -f $sf)
    $aPath = Join-Path $baDir ("after_src_{0:D4}.png" -f $sf)

    if (Test-Path $bPath) {
        $bmpB = [System.Drawing.Bitmap]::FromFile($bPath)
        $yB = Get-MeanLuma $bmpB
        $g.DrawImage($bmpB, 0, ($r * $h), $w, $h)
        $g.FillRectangle($brushBg, 0, ($r * $h), $w, 32)
        $g.DrawString("BEFORE | $lbl | Y=$yB", $font, $brushBefore, 8, ($r * $h + 6))
        $bmpB.Dispose()
    }
    if (Test-Path $aPath) {
        $bmpA = [System.Drawing.Bitmap]::FromFile($aPath)
        $yA = Get-MeanLuma $bmpA
        $g.DrawImage($bmpA, $w, ($r * $h), $w, $h)
        $g.FillRectangle($brushBg, $w, ($r * $h), $w, 32)
        $g.DrawString("AFTER (Stabilized + CDL) | $lbl | Y=$yA", $font, $brushAfter, ($w + 8), ($r * $h + 6))
        $bmpA.Dispose()
        Write-Output ("Row {0} ({1}): Before Y={2} -> After Y={3}" -f $r, $lbl, $yB, $yA)
    }
}

$outBoard = Join-Path $draftDir "before_after_audit.png"
$board.Save($outBoard, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$board.Dispose()
Write-Output "Saved $outBoard"
