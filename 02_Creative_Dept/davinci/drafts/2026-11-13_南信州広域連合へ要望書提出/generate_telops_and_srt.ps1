Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
$finalDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
$hDir = "H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
$telopDir = Join-Path $draftDir "telops_png"
New-Item -ItemType Directory -Force -Path $telopDir | Out-Null

$subs = @(
    @{ id=1;  s=0.00;  e=3.10;  spk="検証会議 代表 小林 伸"; role="rep"; text="（11月2日の検証会議に）ご出席いただきまして、誠にありがとうございました。" },
    @{ id=2;  s=3.40;  e=6.30;  spk="検証会議 代表 小林 伸"; role="rep"; text="また今日は、広域連合議会の前の大事な時間に" },
    @{ id=3;  s=6.40;  e=10.60; spk="検証会議 代表 小林 伸"; role="rep"; text="お時間を取っていただきまして、誠にありがとうございます。" },
    @{ id=4;  s=11.20; e=15.60; spk="検証会議 代表 小林 伸"; role="rep"; text="先日の検証会議を受けまして、私どもも" },
    @{ id=5;  s=16.00; e=20.30; spk="検証会議 代表 小林 伸"; role="rep"; text="重大な決断をしていただいたと思いながら、" },
    @{ id=6;  s=20.70; e=23.70; spk="検証会議 代表 小林 伸"; role="rep"; text="まだ要望事項がいくつかありますので、" },
    @{ id=7;  s=23.80; e=26.80; spk="検証会議 代表 小林 伸"; role="rep"; text="ぜひ今日は受け取っていただきたいということで、" },
    @{ id=8;  s=27.40; e=31.20; spk="検証会議 代表 小林 伸"; role="rep"; text="こちらは検証会議の一部のメンバーなんですけれども、" },
    @{ id=9;  s=31.30; e=34.40; spk="検証会議 代表 小林 伸"; role="rep"; text="今日は一緒について来たいということで来させていただきました。" },
    @{ id=10; s=34.50; e=36.50; spk="検証会議 代表 小林 伸"; role="rep"; text="よろしくお願いいたします。" },
    @{ id=11; s=37.60; e=40.80; spk="検証会議 代表 小林 伸"; role="rep"; text="お渡しする要望事項といたしましては、" },
    @{ id=12; s=41.50; e=44.50; spk="検証会議 代表 小林 伸"; role="rep"; text="要望事項といたしましては、" },
    @{ id=13; s=45.60; e=49.60; spk="検証会議 代表 小林 伸"; role="rep"; text="先日、連合長さんには、" },
    @{ id=14; s=51.00; e=55.40; spk="検証会議 代表 小林 伸"; role="rep"; text="「残置物の撤去」それから「第三者による監査」" },
    @{ id=15; s=56.20; e=60.20; spk="検証会議 代表 小林 伸"; role="rep"; text="それとその他、職員の処分等々の" },
    @{ id=16; s=60.40; e=64.30; spk="検証会議 代表 小林 伸"; role="rep"; text="お話をいただきましたけれども、" },
    @{ id=17; s=65.00; e=68.70; spk="検証会議 代表 小林 伸"; role="rep"; text="それにつきまして、残置物の撤去について" },
    @{ id=18; s=68.90; e=73.30; spk="検証会議 代表 小林 伸"; role="rep"; text="いつ頃していただけるんだろうかとか、2番目の" },
    @{ id=19; s=74.80; e=77.30; spk="検証会議 代表 小林 伸"; role="rep"; text="第三者による監査については、" },
    @{ id=20; s=77.40; e=81.80; spk="検証会議 代表 小林 伸"; role="rep"; text="できれば私どもも、ある部分混ぜていただきたいとか、" },
    @{ id=21; s=82.60; e=85.50; spk="検証会議 代表 小林 伸"; role="rep"; text="それからその他の項目もありますので、" },
    @{ id=22; s=85.70; e=89.30; spk="検証会議 代表 小林 伸"; role="rep"; text="よろしくお受け取りをお願いしたいと思います。" },
    @{ id=23; s=97.30; e=100.80; spk="要望書の手交"; role="both"; text="「このような内容ですので。」「はい、承知しました。」" },
    @{ id=24; s=114.50; e=118.80; spk="検証会議 代表 小林 伸"; role="rep"; text="今日は取材したいということもあり、マスコミも来ておりますけれども、" },
    @{ id=25; s=119.00; e=122.00; spk="検証会議 代表 小林 伸"; role="rep"; text="どうぞよろしくお願いしたいと思います。" },
    @{ id=26; s=122.40; e=125.80; spk="検証会議 代表 小林 伸"; role="rep"; text="私どもも時間的な制約があるものですから、" },
    @{ id=27; s=126.10; e=130.00; spk="検証会議 代表 小林 伸"; role="rep"; text="なんとか今月いっぱいに、かなりの部分のお答えをいただきたいと思っておりますので、" },
    @{ id=28; s=130.10; e=134.30; spk="検証会議 代表 小林 伸"; role="rep"; text="よろしくご協議をしていただきたいと思っております。お願いします。" },
    @{ id=29; s=138.30; e=141.20; spk="検証会議 代表 小林 伸"; role="rep"; text="（同行メンバーへ）何か補足することはありませんか？" },
    @{ id=30; s=141.80; e=143.60; spk="検証会議 代表・同行メンバー"; role="rep"; text="「いいですか？」「はい。」" },
    @{ id=31; s=144.00; e=147.20; spk="検証会議 代表 小林 伸"; role="rep"; text="今日は大事な時間の前に時間を取っていただきまして、誠にありがとうございます。" },
    @{ id=32; s=147.30; e=149.10; spk="検証会議 代表・同行メンバー"; role="rep"; text="よろしくお願いいたします。" },
    @{ id=33; s=149.20; e=152.90; spk="南信州広域連合長 佐藤 健（飯田市長）"; role="head"; text="先日の説明会では大変お世話になりました。ありがとうございました。" },
    @{ id=34; s=153.50; e=158.00; spk="南信州広域連合長 佐藤 健（飯田市長）"; role="head"; text="今日いただきました要望書につきましては、誠意をもって回答したいと思います。" },
    @{ id=35; s=158.10; e=161.30; spk="一同"; role="both"; text="「よろしくお願いいたします。」「ありがとうございました。」" }
)

