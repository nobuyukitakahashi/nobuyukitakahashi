const fs = require('fs');
const path = require('path');
const { chromium } = require('C:/Users/nobuy/AppData/Roaming/npm/node_modules/notebooklm-mcp/node_modules/patchright');

const ASSETS_DIR = path.resolve(__dirname, '../../../00_COO/projects/kinoshita_kensetsu/sources/extracted_assets');
const DRAFTS_DIR = __dirname;
const FINAL_DIR = path.resolve(__dirname, '../final_outputs');

function getAssetDataUrl(filename) {
  const filePath = path.join(ASSETS_DIR, filename);
  const buf = fs.readFileSync(filePath);
  return `data:image/jpeg;base64,${buf.toString('base64')}`;
}

const assets = {
  cm1_girl: getAssetDataUrl('img_obj4_1920x1080.jpg'),
  cover_team: getAssetDataUrl('img_obj11_2079x1309.jpg'),
  logo_sm: getAssetDataUrl('img_obj36_300x300.jpg'),
  logo_lg: getAssetDataUrl('img_obj267_434x434.jpg'),
  hq_bldg: getAssetDataUrl('img_obj35_789x943.jpg'),
  p04_bldg: getAssetDataUrl('img_obj44_1330x2250.jpg'),
  p05_bldg: getAssetDataUrl('img_obj50_1195x2250.jpg'),
  p07_night: getAssetDataUrl('img_obj59_1980x2250.jpg'),
  p08_nakata: getAssetDataUrl('img_obj187_762x911.jpg'),
  proj01: getAssetDataUrl('img_obj63_1680x2250.jpg'),
  proj02: getAssetDataUrl('img_obj73_832x1114.jpg'),
  proj03: getAssetDataUrl('img_obj85_710x951.jpg'),
  proj04: getAssetDataUrl('img_obj95_883x1183.jpg'),
  proj05: getAssetDataUrl('img_obj107_853x1142.jpg'),
  proj06: getAssetDataUrl('img_obj117_573x767.jpg'),
  p15_nagoya: getAssetDataUrl('img_obj141_766x1165.jpg'),
  p16_aoi: getAssetDataUrl('img_obj151_939x1034.jpg'),
  p17_ic: getAssetDataUrl('img_obj161_1362x1500.jpg'),
  voice_hk: getAssetDataUrl('img_obj173_663x883.jpg'),
  voice_rk1: getAssetDataUrl('img_obj174_663x883.jpg'),
  voice_rk2: getAssetDataUrl('img_obj175_663x883.jpg'),
  voice_sk: getAssetDataUrl('img_obj179_1259x1679.jpg'),
  voice_ak: getAssetDataUrl('img_obj183_1259x1679.jpg'),
  cm2_bridge: getAssetDataUrl('img_obj129_1920x1080.jpg'),
  cm3_ojt: getAssetDataUrl('img_obj135_1920x1080.jpg'),
  p23_tunnel: getAssetDataUrl('img_obj215_666x960.jpg'),
  cert_kenko: getAssetDataUrl('img_obj222_980x269.jpg'),
  cert_kosodate: getAssetDataUrl('img_obj225_270x270.jpg'),
  cert_iki1: getAssetDataUrl('img_obj228_310x344.jpg'),
  cert_iki2: getAssetDataUrl('img_obj229_337x344.jpg'),
  p28_bldg: getAssetDataUrl('img_obj241_987x1609.jpg'),
  char1: getAssetDataUrl('img_obj262_406x1200.jpg'),
  char2: getAssetDataUrl('img_obj263_422x1198.jpg'),
  char3: getAssetDataUrl('img_obj264_456x1200.jpg'),
  char4: getAssetDataUrl('img_obj265_341x1198.jpg'),
  char5: getAssetDataUrl('img_obj266_396x1200.jpg'),
};

