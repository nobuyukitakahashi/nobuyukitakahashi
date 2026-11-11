$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$draftDir = $PSScriptRoot
$finalDir = Join-Path (Split-Path $draftDir -Parent) "final_outputs"

# Find Edge or Chrome executable
$browser = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $browser)) {
    $browser = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}
if (-not (Test-Path $browser)) {
    $browser = "C:\Program Files\Google\Chrome\Application\chrome.exe"
}
Write-Host "Using browser: $browser"

$tmpDir = Join-Path $env:TEMP "cvn_logo_render"
$userData = Join-Path $env:TEMP "edge_headless_profile"
if (-not (Test-Path $tmpDir)) { New-Item -ItemType Directory -Path $tmpDir | Out-Null }

# Render each individual SVG to high-res PNG (1600x400)
foreach ($id in @("1A", "1B", "2A", "2B", "3A", "3B")) {
    $svgContent = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_$id.svg"), $utf8NoBom)
    $html = @"
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1600px; height: 420px;
    background: #FFFFFF;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
    font-family: 'Segoe UI', 'Hiragino Sans', 'Meiryo', sans-serif;
  }
  .wrap {
    width: 1520px; height: 360px;
    border: 1px solid #E6F0EC;
    border-radius: 16px;
    background: #FFFFFF;
    display: flex; align-items: center; justify-content: center;
    padding: 24px 40px;
    position: relative;
  }
  .badge {
    position: absolute; top: 14px; left: 20px;
    font-size: 13px; font-weight: 700; color: #00a273;
    letter-spacing: 0.06em;
    background: #E8F7F2; padding: 4px 12px; border-radius: 99px;
  }
  .cmyk {
    position: absolute; bottom: 12px; right: 20px;
    font-size: 12px; color: #647D75; font-family: Consolas, monospace;
  }
  svg { max-width: 1400px; max-height: 270px; width: auto; height: auto; }
</style>
</head>
<body>
  <div class="wrap">
    <div class="badge">PROPOSAL $id</div>
    $svgContent
    <div class="cmyk">Primary: CMYK C90 M0 Y70 K0 (#00a273)</div>
  </div>
</body>
</html>
"@
    $tmpHtml = Join-Path $tmpDir "render_$id.html"
    $tmpPng  = Join-Path $tmpDir "logo_$id.png"
    $outPng  = Join-Path $finalDir "logo_$id.png"
    $prof    = Join-Path $tmpDir "prof_$id"
    if (Test-Path $tmpPng) { Remove-Item $tmpPng -Force }
    [System.IO.File]::WriteAllText($tmpHtml, $html, $utf8NoBom)
    $p = Start-Process -FilePath $browser -ArgumentList @("--headless=new","--disable-gpu","--no-sandbox","--user-data-dir=$prof","--hide-scrollbars","--window-size=1600,420","--screenshot=$tmpPng",$tmpHtml) -Wait -PassThru -WindowStyle Hidden
    Copy-Item -Path $tmpPng -Destination $outPng -Force
    Write-Host "Rendered $outPng (exists: $(Test-Path $outPng))"
}

# Build 6-proposals overview board (1920x1320)
$s1A = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_1A.svg"), $utf8NoBom)
$s1B = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_1B.svg"), $utf8NoBom)
$s2A = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_2A.svg"), $utf8NoBom)
$s2B = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_2B.svg"), $utf8NoBom)
$s3A = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_3A.svg"), $utf8NoBom)
$s3B = [System.IO.File]::ReadAllText((Join-Path $finalDir "logo_3B.svg"), $utf8NoBom)

