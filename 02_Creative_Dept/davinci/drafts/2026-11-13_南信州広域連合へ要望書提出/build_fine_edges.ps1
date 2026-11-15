Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
$framesDir = Join-Path $draftDir "frames_raw"

function Build-FineSheet {
    param([int[]]$Offsets, [string]$OutName, [int]$Cols = 5)
    $thumbW = 384
    $thumbH = 216
    $rows = [math]::Ceiling($Offsets.Count / $Cols)
    $sheet = New-Object System.Drawing.Bitmap(($Cols * $thumbW), ($rows * $thumbH))
    $g = [System.Drawing.Graphics]::FromImage($sheet)
    $g.Clear([System.Drawing.Color]::FromArgb(24, 24, 24))
    $font = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)
    $brushBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(200, 0, 0, 0))
    $brushFg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Yellow)

    $prevVals = $null
    for ($i = 0; $i -lt $Offsets.Count; $i++) {
        $off = $Offsets[$i]
        $sec = [math]::Round($off / 29.97, 2)
        $pngPath = Join-Path $framesDir ("f_{0:D4}.png" -f $off)
        if (Test-Path $pngPath) {
            $img = [System.Drawing.Bitmap]::FromFile($pngPath)
            $r = [math]::Floor($i / $Cols)
            $c = $i % $Cols
            $x = $c * $thumbW
            $y = $r * $thumbH
            $g.DrawImage($img, $x, $y, $thumbW, $thumbH)

            $curVals = New-Object double[] (32 * 18)
            $sumY = 0.0
            $idx = 0
            for ($sy = 0; $sy -lt 18; $sy++) {
                $py = [int](($sy + 0.5) * $img.Height / 18)
                for ($sx = 0; $sx -lt 32; $sx++) {
                    $px = [int](($sx + 0.5) * $img.Width / 32)
                    $col = $img.GetPixel($px, $py)
                    $luma = 0.299 * $col.R + 0.587 * $col.G + 0.114 * $col.B
                    $curVals[$idx] = $luma
                    $sumY += $luma
                    $idx++
                }
            }
            $meanY = [math]::Round($sumY / (32 * 18), 1)
            $diff = 0.0
            if ($prevVals -ne $null) {
                $sumDiff = 0.0
                for ($k = 0; $k -lt $curVals.Length; $k++) {
                    $sumDiff += [math]::Abs($curVals[$k] - $prevVals[$k])
                }
                $diff = [math]::Round($sumDiff / $curVals.Length, 1)
            }
            $prevVals = $curVals

            $g.FillRectangle($brushBg, $x, $y, $thumbW, 26)
            $label = "f={0:D4} ({1:F2}s) Y={2:F1} d={3:F1}" -f $off, $sec, $meanY, $diff
            $g.DrawString($label, $font, $brushFg, ($x + 4), ($y + 4))
            Write-Output ("{0}: {1}" -f $OutName, $label)
            $img.Dispose()
        }
    }
    $outPath = Join-Path $draftDir $OutName
    $sheet.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $sheet.Dispose()
}

$fineStart = 0..18 | ForEach-Object { 150 + $_ * 5 }
Build-FineSheet -Offsets $fineStart -OutName "contact_fine_start_150_240.png" -Cols 5

$fineEnd = @(0..24 | ForEach-Object { 5025 + $_ * 3 }) + @(5099)
Build-FineSheet -Offsets $fineEnd -OutName "contact_fine_end_5025_5099.png" -Cols 5
