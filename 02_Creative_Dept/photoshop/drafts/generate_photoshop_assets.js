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
  night_condo: getAssetDataUrl('img_obj59_1980x2250.jpg'),
  condo_ext: getAssetDataUrl('img_obj50_1195x2250.jpg'),
  smart_ic: getAssetDataUrl('img_obj161_1362x1500.jpg'),
  logo_sm: getAssetDataUrl('img_obj36_300x300.jpg'),
  logo_lg: getAssetDataUrl('img_obj267_434x434.jpg'),
  cover_team: getAssetDataUrl('img_obj11_2079x1309.jpg'),
  img175: getAssetDataUrl('img_obj175_663x883.jpg'),
  img174: getAssetDataUrl('img_obj174_663x883.jpg'),
  img173: getAssetDataUrl('img_obj173_663x883.jpg'),
  img179: getAssetDataUrl('img_obj179_1259x1679.jpg'),
  img183: getAssetDataUrl('img_obj183_1259x1679.jpg'),
};

function buildPhotoCardsHtml() {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&family=Noto+Serif+JP:wght@900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
<style>
  :root {
    --red: #D70015;
    --dark: #0F141D;
    --yellow: #FFD700;
    --sans: 'Noto Sans JP', sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #222; font-family: var(--sans); font-weight: 900; }
  .card {
    position: relative;
    width: 1600px;
    height: 1000px;
    overflow: hidden;
    background: #FFFFFF;
    margin-bottom: 40px;
  }
</style>
</head>
<body>

<!-- ==================== PHOTO 01: 名古屋の高層マンション×創業113年 ==================== -->
<div class="card" id="kinoshita_photo01">
  <img src="${assets.night_condo}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:left center;" />
  <div style="position:absolute; inset:0; background:linear-gradient(90deg, rgba(10,14,22,0.28) 0%, rgba(10,14,22,0.82) 36%, rgba(10,14,22,0.96) 100%);"></div>
  <div style="position:absolute; inset:0; border:16px solid var(--red); pointer-events:none;"></div>

  <div style="position:relative; z-index:10; width:100%; height:100%; padding:64px 72px; display:flex; flex-direction:column; justify-content:space-between; align-items:flex-end; text-align:right;">
    <div style="background:rgba(15,20,29,0.85); border-left:18px solid var(--red); padding:28px 44px; border-radius:12px; box-shadow:0 12px 32px rgba(0,0,0,0.6);">
      <div style="font-size:132px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.02em; text-shadow:0 6px 20px rgba(0,0,0,0.8); white-space:nowrap;">
        名古屋の空に残る仕事
      </div>
    </div>

    <div style="background:var(--red); border:6px solid #FFFFFF; padding:28px 48px; border-radius:16px; box-shadow:0 16px 36px rgba(0,0,0,0.65);">
      <div style="font-size:144px; font-weight:900; color:#FFFFFF; line-height:1.1; letter-spacing:-0.02em; white-space:nowrap;">
        高層マンション <span style="color:var(--yellow); font-size:158px;">29棟</span>
      </div>
    </div>

    <div style="display:flex; align-items:center; gap:32px; background:rgba(255,255,255,0.96); padding:22px 44px; border-radius:16px; box-shadow:0 12px 32px rgba(0,0,0,0.6);">
      <img src="${assets.logo_sm}" style="width:118px; height:118px; object-fit:contain;" />
      <div style="font-size:122px; font-weight:900; color:#111111; line-height:1.1; letter-spacing:-0.02em; white-space:nowrap;">
        創業<span style="color:var(--red);">113年</span> 木下建設
      </div>
    </div>
  </div>
</div>

<!-- ==================== PHOTO 02: 圧倒的な待遇・働きやすさ 4大数値 ==================== -->
<div class="card" id="kinoshita_photo02" style="background:#0F141D; padding:20px; display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); grid-template-rows:minmax(0, 1fr) minmax(0, 1fr); gap:20px;">
  <!-- 左上: 初任給 28.9万円 -->
  <div style="background:#FFFFFF; border-radius:18px; border-top:18px solid var(--red); padding:20px 16px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; overflow:hidden;">
    <div style="font-size:90px; font-weight:900; color:#111111; line-height:1.15; letter-spacing:-0.04em; white-space:nowrap;">
      初任給 <span style="color:var(--red); font-size:116px;">28.9万円</span>
    </div>
    <div style="margin-top:20px; background:#FFF0F2; border:4px solid var(--red); border-radius:12px; padding:8px 24px; font-size:68px; font-weight:900; color:var(--red); line-height:1.2; letter-spacing:-0.02em; white-space:nowrap;">
      名古屋支店・手当込
    </div>
  </div>

  <!-- 右上: 賞与 年3回 -->
  <div style="background:#182232; border-radius:18px; border-top:18px solid var(--yellow); padding:20px 16px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; overflow:hidden;">
    <div style="font-size:100px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.02em; white-space:nowrap;">
      賞与 <span style="color:var(--yellow); font-size:132px;">年3回</span>
    </div>
    <div style="margin-top:20px; background:rgba(255,255,255,0.12); border:4px solid var(--yellow); border-radius:12px; padding:8px 32px; font-size:68px; font-weight:900; color:var(--yellow); line-height:1.2; white-space:nowrap;">
      令和7年度実績
    </div>
  </div>

  <!-- 左下: 残業 月11時間 -->
  <div style="background:#182232; border-radius:18px; border-top:18px solid var(--yellow); padding:20px 16px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; overflow:hidden;">
    <div style="font-size:96px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.03em; white-space:nowrap;">
      残業 <span style="color:var(--yellow); font-size:122px;">月11時間</span>
    </div>
    <div style="margin-top:20px; background:rgba(255,255,255,0.12); border:4px solid var(--yellow); border-radius:12px; padding:8px 24px; font-size:68px; font-weight:900; color:#FFFFFF; line-height:1.2; letter-spacing:-0.02em; white-space:nowrap;">
      若手平均・DX推進
    </div>
  </div>

  <!-- 右下: 年間休日 123日 -->
  <div style="background:#FFFFFF; border-radius:18px; border-top:18px solid var(--red); padding:20px 16px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; overflow:hidden;">
    <div style="font-size:88px; font-weight:900; color:#111111; line-height:1.15; letter-spacing:-0.04em; white-space:nowrap;">
      年間休日 <span style="color:var(--red); font-size:120px;">123日</span>
    </div>
    <div style="margin-top:20px; background:#FFF0F2; border:4px solid var(--red); border-radius:12px; padding:8px 24px; font-size:68px; font-weight:900; color:var(--red); line-height:1.2; letter-spacing:-0.02em; white-space:nowrap;">
      有給 入社時10日
    </div>
  </div>
</div>

<!-- ==================== PHOTO 03: 名古屋支店の施工実績・勤務地 ==================== -->
<div class="card" id="kinoshita_photo03" style="display:flex;">
  <div style="width:500px; height:1000px; position:relative; flex-shrink:0;">
    <img src="${assets.condo_ext}" style="width:100%; height:100%; object-fit:cover; object-position:center top;" />
  </div>
  <div style="width:1100px; height:1000px; background:var(--dark); border-left:16px solid var(--red); padding:52px 36px; display:flex; flex-direction:column; justify-content:space-around; align-items:center; text-align:center;">
    <div style="width:100%; background:#FFFFFF; border-radius:16px; padding:26px 16px;">
      <div style="font-size:98px; font-weight:900; color:#111111; line-height:1.15; letter-spacing:-0.02em; white-space:nowrap;">
        勤務地：<span style="color:var(--red);">名古屋支店</span>
      </div>
    </div>

    <div style="font-size:102px; font-weight:900; color:var(--yellow); line-height:1.15; letter-spacing:-0.02em; white-space:nowrap;">
      昭和区・御器所駅圏
    </div>

    <div style="width:100%; background:var(--red); border:5px solid #FFFFFF; border-radius:16px; padding:26px 16px;">
      <div style="font-size:84px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.02em; white-space:nowrap;">
        都心RC15階建 多数施工
      </div>
    </div>
  </div>
</div>

<!-- ==================== PHOTO 04: 奨学金返還支援＆資格全額負担 ==================== -->
<div class="card" id="kinoshita_photo04" style="display:flex; flex-direction:column;">
  <!-- 上段: 奨学金返還支援 / 月2.5万円×10年 -->
  <div style="height:500px; width:100%; background:#FFFFFF; border:16px solid var(--red); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:20px 40px;">
    <div style="background:var(--red); color:#FFFFFF; font-size:92px; font-weight:900; padding:10px 64px; border-radius:16px; line-height:1.15; margin-bottom:24px; white-space:nowrap;">
      奨学金返還支援
    </div>
    <div style="font-size:148px; font-weight:900; color:var(--red); line-height:1.08; letter-spacing:-0.01em; white-space:nowrap;">
      月2.5万円×10年
    </div>
  </div>

  <!-- 下段: 資格の講習・受験費用 / 会社が全額負担 -->
  <div style="height:500px; width:100%; background:var(--dark); border-left:16px solid var(--yellow); border-right:16px solid var(--yellow); border-bottom:16px solid var(--yellow); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:20px 40px;">
    <div style="font-size:94px; font-weight:900; color:#FFFFFF; line-height:1.15; margin-bottom:20px; white-space:nowrap;">
      資格の講習・受験費用
    </div>
    <div style="background:var(--yellow); color:#111111; font-size:144px; font-weight:900; padding:10px 64px; border-radius:16px; line-height:1.1; letter-spacing:-0.01em; white-space:nowrap;">
      会社が全額負担
    </div>
  </div>
</div>

<!-- ==================== PHOTO 05: 大規模インフラ土木 × 建設DX ==================== -->
<div class="card" id="kinoshita_photo05" style="display:flex;">
  <div style="width:500px; height:1000px; position:relative; flex-shrink:0;">
    <img src="${assets.smart_ic}" style="width:100%; height:100%; object-fit:cover; object-position:center;" />
  </div>
  <div style="width:1100px; height:1000px; background:var(--dark); border-left:16px solid var(--red); padding:52px 36px; display:flex; flex-direction:column; justify-content:space-around; align-items:center; text-align:center;">
    <div style="width:100%; background:#FFFFFF; border-radius:16px; padding:26px 16px;">
      <div style="font-size:102px; font-weight:900; color:#111111; line-height:1.15; letter-spacing:-0.01em; white-space:nowrap;">
        大規模インフラ土木
      </div>
    </div>

    <div style="font-size:94px; font-weight:900; color:var(--yellow); line-height:1.15; letter-spacing:-0.02em; white-space:nowrap;">
      橋梁・トンネル・道路
    </div>

    <div style="width:100%; background:var(--red); border:5px solid #FFFFFF; border-radius:16px; padding:26px 16px;">
      <div style="font-size:84px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.03em; white-space:nowrap;">
        DXで作業 <span style="color:var(--yellow);">▲23.4%削減</span>
      </div>
    </div>
  </div>
</div>

<!-- ==================== PHOTO 06: リクルートサイト特大QRコード＆URL専用パネル ==================== -->
<div class="card" id="kinoshita_photo06" style="display:flex; background:var(--dark);">
  <!-- 左側: 740px幅に720x720 超特大・高コントラストQRコード -->
  <div style="width:740px; height:1000px; background:#FFFFFF; border-right:14px solid var(--red); display:flex; flex-direction:column; align-items:center; justify-content:center; padding:16px; flex-shrink:0;">
    <div id="qr-recruit" style="width:708px; height:708px; display:flex; align-items:center; justify-content:center; background:#FFFFFF; border:8px solid #111111; border-radius:16px; padding:10px;"></div>
    <div style="margin-top:18px; background:var(--red); color:#FFFFFF; font-size:72px; font-weight:900; padding:8px 32px; border-radius:12px; line-height:1.15; white-space:nowrap;">
      ▲ スマホでQR読取
    </div>
  </div>

  <!-- 右側: 幅860px 特大文字パネル -->
  <div style="width:860px; height:1000px; background:var(--dark); padding:32px 24px; display:flex; flex-direction:column; justify-content:space-between;">
    <!-- 1. 木下建設 リクルートサイト (92px) -->
    <div style="background:#FFFFFF; border-radius:16px; padding:18px 20px; border-left:16px solid var(--red);">
      <div style="font-size:76px; font-weight:900; color:var(--red); line-height:1.1;">木下建設</div>
      <div style="font-size:92px; font-weight:900; color:#111111; line-height:1.12; letter-spacing:-0.03em; white-space:nowrap;">
        リクルートサイト
      </div>
    </div>

    <!-- 2. Web説明会・見学会申込 (70px) -->
    <div style="font-size:70px; font-weight:900; color:var(--yellow); line-height:1.18; letter-spacing:-0.04em; text-align:center; white-space:nowrap;">
      Web説明会・見学会申込
    </div>

    <!-- 3. kinoshitakensetsu.jp/recruit (72px 極太・背景ハイライト枠付き) -->
    <div style="background:var(--red); border:6px solid #FFFFFF; border-radius:16px; padding:20px 16px; text-align:center;">
      <div style="font-size:72px; font-weight:900; color:#FFFFFF; line-height:1.15; letter-spacing:-0.03em; white-space:nowrap;">
        kinoshitakensetsu.jp
      </div>
      <div style="font-size:82px; font-weight:900; color:var(--yellow); line-height:1.12; letter-spacing:0.01em; white-space:nowrap;">
        /recruit
      </div>
    </div>

    <!-- 4. ★5/30(土) 愛名会 企業研究会参加 (68px) -->
    <div style="background:#1E293B; border:4px solid var(--yellow); border-radius:16px; padding:16px 16px; text-align:center;">
      <div style="font-size:68px; font-weight:900; color:#FFFFFF; line-height:1.18; letter-spacing:-0.02em; white-space:nowrap;">
        <span style="color:var(--yellow);">★5/30(土)</span> 愛名会
      </div>
      <div style="font-size:72px; font-weight:900; color:var(--yellow); line-height:1.18; letter-spacing:-0.01em; white-space:nowrap;">
        企業研究会参加！
      </div>
    </div>
  </div>
</div>

<script>
  (function() {
    if (typeof qrcode !== 'undefined') {
      var qr = qrcode(0, 'L');
      qr.addData('https://www.kinoshitakensetsu.jp/recruit');
      qr.make();
      var el = document.getElementById('qr-recruit');
      if (el) {
        el.innerHTML = qr.createSvgTag({ cellSize: 16, margin: 2, scalable: true });
        var svg = el.querySelector('svg');
        if (svg) {
          svg.style.width = '672px';
          svg.style.height = '672px';
        }
      }
    }
  })();
</script>
</body>
</html>`;
}

function buildThumbnailGridHtml(photoPaths) {
  const itemsHtml = photoPaths.map((p, idx) => {
    const buf = fs.readFileSync(p);
    const b64 = `data:image/jpeg;base64,${buf.toString('base64')}`;
    return `
      <div style="width:240px; height:150px; border:1px solid #CCC; overflow:hidden; background:#FFF;">
        <img src="${b64}" style="width:240px; height:150px; object-fit:cover; display:block;" />
      </div>
    `;
  }).join('');

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #F5F5F5; font-family: sans-serif; padding: 16px; width: 760px; }
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 240px);
    gap: 8px;
    width: 736px;
  }
</style>
</head>
<body>
  <div style="font-size:14px; font-weight:bold; color:#333; margin-bottom:10px;">
    愛名会 公開ページ実寸シミュレーション（240×150px × 6枚 ／ 全体幅760px）
  </div>
  <div class="grid">
    ${itemsHtml}
  </div>
</body>
</html>`;
}

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  });

  const photoPage = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  const photoHtmlPath = path.join(DRAFTS_DIR, 'photo_cards.html');
  fs.writeFileSync(photoHtmlPath, buildPhotoCardsHtml(), 'utf8');
  await photoPage.goto(`file:///${photoHtmlPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' });
  await photoPage.evaluate(() => document.fonts.ready);

  const generatedPaths = [];
  for (let i = 1; i <= 6; i++) {
    const id = `kinoshita_photo0${i}`;
    const el = await photoPage.$(`#${id}`);
    const outPath = path.join(FINAL_DIR, `${id}.jpg`);
    await el.screenshot({ path: outPath, type: 'jpeg', quality: 92 });
    const st = fs.statSync(outPath);
    console.log(`${id}.jpg: ${(st.size / 1024).toFixed(1)} KB`);
    generatedPaths.push(outPath);
  }

  // Generate 240x150 thumbnail grid verification image (width 760px)
  const thumbPage = await browser.newPage({ viewport: { width: 760, height: 360 } });
  const thumbHtmlPath = path.join(DRAFTS_DIR, 'thumbnail_grid_check.html');
  fs.writeFileSync(thumbHtmlPath, buildThumbnailGridHtml(generatedPaths), 'utf8');
  await thumbPage.goto(`file:///${thumbHtmlPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' });
  const thumbOutPath = path.join(DRAFTS_DIR, 'thumbnail_grid_check.jpg');
  await thumbPage.screenshot({ path: thumbOutPath, type: 'jpeg', quality: 92 });
  console.log(`thumbnail_grid_check.jpg: ${(fs.statSync(thumbOutPath).size / 1024).toFixed(1)} KB`);

  await browser.close();
})();
