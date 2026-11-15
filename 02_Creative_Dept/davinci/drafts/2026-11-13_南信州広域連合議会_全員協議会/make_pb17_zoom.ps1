Add-Type -AssemblyName System.Drawing
$dir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会\pb17_sync_frames"
$files = Get-ChildItem "$dir\pb17_s*.png" | Where-Object {
    $s = [int]($_.BaseName.Substring(6))
    ($s -ge 28 -and $s -le 55) -or ($s -ge 225 -and $s -le 240) -or ($s -ge 358 -and $s -le 390)
} | Sort-Object Name

$cols = 5
$rows = [math]::Ceiling($files.Count / $cols)
$tw = 380
$th = 160
$bmp = New-Object System.Drawing.Bitmap(($cols * $tw), ($rows * $th))
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::Black)
$font = New-Object System.Drawing.Font("Consolas", 13, [System.Drawing.FontStyle]::Bold)
$brush = [System.Drawing.Brushes]::Yellow
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(190, 0, 0, 0))

$srcRect = New-Object System.Drawing.Rectangle(0, 180, 950, 400)

for ($i = 0; $i -lt $files.Count; $i++) {
    $c = $i % $cols
    $r = [math]::Floor($i / $cols)
    $img = [System.Drawing.Image]::FromFile($files[$i].FullName)
    $dstRect = New-Object System.Drawing.Rectangle(($c * $tw), ($r * $th), $tw, $th)
    $g.DrawImage($img, $dstRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
    $img.Dispose()
    $sec = [int]($files[$i].BaseName.Substring(6))
    $mp3_sec = $sec + 36.6
    $label = "PB17:$($sec)s | MP3(+36.6):$($mp3_sec.ToString('F1'))s"
    $g.FillRectangle($bgBrush, ($c * $tw + 4), ($r * $th + 4), 310, 24)
    $g.DrawString($label, $font, $brush, ($c * $tw + 6), ($r * $th + 5))
}
$g.Dispose()
$out = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会\pb17_zoom_speakers.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "Saved $out ($($files.Count) tiles)"