function buildPitchbookHtml() {
  const projectSlide = (pageNo, projNum, name, loc, date, struct, imgSrc, imgSide, extraNote = '名古屋支店 施工実績より') => {
    const isLeftImg = imgSide === 'left';
    const textBlock = `
      <div class="proj-text ${isLeftImg ? 'pad-right-side' : 'pad-left-side'}">
        <div class="en-label">PROJECT ${projNum}</div>
        <div class="proj-title">プレサンス<br>${name}</div>
        <div class="proj-sub">${extraNote}</div>
        <div class="proj-table">
          <div class="proj-row">
            <div class="proj-th">所在</div>
            <div class="proj-td">${loc}</div>
          </div>
          <div class="proj-row">
            <div class="proj-th">完成</div>
            <div class="proj-td">${date}</div>
          </div>
          <div class="proj-row">
            <div class="proj-th">構造</div>
            <div class="proj-td">${struct}</div>
          </div>
        </div>
      </div>
    `;
    const imgBlock = `
      <div class="proj-img-wrap">
        <img src="${imgSrc}" class="cover-img" data-max="820" />
      </div>
    `;
    return `
      <section class="slide" id="page-${pageNo}">
        <div class="chap-header ${!isLeftImg ? 'on-photo' : ''}">
          <span class="chap-num">03 / 07</span>
          <span class="chap-name">名古屋の高層マンションと地域インフラ</span>
        </div>
        <div class="split-layout ${isLeftImg ? 'img-left' : 'img-right'}">
          ${isLeftImg ? imgBlock + textBlock : textBlock + imgBlock}
        </div>
        <div class="page-num-badge ${!isLeftImg ? 'left-bottom' : 'right-bottom'}">P.${String(pageNo).padStart(2, '0')}</div>
      </section>
    `;
  };

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>木下建設株式会社 2027採用ピッチブック</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --red: #D70015;
    --red-dark: #B00010;
    --black: #181818;
    --gray-dark: #444444;
    --gray-mid: #777777;
    --line: #CCCCCC;
    --bg: #FFFFFF;
    --serif: 'Noto Serif JP', serif;
    --sans: 'Noto Sans JP', sans-serif;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  @page {
    size: 1920px 1080px;
    margin: 0;
  }
  body {
    width: 1920px;
    margin: 0;
    padding: 0;
    background: #FFFFFF;
    color: var(--black);
    font-family: var(--serif);
  }
  .slide {
    position: relative;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    background: #FFFFFF;
    page-break-after: always;
    break-after: page;
  }
  .slide:last-child {
    page-break-after: auto;
    break-after: auto;
  }
  /* Common Header - solid background on photo to prevent Skia PDF FlateDecode rasterization */
  .chap-header {
    position: absolute;
    top: 48px;
    right: 84px;
    z-index: 20;
    display: flex;
    align-items: baseline;
    gap: 22px;
    padding-bottom: 14px;
    border-bottom: 1.5px solid #333;
    font-family: var(--serif);
    color: var(--black);
  }
  .chap-header.on-photo {
    top: 32px;
    right: 0;
    width: 33.5%;
    padding: 18px 56px 18px 36px;
    background: #1E2530;
    color: #FFFFFF;
    border-bottom: 2px solid #D70015;
    justify-content: flex-end;
  }
  .chap-header.on-photo-wide {
    top: 32px;
    right: 0;
    width: 42%;
    padding: 18px 64px 18px 36px;
    background: #1E2530;
    color: #FFFFFF;
    border-bottom: 2px solid #D70015;
    justify-content: flex-end;
  }
  .chap-num {
    font-size: 26px;
    font-weight: 600;
    letter-spacing: 0.05em;
  }
  .chap-name {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 0.03em;
  }
  .en-label {
    font-family: var(--serif);
    font-size: 23px;
    letter-spacing: 0.22em;
    color: #333333;
    text-transform: uppercase;
    margin-bottom: 24px;
  }
  .page-num-badge {
    position: absolute;
    bottom: 26px;
    font-family: var(--sans);
    font-size: 16px;
    font-weight: 500;
    color: #888888;
    letter-spacing: 0.1em;
    z-index: 25;
  }
  .page-num-badge.right-bottom { right: 48px; }
  .page-num-badge.left-bottom { left: 96px; }

  /* Project split layout */
  .split-layout {
    display: flex;
    width: 100%;
    height: 100%;
  }
  .split-layout.img-left .proj-img-wrap { width: 42%; height: 100%; }
  .split-layout.img-left .proj-text { width: 58%; height: 100%; }
  .split-layout.img-right .proj-text { width: 58%; height: 100%; }
  .split-layout.img-right .proj-img-wrap { width: 42%; height: 100%; }
  .cover-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .proj-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .pad-right-side { padding: 80px 96px 60px 96px; }
  .pad-left-side { padding: 80px 96px 60px 96px; }
  .proj-title {
    font-family: var(--serif);
    font-size: 74px;
    font-weight: 700;
    color: var(--red);
    line-height: 1.24;
    margin-bottom: 18px;
  }
  .proj-sub {
    font-size: 32px;
    color: var(--black);
    margin-bottom: 44px;
  }
  .proj-table {
    border-top: 2px solid #222;
    width: 100%;
  }
  .proj-row {
    display: flex;
    align-items: center;
    padding: 32px 0;
    border-bottom: 1px solid #CCCCCC;
  }
  .proj-th {
    width: 340px;
    font-size: 40px;
    font-weight: 600;
    color: var(--black);
  }
  .proj-td {
    flex: 1;
    font-size: 56px;
    font-weight: 700;
    color: var(--red);
  }
</style>
</head>
<body>

<!-- ==================== P.01 表紙 ==================== -->
<section class="slide" id="page-1">
  <div class="chap-header">
    <span class="chap-num">01 / 07</span>
    <span class="chap-name">ごあいさつ</span>
  </div>
  <div style="position:absolute; top:82px; left:98px; width:840px; border-bottom:1.5px solid #444; padding-bottom:24px;">
    <div style="font-size:23px; letter-spacing:0.25em; color:#333;">KINOSHITA KENSETSU — RECRUIT 2027</div>
  </div>
  <div style="position:absolute; top:198px; left:98px; z-index:10; width:820px;">
    <div style="font-size:70px; font-weight:700; color:var(--red); line-height:1.22; margin-bottom:6px;">
      あなたの図面が
    </div>
    <div style="font-size:164px; font-weight:700; color:var(--red); line-height:1.06; letter-spacing:0.02em; margin-bottom:14px;">
      建つ街、
    </div>
    <div style="font-size:66px; font-weight:700; color:var(--red); letter-spacing:0.03em; margin-bottom:36px;">
      未来をつなぐ道。
    </div>
    <div style="font-size:38px; font-weight:700; color:var(--black); line-height:1.52; margin-bottom:38px;">
      愛知工業大学（建築学科・社会基盤学科）・<br>愛工大名電高のみなさんへ
    </div>
    <div style="width:780px; border-top:1.5px solid #555; padding-top:26px; display:flex; align-items:center; gap:28px;">
      <img src="${assets.logo_sm}" data-max="240" style="width:120px; height:120px; object-fit:contain;" />
      <div>
        <div style="font-family:var(--sans); font-size:22px; font-weight:700; color:var(--black); margin-bottom:10px; white-space:nowrap;">
          木下建設株式会社（創業1913年・名古屋支店／長野県飯田市本社）
        </div>
        <div style="display:inline-block; background:#FFF0F2; border:1.5px solid var(--red); color:var(--red); font-family:var(--sans); font-size:18px; font-weight:700; padding:7px 16px; border-radius:6px; white-space:nowrap;">
          ★ 愛知工業大学出身の先輩 2名活躍中！ ／ 名古屋支店 高層マンション施工 29件
        </div>
      </div>
    </div>
  </div>
  <img src="${assets.cover_team}" data-max="1000" style="position:absolute; right:0; bottom:0; width:1010px; height:640px; object-fit:cover; object-position:top center; z-index:5;" />
  <div class="page-num-badge left-bottom">P.01</div>
</section>

<!-- ==================== P.02 目次 (CONTENTS) ==================== -->
<section class="slide" id="page-2">
  <div class="chap-header">
    <span class="chap-num">01 / 07</span>
    <span class="chap-name">ごあいさつ</span>
  </div>
  <div style="display:flex; width:100%; height:100%; padding:84px 96px 64px 98px;">
    <div style="width:36%; padding-right:60px;">
      <div class="en-label">CONTENTS</div>
      <div style="font-size:88px; font-weight:700; color:var(--red); line-height:1.25; margin-top:40px; margin-bottom:44px;">
        会社案内<br>の流れ
      </div>
      <div style="width:84px; height:10px; background:var(--red); margin-bottom:36px;"></div>
      <div style="font-size:38px; font-weight:600; color:var(--black); margin-bottom:24px;">
        全 7 章・全 28 ページ
      </div>
      <div style="font-family:var(--sans); font-size:21px; color:#444; line-height:1.75; background:#F8F8F8; padding:24px; border-left:5px solid var(--red);">
        <strong>【愛名会 2027企業案内 特別編集版】</strong><br>
        愛知工業大学 工学部（建築学科・社会基盤学科）および愛工大名電高（科学技術科）のみなさんに向けて、名古屋支店の高層マンション実績や大規模インフラ土木、働き方・待遇をまとめました。
      </div>
    </div>
    <div style="width:64%; display:flex; flex-direction:column; justify-content:center; padding-top:40px;">
      <div style="border-top:2px solid #222;">
        ${[
          ['01', 'ごあいさつ', '愛知工業大学・愛工大名電高のみなさんへ', 'P.03'],
          ['02', '木下建設とは', '創業113年の歴史・数字で見る木下建設・4つの拠点', 'P.04 – P.06'],
          ['03', '名古屋の高層マンションと地域インフラ', '名古屋支店 施工実績29件（PROJECT 01〜06）・名古屋勤務', 'P.07 – P.15'],
          ['04', '仕事と先輩の声', '施工管理の仕事・2025年入社＆女性先輩の声・建設DX', 'P.16 – P.21'],
          ['05', 'お金と安心', '奨学金月2.5万円支援・資格全額負担・初任給28.9万円・認証', 'P.22 – P.25'],
          ['06', '成長の道すじ', '入社1〜2年目の育成ステップ・大規模土木・経営者メッセージ', 'P.26 – P.27'],
          ['07', '応募の案内・お問い合わせ', '5/30(土) 愛名会企業研究会・選考の流れ・名古屋支店連絡先', 'P.28'],
        ].map(([num, title, sub, pg]) => `
          <div style="display:flex; align-items:center; padding:24px 0; border-bottom:1px solid #CCC;">
            <div style="width:110px; font-size:48px; font-weight:700; color:var(--red);">${num}</div>
            <div style="flex:1;">
              <div style="font-size:38px; font-weight:700; color:var(--black); line-height:1.2;">${title}</div>
              <div style="font-family:var(--sans); font-size:19px; color:#555; margin-top:6px;">${sub}</div>
            </div>
            <div style="width:210px; text-align:right; font-size:34px; font-weight:600; color:var(--black);">${pg}</div>
          </div>
        `).join('')}
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.02</div>
</section>

<!-- ==================== P.03 01 ごあいさつ ==================== -->
<section class="slide" id="page-3">
  <div class="chap-header on-photo">
    <span class="chap-num">01 / 07</span>
    <span class="chap-name">ごあいさつ</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:66.5%; height:100%; background:var(--red); color:#FFFFFF; padding:84px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div style="font-size:24px; letter-spacing:0.25em; margin-bottom:80px;">HELLO</div>
      <div style="font-size:104px; font-weight:700; line-height:1.32; margin-bottom:68px;">
        こんにちは、<br>木下建設です。
      </div>
      <div style="width:100%; height:1.5px; background:#FFFFFF; margin-bottom:48px;"></div>
      <div style="font-size:42px; font-weight:600; line-height:1.55; margin-bottom:20px;">
        愛知工業大学（建築学科・社会基盤学科）・<br>愛工大名電高のみなさんへ
      </div>
      <div style="font-size:36px; font-weight:600; margin-bottom:36px;">
        長野県飯田市（本社）＆名古屋支店の総合建設会社
      </div>
      <div style="display:inline-flex; align-items:center; gap:16px; background:#FFFFFF; color:var(--red); padding:14px 28px; border-radius:8px; width:fit-content; font-family:var(--sans); font-size:25px; font-weight:700;">
        <span>★ 愛知工業大学出身の先輩も 2名活躍中！（2026年3月時点）</span>
      </div>
    </div>
    <div style="width:33.5%; height:100%; background:#FFFFFF; display:flex; flex-direction:column;">
      <div style="height:71%; width:100%; overflow:hidden;">
        <img src="${assets.hq_bldg}" data-max="800" class="cover-img" />
      </div>
      <div style="height:29%; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px;">
        <img src="${assets.logo_sm}" data-max="240" style="width:150px; height:150px; object-fit:contain;" />
        <div style="font-family:var(--sans); font-size:18px; color:#555; font-weight:500;">木下建設株式会社 本社社屋</div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.03</div>
</section>

<!-- ==================== P.04 02 木下建設とは① ==================== -->
<section class="slide" id="page-4">
  <div class="chap-header on-photo">
    <span class="chap-num">02 / 07</span>
    <span class="chap-name">木下建設とは</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:66.5%; height:100%; padding:80px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">CHAPTER 02 — ABOUT US</div>
      <div style="font-size:78px; font-weight:700; color:var(--red); margin-top:10px; margin-bottom:0px;">
        1913年 創業
      </div>
      <div style="display:flex; align-items:baseline; gap:44px; margin-bottom:32px;">
        <div style="font-size:340px; font-weight:700; color:var(--red); line-height:0.92; letter-spacing:-0.03em;">113</div>
        <div>
          <div style="font-size:48px; font-weight:700; color:var(--red); margin-bottom:16px;">2026年現在</div>
          <div style="font-size:138px; font-weight:700; color:var(--red); line-height:1;">年目</div>
        </div>
      </div>
      <div style="border-top:2px solid #222; padding-top:34px; display:flex; gap:64px; align-items:baseline;">
        <div style="font-size:48px; font-weight:700; color:var(--black);">大正2年7月2日</div>
        <div style="font-size:48px; font-weight:700; color:var(--black);">長野県百年企業</div>
      </div>
      <div style="font-family:var(--sans); font-size:23px; color:#555; margin-top:20px;">
        「古い伝統・新しい技術」 ― 1世紀を超える信頼の施工力と、最先端の建設DX（i-Construction）で未来を創ります。
      </div>
    </div>
    <div style="width:33.5%; height:100%;">
      <img src="${assets.p04_bldg}" data-max="820" class="cover-img" />
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.04</div>
</section>

<!-- ==================== P.05 02 木下建設とは② ==================== -->
<section class="slide" id="page-5">
  <div class="chap-header on-photo">
    <span class="chap-num">02 / 07</span>
    <span class="chap-name">木下建設とは</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:66.5%; height:100%; padding:76px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">IN NUMBERS</div>
      <div style="font-size:74px; font-weight:700; color:var(--red); margin-bottom:28px;">
        数字で見る木下建設
      </div>
      <div style="border-top:1.5px solid #444; border-bottom:1.5px solid #444;">
        <div style="display:flex; border-bottom:1px solid #CCC;">
          <div style="width:50%; padding:28px 24px 28px 0; border-right:1px solid #888;">
            <div style="display:flex; align-items:baseline; gap:12px;">
              <span style="font-size:128px; font-weight:700; color:var(--red); line-height:1;">131</span>
              <span style="font-size:48px; font-weight:700; color:var(--red);">名</span>
            </div>
            <div style="font-size:36px; font-weight:600; color:var(--black); margin-top:10px;">社員数</div>
            <div style="font-family:var(--sans); font-size:19px; color:#555; margin-top:6px;">
              2026年6月時点（男性115名・女性16名）<br>※2026年10月時点：128名
            </div>
          </div>
          <div style="width:50%; padding:28px 0 28px 40px;">
            <div style="display:flex; align-items:baseline; gap:10px;">
              <span style="font-size:48px; font-weight:700; color:var(--red);">約</span>
              <span style="font-size:120px; font-weight:700; color:var(--red); line-height:1;">82.6</span>
              <span style="font-size:48px; font-weight:700; color:var(--red);">億円</span>
            </div>
            <div style="font-size:36px; font-weight:600; color:var(--black); margin-top:10px;">売上高</div>
            <div style="font-family:var(--sans); font-size:19px; color:#555; margin-top:6px;">
              82億5,998万円（2026年5月期実績）
            </div>
          </div>
        </div>
        <div style="display:flex;">
          <div style="width:50%; padding:28px 24px 28px 0; border-right:1px solid #888;">
            <div style="display:flex; align-items:baseline; gap:12px;">
              <span style="font-size:100px; font-weight:700; color:var(--red); line-height:1.1;">7,500</span>
              <span style="font-size:44px; font-weight:700; color:var(--red);">万円</span>
            </div>
            <div style="font-size:36px; font-weight:600; color:var(--black); margin-top:10px;">資本金</div>
          </div>
          <div style="width:50%; padding:28px 0 28px 40px;">
            <div style="display:flex; align-items:baseline; gap:16px;">
              <span style="font-size:124px; font-weight:700; color:var(--red); line-height:1;">4</span>
              <span style="font-size:48px; font-weight:700; color:var(--red);">拠点</span>
            </div>
            <div style="font-size:36px; font-weight:600; color:var(--black); margin-top:10px;">本社と3つの支店</div>
            <div style="font-family:var(--sans); font-size:19px; color:var(--red); font-weight:700; margin-top:6px;">
              ★ 愛知工業大学出身の先輩 2名在籍（2026年3月時点）
            </div>
          </div>
        </div>
      </div>
      <div style="font-size:26px; color:var(--black); margin-top:26px;">
        社員数 2026年6月時点（10月時点128名） ／ 売上高 2026年5月期実績
      </div>
    </div>
    <div style="width:33.5%; height:100%;">
      <img src="${assets.p05_bldg}" data-max="820" class="cover-img" />
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.05</div>
</section>

<!-- ==================== P.06 02 木下建設とは③ ==================== -->
<section class="slide" id="page-6">
  <div class="chap-header">
    <span class="chap-num">02 / 07</span>
    <span class="chap-name">木下建設とは</span>
  </div>
  <div style="padding:80px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label">FOUR BASES</div>
    <div style="font-size:76px; font-weight:700; color:var(--red); margin-bottom:40px;">
      本社と3つの支店、4つの拠点
    </div>
    <div style="display:flex; flex:1; gap:72px;">
      <div style="width:52%; border-top:1.5px solid #333; border-bottom:1.5px solid #333; position:relative; display:flex; align-items:center; justify-content:center;">
        <svg width="900" height="620" viewBox="0 0 900 620" style="width:100%; height:100%;">
          <line x1="150" y1="140" x2="360" y2="330" stroke="#222" stroke-width="3.5" stroke-dasharray="10,10" />
          <line x1="590" y1="155" x2="360" y2="330" stroke="#222" stroke-width="3.5" stroke-dasharray="10,10" />
          <line x1="155" y1="510" x2="360" y2="330" stroke="#222" stroke-width="3.5" stroke-dasharray="10,10" />
          <circle cx="150" cy="140" r="38" fill="#FFF" stroke="#D70015" stroke-width="8" />
          <text x="210" y="128" font-family="Noto Serif JP" font-size="40" font-weight="700" fill="#D70015">安曇野支店</text>
          <text x="210" y="176" font-family="Noto Serif JP" font-size="32" fill="#181818">安曇野市</text>
          <circle cx="590" cy="155" r="38" fill="#FFF" stroke="#D70015" stroke-width="8" />
          <text x="650" y="140" font-family="Noto Serif JP" font-size="40" font-weight="700" fill="#D70015">甲信支店</text>
          <text x="650" y="188" font-family="Noto Serif JP" font-size="32" fill="#181818">諏訪郡富士見町</text>
          <circle cx="360" cy="330" r="68" fill="#D70015" />
          <text x="455" y="330" font-family="Noto Serif JP" font-size="52" font-weight="700" fill="#D70015">本社</text>
          <text x="455" y="388" font-family="Noto Serif JP" font-size="36" fill="#181818">長野県飯田市</text>
          <circle cx="155" cy="500" r="50" fill="#FFF" stroke="#D70015" stroke-width="9" />
          <text x="235" y="495" font-family="Noto Serif JP" font-size="48" font-weight="700" fill="#D70015">名古屋支店</text>
          <text x="235" y="550" font-family="Noto Serif JP" font-size="34" font-weight="600" fill="#181818">東海地方全域を担当（名古屋市昭和区阿由知通）</text>
        </svg>
      </div>
      <div style="width:48%; display:flex; flex-direction:column; justify-content:center;">
        <div style="width:68px; height:9px; background:var(--red); margin-bottom:24px;"></div>
        <div style="font-size:64px; font-weight:700; color:var(--red); margin-bottom:20px;">建築（建築学科）</div>
        <div style="font-size:36px; line-height:1.6; color:var(--black); padding-bottom:44px; border-bottom:1.5px solid #AAA;">
          都市型高層マンション（名古屋支店29件）・<br>官公庁・学校・病院・福祉施設・<br>オフィスビル・工場・店舗・住宅
        </div>
        <div style="font-size:64px; font-weight:700; color:var(--red); margin-top:44px; margin-bottom:20px;">土木（社会基盤学科）</div>
        <div style="font-size:36px; line-height:1.6; color:var(--black);">
          高速道路・スマートIC・トンネル・高架橋・<br>河川・ダム・リニア関連道路整備事業
        </div>
      </div>
    </div>
    <div style="font-size:21px; letter-spacing:0.2em; color:#333; margin-top:18px;">DIAGRAM — NOT TO SCALE</div>
  </div>
  <div class="page-num-badge right-bottom">P.06</div>
</section>

<!-- ==================== P.07 03 名古屋の空に、残るしごと。 ==================== -->
<section class="slide" id="page-7">
  <div class="chap-header">
    <span class="chap-num">03 / 07</span>
    <span class="chap-name">名古屋の高層マンションと地域インフラ</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:49.5%; height:100%;">
      <img src="${assets.p07_night}" data-max="880" class="cover-img" />
    </div>
    <div style="width:50.5%; height:100%; padding:100px 96px 80px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div style="font-size:150px; font-weight:600; color:var(--red); line-height:1; padding-bottom:28px; border-bottom:1.5px solid #333; margin-bottom:52px;">
        03
      </div>
      <div style="font-size:84px; font-weight:700; color:var(--red); line-height:1.32; margin-bottom:48px;">
        名古屋の空に、<br>残るしごと。
      </div>
      <div style="font-size:38px; line-height:1.75; color:var(--black); margin-bottom:32px;">
        名古屋支店は、<br>
        高層マンションの建設に<br>
        多くの実績があります。
      </div>
      <div style="font-family:var(--sans); font-size:22px; line-height:1.7; color:#444; background:#F8F8F8; padding:22px 26px; border-left:5px solid var(--red);">
        名古屋都心（千種区・昭和区・中区・西区等）のランドマークとなるRC造10〜15階建てマンションを多数施工。さらに各拠点では橋梁・トンネル・スマートIC等の大規模インフラ土木も推進しています。
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.07</div>
</section>

<!-- ==================== P.08 03 名古屋支店の施工実績 29件（旧P.23移動） ==================== -->
<section class="slide" id="page-8">
  <div class="chap-header">
    <span class="chap-num">03 / 07</span>
    <span class="chap-name">名古屋の高層マンションと地域インフラ</span>
  </div>
  <div style="padding:76px 96px 60px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label">TRACK RECORD IN NAGOYA</div>
    <div style="display:flex; flex:1; gap:84px; align-items:center; margin-top:10px;">
      <div style="width:39%; height:840px; display:flex; flex-direction:column;">
        <div style="flex:1; overflow:hidden;">
          <img src="${assets.p08_nakata}" data-max="800" class="cover-img" />
        </div>
        <div style="font-size:26px; color:var(--black); margin-top:16px; white-space:nowrap;">
          プレサンス仲田二丁目（千種区・令和7年9月完成）
        </div>
      </div>
      <div style="width:61%; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:74px; font-weight:700; color:var(--red); padding-bottom:28px; border-bottom:1.5px solid #333; margin-bottom:32px;">
          名古屋支店の施工実績
        </div>
        <div style="display:flex; align-items:baseline; gap:36px; padding-bottom:36px; border-bottom:1px solid #CCC;">
          <div style="font-size:190px; font-weight:700; color:var(--red); line-height:0.95;">29</div>
          <div style="font-size:72px; font-weight:700; color:var(--red);">件</div>
          <div style="font-size:36px; color:var(--black); line-height:1.45; margin-left:16px;">
            平成26年〜令和7年に<br>完成した工事
          </div>
        </div>
        <div class="proj-table" style="border-top:none;">
          <div class="proj-row">
            <div class="proj-th" style="width:360px;">10階以上</div>
            <div class="proj-td">19 件</div>
          </div>
          <div class="proj-row">
            <div class="proj-th" style="width:360px;">15階建て</div>
            <div class="proj-td">8 件</div>
          </div>
          <div class="proj-row">
            <div class="proj-th" style="width:360px;">最新の完成</div>
            <div class="proj-td">令和7年9月</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.08</div>
</section>

<!-- ==================== P.09〜P.14 PROJECT 01〜06 ==================== -->
${projectSlide(9, '01', '橋本町一丁目', '名古屋市千種区', '平成31年2月', 'RC 13階', assets.proj01, 'left')}
${projectSlide(10, '02', '阿由知通一丁目', '名古屋市昭和区', '令和7年1月', 'RC 15階', assets.proj02, 'right', '名古屋支店 施工実績より（名古屋支店至近）')}
${projectSlide(11, '03', '新栄一丁目', '名古屋市中区', '令和4年8月', 'RC 15階', assets.proj03, 'left')}
${projectSlide(12, '04', '新栄二丁目', '名古屋市中区', '令和4年12月', 'RC 15階', assets.proj04, 'right')}
${projectSlide(13, '05', '押切二丁目', '名古屋市西区', '令和6年9月', 'RC 15階', assets.proj05, 'left')}
${projectSlide(14, '06', '那古野二丁目', '名古屋市西区', '令和7年5月', 'RC 15階', assets.proj06, 'right')}

<!-- ==================== P.15 03 名古屋で、働ける。 ==================== -->
<section class="slide" id="page-15">
  <div class="chap-header on-photo">
    <span class="chap-num">03 / 07</span>
    <span class="chap-name">名古屋の高層マンションと地域インフラ</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:62.5%; height:100%; padding:80px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">WORK IN NAGOYA</div>
      <div style="font-size:132px; font-weight:700; color:var(--red); line-height:1.22; margin-top:16px; margin-bottom:56px;">
        名古屋で、<br>働ける。
      </div>
      <div style="border-top:2px solid #222;">
        <div style="padding:34px 0; border-bottom:1px solid #CCC; font-size:40px; font-weight:700; color:var(--black);">
          勤務地は名古屋支店管内（昭和区阿由知通）となります。
        </div>
        <div style="padding:34px 0; border-bottom:1px solid #CCC; font-size:36px; font-weight:600; color:var(--black); line-height:1.5;">
          本社（長野県飯田市）や各支店での<br>大規模土木・建築勤務ご希望の方も歓迎しております。
        </div>
      </div>
      <div style="font-family:var(--sans); font-size:22px; color:#444; margin-top:28px; line-height:1.7;">
        ● 名古屋支店：〒466-0027 名古屋市昭和区阿由知通1-12-3（地下鉄「御器所駅」徒歩圏内）<br>
        ● 建築学科の方も社会基盤学科（土木）の方も、希望する勤務エリアを尊重して配属を決定します。
      </div>
    </div>
    <div style="width:37.5%; height:100%;">
      <img src="${assets.p15_nagoya}" data-max="820" class="cover-img" />
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.15</div>
</section>

<!-- ==================== P.16 04 仕事と先輩の声① ==================== -->
<section class="slide" id="page-16">
  <div class="chap-header">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:44%; height:100%; display:flex; flex-direction:column;">
      <div style="height:86%; width:100%; overflow:hidden;">
        <img src="${assets.p16_aoi}" data-max="820" class="cover-img" />
      </div>
      <div style="height:14%; padding:22px 44px; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:30px; color:var(--black); line-height:1.45;">
          写真：プレサンス葵一丁目<br>名古屋市中区・令和4年1月完成
        </div>
      </div>
    </div>
    <div style="width:56%; height:100%; padding:84px 96px 60px 84px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">WORK</div>
      <div style="font-size:64px; font-weight:700; color:var(--red); line-height:1.36; margin-bottom:48px;">
        現場を、<br>設計どおりに、<br>安全に進める仕事。
      </div>
      <div style="font-size:38px; color:var(--black); margin-bottom:24px;">
        施工管理の主な仕事
      </div>
      <div class="proj-table">
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:220px;">工程</div>
          <div class="proj-td" style="font-size:48px;">工程表の作成</div>
        </div>
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:220px;">手配</div>
          <div class="proj-td" style="font-size:48px;">下請・資材の手配と検査</div>
        </div>
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:220px;">記録</div>
          <div class="proj-td" style="font-size:48px;">測量・写真での記録管理</div>
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.16</div>
</section>

<!-- ==================== P.17 04 仕事と先輩の声② ==================== -->
<section class="slide" id="page-17">
  <div class="chap-header on-photo-wide">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:55.5%; height:100%; padding:84px 72px 60px 96px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">WORK</div>
      <div style="font-size:64px; font-weight:700; color:var(--red); line-height:1.36; margin-bottom:48px;">
        入社1〜2年目は、<br>先輩のもとで学び、<br>将来は1人で現場へ。
      </div>
      <div style="font-size:38px; color:var(--black); margin-bottom:24px;">
        土木も建築も、仕事の進め方は同じ
      </div>
      <div class="proj-table">
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:200px;">図面</div>
          <div class="proj-td" style="font-size:46px;">パソコンで作成</div>
        </div>
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:200px;">出身</div>
          <div class="proj-td" style="font-size:46px;">文系の現場担当者も活躍</div>
        </div>
        <div class="proj-row" style="padding:28px 0;">
          <div class="proj-th" style="width:200px;">土木</div>
          <div class="proj-td" style="font-size:46px;">トンネル・高架橋・ダム</div>
        </div>
      </div>
    </div>
    <div style="width:44.5%; height:100%; display:flex; flex-direction:column;">
      <div style="height:86%; width:100%; overflow:hidden;">
        <img src="${assets.p17_ic}" data-max="820" class="cover-img" />
      </div>
      <div style="height:14%; padding:24px 36px; display:flex; align-items:center;">
        <div style="font-size:32px; color:var(--black);">
          写真：座光寺スマートIC接続道路（土木）
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.17</div>
</section>

<!-- ==================== P.18 04 仕事と先輩の声③ (先輩、一言！) ==================== -->
<section class="slide" id="page-18">
  <div class="chap-header">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="padding:72px 96px 48px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label" style="margin-bottom:14px;">VOICES — NAGOYA BRANCH</div>
    <div style="display:flex; align-items:baseline; justify-content:space-between; margin-bottom:20px;">
      <div>
        <div style="font-size:74px; font-weight:700; color:var(--red); line-height:1.2;">先輩、一言！</div>
        <div style="font-size:38px; color:var(--black); margin-top:8px;">名古屋支店 建築工事部・2025年入社の先輩</div>
      </div>
      <div style="background:#FFF0F2; border:1.5px solid var(--red); color:var(--red); font-family:var(--sans); font-size:22px; font-weight:700; padding:10px 24px; border-radius:8px;">
        ★ 全社で愛知工業大学出身の先輩も 2名活躍中！
      </div>
    </div>
    <div style="display:flex; flex:1; gap:64px; margin-top:8px;">
      <!-- Col 1 -->
      <div style="flex:1; display:flex; flex-direction:column;">
        <div style="height:430px; display:flex; justify-content:center; align-items:flex-end; padding-bottom:10px;">
          <img src="${assets.voice_hk}" data-max="560" style="height:420px; object-fit:contain;" />
        </div>
        <div style="border-top:2px solid #222; padding-top:20px;">
          <div style="font-size:36px; font-weight:700; color:var(--red); line-height:1.42; min-height:110px;">
            「優しい先輩が多く<br>働きやすいです！」
          </div>
          <div style="display:flex; align-items:center; gap:24px; margin-top:16px;">
            <div style="font-size:44px; font-weight:700; color:var(--black); white-space:nowrap;">H.K さん</div>
            <div style="font-size:24px; color:#333; line-height:1.35;">名古屋支店建築工事部<br>2025年入社</div>
          </div>
        </div>
      </div>
      <!-- Col 2 -->
      <div style="flex:1; display:flex; flex-direction:column;">
        <div style="height:430px; display:flex; justify-content:center; align-items:flex-end; padding-bottom:10px;">
          <img src="${assets.voice_rk1}" data-max="560" style="height:420px; object-fit:contain;" />
        </div>
        <div style="border-top:2px solid #222; padding-top:20px;">
          <div style="font-size:36px; font-weight:700; color:var(--red); line-height:1.42; min-height:110px;">
            「ここより<br>良い職場はないです！」
          </div>
          <div style="display:flex; align-items:center; gap:24px; margin-top:16px;">
            <div style="font-size:44px; font-weight:700; color:var(--black); white-space:nowrap;">R.K さん</div>
            <div style="font-size:24px; color:#333; line-height:1.35;">名古屋支店建築工事部<br>2025年入社</div>
          </div>
        </div>
      </div>
      <!-- Col 3 -->
      <div style="flex:1; display:flex; flex-direction:column;">
        <div style="height:430px; display:flex; justify-content:center; align-items:flex-end; padding-bottom:10px;">
          <img src="${assets.voice_rk2}" data-max="560" style="height:420px; object-fit:contain;" />
        </div>
        <div style="border-top:2px solid #222; padding-top:20px;">
          <div style="font-size:36px; font-weight:700; color:var(--red); line-height:1.42; min-height:110px;">
            「形に残る仕事を<br>一緒にしましょう。<br>待ってます！」
          </div>
          <div style="display:flex; align-items:center; gap:20px; margin-top:16px;">
            <div style="font-size:34px; font-weight:700; color:var(--black); white-space:nowrap;">2025年入社の先輩</div>
            <div style="font-size:22px; color:#333; line-height:1.35; white-space:nowrap;">名古屋支店建築工事部<br>（建築施工担当）</div>
          </div>
        </div>
      </div>
    </div>
    <div style="text-align:right; font-size:22px; color:#444; margin-top:8px;">
      イラストはイメージです（ご本人ではありません）
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.18</div>
</section>

<!-- ==================== P.19 04 仕事と先輩の声④ (S.Kさん) ==================== -->
<section class="slide" id="page-19">
  <div class="chap-header">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="display:flex; width:100%; height:100%; padding:80px 96px 56px 96px;">
    <div style="width:36%; display:flex; flex-direction:column; align-items:center; justify-content:flex-end;">
      <img src="${assets.voice_sk}" data-max="700" style="height:820px; object-fit:contain;" />
      <div style="font-size:21px; color:#444; margin-top:16px; align-self:flex-start;">
        イラストはイメージです（ご本人ではありません）
      </div>
    </div>
    <div style="width:64%; padding-left:64px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">INTERVIEW</div>
      <div style="font-size:88px; font-weight:700; color:var(--red); line-height:1.15; margin-bottom:16px;">
        S.K さん
      </div>
      <div style="font-size:40px; font-weight:700; color:var(--black); padding-bottom:28px; border-bottom:1.5px solid #333; margin-bottom:44px;">
        安曇野支店 工事係 ― 土木女子（社会基盤・インフラ）
      </div>
      <div style="display:flex; align-items:center; gap:18px; margin-bottom:18px;">
        <div style="width:10px; height:42px; background:var(--red);"></div>
        <div style="font-size:38px; font-weight:700; color:var(--black);">職場の雰囲気</div>
      </div>
      <div style="font-size:30px; line-height:1.68; color:var(--black); margin-bottom:48px;">
        「分からないこともすぐに聞ける、温かい雰囲気の職場です！毎日明るくにぎやかで、チームで協力しながら支店で働いています。新しい方でもすぐに馴染めると思います。」
      </div>
      <div style="display:flex; align-items:center; gap:18px; margin-bottom:18px;">
        <div style="width:10px; height:42px; background:var(--red);"></div>
        <div style="font-size:38px; font-weight:700; color:var(--black);">これからの目標</div>
      </div>
      <div style="font-size:30px; line-height:1.68; color:var(--black);">
        「今は現場での経験を通して仕事を一つひとつ覚えることが目標です。必要な資格を習得しながらスキルアップできるよう努力して、頼られる先輩になりたいです。」
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.19</div>
</section>

<!-- ==================== P.20 04 仕事と先輩の声⑤ (A.Kさん) ==================== -->
<section class="slide" id="page-20">
  <div class="chap-header">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="display:flex; width:100%; height:100%; padding:80px 96px 56px 96px;">
    <div style="width:62%; padding-right:48px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">INTERVIEW</div>
      <div style="font-size:88px; font-weight:700; color:var(--red); line-height:1.15; margin-bottom:16px;">
        A.K さん
      </div>
      <div style="font-size:40px; font-weight:700; color:var(--black); padding-bottom:28px; border-bottom:1.5px solid #333; margin-bottom:44px;">
        建築事業本部 ― 子育て真っ最中
      </div>
      <div style="display:flex; align-items:center; gap:18px; margin-bottom:18px;">
        <div style="width:10px; height:42px; background:var(--red);"></div>
        <div style="font-size:38px; font-weight:700; color:var(--black);">職場の雰囲気</div>
      </div>
      <div style="font-size:30px; line-height:1.68; color:var(--black); margin-bottom:48px;">
        「アットホームでみんな優しく困ったことも聞きやすいです。妊娠中の体調不良、子どものことでの急なお休みにも理解があり、とっても働きやすい職場です。産休育休制度も整っているので、女性の方も安心して働けると思います。」
      </div>
      <div style="display:flex; align-items:center; gap:18px; margin-bottom:18px;">
        <div style="width:10px; height:42px; background:var(--red);"></div>
        <div style="font-size:38px; font-weight:700; color:var(--black);">心掛けていること</div>
      </div>
      <div style="font-size:30px; line-height:1.68; color:var(--black);">
        「任された業務には全力で取り組み、常に明るく前向きな姿勢で仕事に取り組むことを心掛けています。」
      </div>
    </div>
    <div style="width:38%; display:flex; flex-direction:column; align-items:center; justify-content:flex-end;">
      <img src="${assets.voice_ak}" data-max="700" style="height:820px; object-fit:contain;" />
      <div style="font-size:21px; color:#444; margin-top:16px;">
        イラストはイメージです（ご本人ではありません）
      </div>
    </div>
  </div>
  <div class="page-num-badge left-bottom">P.20</div>
</section>

<!-- ==================== P.21 04 正直に話します ==================== -->
<section class="slide" id="page-21">
  <div class="chap-header">
    <span class="chap-num">04 / 07</span>
    <span class="chap-name">仕事と先輩の声</span>
  </div>
  <div style="padding:76px 96px 60px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label">HONESTLY</div>
    <div style="font-size:80px; font-weight:700; color:var(--red); margin-bottom:40px;">
      正直に話します
    </div>
    <div style="display:flex; flex:1; gap:48px; align-items:stretch;">
      <div style="width:30%; display:flex; flex-direction:column;">
        <div style="height:10px; background:#181818; margin-bottom:28px;"></div>
        <div style="font-size:44px; font-weight:700; color:var(--black); margin-bottom:32px;">大変なこと</div>
        <div style="padding:28px 0; border-bottom:1px solid #CCC; display:flex; gap:24px; align-items:baseline;">
          <span style="font-size:44px; font-weight:700; color:var(--red);">1</span>
          <span style="font-size:38px; font-weight:700; color:var(--red);">天候に左右される</span>
        </div>
        <div style="padding:28px 0; border-bottom:1px solid #CCC; display:flex; gap:24px; align-items:baseline;">
          <span style="font-size:44px; font-weight:700; color:var(--red);">2</span>
          <span style="font-size:38px; font-weight:700; color:var(--red);">現場が毎回変わる</span>
        </div>
        <div style="font-size:30px; color:var(--black); margin-top:32px; line-height:1.5;">
          屋外で、移動の多い仕事です
        </div>
      </div>
      <div style="width:36%; display:flex; flex-direction:column;">
        <div style="height:10px; background:var(--red); margin-bottom:28px;"></div>
        <div style="font-size:44px; font-weight:700; color:var(--black); margin-bottom:32px;">その対策</div>
        <div style="padding:28px 0; border-bottom:1px solid #CCC;">
          <div style="display:flex; gap:20px; align-items:baseline;">
            <span style="font-size:44px; font-weight:700; color:var(--red);">1</span>
            <span style="font-size:38px; font-weight:700; color:var(--red); white-space:nowrap;">ICTで効率化（23.4%削減）</span>
          </div>
          <div style="font-family:var(--sans); font-size:19px; color:#444; margin-top:8px; padding-left:44px; white-space:nowrap;">
            ドローン測量・3D点群データ内製化で作業時間を大幅短縮
          </div>
        </div>
        <div style="padding:28px 0; border-bottom:1px solid #CCC;">
          <div style="display:flex; gap:20px; align-items:baseline;">
            <span style="font-size:44px; font-weight:700; color:var(--red);">2</span>
            <span style="font-size:38px; font-weight:700; color:var(--red); white-space:nowrap;">若手の残業 月平均 11 時間</span>
          </div>
          <div style="font-family:var(--sans); font-size:19px; color:#444; margin-top:8px; padding-left:44px; white-space:nowrap;">
            1日あたり約30分！タブレット活用とチーム分業を推進
          </div>
        </div>
        <div style="font-size:30px; color:var(--black); margin-top:32px; line-height:1.5;">
          ドローン・3Dデータを活用
        </div>
      </div>
      <div style="width:34%; display:flex; flex-direction:column; justify-content:center;">
        <div style="border-radius:12px; overflow:hidden; border:2px solid #DDD;">
          <img src="${assets.cm3_ojt}" data-max="800" style="width:100%; height:440px; object-fit:cover; display:block;" />
        </div>
        <div style="font-family:var(--sans); font-size:19px; color:#444; margin-top:16px; line-height:1.5; text-align:center; white-space:nowrap;">
          ▲ 先輩社員とタブレット・図面を用いた現場OJT（イメージ）
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.21</div>
</section>

<!-- ==================== P.22 05 お金と安心① (奨学金返還支援) ==================== -->
<section class="slide" id="page-22">
  <div class="chap-header">
    <span class="chap-num">05 / 07</span>
    <span class="chap-name">お金と安心</span>
  </div>
  <div style="padding:84px 96px 64px 96px; width:100%; height:100%; display:flex; flex-direction:column; justify-content:center;">
    <div class="en-label">CHAPTER 05 — SCHOLARSHIP SUPPORT</div>
    <div style="display:flex; align-items:center; gap:32px; margin-bottom:20px;">
      <div style="font-size:56px; font-weight:700; color:var(--black);">
        奨学金の返還を会社が支援
      </div>
      <div style="background:var(--red); color:#FFF; font-family:var(--sans); font-size:28px; font-weight:700; padding:10px 28px; border-radius:40px;">
        10年間で最大 300 万円相当を支援！
      </div>
    </div>
    <div style="display:flex; align-items:baseline; gap:24px; padding-bottom:44px; border-bottom:1.5px solid #333; margin-bottom:48px;">
      <span style="font-size:120px; font-weight:700; color:var(--red);">月</span>
      <span style="font-size:330px; font-weight:700; color:var(--red); line-height:0.9;">2.5</span>
      <span style="font-size:120px; font-weight:700; color:var(--red);">万円以内</span>
    </div>
    <div style="display:flex;">
      <div style="width:50%; padding-right:48px; border-right:1.5px solid #AAA;">
        <div style="font-size:38px; color:var(--black); margin-bottom:20px;">期間</div>
        <div style="font-size:64px; font-weight:700; color:var(--black);">入社 10 年目まで</div>
      </div>
      <div style="width:50%; padding-left:64px;">
        <div style="font-size:38px; color:var(--black); margin-bottom:20px;">返済月額が 2.5 万円未満のとき</div>
        <div style="font-size:64px; font-weight:700; color:var(--black);">返済月額と同額を支援</div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.22</div>
</section>

<!-- ==================== P.23 05 お金と安心② (資格支援) ==================== -->
<section class="slide" id="page-23">
  <div class="chap-header">
    <span class="chap-num">05 / 07</span>
    <span class="chap-name">お金と安心</span>
  </div>
  <div style="display:flex; width:100%; height:100%;">
    <div style="width:39%; height:100%; position:relative;">
      <img src="${assets.p23_tunnel}" data-max="800" class="cover-img" />
      <div style="position:absolute; bottom:20px; left:20px; background:#181818; color:#FFF; font-family:var(--sans); font-size:18px; padding:6px 14px; border-radius:4px;">
        施工実績：粒良脇トンネル（土木）
      </div>
    </div>
    <div style="width:61%; height:100%; padding:84px 96px 60px 84px; display:flex; flex-direction:column; justify-content:center;">
      <div class="en-label">LICENSES &amp; TRAINING</div>
      <div style="font-size:68px; font-weight:700; color:var(--red); line-height:1.34; padding-bottom:36px; border-bottom:1.5px solid #333; margin-bottom:32px;">
        資格の講習・受験費用は<br>会社が全額負担。
      </div>
      <div style="font-size:38px; font-weight:700; color:var(--black); margin-bottom:20px;">
        対象の資格（例）
      </div>
      <div style="font-size:38px; font-weight:700; color:var(--red); line-height:1.68; padding-bottom:32px; border-bottom:1px solid #AAA; margin-bottom:32px;">
        1・2級 施工管理技士 ／ 1・2級 建築士<br>
        技術士・技術士補<br>
        1・2級 管工事・電気工事施工管理技士<br>
        ほか多数
      </div>
      <div style="font-size:46px; font-weight:700; color:var(--black); line-height:1.55;">
        取得後は、毎月 資格手当<br>
        新人研修・講演会の受講も
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.23</div>
</section>

<!-- ==================== P.24 05 お金と安心③ (働き方と待遇) ==================== -->
<section class="slide" id="page-24">
  <div class="chap-header">
    <span class="chap-num">05 / 07</span>
    <span class="chap-name">お金と安心</span>
  </div>
  <div style="padding:80px 96px 60px 96px; width:100%; height:100%; display:flex; flex-direction:column; justify-content:center;">
    <div class="en-label">WORK STYLE &amp; COMPENSATION</div>
    <div style="font-size:80px; font-weight:700; color:var(--red); margin-bottom:40px;">
      働き方と待遇
    </div>
    <div style="display:grid; grid-template-columns: 1.35fr 0.9fr 1.1fr 1.05fr; gap:36px; padding-bottom:44px; border-bottom:1.5px solid #333; margin-bottom:48px;">
      <div style="border-top:1.5px solid #333; padding-top:24px;">
        <div style="font-size:32px; font-weight:600; color:var(--black); margin-bottom:28px;">初任給（月額・手当込み）</div>
        <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:20px;">
          <span style="font-size:92px; font-weight:700; color:var(--red); line-height:1;">289,000</span>
          <span style="font-size:40px; font-weight:700; color:var(--red);">円</span>
        </div>
        <div style="font-size:24px; color:var(--black);">名古屋支店勤務・R9.4入社基準</div>
      </div>
      <div style="border-top:1.5px solid #333; padding-top:24px;">
        <div style="font-size:32px; font-weight:600; color:var(--black); margin-bottom:28px;">賞与</div>
        <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:20px;">
          <span style="font-size:52px; font-weight:700; color:var(--red);">年</span>
          <span style="font-size:104px; font-weight:700; color:var(--red); line-height:1;">3</span>
          <span style="font-size:52px; font-weight:700; color:var(--red);">回</span>
        </div>
        <div style="font-size:24px; color:var(--black);">令和7年度実績</div>
      </div>
      <div style="border-top:1.5px solid #333; padding-top:24px;">
        <div style="font-size:32px; font-weight:600; color:var(--black); margin-bottom:28px;">年間休日</div>
        <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:20px;">
          <span style="font-size:104px; font-weight:700; color:var(--red); line-height:1;">123</span>
          <span style="font-size:44px; font-weight:700; color:var(--red);">日</span>
        </div>
        <div style="font-size:22px; color:var(--black); line-height:1.45;">
          R7実績（R8年度122日）<br>有給休暇 入社時10日付与
        </div>
      </div>
      <div style="border-top:1.5px solid #333; padding-top:24px;">
        <div style="font-size:32px; font-weight:600; color:var(--black); margin-bottom:28px;">若手の残業</div>
        <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:20px;">
          <span style="font-size:42px; font-weight:700; color:var(--red);">月平均</span>
          <span style="font-size:104px; font-weight:700; color:var(--red); line-height:1;">11</span>
          <span style="font-size:42px; font-weight:700; color:var(--red);">時間</span>
        </div>
        <div style="font-size:24px; color:var(--black);">1日あたり約30分・DX推進</div>
      </div>
    </div>
    <div>
      <div style="width:68px; height:9px; background:var(--red); margin-bottom:20px;"></div>
      <div style="font-size:54px; font-weight:700; color:var(--red); margin-bottom:18px;">
        認証・登録を、3つ。
      </div>
      <div style="font-size:34px; color:var(--black);">
        健康・子育て・働き方の取り組み。詳しくは次のページへ。
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.24</div>
</section>

<!-- ==================== P.25 05 お金と安心④ (3つの公的認証) ==================== -->
<section class="slide" id="page-25">
  <div class="chap-header">
    <span class="chap-num">05 / 07</span>
    <span class="chap-name">お金と安心</span>
  </div>
  <div style="padding:68px 96px 48px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label" style="margin-bottom:14px;">CERTIFIED — HEALTH × FAMILY × WORK STYLE</div>
    <div style="font-size:72px; font-weight:700; color:var(--red); margin-bottom:24px;">
      安心して、長く働ける。
    </div>
    <div style="background:var(--red); color:#FFF; text-align:center; font-size:40px; font-weight:700; padding:16px; margin-bottom:28px; letter-spacing:0.05em;">
      健康 × 子育て × 働き方 ― 3つの柱で支える職場
    </div>
    <div style="display:flex; flex:1; gap:36px;">
      <div style="flex:1; border:1.5px solid #222; border-top:10px solid var(--red); padding:28px 32px; display:flex; flex-direction:column;">
        <div style="font-size:38px; font-weight:700; color:var(--red); margin-bottom:16px;">01 健康</div>
        <div style="height:150px; display:flex; align-items:center; justify-content:center; border-bottom:1px solid #CCC; margin-bottom:22px;">
          <img src="${assets.cert_kenko}" data-max="500" style="max-width:92%; max-height:125px; object-fit:contain;" />
        </div>
        <div style="font-size:32px; font-weight:700; color:var(--black); line-height:1.38; margin-bottom:14px;">
          健康経営優良法人 2026<br>（中小規模法人部門）
        </div>
        <div style="font-size:25px; font-weight:700; color:var(--red); margin-bottom:24px;">
          2026年3月9日認定
        </div>
        <div style="font-family:var(--sans); font-size:22px; color:#222; line-height:1.6; margin-top:auto;">
          社員の健康管理を経営の視点で考え、戦略的に取り組んでいると認められました。
        </div>
      </div>
      <div style="flex:1; border:1.5px solid #222; border-top:10px solid var(--red); padding:28px 32px; display:flex; flex-direction:column;">
        <div style="font-size:38px; font-weight:700; color:var(--red); margin-bottom:16px;">02 子育て</div>
        <div style="height:150px; display:flex; align-items:center; justify-content:center; border-bottom:1px solid #CCC; margin-bottom:22px;">
          <img src="${assets.cert_kosodate}" data-max="300" style="max-height:130px; object-fit:contain;" />
        </div>
        <div style="font-size:32px; font-weight:700; color:var(--black); line-height:1.38; margin-bottom:14px;">
          「社員の子育て応援宣言」<br>登録
        </div>
        <div style="font-size:24px; font-weight:700; color:var(--red); line-height:1.45; margin-bottom:20px;">
          初回登録 2014年12月1日<br>最終更新 2025年10月17日
        </div>
        <div style="font-family:var(--sans); font-size:22px; color:#222; line-height:1.6; margin-top:auto;">
          有給休暇を取りやすくし、学校行事や夏・冬・春休みの長期休暇を応援します。
        </div>
      </div>
      <div style="flex:1; border:1.5px solid #222; border-top:10px solid var(--red); padding:28px 32px; display:flex; flex-direction:column;">
        <div style="font-size:38px; font-weight:700; color:var(--red); margin-bottom:16px;">03 働き方</div>
        <div style="height:150px; display:flex; align-items:center; justify-content:center; gap:28px; border-bottom:1px solid #CCC; margin-bottom:22px;">
          <img src="${assets.cert_iki1}" data-max="300" style="max-height:130px; object-fit:contain;" />
          <img src="${assets.cert_iki2}" data-max="300" style="max-height:130px; object-fit:contain;" />
        </div>
        <div style="font-size:31px; font-weight:700; color:var(--black); line-height:1.38; margin-bottom:12px;">
          職場いきいき<br>アドバンスカンパニー認証
        </div>
        <div style="font-size:22px; font-weight:700; color:var(--red); line-height:1.45; margin-bottom:16px;">
          ワークライフバランス ★★★<br>ネクストジェネレーション ★★★<br>令和7年10月1日認証
        </div>
        <div style="font-family:var(--sans); font-size:21px; color:#222; line-height:1.55; margin-top:auto;">
          長野県の認証。★は認証の回数（旧制度を含む）、有効期間は3年です。
        </div>
      </div>
    </div>
    <div style="height:8px; background:#181818; margin-top:20px;"></div>
  </div>
  <div class="page-num-badge right-bottom">P.25</div>
</section>

<!-- ==================== P.26 06 成長の道すじ① ==================== -->
<section class="slide" id="page-26">
  <div class="chap-header">
    <span class="chap-num">06 / 07</span>
    <span class="chap-name">成長の道すじ</span>
  </div>
  <div style="padding:76px 96px 56px 96px; width:100%; height:100%; display:flex; flex-direction:column;">
    <div class="en-label">CHAPTER 06 — CAREER PATH</div>
    <div style="font-size:80px; font-weight:700; color:var(--red); margin-bottom:32px;">
      入社1〜2年目は、先輩のもとで。
    </div>
    <div style="display:flex; background:var(--red); color:#FFF; margin-bottom:28px;">
      <div style="width:50%; padding:24px 44px; font-size:48px; font-weight:700; border-right:3px solid #FFF;">1年目</div>
      <div style="width:50%; padding:24px 44px; font-size:48px; font-weight:700;">2年目</div>
    </div>
    <div style="text-align:center; font-size:56px; font-weight:700; color:var(--red); padding:16px 0 36px 0; border-bottom:1.5px solid #333; margin-bottom:36px;">
      先輩のもとで知識を学ぶ（3年目以降、段階的に1人で現場へ）
    </div>
    <div style="display:flex; flex:1; gap:60px; align-items:center;">
      <div style="width:54%;">
        <div style="font-size:56px; font-weight:700; color:var(--red); margin-bottom:20px;">
          土木も、街づくり。
        </div>
        <div style="font-size:38px; line-height:1.65; color:var(--black); margin-bottom:20px;">
          高速道路・トンネル・河川。<br>
          リニア関連の道路整備で、<br>
          仕事が増えています。
        </div>
        <div style="font-family:var(--sans); font-size:21px; color:#444; line-height:1.6;">
          社会基盤学科（土木）のみなさんが学んだ構造力学・測量・地盤・コンクリートの知識を、地域の大型インフラ整備で存分に発揮できます。
        </div>
      </div>
      <div style="width:46%; display:flex; flex-direction:column;">
        <div style="border-radius:12px; overflow:hidden; border:2px solid #DDD;">
          <img src="${assets.cm2_bridge}" data-max="800" style="width:100%; height:310px; object-fit:cover; display:block;" />
        </div>
        <div style="font-family:var(--sans); font-size:18px; color:#555; margin-top:10px; text-align:right;">
          ▲ 高架橋・インフラ建設現場イメージ
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.26</div>
</section>

<!-- ==================== P.27 06 成長の道すじ② (経営者メッセージ) ==================== -->
<section class="slide" id="page-27">
  <div class="chap-header">
    <span class="chap-num">06 / 07</span>
    <span class="chap-name">成長の道すじ</span>
  </div>
  <div style="padding:84px 96px 64px 96px; width:100%; height:100%; display:flex; flex-direction:column; justify-content:center;">
    <div class="en-label">MESSAGE FROM THE PRESIDENT</div>
    <div style="font-size:80px; font-weight:700; color:var(--red); margin-bottom:20px;">
      経営者メッセージ
    </div>
    <div style="display:flex; align-items:baseline; gap:36px; padding-bottom:32px; border-bottom:1.5px solid #333; margin-bottom:52px;">
      <span style="font-size:42px; font-weight:700; color:var(--black);">代表取締役社長</span>
      <span style="font-size:54px; font-weight:700; color:var(--black); letter-spacing:0.08em;">木下 勝貴</span>
    </div>
    <div style="display:flex; gap:84px;">
      <div style="width:50%;">
        <div style="width:68px; height:9px; background:var(--red); margin-bottom:24px;"></div>
        <div style="font-size:48px; font-weight:700; color:var(--red); margin-bottom:28px;">
          こんな会社です
        </div>
        <div style="font-size:31px; line-height:1.72; color:var(--black);">
          「創業113年目を迎えた木下建設株式会社は、総合建設業として道路河川などのインフラ整備や病院・学校・商工業施設・高層マンションの建築などに携わり、優れた施工技術で高い評価を得ています。名古屋支店や安曇野支店をはじめ各拠点を更に充実させて、地域の発展に貢献できるよう社員一丸となって取り組んでいます。」
        </div>
      </div>
      <div style="width:50%;">
        <div style="width:68px; height:9px; background:var(--red); margin-bottom:24px;"></div>
        <div style="font-size:48px; font-weight:700; color:var(--red); margin-bottom:28px;">
          こんな人と働きたい
        </div>
        <div style="font-size:31px; line-height:1.72; color:var(--black);">
          「当社は、アットホームな雰囲気の明るい会社です。人材育成に力を入れると共に、やりがいと達成感が得られる仕事となるよう取り組んでいます。明るい未来を一緒に創っていただける皆さん、男女問わずよろしくお願いします。」
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.27</div>
</section>

<!-- ==================== P.28 07 応募の案内・お問い合わせ ==================== -->
<section class="slide" id="page-28">
  <div style="background:var(--red); color:#FFF; padding:34px 96px; display:flex; justify-content:space-between; align-items:center;">
    <div>
      <div style="font-size:20px; letter-spacing:0.22em; margin-bottom:8px;">CHAPTER 07 — HOW TO APPLY &amp; CONTACT</div>
      <div style="font-size:54px; font-weight:700; line-height:1.25;">
        あなたが描く図面を、一緒に街に建てましょう。
      </div>
    </div>
    <div style="text-align:right; border-bottom:1.5px solid #FFFFFF; padding-bottom:10px;">
      <span style="font-size:28px; font-weight:600; margin-right:18px;">07 / 07</span>
      <span style="font-size:26px;">応募の案内</span>
    </div>
  </div>

  <div style="margin:24px 96px 0 96px; background:#FFF6E5; border:3px solid var(--red); border-radius:10px; padding:16px 32px; display:flex; align-items:center; justify-content:space-between;">
    <div style="display:flex; align-items:center; gap:20px;">
      <span style="background:var(--red); color:#FFF; font-family:var(--sans); font-size:22px; font-weight:700; padding:8px 20px; border-radius:6px;">学内イベント出展</span>
      <span style="font-family:var(--sans); font-size:30px; font-weight:700; color:var(--red);">
        令和8年5月30日（土）午前の部「愛名会 企業研究会」参加決定！
      </span>
    </div>
    <span style="font-family:var(--sans); font-size:20px; font-weight:700; color:#222;">
      名古屋支店での会社説明会・現場見学会も随時受付中！
    </span>
  </div>

  <div style="display:flex; flex:1; padding:24px 96px 36px 96px; gap:64px;">
    <div style="width:50%; display:flex; flex-direction:column;">
      <div style="font-size:44px; font-weight:700; color:var(--red); padding-bottom:14px; border-bottom:2px solid #222; margin-bottom:12px;">
        選考の流れ
      </div>
      ${[
        ['01', '会社説明会（現場見学）', '随時開催。希望の日時をお知らせください'],
        ['02', '応募書類を提出', '履歴書・卒業見込証明書・成績証明書'],
        ['03', '選考（名古屋支店 または 本社）', '名古屋支店（名古屋市昭和区阿由知通1-12-3）※本社（飯田市）希望も可'],
        ['04', 'Webからも申込可', '木下建設ホームページ内『リクルートサイト』またはメールにて受付'],
      ].map(([n, t, s]) => `
        <div style="display:flex; align-items:center; padding:16px 0; border-bottom:1px solid #CCC;">
          <div style="width:90px; font-size:44px; font-weight:700; color:var(--red);">${n}</div>
          <div>
            <div style="font-size:31px; font-weight:700; color:var(--black);">${t}</div>
            <div style="font-family:var(--sans); font-size:20px; color:#444; margin-top:4px;">${s}</div>
          </div>
        </div>
      `).join('')}
      <div style="margin-top:auto; display:flex; align-items:center; gap:20px; padding-top:14px;">
        <img src="${assets.logo_lg}" data-max="200" style="width:86px; height:86px; object-fit:contain;" />
        <div style="font-family:var(--sans); font-size:20px; font-weight:700; color:var(--black); line-height:1.5;">
          説明会のあとのご連絡・ご質問は、木下建設へ直接どうぞ。<br>
          <span style="color:var(--red);">愛知工業大学（建築学科・社会基盤学科）・愛工大名電高のみなさんのご応募をお待ちしています！</span>
        </div>
      </div>
    </div>

    <div style="width:50%; display:flex; flex-direction:column; justify-content:space-between;">
      <div style="background:#F9F9F9; border:1.5px solid #CCC; border-top:6px solid var(--red); padding:24px 28px; border-radius:8px;">
        <div style="font-size:36px; font-weight:700; color:var(--red); margin-bottom:14px;">
          応募・お問い合わせ窓口
        </div>
        <div style="font-family:var(--sans); font-size:24px; font-weight:700; color:var(--black); margin-bottom:14px;">
          総務本部総務部 採用担当：向野 浩幸（こうの ひろゆき）
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px; margin-bottom:16px;">
          <div style="background:#FFF; padding:14px 16px; border:1px solid #DDD; border-radius:6px;">
            <div style="font-family:var(--sans); font-size:16px; color:#555; font-weight:700; white-space:nowrap;">名古屋支店 TEL（昭和区阿由知通1-12-3）</div>
            <div style="font-size:40px; font-weight:700; color:var(--red); margin-top:4px;">052-741-6220</div>
          </div>
          <div style="background:#FFF; padding:14px 16px; border:1px solid #DDD; border-radius:6px;">
            <div style="font-family:var(--sans); font-size:16px; color:#555; font-weight:700; white-space:nowrap;">本社 総務部 TEL（長野県飯田市松尾町1-22）</div>
            <div style="font-size:40px; font-weight:700; color:var(--red); margin-top:4px;">0265-22-2780</div>
          </div>
        </div>
        <div style="display:flex; gap:28px; font-family:var(--sans); font-size:21px; font-weight:700; color:var(--black); white-space:nowrap;">
          <div>E-Mail: <span style="color:var(--red);">hr@kinoken.co.jp</span></div>
          <div>Web: <span style="color:var(--red);">https://www.kinoshitakensetsu.jp/</span></div>
        </div>
      </div>

      <div style="display:flex; align-items:flex-end; justify-content:space-around; height:310px; padding-top:10px; position:relative;">
        <img src="${assets.char1}" data-max="400" style="height:295px; object-fit:contain;" />
        <img src="${assets.char2}" data-max="400" style="height:295px; object-fit:contain;" />
        <img src="${assets.char3}" data-max="400" style="height:295px; object-fit:contain;" />
        <img src="${assets.char4}" data-max="400" style="height:295px; object-fit:contain;" />
        <img src="${assets.char5}" data-max="400" style="height:295px; object-fit:contain;" />
        <div style="position:absolute; right:0; bottom:0; font-size:16px; color:#666; background:#FFFFFF; padding:2px 6px;">
          ※イラストはイメージです（ご本人ではありません）
        </div>
      </div>
    </div>
  </div>
  <div class="page-num-badge right-bottom">P.28</div>
</section>

</body>
</html>`;
}

function buildFlyerHtml() {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>木下建設株式会社 2027採用・会社説明会案内チラシ</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --red: #D70015;
    --dark: #181818;
    --serif: 'Noto Serif JP', serif;
    --sans: 'Noto Sans JP', sans-serif;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  @page {
    size: 1240px 1754px;
    margin: 0;
  }
  body {
    width: 1240px;
    height: 1754px;
    margin: 0;
    padding: 0;
    background: #FFFFFF;
    color: var(--dark);
    font-family: var(--sans);
    overflow: hidden;
  }
  .flyer-wrap {
    width: 1240px;
    height: 1754px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    background: #FFFFFF;
  }
</style>
</head>
<body>
<div class="flyer-wrap">
  <!-- Top Header Banner (116px) -->
  <div style="background:var(--red); color:#FFF; padding:18px 32px; display:flex; justify-content:space-between; align-items:center; height:112px;">
    <div>
      <div style="display:inline-block; background:#FFF; color:var(--red); font-size:16px; font-weight:700; padding:4px 14px; border-radius:4px; margin-bottom:8px;">
        学校法人名古屋電機学園「愛名会 2027企業案内」特別号
      </div>
      <div style="font-size:25px; font-weight:700; letter-spacing:0.01em; white-space:nowrap;">
        愛知工業大学（建築学科・社会基盤学科）・愛工大名電高のみなさんへ
      </div>
    </div>
    <div style="text-align:right; display:flex; align-items:center; gap:14px; white-space:nowrap;">
      <div>
        <div style="font-size:14px;">創業1913年（113年目）の総合建設会社</div>
        <div style="font-family:var(--serif); font-size:28px; font-weight:700;">木下建設株式会社</div>
      </div>
      <img src="${assets.logo_sm}" data-max="160" style="width:64px; height:64px; border-radius:50%; background:#FFF; padding:4px;" />
    </div>
  </div>

  <!-- Hero Section (350px) -->
  <div style="position:relative; height:350px; display:flex; border-bottom:4px solid var(--red);">
    <div style="width:56%; padding:24px 40px; display:flex; flex-direction:column; justify-content:center; background:#FFF8F8;">
      <div style="font-family:var(--serif); font-size:28px; font-weight:700; color:var(--red); margin-bottom:4px; white-space:nowrap;">
        あなたの図面が建つ街、未来をつなぐ道。
      </div>
      <div style="font-family:var(--serif); font-size:56px; font-weight:700; color:var(--dark); line-height:1.15; margin-bottom:14px;">
        名古屋で、働ける。<br>
        <span style="color:var(--red); font-size:44px;">都市建築 × 大規模土木</span>
      </div>
      <div style="font-size:18px; line-height:1.55; color:#222; margin-bottom:16px;">
        名古屋支店（昭和区阿由知通）管内で<strong>高層RCマンション29件</strong>の施工実績！本社・各支店では高速道路・スマートIC・橋梁・トンネル等の大型インフラ整備も推進しています。
      </div>
      <div style="display:flex; gap:10px; white-space:nowrap;">
        <span style="background:var(--red); color:#FFF; font-size:15px; font-weight:700; padding:6px 12px; border-radius:6px;">
          ★ 愛工大出身の先輩 2名活躍中！
        </span>
        <span style="background:#181818; color:#FFF; font-size:15px; font-weight:700; padding:6px 12px; border-radius:6px;">
          ★ 2025年入社の若手先輩も名古屋支店に在籍
        </span>
      </div>
    </div>
    <div style="width:44%; height:100%; display:grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap:4px; background:#DDD;">
      <div style="position:relative; overflow:hidden;">
        <img src="${assets.p07_night}" data-max="500" style="width:100%; height:100%; object-fit:cover;" />
        <div style="position:absolute; bottom:4px; left:4px; background:#181818; color:#FFF; font-size:12px; padding:2px 7px;">名古屋 高層マンション実績29件</div>
      </div>
      <div style="position:relative; overflow:hidden;">
        <img src="${assets.proj02}" data-max="500" style="width:100%; height:100%; object-fit:cover;" />
        <div style="position:absolute; bottom:4px; left:4px; background:#181818; color:#FFF; font-size:12px; padding:2px 7px;">プレサンス阿由知通一丁目(R7.1)</div>
      </div>
      <div style="position:relative; overflow:hidden;">
        <img src="${assets.p17_ic}" data-max="500" style="width:100%; height:100%; object-fit:cover;" />
        <div style="position:absolute; bottom:4px; left:4px; background:#181818; color:#FFF; font-size:12px; padding:2px 7px;">座光寺スマートIC接続道路(土木)</div>
      </div>
      <div style="position:relative; overflow:hidden;">
        <img src="${assets.cm3_ojt}" data-max="500" style="width:100%; height:100%; object-fit:cover;" />
        <div style="position:absolute; bottom:4px; left:4px; background:#181818; color:#FFF; font-size:12px; padding:2px 7px;">1〜2年目は先輩のもとでOJT</div>
      </div>
    </div>
  </div>

  <!-- 6 Killer Facts Grid -->
  <div style="padding:18px 40px; background:#F6F6F6;">
    <div style="text-align:center; font-family:var(--serif); font-size:27px; font-weight:700; color:var(--red); margin-bottom:14px;">
      ― 施工管理の「3大不安」を解消する、木下建設の6大キラーファクト ―
    </div>
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:14px;">
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">① 初任給（名古屋支店・R9.4基準）</div>
        <div style="font-family:var(--serif); font-size:44px; font-weight:700; color:var(--red); line-height:1.12; margin:4px 0;">
          289,000<span style="font-size:24px;">円</span>
        </div>
        <div style="font-size:15px; color:#222;">月額・手当込み ／ <strong>賞与 年3回</strong>（令和7年度実績）の高水準待遇！</div>
      </div>
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">② 奨学金の返還を会社が支援</div>
        <div style="font-family:var(--serif); font-size:44px; font-weight:700; color:var(--red); line-height:1.12; margin:4px 0;">
          <span style="font-size:24px;">月</span>2.5<span style="font-size:24px;">万円以内</span>
        </div>
        <div style="font-size:15px; color:#222;">入社10年目まで（<strong>最大300万円相当</strong>）返還を支援！</div>
      </div>
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">③ 建設DX推進 × 若手の残業時間</div>
        <div style="font-family:var(--serif); font-size:44px; font-weight:700; color:var(--red); line-height:1.12; margin:4px 0;">
          <span style="font-size:22px;">月平均</span> 11<span style="font-size:24px;">時間</span>
        </div>
        <div style="font-size:15px; color:#222;">ドローン・3Dデータ内製化で<strong>作業時間を23.4%削減</strong>！</div>
      </div>
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">④ ワークライフバランスと休日</div>
        <div style="font-family:var(--serif); font-size:44px; font-weight:700; color:var(--red); line-height:1.12; margin:4px 0;">
          <span style="font-size:22px;">年間休日</span> 123<span style="font-size:24px;">日</span>
        </div>
        <div style="font-size:15px; color:#222;">R7実績（R8年度122日）＋<strong>有給休暇 入社時10日付与</strong>！</div>
      </div>
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">⑤ 資格取得フルサポート</div>
        <div style="font-family:var(--serif); font-size:28px; font-weight:700; color:var(--red); line-height:1.25; margin:8px 0; white-space:nowrap;">
          講習・受験費用 全額負担
        </div>
        <div style="font-size:15px; color:#222;">建築士・施工管理技士・技術士等＋<strong>毎月資格手当支給</strong></div>
      </div>
      <div style="background:#FFF; border:1.5px solid #DDD; border-top:6px solid var(--red); border-radius:8px; padding:14px 18px;">
        <div style="font-size:16px; font-weight:700; color:#555;">⑥ 企業規模と安定基盤</div>
        <div style="font-family:var(--serif); font-size:42px; font-weight:700; color:var(--red); line-height:1.12; margin:4px 0;">
          <span style="font-size:20px;">売上高</span> 約82.6<span style="font-size:22px;">億円</span>
        </div>
        <div style="font-size:15px; color:#222;">社員数131名（2026.6時点）／4拠点（名古屋・飯田・安曇野・甲信）</div>
      </div>
    </div>
  </div>

  <!-- Middle Section: Business Scope & Voices & Certifications -->
  <div style="padding:16px 40px; display:flex; gap:24px; flex:1;">
    <div style="width:52%; display:flex; flex-direction:column; justify-content:space-between;">
      <div style="border:1.5px solid #CCC; border-radius:8px; padding:16px 20px;">
        <div style="font-family:var(--serif); font-size:22px; font-weight:700; color:var(--red); border-bottom:2px solid var(--red); padding-bottom:6px; margin-bottom:10px; white-space:nowrap;">
          ■ 学科別 フィールド紹介（1〜2年目は先輩のもとでOJT）
        </div>
        <div style="margin-bottom:10px;">
          <div style="font-size:18px; font-weight:700; color:var(--dark);">【建築学科・科学技術科】名古屋都心の高層マンション＆施設建築</div>
          <div style="font-size:15px; color:#333; line-height:1.5; margin-top:4px;">
            千種区・昭和区・中区・西区等でRC10〜15階建てマンション29件を施工（10階以上19件・15階建8件）。勤務地は名古屋支店管内（昭和区阿由知通）が基本です。
          </div>
        </div>
        <div>
          <div style="font-size:18px; font-weight:700; color:var(--dark);">【社会基盤学科・科学技術科】高速道路・橋梁・トンネル・建設DX</div>
          <div style="font-size:15px; color:#333; line-height:1.5; margin-top:4px;">
            座光寺スマートIC接続道路・粒良脇トンネル・リニア関連道路整備など、地域の大型インフラを推進。ドローンや3D点群ICT施工の最前線で活躍できます。
          </div>
        </div>
      </div>

      <div style="border:1.5px solid #CCC; border-radius:8px; padding:14px 20px; display:flex; align-items:center; justify-content:space-between; background:#FAFAFA;">
        <div>
          <div style="font-size:18px; font-weight:700; color:var(--red);">■ 公的認証・登録を3つ取得！</div>
          <div style="font-size:15px; color:#333; margin-top:4px; line-height:1.45;">
            ① 健康経営優良法人2026 ／ ② 社員の子育て応援宣言<br>
            ③ 職場いきいきアドバンスカンパニー認証（★★★）
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <img src="${assets.cert_kenko}" data-max="240" style="height:38px; object-fit:contain;" />
          <img src="${assets.cert_kosodate}" data-max="160" style="height:48px; object-fit:contain;" />
          <img src="${assets.cert_iki1}" data-max="160" style="height:48px; object-fit:contain;" />
          <img src="${assets.cert_iki2}" data-max="160" style="height:48px; object-fit:contain;" />
        </div>
      </div>
    </div>

    <div style="width:48%; border:1.5px solid #CCC; border-radius:8px; padding:16px 20px; display:flex; flex-direction:column; justify-content:space-between;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; border-bottom:2px solid var(--red); padding-bottom:6px; margin-bottom:8px;">
        <span style="font-family:var(--serif); font-size:22px; font-weight:700; color:var(--red);">■ 先輩社員からのメッセージ</span>
        <span style="font-size:13px; color:#666; white-space:nowrap;">※イラストはイメージです</span>
      </div>
      <div style="display:flex; align-items:center; gap:14px; padding-bottom:8px; border-bottom:1px dashed #CCC;">
        <img src="${assets.voice_hk}" data-max="200" style="width:60px; height:76px; object-fit:cover; object-position:top; border-radius:6px; background:#F0F0F0;" />
        <div>
          <div style="font-size:17px; font-weight:700; color:var(--red);">「優しい先輩が多く働きやすいです！」</div>
          <div style="font-size:15px; font-weight:700; color:#222;">H.Kさん（名古屋支店 建築工事部・2025年入社）</div>
          <div style="font-size:14px; color:#444;">分からないこともすぐ聞ける温かい職場で1年目から安心です。</div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:14px; padding-bottom:8px; border-bottom:1px dashed #CCC;">
        <img src="${assets.voice_rk1}" data-max="200" style="width:60px; height:76px; object-fit:cover; object-position:top; border-radius:6px; background:#F0F0F0;" />
        <div>
          <div style="font-size:17px; font-weight:700; color:var(--red);">「ここより良い職場はない！形に残る仕事を」</div>
          <div style="font-size:15px; font-weight:700; color:#222;">R.Kさん（名古屋支店 建築工事部・2025年入社）</div>
          <div style="font-size:14px; color:#444;">15階建てマンションが立ち上がる達成感と充実の福利厚生が魅力！</div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:14px;">
        <img src="${assets.voice_sk}" data-max="200" style="width:60px; height:76px; object-fit:cover; object-position:top; border-radius:6px; background:#F0F0F0;" />
        <div>
          <div style="font-size:17px; font-weight:700; color:var(--red);">「チームで協力する明るい職場！女性も安心」</div>
          <div style="font-size:15px; font-weight:700; color:#222;">S.Kさん（土木女子）＆ A.Kさん（建築・子育て中）</div>
          <div style="font-size:14px; color:#444;">資格取得支援や産休育休・急なお休みへの理解も深く長く働けます。</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom Event & Contact Footer -->
  <div style="background:#181818; color:#FFF; padding:18px 40px;">
    <div style="background:#FFF6E5; color:var(--dark); border:2.5px solid var(--red); border-radius:8px; padding:10px 16px; margin-bottom:14px; display:flex; align-items:center; justify-content:space-between; white-space:nowrap;">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="background:var(--red); color:#FFF; font-size:15px; font-weight:700; padding:4px 10px; border-radius:4px; white-space:nowrap;">注目イベント</span>
        <span style="font-size:19px; font-weight:700; color:var(--red); white-space:nowrap;">
          令和8年5月30日（土）午前の部「愛名会 企業研究会」出展決定！
        </span>
      </div>
      <span style="font-size:14px; font-weight:700; color:#222; white-space:nowrap;">選考会場：名古屋支店（昭和区阿由知通1-12-3）※本社希望も可</span>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-size:18px; font-weight:700; color:#FFD700; margin-bottom:4px; white-space:nowrap;">
          ■ 会社説明会・名古屋市内の現場見学会 随時開催中！お気軽にご連絡ください
        </div>
        <div style="font-size:17px; font-weight:700; white-space:nowrap;">
          お問い合わせ先：木下建設株式会社 総務本部総務部 採用担当　向野 浩幸（こうの ひろゆき）
        </div>
        <div style="font-size:16px; color:#CCC; margin-top:3px; white-space:nowrap;">
          E-Mail: <strong style="color:#FFF;">hr@kinoken.co.jp</strong> ／ 公式サイト: <strong style="color:#FFF;">https://www.kinoshitakensetsu.jp/</strong>
        </div>
      </div>
      <div style="display:flex; gap:16px; text-align:right; white-space:nowrap;">
        <div style="background:#2A2A2A; padding:8px 16px; border-radius:6px; border-left:4px solid var(--red);">
          <div style="font-size:13px; color:#CCC; white-space:nowrap;">名古屋支店 TEL（昭和区阿由知通）</div>
          <div style="font-family:var(--serif); font-size:28px; font-weight:700; color:#FFF;">052-741-6220</div>
        </div>
        <div style="background:#2A2A2A; padding:8px 16px; border-radius:6px; border-left:4px solid var(--red);">
          <div style="font-size:13px; color:#CCC; white-space:nowrap;">本社 総務部 TEL（長野県飯田市）</div>
          <div style="font-family:var(--serif); font-size:28px; font-weight:700; color:#FFF;">0265-22-2780</div>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>`;
}

