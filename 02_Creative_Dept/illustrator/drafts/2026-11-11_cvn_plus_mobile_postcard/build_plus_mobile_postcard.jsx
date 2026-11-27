// cvn プラスモバイル 圧着はがき面デザイン (100mm x 150mm / CMYK印刷仕様)
// コンセプト: 白基調 (White Base) × プライマリーグリーン (C:90 M:0 Y:70 K:0) × モダン・エディトリアルタイポグラフィ

(function () {
  var MM = 72.0 / 25.4;
  var W_MM = 100.0;
  var H_MM = 150.0;
  var BLEED_MM = 3.0;

  // 既存のドキュメントをすべて閉じてクリーンな状態から開始
  while (app.documents.length > 0) {
    app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
  }

  function makeCMYK(c, m, y, k) {
    var col = new CMYKColor();
    col.cyan = c;
    col.magenta = m;
    col.yellow = y;
    col.black = k;
    return col;
  }

  function getFont(names) {
    for (var i = 0; i < names.length; i++) {
      try {
        return app.textFonts.getByName(names[i]);
      } catch (e) {}
    }
    return app.textFonts[0];
  }

  // ドキュメント新規作成 (CMYK / 100mm x 150mm)
  var preset = new DocumentPreset();
  preset.title = "cvn_plus_mobile_postcard_100x150";
  preset.width = W_MM * MM;
  preset.height = H_MM * MM;
  preset.colorMode = DocumentColorSpace.CMYK;
  preset.units = RulerUnits.Millimeters;

  var doc = app.documents.addDocument(DocumentColorSpace.CMYK, preset);
  var r = doc.artboards[0].artboardRect; // [left, top, right, bottom]

  function px(mmX) { return r[0] + mmX * MM; }
  function py(mmY) { return r[1] - mmY * MM; }

  // スウォッチ登録（白基調 ＋ C90M0Y70K0 プライマリーグリーン ＋ 無彩色モノトーン）
  function addSwatch(name, col) {
    try {
      var sw = doc.swatches.add();
      sw.name = name;
      sw.color = col;
    } catch (e) {}
    return col;
  }

  var C_PRIMARY    = addSwatch("CVN_Primary_C90M0Y70K0", makeCMYK(90, 0, 70, 0));
  var C_MINT_TINT  = addSwatch("CVN_Mint_Tint",          makeCMYK(7, 0, 5, 0));
  var C_MINT_LINE  = addSwatch("CVN_Mint_Line",          makeCMYK(35, 0, 25, 0));
  var C_MINT_SOFT  = addSwatch("CVN_Mint_Soft",          makeCMYK(16, 0, 12, 0));
  var C_BLACK      = addSwatch("CVN_RichBlack",          makeCMYK(20, 15, 15, 90));
  var C_DARK_GRAY  = addSwatch("CVN_DarkGray",           makeCMYK(15, 10, 10, 60));
  var C_LIGHT_GRAY = addSwatch("CVN_LightGray",          makeCMYK(8, 5, 5, 18));
  var C_WHITE      = makeCMYK(0, 0, 0, 0);

  // フォント定義（源ノ角ゴシック JP / SourceHanSansJP に完全統一）
  var F_JP_HEAVY = getFont(["SourceHanSansJP-Heavy", "SourceHanSans-Bold"]);
  var F_JP_BOLD  = getFont(["SourceHanSansJP-Bold", "SourceHanSans-Bold"]);
  var F_JP_MED   = getFont(["SourceHanSansJP-Medium", "SourceHanSans-Medium"]);
  var F_EN_BLACK = getFont(["SourceHanSansJP-Heavy", "SourceHanSans-Bold"]);
  var F_EN_BOLD  = getFont(["SourceHanSansJP-Bold", "SourceHanSans-Bold"]);

  // 図形描画ヘルパー
  function drawRect(layer, x, y, w, h, fillCol, strokeCol, strokeW) {
    var p = layer.pathItems.rectangle(py(y), px(x), w * MM, h * MM);
    if (fillCol) { p.filled = true; p.fillColor = fillCol; } else { p.filled = false; }
    if (strokeCol) { p.stroked = true; p.strokeColor = strokeCol; p.strokeWidth = (strokeW || 0.3) * MM; } else { p.stroked = false; }
    return p;
  }

  function drawRoundRect(layer, x, y, w, h, rad, fillCol, strokeCol, strokeW) {
    var p = layer.pathItems.roundedRectangle(py(y), px(x), w * MM, h * MM, rad * MM, rad * MM);
    if (fillCol) { p.filled = true; p.fillColor = fillCol; } else { p.filled = false; }
    if (strokeCol) { p.stroked = true; p.strokeColor = strokeCol; p.strokeWidth = (strokeW || 0.3) * MM; } else { p.stroked = false; }
    return p;
  }

  function drawCircle(layer, cx, cy, diam, fillCol, strokeCol, strokeW) {
    var p = layer.pathItems.ellipse(py(cy - diam / 2), px(cx - diam / 2), diam * MM, diam * MM);
    if (fillCol) { p.filled = true; p.fillColor = fillCol; } else { p.filled = false; }
    if (strokeCol) { p.stroked = true; p.strokeColor = strokeCol; p.strokeWidth = (strokeW || 0.3) * MM; } else { p.stroked = false; }
    return p;
  }

  function drawLine(layer, x1, y1, x2, y2, strokeCol, strokeW) {
    var p = layer.pathItems.add();
    p.setEntirePath([[px(x1), py(y1)], [px(x2), py(y2)]]);
    p.filled = false;
    p.stroked = true;
    p.strokeColor = strokeCol;
    p.strokeWidth = (strokeW || 0.25) * MM;
    return p;
  }

  function drawPlusSymbol(layer, cx, cy, size, thickness, fillCol, strokeCol, strokeW) {
    // 一体型のクロス（＋）ポリゴンを12頂点で正確に描画（重なり線が出ない美しいベクター）
    var hs = size / 2.0;
    var ht = thickness / 2.0;
    var pts = [
      [cx - ht, cy - hs],
      [cx + ht, cy - hs],
      [cx + ht, cy - ht],
      [cx + hs, cy - ht],
      [cx + hs, cy + ht],
      [cx + ht, cy + ht],
      [cx + ht, cy + hs],
      [cx - ht, cy + hs],
      [cx - ht, cy + ht],
      [cx - hs, cy + ht],
      [cx - hs, cy - ht],
      [cx - ht, cy - ht]
    ];
    var p = layer.pathItems.add();
    var arr = [];
    for (var i = 0; i < pts.length; i++) {
      arr.push([px(pts[i][0]), py(pts[i][1])]);
    }
    p.setEntirePath(arr);
    p.closed = true;
    if (fillCol) { p.filled = true; p.fillColor = fillCol; } else { p.filled = false; }
    if (strokeCol) { p.stroked = true; p.strokeColor = strokeCol; p.strokeWidth = (strokeW || 0.25) * MM; } else { p.stroked = false; }
    return p;
  }

  function addAreaText(layer, x, y, w, h, content, font, sizePt, col, align, tracking, leadingPt) {
    var box = layer.pathItems.rectangle(py(y), px(x), w * MM, h * MM);
    var tf = layer.textFrames.areaText(box);
    tf.contents = content;
    var attr = tf.textRange.characterAttributes;
    attr.textFont = font;
    attr.size = sizePt;
    attr.fillColor = col;
    if (tracking !== undefined && tracking !== null) {
      attr.tracking = tracking;
    }
    if (leadingPt) {
      attr.autoLeading = false;
      attr.leading = leadingPt;
    }
    for (var i = 0; i < tf.paragraphs.length; i++) {
      tf.paragraphs[i].paragraphAttributes.justification = align || Justification.LEFT;
    }
    return tf;
  }

  // レイヤー構成
  var layBg    = doc.layers[0]; layBg.name = "01_White_Base_Geometry";
  var layBrand = doc.layers.add(); layBrand.name = "02_Brand_Typography";
  var layPrice = doc.layers.add(); layPrice.name = "03_Editorial_Price";
  var layValue = doc.layers.add(); layValue.name = "04_Three_Pillars";
  var layFoot  = doc.layers.add(); layFoot.name = "05_Minimal_Footer";

  // =========================================================
  // 1. 白基調ベース & 洗練されたジオメトリック・プラス装飾
  // =========================================================
  // 紙面全体: 純白ベース（塗り足し3mm込み）
  drawRect(layBg, -BLEED_MM, -BLEED_MM, W_MM + BLEED_MM * 2, H_MM + BLEED_MM * 2, C_WHITE, null);

  // 上端エッジのプライマリーグリーン・アクセントバー（塗り足し込み）
  drawRect(layBg, -BLEED_MM, -BLEED_MM, W_MM + BLEED_MM * 2, BLEED_MM + 2.5, C_PRIMARY, null);

  // 右上〜中盤の建築的・大型「＋」ジオメトリックモチーフ（文字やヘッダー線と一切干渉しない黄金空間 x:65-99, y:23-57 に配置）
  // 1) 極薄ミントの大型ソリッド「＋」
  drawPlusSymbol(layBg, 83.5, 41.0, 31.0, 9.2, C_MINT_TINT, null);
  // 2) 少しオフセットした位置に細いグリーンラインの「＋」（モダングラフィックの奥行き）
  drawPlusSymbol(layBg, 79.5, 44.0, 25.0, 7.2, null, C_MINT_SOFT, 0.25);

  // =========================================================
  // 2. ヘッダー & 公式 cvn ベクターロゴ配置
  // =========================================================
  // 公式 logo-nn4.svg を開いてベクターパスをコピーし、C:90 M:0 Y:70 K:0 を厳密適用
  var svgPath = new File("G:/マイドライブ/obsidian/nobuyukitakahashi/02_Creative_Dept/illustrator/drafts/logo-nn4.svg");
  if (svgPath.exists) {
    var svgDoc = app.open(svgPath);
    var topItem = svgDoc.pageItems[0];
    var logoGroup = topItem.duplicate(layBrand, ElementPlacement.PLACEATBEGINNING);
    logoGroup.name = "cvn_Official_Logo";
    svgDoc.close(SaveOptions.DONOTSAVECHANGES);
    app.activeDocument = doc;

    // グループ内の全PathItemにC:90 M:0 Y:70 K:0を適用
    for (var pi = 0; pi < logoGroup.pathItems.length; pi++) {
      var pItem = logoGroup.pathItems[pi];
      if (pItem.filled) {
        pItem.fillColor = C_PRIMARY;
      }
      if (pItem.stroked) {
        pItem.strokeColor = C_PRIMARY;
      }
    }

    // ロゴのサイズと位置を調整（左マージン 9mm, 上から 10.0mm, 幅 27mm）
    var targetLogoW = 27.0 * MM;
    var scaleRatio = (targetLogoW / logoGroup.width) * 100.0;
    logoGroup.resize(scaleRatio, scaleRatio);
    logoGroup.position = [px(9.0), py(10.0)];
  }

  // ヘッダー下の極細セパレーターライン
  drawLine(layBrand, 9.0, 19.5, 91.0, 19.5, C_LIGHT_GRAY, 0.18);

  // =========================================================
  // 3. ブランド・ヒーロー・タイポグラフィ
  // =========================================================
  // 英語リードコピー
  addAreaText(layBrand, 9.0, 23.5, 82.0, 4.0, "SMART MOBILE SERVICE", F_EN_BOLD, 7.2, C_PRIMARY, Justification.LEFT, 220);

  // サブキャッチ（ブランド導入）
  addAreaText(layBrand, 9.0, 28.5, 82.0, 5.0, "テレビ・ネットに「＋」するだけ。", F_JP_BOLD, 10.0, C_DARK_GRAY, Justification.LEFT, 20);

  // メインブランドタイトル: 「プラス」 (Rich Black) ＋ 「モバイル」 (Primary Green C90M0Y70K0)
  addAreaText(layBrand, 8.0, 33.6, 75.0, 14.5, "プラス", F_JP_HEAVY, 33.5, C_BLACK, Justification.LEFT, -40);
  // 「プラス」の右横に象徴的なプライマリーグリーンのソリッド「＋」
  drawPlusSymbol(layBrand, 52.0, 39.6, 7.6, 2.3, C_PRIMARY, null);

  addAreaText(layBrand, 8.0, 45.8, 82.0, 14.5, "モバイル", F_JP_HEAVY, 33.5, C_PRIMARY, Justification.LEFT, -40);

  // ブランド・タグライン（左にプライマリーグリーンの縦アクセントバー）
  drawRect(layBrand, 9.0, 61.5, 1.1, 8.5, C_PRIMARY, null);
  addAreaText(layBrand, 12.2, 61.3, 78.0, 5.0, "今のスマホそのまま、月額ずっとこの安さ。", F_JP_BOLD, 9.5, C_BLACK, Justification.LEFT, 10);
  addAreaText(layBrand, 12.2, 66.3, 78.0, 4.5, "光キャストTV ＋ いい-NET光 セット割プラン", F_JP_MED, 7.2, C_DARK_GRAY, Justification.LEFT, 10);

  // =========================================================
  // 4. モダン・エディトリアル・プライスセクション
  // =========================================================
  var pTop = 74.0;
  var pHeight = 35.5;

  // 背景にごく淡いミントティントを敷き、上下をシャープなグリーン罫線で挟む（角丸ボックスを排除）
  drawRect(layPrice, 9.0, pTop, 82.0, pHeight, C_MINT_TINT, null);
  drawRect(layPrice, 9.0, pTop, 82.0, 0.8, C_PRIMARY, null);
  drawLine(layPrice, 9.0, pTop + pHeight, 91.0, pTop + pHeight, C_PRIMARY, 0.35);

  // 左側ブロック: 音声付きSIM / 3GBプラン
  drawRect(layPrice, 13.0, pTop + 4.2, 24.0, 4.8, C_PRIMARY, null);
  addAreaText(layPrice, 13.0, pTop + 5.2, 24.0, 3.8, "音声付きSIM", F_JP_BOLD, 7.2, C_WHITE, Justification.CENTER, 30);

  addAreaText(layPrice, 12.8, pTop + 10.2, 25.0, 8.0, "3GB", F_EN_BLACK, 19.0, C_BLACK, Justification.LEFT, -10);
  addAreaText(layPrice, 13.0, pTop + 17.8, 25.0, 4.5, "プラン / 月額", F_JP_BOLD, 7.8, C_DARK_GRAY, Justification.LEFT, 10);

  // 中央〜右側: 特大 550 円(税込)
  addAreaText(layPrice, 38.0, pTop + 2.8, 39.0, 20.0, "550", F_EN_BLACK, 45.0, C_PRIMARY, Justification.RIGHT, -35);
  addAreaText(layPrice, 78.2, pTop + 6.5, 11.0, 4.0, "(税込)", F_JP_BOLD, 6.8, C_DARK_GRAY, Justification.LEFT, 0);
  addAreaText(layPrice, 78.0, pTop + 11.2, 12.0, 9.0, "円〜", F_JP_HEAVY, 15.0, C_BLACK, Justification.LEFT, -20);

  // プライス内セパレーター（極細ライン）
  drawLine(layPrice, 13.0, pTop + 24.2, 87.0, pTop + 24.2, C_MINT_LINE, 0.2);

  // 下段: 選べる3つの容量プラン（整然とした3カラム・タイポグラフィ）
  var plans = [
    { cap: "3GB",  price: "550円" },
    { cap: "10GB", price: "1,650円" },
    { cap: "30GB", price: "2,750円" }
  ];
  var colW = 74.0 / 3.0;
  for (var i = 0; i < 3; i++) {
    var cx = 13.0 + i * colW;
    if (i > 0) {
      drawLine(layPrice, cx, pTop + 26.0, cx, pTop + 33.2, C_MINT_LINE, 0.2);
    }
    addAreaText(layPrice, cx + 1.5, pTop + 26.2, 10.5, 4.0, plans[i].cap, F_EN_BOLD, 7.8, C_PRIMARY, Justification.LEFT, 0);
    addAreaText(layPrice, cx + 10.5, pTop + 26.0, colW - 12.0, 4.5, plans[i].price, F_JP_HEAVY, 8.2, C_BLACK, Justification.RIGHT, 0);
    addAreaText(layPrice, cx + 1.5, pTop + 30.2, colW - 3.0, 3.5, "月額（税込）", F_JP_MED, 5.2, C_DARK_GRAY, Justification.RIGHT, 0);
  }

  // =========================================================
  // 5. 3つのコアバリュー（01 / 02 / 03 スイスグリッド）
  // =========================================================
  var vTop = 114.5;
  var vColW = 25.5;
  var vGap = 2.75;
  var values = [
    { num: "01", title: "ドコモ回線",     sub: "全国エリアで安心品質" },
    { num: "02", title: "スマホそのまま", sub: "SIM差替・2枚までOK" },
    { num: "03", title: "ギガ繰越対応",   sub: "余った容量は翌月へ" }
  ];

  for (var v = 0; v < 3; v++) {
    var vx = 9.0 + v * (vColW + vGap);
    // ナンバー + グリーンショートライン
    addAreaText(layValue, vx, vTop, 10.0, 4.5, values[v].num, F_EN_BLACK, 9.0, C_PRIMARY, Justification.LEFT, 20);
    drawRect(layValue, vx + 6.8, vTop + 1.8, vColW - 6.8, 0.35, C_MINT_LINE, null);

    // タイトル & サブコピー
    addAreaText(layValue, vx, vTop + 5.2, vColW, 4.5, values[v].title, F_JP_BOLD, 8.0, C_BLACK, Justification.LEFT, 0);
    addAreaText(layValue, vx, vTop + 9.8, vColW, 3.8, values[v].sub, F_JP_MED, 5.8, C_DARK_GRAY, Justification.LEFT, 0);
  }

  // =========================================================
  // 6. ミニマル・フッター（白基調のままシャープに締める）
  // =========================================================
  drawLine(layFoot, 9.0, 131.5, 91.0, 131.5, C_LIGHT_GRAY, 0.2);

  // 左側: Web検索ボックス（白背景＋プライマリーグリーン枠）
  drawRect(layFoot, 9.0, 135.0, 44.0, 5.6, C_WHITE, C_PRIMARY, 0.35);
  // 左端のグリーンアクセントブロック
  drawRect(layFoot, 9.0, 135.0, 1.8, 5.6, C_PRIMARY, null);
  addAreaText(layFoot, 12.5, 136.4, 34.0, 4.0, "cvn プラスモバイル", F_JP_BOLD, 7.2, C_BLACK, Justification.LEFT, 10);
  // ミニマルな虫眼鏡アイコン（グリーン）
  drawCircle(layFoot, 48.8, 137.3, 1.9, null, C_PRIMARY, 0.38);
  drawLine(layFoot, 49.55, 138.05, 50.55, 139.05, C_PRIMARY, 0.38);

  // URL
  addAreaText(layFoot, 9.0, 142.0, 48.0, 3.8, "castvision.net/service/mobile/", F_EN_BOLD, 6.0, C_DARK_GRAY, Justification.LEFT, 15);

  // 右側: フリーコール & 社名
  addAreaText(layFoot, 55.0, 134.8, 36.0, 3.5, "お問い合わせ（受付 9:00〜17:00）", F_JP_MED, 5.5, C_DARK_GRAY, Justification.RIGHT, 0);
  addAreaText(layFoot, 55.0, 137.8, 36.0, 5.0, "0800-800-2794", F_EN_BLACK, 10.0, C_BLACK, Justification.RIGHT, 20);
  addAreaText(layFoot, 55.0, 142.5, 36.0, 3.8, "株式会社シーブイエヌ", F_JP_BOLD, 6.5, C_BLACK, Justification.RIGHT, 20);

  // 最下端エッジ: プライマリーグリーン・ボトムバー（塗り足し込み）
  drawRect(layFoot, -BLEED_MM, 148.0, W_MM + BLEED_MM * 2, 2.0 + BLEED_MM, C_PRIMARY, null);

  return "OK: Rebuilt White & C90M0Y70K0 Modern Postcard";
})();
