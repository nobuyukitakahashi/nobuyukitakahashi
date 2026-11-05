# Generate 6 SVG logos for cvn plus mobile (Refined v3: 100% #00a273, perfected 's' and Katakana typography)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$draftDir = $PSScriptRoot
$finalDir = Join-Path (Split-Path $draftDir -Parent) "final_outputs"
if (-not (Test-Path $finalDir)) { New-Item -ItemType Directory -Path $finalDir | Out-Null }

$pathsJson = [System.IO.File]::ReadAllText((Join-Path $draftDir "cvn_paths.json"), $utf8NoBom) | ConvertFrom-Json
$cPath = $pathsJson.c
$vPath = $pathsJson.v
$nPath = $pathsJson.n

$primary = "#00a273"   # CMYK: C90 M0 Y70 K0 (Corporate Emerald Green)
$white   = "#FFFFFF"   # CMYK: C0 M0 Y0 K0 (Pure White)

$cvnGroup = @"
  <!-- Parent Brand Logo: cvn (Original Vector Contour, CMYK C90 M0 Y70 K0 / #00a273) -->
  <g id="cvn-mark" fill="$primary">
    <path d="$cPath" />
    <path d="$vPath" />
    <path d="$nPath" />
  </g>
"@

# ==============================================================================
# Helper: Refined Corporate Rounded Geometric Katakana "プラスモバイル" (v3)
# Engineered with architectural proportions, wide inner counters, and pure
# capsule terminals (stroke-linecap="round" stroke-linejoin="round").
# Local coordinate system: Y=10..96 (height 86), total width X=0..820
# ==============================================================================
function Get-KatakanaPlusMobile($xOffset, $yOffset, $scale, $color, $sw) {
    $r = [math]::Round($sw * 0.62, 1)
    $rStroke = [math]::Round($sw * 0.48, 1)
    $dakSw = [math]::Round($sw * 0.62, 1)
    return @"
  <g transform="translate($xOffset, $yOffset) scale($scale)" fill="none" stroke="$color" stroke-width="$sw" stroke-linecap="round" stroke-linejoin="round">
    <!-- プ: clean horizontal top bar + smooth cubic sweep + precision circular handakuten -->
    <path d="M 10,24 H 74 C 74,58 54,84 18,94" />
    <circle cx="88" cy="15" r="$r" fill="none" stroke="$color" stroke-width="$rStroke" />
    <!-- ラ: balanced upper bar + wide lower bar with smooth architectural sweep -->
    <path d="M 130,20 H 192" />
    <path d="M 120,45 H 200 C 198,74 176,90 138,95" />
    <!-- ス: wide horizontal bar + smooth diagonal sweep + tangent right leg -->
    <path d="M 236,23 H 302 C 292,55 266,79 230,94" />
    <path d="M 273,58 C 287,70 301,82 313,94" />
    <!-- モ: generous vertical spacing between horizontal bars + wide rounded bottom counter -->
    <path d="M 356,24 H 428" />
    <path d="M 348,54 H 436" />
    <path d="M 382,24 V 76 C 382,89 390,94 406,94 H 432" />
    <!-- バ: symmetrical outward/inward curved strokes + neatly aligned dakuten ticks -->
    <path d="M 484,32 C 479,56 470,76 456,92" />
    <path d="M 520,32 C 532,54 543,74 552,92" />
    <path d="M 544,13 L 551,26" stroke-width="$dakSw" />
    <path d="M 559,9 L 566,22" stroke-width="$dakSw" />
    <!-- イ: gentle diagonal sweep + firm vertical stem centered in the counter -->
    <path d="M 656,16 C 636,38 608,55 580,67" />
    <path d="M 626,43 V 95" />
    <!-- ル: poised left curved stem + right vertical stem with clean 45-deg upward sweep -->
    <path d="M 702,22 V 52 C 702,72 693,85 680,94" />
    <path d="M 738,18 V 82 C 738,91 743,94 752,94 C 767,94 782,81 792,62" />
  </g>
"@
}

function Get-KatakanaStacked($xOffset, $yOffset1, $yOffset2, $scale1, $scale2, $color, $sw1, $sw2) {
    $r1 = [math]::Round($sw1 * 0.62, 1)
    $rStroke1 = [math]::Round($sw1 * 0.48, 1)
    $dakSw2 = [math]::Round($sw2 * 0.62, 1)
    return @"
  <!-- Row 1: プラス (Primary #00a273) -->
  <g transform="translate($xOffset, $yOffset1) scale($scale1)" fill="none" stroke="$color" stroke-width="$sw1" stroke-linecap="round" stroke-linejoin="round">
    <!-- プ -->
    <path d="M 10,24 H 74 C 74,58 54,84 18,94" />
    <circle cx="88" cy="15" r="$r1" fill="none" stroke="$color" stroke-width="$rStroke1" />
    <!-- ラ -->
    <path d="M 130,20 H 192" />
    <path d="M 120,45 H 200 C 198,74 176,90 138,95" />
    <!-- ス -->
    <path d="M 236,23 H 302 C 292,55 266,79 230,94" />
    <path d="M 273,58 C 287,70 301,82 313,94" />
  </g>
  <!-- Row 2: モバイル (Primary #00a273) -->
  <g transform="translate($xOffset, $yOffset2) scale($scale2)" fill="none" stroke="$color" stroke-width="$sw2" stroke-linecap="round" stroke-linejoin="round">
    <!-- モ -->
    <path d="M 10,24 H 82" />
    <path d="M 2,54 H 90" />
    <path d="M 36,24 V 76 C 36,89 44,94 60,94 H 86" />
    <!-- バ -->
    <path d="M 138,32 C 133,56 124,76 110,92" />
    <path d="M 174,32 C 186,54 197,74 206,92" />
    <path d="M 198,13 L 205,26" stroke-width="$dakSw2" />
    <path d="M 213,9 L 220,22" stroke-width="$dakSw2" />
    <!-- イ -->
    <path d="M 310,16 C 290,38 262,55 234,67" />
    <path d="M 280,43 V 95" />
    <!-- ル -->
    <path d="M 356,22 V 52 C 356,72 347,85 334,94" />
    <path d="M 392,18 V 82 C 392,91 397,94 406,94 C 421,94 436,81 446,62" />
  </g>
"@
}

# ==============================================================================
# Helper: English Custom Geometric Round Letters ("plus" & "mobile") (v3)
# Refined 's' using symmetric C1-continuous circular-arc cubic Beziers matching
# the exact 's' in original tagline "cast / vision".
# ==============================================================================
function Get-EnglishWordPlus($xOffset, $yOffset, $scale, $color, $sw) {
    return @"
  <g transform="translate($xOffset, $yOffset) scale($scale)" fill="none" stroke="$color" stroke-width="$sw" stroke-linecap="round" stroke-linejoin="round">
    <!-- p: stem at x=10 (38..122) + tangential circular bowl at cx=38, cy=67, r=28 -->
    <path d="M 10,38 V 122" />
    <circle cx="38" cy="67" r="28" />
    <!-- l: clean vertical capsule stem at x=94 -->
    <path d="M 94,10 V 96" />
    <!-- u: spurless inverted-n arch (exact DNA of cvn's 'n' rotated 180 deg) -->
    <path d="M 124,38 V 70 C 124,86 136,96 152,96 C 168,96 180,86 180,70 V 38" />
    <!-- s: C1-continuous circular-arc geometric S matching original 'cast / vision' -->
    <path d="M 245,49 C 242,41 235,38 226,38 C 214,38 206,44 206,52 C 206,61 214,64 226,67 C 238,70 247,73 247,82 C 247,91 238,96 226,96 C 216,96 208,92 205,84" />
  </g>
"@
}

function Get-EnglishWordMobile($xOffset, $yOffset, $scale, $color, $sw) {
    $dotR = [math]::Round($sw * 0.58, 1)
    return @"
  <g transform="translate($xOffset, $yOffset) scale($scale)" fill="none" stroke="$color" stroke-width="$sw" stroke-linecap="round" stroke-linejoin="round">
    <!-- m: spurless double arch (exact twin-tunnel continuation of cvn's 'n') -->
    <path d="M 8,96 V 62 C 8,46 19,38 34,38 C 49,38 60,46 60,62 V 96" />
    <path d="M 60,62 C 60,46 71,38 86,38 C 101,38 112,46 112,62 V 96" />
    <!-- o: pure geometric circle -->
    <circle cx="168" cy="67" r="29" />
    <!-- b: ascender stem at x=226 (10..96) + tangential circular bowl at cx=254, cy=67, r=28 -->
    <path d="M 226,10 V 96" />
    <circle cx="254" cy="67" r="28" />
    <!-- i: capsule stem + circular dot -->
    <path d="M 310,40 V 96" />
    <circle cx="310" cy="14" r="$dotR" fill="$color" stroke="none" />
    <!-- l: clean vertical capsule stem -->
    <path d="M 340,10 V 96" />
    <!-- e: rounded geometric e with horizontal crossbar and wide aperture like cvn's 'c' -->
    <path d="M 370,66 H 424 C 424,48 411,38 396,38 C 379,38 367,50 367,67 C 367,84 380,96 398,96 C 410,96 418,91 423,85" />
  </g>
"@
}

# ==============================================================================
# PROPOSAL 1-A: cvn プラスモバイル (Horizontal Minimal 1-Line, 100% #00a273)
# ==============================================================================
$svg1A = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1740 316" width="1740" height="316">
  <rect x="-45" y="-45" width="1740" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- Gutter: X=660..726 (66px = 1x cvn stem width) -->
$(Get-KatakanaPlusMobile 726 52 1.13 $primary 17.5)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_1A.svg"), $svg1A, $utf8NoBom)

# ==============================================================================
# PROPOSAL 1-B: cvn | プラス / モバイル (Architectural 2-Tier Lockup, 100% #00a273)
# ==============================================================================
$svg1B = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1260 316" width="1260" height="316">
  <rect x="-45" y="-45" width="1260" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- Architectural Capsule Divider at X=702 (100% #00a273) -->
  <line x1="702" y1="12" x2="702" y2="212" stroke="$primary" stroke-width="10" stroke-linecap="round" />
  <!-- 2-Tier Stacked Katakana in 100% Primary #00a273 aligned to cvn Top & Bottom -->
$(Get-KatakanaStacked 742 0 116 0.96 0.96 $primary 16.0 17.0)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_1B.svg"), $svg1B, $utf8NoBom)

# ==============================================================================
# PROPOSAL 2-A: cvn plus / mobile (Origin Grid 2-Tier Stack, 100% #00a273)
# ==============================================================================
$svg2A = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1240 316" width="1240" height="316">
  <rect x="-45" y="-45" width="1240" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- Origin Grid 2-Tier Stack at X=721, matching cvn height (Y=0..223) -->
$(Get-EnglishWordPlus 721 -2 0.94 $primary 17.5)
$(Get-EnglishWordMobile 721 118 0.94 $primary 17.5)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_2A.svg"), $svg2A, $utf8NoBom)

# ==============================================================================
# PROPOSAL 2-B: cvn plus mobile (Modern 1-Line Weight Contrast, 100% #00a273)
# ==============================================================================
$svg2B = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1660 316" width="1660" height="316">
  <rect x="-45" y="-45" width="1660" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- 1-Line Weight Contrast: 'plus' (Medium Round) + 'mobile' (Bold Round) aligned on baseline -->
$(Get-EnglishWordPlus 726 54 1.18 $primary 13.0)
$(Get-EnglishWordMobile 1062 54 1.18 $primary 20.0)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_2B.svg"), $svg2B, $utf8NoBom)

# ==============================================================================
# PROPOSAL 3-A: cvn + mobile (Geometric Capsule Plus Lockup, 100% #00a273)
# ==============================================================================
$svg3A = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1540 316" width="1540" height="316">
  <rect x="-45" y="-45" width="1540" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- Geometric Capsule Cross '+' (Center X=784, Y=112, arm length=124, stroke=36) -->
  <g stroke="$primary" stroke-width="36" stroke-linecap="round">
    <line x1="722" y1="112" x2="846" y2="112" />
    <line x1="784" y1="50"  x2="784" y2="174" />
  </g>
  <!-- 'mobile' in matching bold geometric round -->
$(Get-EnglishWordMobile 896 44 1.25 $primary 19.0)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_3A.svg"), $svg3A, $utf8NoBom)

# ==============================================================================
# PROPOSAL 3-B: cvn [+mobile] (Compact Pill Unit + Kana Sub-label, 100% #00a273 & White)
# ==============================================================================
$svg3B = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -45 1440 316" width="1440" height="316">
  <rect x="-45" y="-45" width="1440" height="316" fill="#FFFFFF" />
$cvnGroup
  <!-- Modern Capsule Pill Container for '+mobile' (X=716..1336, Y=4..166, rx=81, 100% #00a273) -->
  <rect x="716" y="4" width="620" height="162" rx="81" fill="$primary" />
  <!-- White Capsule '+' inside Pill -->
  <g stroke="$white" stroke-width="22" stroke-linecap="round">
    <line x1="766" y1="85" x2="838" y2="85" />
    <line x1="802" y1="49" x2="802" y2="121" />
  </g>
  <!-- White 'mobile' tightly locked with '+' inside Pill -->
$(Get-EnglishWordMobile 864 24 0.96 $white 18.0)
  <!-- Clean Japanese Sub-label 'プラスモバイル' in 100% Primary #00a273 aligned below the pill -->
$(Get-KatakanaPlusMobile 852 180 0.43 $primary 18.0)
</svg>
"@
[System.IO.File]::WriteAllText((Join-Path $finalDir "logo_3B.svg"), $svg3B, $utf8NoBom)

Write-Host "Regenerated all 6 SVG files (v3 - 100% #00a273) in $finalDir"