async function optimizeImagesInPage(page, quality = 0.65) {
  await page.evaluate(async (q) => {
    const imgs = Array.from(document.querySelectorAll('img'));
    for (const img of imgs) {
      if (!img.complete) {
        await new Promise((r) => { img.onload = r; img.onerror = r; });
      }
      const maxDim = parseInt(img.getAttribute('data-max') || '700', 10);
      const nw = img.naturalWidth;
      const nh = img.naturalHeight;
      if (!nw || !nh) continue;
      let tw = nw;
      let th = nh;
      if (nw > maxDim || nh > maxDim) {
        if (nw >= nh) {
          tw = maxDim;
          th = Math.round((nh * maxDim) / nw);
        } else {
          th = maxDim;
          tw = Math.round((nw * maxDim) / nh);
        }
      }
      const canvas = document.createElement('canvas');
      canvas.width = tw;
      canvas.height = th;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, tw, th);
      ctx.drawImage(img, 0, 0, tw, th);
      img.src = canvas.toDataURL('image/jpeg', q);
    }
  }, quality);
}

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  });

  // 1. Build 28-page Pitchbook
  console.log('Generating 28-page pitchbook...');
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const pitchbookHtml = buildPitchbookHtml();
  const pitchbookHtmlPath = path.join(DRAFTS_DIR, 'pitchbook_28p.html');
  fs.writeFileSync(pitchbookHtmlPath, pitchbookHtml, 'utf8');
  await page.goto(`file:///${pitchbookHtmlPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await optimizeImagesInPage(page, 0.65);

  const previewPages = [1, 2, 3, 5, 8, 15, 18, 21, 24, 26, 28];
  for (const pNo of previewPages) {
    const el = await page.$(`#page-${pNo}`);
    if (el) {
      await el.screenshot({
        path: path.join(DRAFTS_DIR, `preview_p${String(pNo).padStart(2, '0')}.jpg`),
        type: 'jpeg',
        quality: 85,
      });
    }
  }

  const pitchbookPdfPath = path.join(FINAL_DIR, 'kinoshita_2027_recruit_pitchbook.pdf');
  await page.pdf({
    path: pitchbookPdfPath,
    width: '1920px',
    height: '1080px',
    printBackground: true,
    margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' },
  });
  let pbStat = fs.statSync(pitchbookPdfPath);
  console.log(`Vector Pitchbook PDF size: ${(pbStat.size / (1024 * 1024)).toFixed(2)} MB`);

  // Guarantee < 3.8MB (if Chromium CJK font subsetting still exceeds 3.8MB, build ultra-clean 1920x1080 slide deck PDF with zero CJK font bloat)
  if (pbStat.size > 3.8 * 1024 * 1024) {
    console.log('Vector PDF exceeded 3.8MB due to CJK font tables; building optimized 1920x1080 28-page PDF...');
    const slideDataUrls = [];
    for (let i = 1; i <= 28; i++) {
      const el = await page.$(`#page-${i}`);
      const buf = await el.screenshot({ type: 'jpeg', quality: 68 });
      slideDataUrls.push(`data:image/jpeg;base64,${buf.toString('base64')}`);
    }
    const slimHtml = `<!DOCTYPE html><html><head><style>
      * { margin:0; padding:0; box-sizing:border-box; }
      @page { size: 1920px 1080px; margin: 0; }
      body { width: 1920px; margin: 0; }
      .p { width: 1920px; height: 1080px; page-break-after: always; break-after: page; overflow: hidden; }
      .p:last-child { page-break-after: auto; break-after: auto; }
      img { width: 1920px; height: 1080px; display: block; }
    </style></head><body>${slideDataUrls.map(u => `<div class="p"><img src="${u}"/></div>`).join('')}</body></html>`;
    const slimPage = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    const slimPath = path.join(DRAFTS_DIR, 'pitchbook_slim.html');
    fs.writeFileSync(slimPath, slimHtml, 'utf8');
    await slimPage.goto(`file:///${slimPath.replace(/\\/g, '/')}`, { waitUntil: 'load' });
    await slimPage.pdf({
      path: pitchbookPdfPath,
      width: '1920px',
      height: '1080px',
      printBackground: true,
      margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' },
    });
    pbStat = fs.statSync(pitchbookPdfPath);
    console.log(`Optimized Pitchbook PDF size: ${(pbStat.size / (1024 * 1024)).toFixed(2)} MB`);
  }

  // 2. Build 1-page A4 Briefing Flyer PDF
  console.log('Generating 1-page briefing flyer PDF...');
  const flyerPage = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
  const flyerHtml = buildFlyerHtml();
  const flyerHtmlPath = path.join(DRAFTS_DIR, 'briefing_flyer.html');
  fs.writeFileSync(flyerHtmlPath, flyerHtml, 'utf8');
  await flyerPage.goto(`file:///${flyerHtmlPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' });
  await flyerPage.evaluate(() => document.fonts.ready);
  await optimizeImagesInPage(flyerPage, 0.78);

  await flyerPage.screenshot({
    path: path.join(DRAFTS_DIR, 'preview_flyer.jpg'),
    type: 'jpeg',
    quality: 88,
  });

  const flyerPdfPath = path.join(FINAL_DIR, 'kinoshita_2027_briefing_flyer.pdf');
  await flyerPage.pdf({
    path: flyerPdfPath,
    width: '1240px',
    height: '1754px',
    printBackground: true,
    margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' },
  });
  const flStat = fs.statSync(flyerPdfPath);
  console.log(`Flyer PDF size: ${(flStat.size / (1024 * 1024)).toFixed(2)} MB`);

  await browser.close();
})();
