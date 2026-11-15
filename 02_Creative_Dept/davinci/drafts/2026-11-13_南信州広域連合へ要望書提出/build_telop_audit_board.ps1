Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
$finalDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
$auditDir = Join-Path $draftDir "telop_audit_frames"

$files = @(
    @{ file="telop_check_1_1s.png";   lbl="t=1.5s | Opening Greeting (Rep. Kobayashi)" },
    @{ file="telop_check_2_8s.png";   lbl="t=8.0s | Gratitude for Time Before Council (Rep. Kobayashi)" },
    @{ file="telop_check_3_53s.png";  lbl="t=53.0s | Key Petition Items: Removal & Audit (Rep. Kobayashi)" },
    @{ file="telop_check_4_99s.png";  lbl="t=99.0s | Petition Handoff to Union Head" },
    @{ file="telop_check_5_128s.png"; lbl="t=128.0s | Request for Response Within This Month (Rep. Kobayashi)" },
    @{ file="telop_check_6_155s.png"; lbl="t=155.5s | Response from Union Head Sato (Mayor of Iida)" }
)

$w = 960
$h = 540
$cols = 2
$rows = 3
$board = New-Object System.Drawing.Bitmap(($cols * $w), ($rows * $h))
$g = [System.Drawing.Graphics]::FromImage($board)
$g.Clear([System.Drawing.Color]::FromArgb(18, 18, 18))

$font = New-Object System.Drawing.Font("Consolas", 15, [System.Drawing.FontStyle]::Bold)
$brushBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(210, 0, 0, 0))
$brushFg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 120, 255, 160))

for ($i = 0; $i -lt $files.Count; $i++) {
    $fp = Join-Path $auditDir $files[$i].file
    if (Test-Path $fp) {
        $img = [System.Drawing.Bitmap]::FromFile($fp)
        $r = [math]::Floor($i / $cols)
        $c = $i % $cols
        $x = $c * $w
        $y = $r * $h
        $g.DrawImage($img, $x, $y, $w, $h)
        $g.FillRectangle($brushBg, $x, $y, $w, 34)
        $g.DrawString($files[$i].lbl, $font, $brushFg, ($x + 10), ($y + 6))
        $img.Dispose()
    }
}

$outBoard = Join-Path $finalDir "keyframes_telop_audit_board.png"
$board.Save($outBoard, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$board.Dispose()
Write-Output "Saved $outBoard"