$boardHtml = @"
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1600px; height: 980px;
    background: #F4F8F6;
    font-family: 'Segoe UI', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
    color: #142E28;
    padding: 26px 36px;
    overflow: hidden;
  }
  header {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 18px; padding-bottom: 12px;
    border-bottom: 2px solid #00a273;
  }
  header h1 { font-size: 22px; font-weight: 800; color: #142E28; letter-spacing: 0.02em; }
  header h1 span { color: #00a273; }
  header .meta { font-size: 12px; color: #3D5A52; font-weight: 600; text-align: right; }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: repeat(3, 272px);
    gap: 16px 24px;
  }
  .card {
    background: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #D5E6DF;
    box-shadow: 0 4px 12px rgba(0, 162, 115, 0.05);
    padding: 14px 22px;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .card-head {
    display: flex; justify-content: space-between; align-items: center;
  }
  .tag {
    background: #00a273; color: #FFFFFF;
    font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px;
  }
  .cat {
    font-size: 12px; font-weight: 700; color: #00a273;
    background: #E8F7F2; padding: 3px 10px; border-radius: 99px;
  }
  .logo-box {
    flex: 1; display: flex; align-items: center; justify-content: center;
    padding: 6px;
  }
  .logo-box svg { max-width: 680px; max-height: 150px; width: auto; height: auto; }
  .card-foot {
    border-top: 1px solid #EEF5F2; padding-top: 8px;
    display: flex; justify-content: space-between; align-items: center;
    font-size: 11.5px; color: #4A665E;
  }
  .card-foot strong { color: #142E28; font-size: 12.5px; }
</style>
</head>
<body>
  <header>
    <div>
      <h1>株式会社cvn 新ブランド <span>「cvn プラスモバイル」</span> ロゴデザイン6案一覧比較ボード</h1>
    </div>
    <div class="meta">
      Primary Color: <strong>CMYK C:90% M:0% Y:70% K:0%</strong> (Web HEX: <strong>#00a273</strong>) ｜ Design Concept: Modern, Minimal &amp; Geometric Round
    </div>
  </header>
  <div class="grid">
    <div class="card">
      <div class="card-head"><span class="tag">案 1-A</span><span class="cat">① 日本語表記「プラスモバイル」｜Horizontal Minimal</span></div>
      <div class="logo-box">$s1A</div>
      <div class="card-foot"><strong>ミニマル・ラウンド・ホリゾンタル（1行横並び）</strong><span>CMYK: C90 M0 Y70 K0 単色 ｜ Webヘッダー・TVCM・チラシ向け</span></div>
    </div>
    <div class="card">
      <div class="card-head"><span class="tag">案 1-B</span><span class="cat">① 日本語表記「プラスモバイル」｜Architectural 2-Tier</span></div>
      <div class="logo-box">$s1B</div>
      <div class="card-foot"><strong>アーキテクチャル・2段スタック（スレート2トーン）</strong><span>C90 M0 Y70 K0 × C85 M45 Y65 K70 ｜ 店舗看板・パンフ・名刺向け</span></div>
    </div>
    <div class="card">
      <div class="card-head"><span class="tag">案 2-A</span><span class="cat">② 英語フル表記「plus mobile」｜Origin Grid 2-Tier</span></div>
      <div class="logo-box">$s2A</div>
      <div class="card-foot"><strong>オリジン・2段グリッド（原画タグライン構造完全継承）</strong><span>CMYK: C90 M0 Y70 K0 単色 ｜ CI基準ロゴ・コーポレート・SIM台紙向け</span></div>
    </div>
    <div class="card">
      <div class="card-head"><span class="tag">案 2-B</span><span class="cat">② 英語フル表記「plus mobile」｜Modern Weight Contrast</span></div>
      <div class="logo-box">$s2B</div>
      <div class="card-foot"><strong>モダン・ウェイトコントラスト（1行スマート欧文）</strong><span>CMYK: C90 M0 Y70 K0 単色 ｜ スマホUI・マイページ・eSIM画面向け</span></div>
    </div>
    <div class="card">
      <div class="card-head"><span class="tag">案 3-A</span><span class="cat">③ 記号＋英語表記「+mobile」｜Geometric Capsule Plus</span></div>
      <div class="logo-box">$s3A</div>
      <div class="card-foot"><strong>ジオメトリック・カプセルプラス（正十字ロックアップ）</strong><span>CMYK: C90 M0 Y70 K0 単色 ｜ セット割訴求・SIMパッケージ・Web広告向け</span></div>
    </div>
    <div class="card">
      <div class="card-head"><span class="tag">案 3-B</span><span class="cat">③ 記号＋英語表記「+mobile」｜Compact Pill Unit</span></div>
      <div class="logo-box">$s3B</div>
      <div class="card-foot"><strong>コンパクト・ピルユニット（カプセルバッジ＋カナ併記）</strong><span>C90 M0 Y70 K0 × 白抜き × スレート ｜ アプリアイコン・SNS・店頭バッジ向け</span></div>
    </div>
  </div>
</body>
</html>
"@
$boardHtmlPath = Join-Path $tmpDir "render_board.html"
$tmpBoardPng   = Join-Path $tmpDir "logo_6proposals_board.png"
$boardPngPath  = Join-Path $finalDir "logo_6proposals_board.png"
$profBoard     = Join-Path $tmpDir "prof_board"
if (Test-Path $tmpBoardPng) { Remove-Item $tmpBoardPng -Force }
[System.IO.File]::WriteAllText($boardHtmlPath, $boardHtml, $utf8NoBom)
$p = Start-Process -FilePath $browser -ArgumentList @("--headless=new","--disable-gpu","--no-sandbox","--user-data-dir=$profBoard","--hide-scrollbars","--window-size=1600,980","--screenshot=$tmpBoardPng",$boardHtmlPath) -Wait -PassThru -WindowStyle Hidden
Copy-Item -Path $tmpBoardPng -Destination $boardPngPath -Force
Write-Host "Rendered $boardPngPath (exists: $(Test-Path $boardPngPath))"