function Format-SrtTime([double]$sec) {
    $ts = [TimeSpan]::FromSeconds($sec)
    return "{0:D2}:{1:D2}:{2:D2},{3:D3}" -f $ts.Hours, $ts.Minutes, $ts.Seconds, $ts.Milliseconds
}

$srtLines = New-Object System.Collections.Generic.List[string]
$manifest = New-Object System.Collections.Generic.List[object]

$fontFamily = New-Object System.Drawing.FontFamily("Yu Gothic UI")
$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center

foreach ($item in $subs) {
    $id = $item.id
    $tStart = Format-SrtTime $item.s
    $tEnd = Format-SrtTime $item.e
    $srtLines.Add("$id")
    $srtLines.Add("$tStart --> $tEnd")
    $srtLines.Add("【$($item.spk)】$($item.text)")
    $srtLines.Add("")

    $pngName = "telop_{0:D3}.png" -f $id
    $pngPath = Join-Path $telopDir $pngName

    $bmp = New-Object System.Drawing.Bitmap(1920, 1080, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))

    # Draw translucent dark lower-third box (x=110..1810, y=932..1050)
    $boxX = 100
    $boxY = 930
    $boxW = 1720
    $boxH = 122
    $bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(215, 12, 18, 28))
    $g.FillRectangle($bgBrush, $boxX, $boxY, $boxW, $boxH)

    # Top accent bar color by speaker role
    if ($item.role -eq "head") {
        $accentCol = [System.Drawing.Color]::FromArgb(255, 78, 188, 255) # Cyan for Union Head
    } elseif ($item.role -eq "both") {
        $accentCol = [System.Drawing.Color]::FromArgb(255, 120, 235, 160) # Mint green for both
    } else {
        $accentCol = [System.Drawing.Color]::FromArgb(255, 255, 205, 86) # Warm gold for Representative
    }
    $accentBrush = New-Object System.Drawing.SolidBrush($accentCol)
    $g.FillRectangle($accentBrush, $boxX, $boxY, $boxW, 5)

    # Speaker tag pill
    $spkPath = New-Object System.Drawing.Drawing2D.GraphicsPath
    $spkPath.AddString("【$($item.spk)】", $fontFamily, [int][System.Drawing.FontStyle]::Bold, 24.0, (New-Object System.Drawing.PointF(960, ($boxY + 26))), $sfCenter)
    $penSpk = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(230, 0, 0, 0), 4.0)
    $penSpk.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $g.DrawPath($penSpk, $spkPath)
    $g.FillPath($accentBrush, $spkPath)

    # Main subtitle text (auto-fit font size 36px or 32px for longer lines)
    $txtLen = $item.text.Length
    $fontSize = if ($txtLen -gt 34) { 31.0 } elseif ($txtLen -gt 28) { 34.0 } else { 38.0 }
    $txtPath = New-Object System.Drawing.Drawing2D.GraphicsPath
    $txtPath.AddString($item.text, $fontFamily, [int][System.Drawing.FontStyle]::Bold, $fontSize, (New-Object System.Drawing.PointF(960, ($boxY + 78))), $sfCenter)
    $penTxt = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(245, 0, 0, 0), 6.0)
    $penTxt.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $g.DrawPath($penTxt, $txtPath)
    $whiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $g.FillPath($whiteBrush, $txtPath)

    $bmp.Save($pngPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()

    $sFrame = [int][math]::Round($item.s * 29.97)
    $eFrame = [int][math]::Round($item.e * 29.97)
    $durFrames = [math]::Max(15, ($eFrame - $sFrame))
    $manifest.Add(@{
        id = $id
        png = $pngPath
        start_sec = $item.s
        end_sec = $item.e
        s_frame = $sFrame
        e_frame = $eFrame
        dur_frames = $durFrames
        speaker = $item.spk
        text = $item.text
    })
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$srtContent = ($srtLines -join "`r`n")
[System.IO.File]::WriteAllText((Join-Path $draftDir "PB130002_編集済_FullHD.srt"), $srtContent, $utf8NoBom)
[System.IO.File]::WriteAllText((Join-Path $finalDir "PB130002_編集済_FullHD.srt"), $srtContent, $utf8NoBom)
[System.IO.File]::WriteAllText((Join-Path $hDir "PB130002_編集済_FullHD.srt"), $srtContent, $utf8NoBom)

$jsonContent = ($manifest | ConvertTo-Json -Depth 4)
[System.IO.File]::WriteAllText((Join-Path $draftDir "subtitles_manifest.json"), $jsonContent, $utf8NoBom)
Write-Output "Generated $($subs.Count) telop PNGs and SRT files!"
