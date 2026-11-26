// build_furusato2026_youtube_thumb.jsx
// 2026 YouTube 
// Adobe Photoshop 2027 (ExtendScript ES3)  1920x1080 Master PSD + 1280x720 YouTube PNG/JPG

app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;

return (function () {
    var PARTS_DIR = "C:/Users/nobuy/OneDrive/My Documents/\u30af\u30e9\u30a4\u30a2\u30f3\u30c8\u5225/\u98ef\u7530\u5546\u5de5\u4f1a\u8b70\u6240_\u98ef\u7530\u8077\u696d\u5b89\u5b9a\u5354\u4f1a/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a_\u30d1\u30fc\u30c4";
    var OUT_DIR   = "g:/\u30de\u30a4\u30c9\u30e9\u30a4\u30d6/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/furusato2026_youtube_thumb";

    // Close previous draft of this same thumbnail document if open
    for (var di = app.documents.length - 1; di >= 0; di--) {
        if (app.documents[di].name.indexOf("Furusato2026_YouTube_Thumbnail") === 0) {
            app.documents[di].close(SaveOptions.DONOTSAVECHANGES);
        }
    }

    var outFolder = new Folder(OUT_DIR);
    if (!outFolder.exists) { outFolder.create(); }

    var W = 1920;
    var H = 1080;
    var RES = 72;

    var FONT_BLACK = "NotoSansJP-Black";
    var FONT_BOLD  = "NotoSansJP-Bold";

    function rgb(r, g, b) {
        var c = new SolidColor();
        c.rgb.red = r;
        c.rgb.green = g;
        c.rgb.blue = b;
        return c;
    }

    var C = {
        navyDark:    rgb(10, 24, 54),     // #0A1836
        navy:        rgb(20, 40, 75),     // #14284B
        blueDeep:    rgb(0, 82, 164),     // #0052A4
        blueMain:    rgb(0, 159, 227),    // #009FE3
        cyanBright:  rgb(20, 206, 255),   // #14CEFF
        orangeRed:   rgb(234, 62, 20),    // #EA3E14
        orangeVivid: rgb(243, 112, 33),   // #F37021
        orangeDeep:  rgb(212, 72, 10),    // #D4480A
        yellowVivid: rgb(255, 238, 36),   // #FFEE24
        yellowSoft:  rgb(255, 246, 128),  // #FFF680
        white:       rgb(255, 255, 255),
        black:       rgb(0, 0, 0)
    };

    // Create fresh 1920x1080 RGB 8-bit document
    var doc = app.documents.add(
        new UnitValue(W, "px"),
        new UnitValue(H, "px"),
        RES,
        "Furusato2026_YouTube_Thumbnail",
        NewDocumentMode.RGB,
        DocumentFill.TRANSPARENT,
        1.0,
        BitsPerChannelType.EIGHT
    );

    // Organize non-destructive LayerSets (bottom-to-top stacking order)
    // Note: adding a LayerSet places it at the top, so add bottom-most first
    var grpBg     = doc.layerSets.add(); grpBg.name     = "01_Background";
    var grpChars  = doc.layerSets.add(); grpChars.name  = "02_Characters";
    var grpHero   = doc.layerSets.add(); grpHero.name   = "03_Typography_and_Logo";
    var grpBadges = doc.layerSets.add(); grpBadges.name = "04_Starburst_and_Badges";
    var grpFrame  = doc.layerSets.add(); grpFrame.name  = "05_Outer_Frame";

    // Helper: polygon points for rounded rectangle
    function roundedRectPts(cx, cy, w, h, r, segs) {
        var pts = [];
        var s = segs || 10;
        var rad = Math.min(r, w / 2, h / 2);
        var x0 = cx - w / 2, y0 = cy - h / 2;
        var x1 = cx + w / 2, y1 = cy + h / 2;
        var corners = [
            { x: x1 - rad, y: y0 + rad, a0: -Math.PI / 2, a1: 0 },
            { x: x1 - rad, y: y1 - rad, a0: 0,            a1: Math.PI / 2 },
            { x: x0 + rad, y: y1 - rad, a0: Math.PI / 2,  a1: Math.PI },
            { x: x0 + rad, y: y0 + rad, a0: Math.PI,      a1: Math.PI * 1.5 }
        ];
        for (var ci = 0; ci < 4; ci++) {
            var co = corners[ci];
            for (var i = 0; i <= s; i++) {
                var a = co.a0 + (co.a1 - co.a0) * (i / s);
                pts.push([co.x + Math.cos(a) * rad, co.y + Math.sin(a) * rad]);
            }
        }
        return pts;
    }

    // Helper: polygon points for multi-point starburst
    function starburstPts(cx, cy, outerR, innerR, points, rotDeg) {
        var pts = [];
        var total = points * 2;
        var baseA = (rotDeg || 0) * Math.PI / 180.0;
        for (var i = 0; i < total; i++) {
            var a = baseA + (i * Math.PI / points);
            var r = (i % 2 === 0) ? outerR : innerR;
            pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
        }
        return pts;
    }

    // Helper: ellipse polygon points
    function ellipsePts(cx, cy, rx, ry, segs) {
        var pts = [];
        var s = segs || 64;
        for (var i = 0; i < s; i++) {
            var a = (i / s) * Math.PI * 2;
            pts.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]);
        }
        return pts;
    }

    // Helper: create filled polygon ArtLayer inside a LayerSet (always placed on top of that group)
    function addPolyLayer(group, name, pts, fillCol, opacityPct, rotDeg) {
        var lyr = group.artLayers.add();
        lyr.name = name;
        doc.activeLayer = lyr;
        doc.selection.select(pts, SelectionType.REPLACE, 0, true);
        doc.selection.fill(fillCol, ColorBlendMode.NORMAL, 100, false);
        doc.selection.deselect();
        if (opacityPct !== undefined && opacityPct !== null) { lyr.opacity = opacityPct; }
        if (rotDeg && rotDeg !== 0) { lyr.rotate(rotDeg, AnchorPosition.MIDDLECENTER); }
        return lyr;
    }

    // Helper: apply live Photoshop Layer Effects (Stroke + Drop Shadow + Outer Glow) via ActionManager
    function applyEffects(lyr, opts) {
        doc.activeLayer = lyr;
        var dSet = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
        ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
        dSet.putReference(charIDToTypeID("null"), ref);

        var dFx = new ActionDescriptor();
        dFx.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), 100.0);

        if (opts.strokePx && opts.strokePx > 0) {
            var dStr = new ActionDescriptor();
            dStr.putBoolean(charIDToTypeID("enab"), true);
            dStr.putEnumerated(charIDToTypeID("Styl"), charIDToTypeID("FStl"), charIDToTypeID("OutF"));
            dStr.putEnumerated(charIDToTypeID("PntT"), charIDToTypeID("FrFl"), charIDToTypeID("SClr"));
            dStr.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Nrml"));
            dStr.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), opts.strokeOp || 100.0);
            dStr.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), opts.strokePx);
            var sc = opts.strokeCol || C.white;
            var dSc = new ActionDescriptor();
            dSc.putDouble(charIDToTypeID("Rd  "), sc.rgb.red);
            dSc.putDouble(charIDToTypeID("Grn "), sc.rgb.green);
            dSc.putDouble(charIDToTypeID("Bl  "), sc.rgb.blue);
            dStr.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), dSc);
            dFx.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), dStr);
        }

        if (opts.shadowDist !== undefined && opts.shadowDist !== null) {
            var dSh = new ActionDescriptor();
            dSh.putBoolean(charIDToTypeID("enab"), true);
            dSh.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
            var shc = opts.shadowCol || C.navyDark;
            var dShc = new ActionDescriptor();
            dShc.putDouble(charIDToTypeID("Rd  "), shc.rgb.red);
            dShc.putDouble(charIDToTypeID("Grn "), shc.rgb.green);
            dShc.putDouble(charIDToTypeID("Bl  "), shc.rgb.blue);
            dSh.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), dShc);
            dSh.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), opts.shadowOp || 85.0);
            dSh.putBoolean(charIDToTypeID("uglg"), false);
            dSh.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), opts.shadowAngle || 135.0);
            dSh.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), opts.shadowDist);
            dSh.putUnitDouble(charIDToTypeID("Ckmt"), charIDToTypeID("#Pxl"), opts.shadowSpread || 0);
            dSh.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), opts.shadowBlur || 0);
            dFx.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), dSh);
        }

        if (opts.glowSize && opts.glowSize > 0) {
            var dGl = new ActionDescriptor();
            dGl.putBoolean(charIDToTypeID("enab"), true);
            dGl.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Nrml"));
            var gc = opts.glowCol || C.white;
            var dGc = new ActionDescriptor();
            dGc.putDouble(charIDToTypeID("Rd  "), gc.rgb.red);
            dGc.putDouble(charIDToTypeID("Grn "), gc.rgb.green);
            dGc.putDouble(charIDToTypeID("Bl  "), gc.rgb.blue);
            dGl.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), dGc);
            dGl.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), opts.glowOp || 95.0);
            dGl.putEnumerated(charIDToTypeID("GlwT"), charIDToTypeID("BETE"), charIDToTypeID("SfBL"));
            dGl.putUnitDouble(charIDToTypeID("Ckmt"), charIDToTypeID("#Pxl"), opts.glowSpread || 45);
            dGl.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), opts.glowSize);
            dFx.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), dGl);
        }

        dSet.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), dFx);
        executeAction(charIDToTypeID("setd"), dSet, DialogModes.NO);
    }

    // Helper: create live editable Text layer centered precisely at (cx, cy) using actual bounds
    function addCenteredText(group, name, txt, cx, cy, sizePx, fontName, col, tracking, rotDeg, leadingPx) {
        var tl = group.artLayers.add();
        tl.kind = LayerKind.TEXT;
        tl.name = name;
        var ti = tl.textItem;
        ti.contents = txt;
        try { ti.font = fontName || FONT_BLACK; } catch (e) {}
        var sizePt = sizePx * (72.0 / doc.resolution);
        ti.size = new UnitValue(sizePt, "pt");
        ti.color = col;
        ti.justification = Justification.CENTER;
        if (tracking !== undefined && tracking !== null) { ti.tracking = tracking; }
        if (leadingPx && leadingPx > 0) {
            ti.useAutoLeading = false;
            ti.leading = new UnitValue(leadingPx * (72.0 / doc.resolution), "pt");
        }
        ti.position = [new UnitValue(cx, "px"), new UnitValue(cy, "px")];
        if (rotDeg && rotDeg !== 0) {
            doc.activeLayer = tl;
            tl.rotate(rotDeg, AnchorPosition.MIDDLECENTER);
        }
        var b = tl.bounds;
        var curCx = (b[0].as("px") + b[2].as("px")) / 2.0;
        var curCy = (b[1].as("px") + b[3].as("px")) / 2.0;
        tl.translate(new UnitValue(cx - curCx, "px"), new UnitValue(cy - curCy, "px"));
        return tl;
    }

    // Helper: import transparent PNG file cleanly into target group, resize to exact width/height, position center
    function importPngAsset(group, name, filePath, targetW, targetH, cx, cy, rotDeg) {
        var f = new File(filePath);
        if (!f.exists) { throw new Error("Missing PNG asset: " + filePath); }
        var srcDoc = app.open(f);
        var dup = srcDoc.activeLayer.duplicate(doc, ElementPlacement.INSIDE);
        srcDoc.close(SaveOptions.DONOTSAVECHANGES);
        app.activeDocument = doc;
        dup.move(group, ElementPlacement.INSIDE);
        dup.name = name;
        doc.activeLayer = dup;

        var b = dup.bounds;
        var curW = b[2].as("px") - b[0].as("px");
        var curH = b[3].as("px") - b[1].as("px");
        var pct = 100.0;
        if (targetW && targetW > 0) {
            pct = (targetW / curW) * 100.0;
        } else if (targetH && targetH > 0) {
            pct = (targetH / curH) * 100.0;
        }
        dup.resize(pct, pct, AnchorPosition.MIDDLECENTER);
        if (rotDeg && rotDeg !== 0) { dup.rotate(rotDeg, AnchorPosition.MIDDLECENTER); }

        var b2 = dup.bounds;
        var curCx = (b2[0].as("px") + b2[2].as("px")) / 2.0;
        var curCy = (b2[1].as("px") + b2[3].as("px")) / 2.0;
        dup.translate(new UnitValue(cx - curCx, "px"), new UnitValue(cy - curCy, "px"));
        return dup;
    }

    // ==================================================================
    // 01. HIGH-ENERGY BACKGROUND (Vivid Blue/Cyan + Sunburst + Speed Slashes)
    // ==================================================================
    var bgBase = addPolyLayer(grpBg, "BG_Base_Blue", [[0, 0], [W, 0], [W, H], [0, H]], C.blueDeep, 100, 0);

    // Rich radial cyan glow center behind the hero composition
    var bgGlow1 = addPolyLayer(grpBg, "BG_Radial_Cyan", ellipsePts(820, 440, 1050, 740, 64), C.blueMain, 85, 0);
    doc.activeLayer = bgGlow1;
    bgGlow1.applyGaussianBlur(140);

    var bgGlow2 = addPolyLayer(grpBg, "BG_Radial_HotCenter", ellipsePts(1420, 640, 520, 480, 64), C.cyanBright, 70, 0);
    doc.activeLayer = bgGlow2;
    bgGlow2.applyGaussianBlur(120);

    // Explosive 16-ray sunburst radiating from hero focus (920, 480)
    var rayLyr = grpBg.artLayers.add();
    rayLyr.name = "BG_Sunburst_16Rays";
    doc.activeLayer = rayLyr;
    var rCx = 900, rCy = 460;
    for (var ri = 0; ri < 16; ri++) {
        var a1 = (ri * 22.5) * Math.PI / 180.0;
        var a2 = (ri * 22.5 + 10.5) * Math.PI / 180.0;
        var rDist = 2300;
        var rPts = [
            [rCx, rCy],
            [rCx + Math.cos(a1) * rDist, rCy + Math.sin(a1) * rDist],
            [rCx + Math.cos(a2) * rDist, rCy + Math.sin(a2) * rDist]
        ];
        doc.selection.select(rPts, SelectionType.REPLACE, 0, true);
        doc.selection.fill(C.cyanBright, ColorBlendMode.NORMAL, 100, false);
    }
    doc.selection.deselect();
    rayLyr.opacity = 24;

    // Dramatic angled vivid-orange power wedge on bottom-right behind characters
    addPolyLayer(grpBg, "BG_Orange_PowerWedge", [[1140, 1080], [1920, 260], [1920, 1080]], C.orangeVivid, 92, 0);
    addPolyLayer(grpBg, "BG_Yellow_SlashLine", [[1100, 1080], [1920, 215], [1920, 255], [1142, 1080]], C.yellowVivid, 95, 0);

    // Subtle dark navy contrast vignette behind upper-left monster number for extreme pop
    var bgContrast = addPolyLayer(grpBg, "BG_TopLeft_DeepShade", ellipsePts(580, 290, 760, 320, 64), C.navyDark, 55, 0);
    doc.activeLayer = bgContrast;
    bgContrast.applyGaussianBlur(110);

    // ==================================================================
    // 02. OFFICIAL CHEERING CHARACTERS (Right side, ZERO fist overlap, flush with bottom!)
    // ==================================================================
    // Soft glowing white/yellow aura behind characters
    var charHalo = addPolyLayer(grpChars, "Chars_Backlight_Halo", ellipsePts(1595, 765, 330, 315, 64), C.yellowSoft, 70, 0);
    doc.activeLayer = charHalo;
    charHalo.applyGaussianBlur(70);

    // Cheering man (back-right)  100% inside right yellow border including raised left fist!
    var chMan = importPngAsset(grpChars, "Char_Man_Cheer", PARTS_DIR + "/03_\u4e0a\u90e8\u4e2d\u592e\u53f3_\u7537\u6027.png", 0, 640, 1664, 774, 1.5);
    applyEffects(chMan, { strokePx: 11, strokeCol: C.white, shadowDist: 14, shadowBlur: 22, shadowOp: 55, shadowCol: C.navyDark });

    // Cheering woman (front-left of pair)  cleanly clear of white title card (x<=1206)
    var chWoman = importPngAsset(grpChars, "Char_Woman_Cheer", PARTS_DIR + "/02_\u4e0a\u90e8\u4e2d\u592e\u5de6_\u5973\u6027.png", 0, 660, 1446, 778, -1.5);
    applyEffects(chWoman, { strokePx: 11, strokeCol: C.white, shadowDist: 14, shadowBlur: 24, shadowOp: 60, shadowCol: C.navyDark });

    // ==================================================================
    // 03. MASSIVE HIGH-CTR TYPOGRAPHY & OFFICIAL LOGO HERO (Left & Center)
    // ==================================================================
    // ROW 1: Top Vivid Orange-Red Hook Ribbon (tilted -1.4 deg)
    addPolyLayer(grpHero, "TopHook_HardShadow", roundedRectPts(636, 108, 1136, 82, 41, 10), C.navyDark, 95, -1.4);
    var topPill = addPolyLayer(grpHero, "TopHook_Pill", roundedRectPts(626, 98, 1136, 82, 41, 10), C.orangeRed, 100, -1.4);
    applyEffects(topPill, { strokePx: 5, strokeCol: C.white });
    addCenteredText(grpHero, "TopHook_Txt", "\u98ef\u7530\u30fb\u4e0b\u4f0a\u90a3 \u6700\u5927\u7d1a\uff01 2026\u5e7412\u670827\u65e5(\u65e5)\u958b\u50ac", 626, 98, 43, FONT_BLACK, C.white, 10, -1.4);

    // ROW 2: MONSTER EYE-CATCH  103 !!
    // Stacked left badge:  (100)
    addPolyLayer(grpHero, "Tag103_Shadow", roundedRectPts(208, 244, 272, 118, 18, 8), C.navyDark, 95, -3.0);
    var tag103 = addPolyLayer(grpHero, "Tag103_Bg", roundedRectPts(200, 236, 272, 118, 18, 8), C.navy, 100, -3.0);
    applyEffects(tag103, { strokePx: 5, strokeCol: C.yellowVivid });
    addCenteredText(grpHero, "Tag103_Line1", "\u53c2\u52a0\u4e88\u5b9a\u4f01\u696d", 200, 212, 36, FONT_BLACK, C.white, 10, -3.0);
    addCenteredText(grpHero, "Tag103_Line2", "100\u793e\u4ee5\u4e0a!", 200, 262, 38, FONT_BLACK, C.yellowVivid, 10, -3.0);

    // MONSTER "103" (246px Yellow + thick Navy stroke + radiant White outer pop + hard shadow!)
    var txt103 = addCenteredText(grpHero, "Hero_103", "103", 566, 304, 246, FONT_BLACK, C.yellowVivid, -35, -2.5);
    applyEffects(txt103, {
        strokePx: 16, strokeCol: C.navyDark,
        glowSize: 28, glowSpread: 65, glowCol: C.white, glowOp: 95,
        shadowDist: 16, shadowBlur: 6, shadowOp: 90, shadowCol: C.navyDark
    });

    // "" (134px Yellow  crisp spacing between 103 and !)
    var txtSha = addCenteredText(grpHero, "Hero_Sha", "\u793e", 836, 342, 134, FONT_BLACK, C.yellowVivid, 0, -2.5);
    applyEffects(txtSha, {
        strokePx: 14, strokeCol: C.navyDark,
        glowSize: 24, glowSpread: 65, glowCol: C.white, glowOp: 95,
        shadowDist: 14, shadowBlur: 6, shadowOp: 90, shadowCol: C.navyDark
    });

    // "!" (98px Pure White with vivid orange/navy punch, zero stroke clash with !)
    var txtShu = addCenteredText(grpHero, "Hero_Daishuketsu", "\u5927\u96c6\u7d50!", 1126, 336, 98, FONT_BLACK, C.white, -18, -2.5);
    applyEffects(txtShu, {
        strokePx: 13, strokeCol: C.orangeDeep,
        glowSize: 20, glowSpread: 60, glowCol: C.white, glowOp: 90,
        shadowDist: 14, shadowBlur: 6, shadowOp: 90, shadowCol: C.navyDark
    });

    // ROW 3: OFFICIAL TITLE CARD (Pure White tilted -1.5 deg, right edge cleanly clear of woman's fist!)
    addPolyLayer(grpHero, "TitleCard_HardShadow", roundedRectPts(638, 626, 1136, 312, 26, 10), C.navyDark, 96, -1.5);
    var titleCard = addPolyLayer(grpHero, "TitleCard_WhiteBg", roundedRectPts(624, 610, 1136, 312, 26, 10), C.white, 100, -1.5);
    applyEffects(titleCard, { strokePx: 9, strokeCol: C.yellowVivid });

    // Genuine Official 2026 Title Logo PNG ( 12.27() 13:00-16:00  / )
    importPngAsset(grpHero, "Official_Title_Logo", PARTS_DIR + "/furusato2027_logo.png", 1068, 0, 624, 610, -1.5);

    // ROW 4: BOTTOM-LEFT ZERO-BARRIER ACTION BAR (Aligned with TitleCard, 100% clear of YT timestamp!)
    addPolyLayer(grpHero, "BotBar_HardShadow", roundedRectPts(636, 922, 1136, 126, 22, 10), C.yellowVivid, 100, 0.8);
    var botBar = addPolyLayer(grpHero, "BotBar_NavyBg", roundedRectPts(624, 910, 1136, 126, 22, 10), C.navy, 100, 0.8);
    applyEffects(botBar, { strokePx: 6, strokeCol: C.cyanBright });

    var botPill = addPolyLayer(grpHero, "BotBar_YellowPill", roundedRectPts(278, 905, 404, 76, 38, 10), C.yellowVivid, 100, 0.8);
    addCenteredText(grpHero, "BotBar_PillTxt", "\u4e88\u7d04\u4e0d\u8981\u30fb\u670d\u88c5\u81ea\u7531", 278, 905, 38, FONT_BLACK, C.navyDark, 4, 0.8);
    addCenteredText(grpHero, "BotBar_MainTxt", "UI\u30bf\u30fc\u30f3\u30fb\u4ee4\u548c10\u5e74\u5352 \u5927\u6b53\u8fce\uff01", 836, 914, 44, FONT_BLACK, C.white, 4, 0.8);

    // ==================================================================
    // 04. EXPLOSIVE UPPER-RIGHT QUO CARD 500 YEN STARBURST SEAL & SPARKLES
    // ==================================================================
    var sbCx = 1666, sbCy = 208;
    addPolyLayer(grpBadges, "QuoSeal_HardShadow", starburstPts(sbCx + 11, sbCy + 13, 170, 140, 18, 6), C.navyDark, 92, 0);
    var quoSeal = addPolyLayer(grpBadges, "QuoSeal_Starburst", starburstPts(sbCx, sbCy, 170, 140, 18, 6), C.orangeRed, 100, 0);
    applyEffects(quoSeal, { strokePx: 8, strokeCol: C.white, shadowDist: 8, shadowBlur: 18, shadowOp: 55, shadowCol: C.navyDark });

    // Inner bright yellow accent ring inside starburst (generous padding around text)
    var quoInner = addPolyLayer(grpBadges, "QuoSeal_InnerRing", ellipsePts(sbCx, sbCy, 132, 132, 64), C.orangeRed, 100, 0);
    applyEffects(quoInner, { strokePx: 4, strokeCol: C.yellowVivid });

    // High-contrast stacked QUO Card offer text (100% leaflet accurate, centered cleanly inside ring)
    var qT1 = addCenteredText(grpBadges, "QuoSeal_Cond", "4\u793e\u8a2a\u554f\u3067", sbCx - 6, sbCy - 86, 30, FONT_BLACK, C.yellowSoft, 8, 7);
    applyEffects(qT1, { strokePx: 5, strokeCol: C.navyDark });
    var qT2 = addCenteredText(grpBadges, "QuoSeal_Name", "\u30af\u30aa\u30ab\u30fc\u30c9", sbCx - 1, sbCy - 38, 39, FONT_BLACK, C.white, 4, 7);
    applyEffects(qT2, { strokePx: 6, strokeCol: C.navyDark });
    var qT3 = addCenteredText(grpBadges, "QuoSeal_500", "500\u5186\u5206", sbCx + 4, sbCy + 20, 60, FONT_BLACK, C.yellowVivid, -15, 7);
    applyEffects(qT3, { strokePx: 8, strokeCol: C.navyDark });
    var qT4 = addCenteredText(grpBadges, "QuoSeal_Pres", "\u30d7\u30ec\u30bc\u30f3\u30c8!", sbCx + 9, sbCy + 78, 33, FONT_BLACK, C.white, 4, 7);
    applyEffects(qT4, { strokePx: 6, strokeCol: C.navyDark });

    // Punchy 4-point sparkles cleanly in open space (ZERO overlap with badges or hands)
    function addSparkle4(name, cx, cy, outerR, innerR, col, rotDeg) {
        var sp = addPolyLayer(grpBadges, name, starburstPts(cx, cy, outerR, innerR, 4, rotDeg || 0), col, 100, 0);
        applyEffects(sp, { shadowDist: 4, shadowBlur: 8, shadowOp: 45, shadowCol: C.navyDark });
    }
    addSparkle4("Sparkle_MidTop",   1384, 114, 38, 12, C.yellowVivid, 20);
    addSparkle4("Sparkle_MidGap",   1370, 266, 26,  9, C.white,       10);
    addSparkle4("Sparkle_MidRight", 1258, 466, 30, 10, C.yellowVivid, 14);
    addSparkle4("Sparkle_FarRight", 1866, 366, 28,  9, C.yellowSoft,  18);

    // ==================================================================
    // 05. OUTER YOUTUBE HIGH-CTR FRAME BORDER (Pops on Light & Dark Feeds!)
    // ==================================================================
    var bW = 18;
    var frameLyr = grpFrame.artLayers.add();
    frameLyr.name = "YouTube_Outer_YellowFrame";
    doc.activeLayer = frameLyr;
    doc.selection.select([[0, 0], [W, 0], [W, H], [0, H]], SelectionType.REPLACE, 0, false);
    doc.selection.select([[bW, bW], [W - bW, bW], [W - bW, H - bW], [bW, H - bW]], SelectionType.DIMINISH, 0, false);
    doc.selection.fill(C.yellowVivid, ColorBlendMode.NORMAL, 100, false);
    doc.selection.deselect();

    // ==================================================================
    // SAVE MASTER PSD (Full Layers Preserved) & EXPORT 1920x1080 + 1280x720
    // ==================================================================
    var psdPath    = OUT_DIR + "/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a2026_YouTube\u30b5\u30e0\u30cd\u30a4\u30eb_master.psd";
    var png1080    = OUT_DIR + "/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a2026_YouTube\u30b5\u30e0\u30cd\u30a4\u30eb_1920x1080.png";
    var png720     = OUT_DIR + "/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a2026_YouTube\u30b5\u30e0\u30cd\u30a4\u30eb_1280x720.png";
    var jpg720     = OUT_DIR + "/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a2026_YouTube\u30b5\u30e0\u30cd\u30a4\u30eb_1280x720.jpg";

    var psdOpts = new PhotoshopSaveOptions();
    psdOpts.layers = true;
    psdOpts.embedColorProfile = true;
    doc.saveAs(new File(psdPath), psdOpts, true, Extension.LOWERCASE);

    var pngOpts = new PNGSaveOptions();
    pngOpts.compression = 6;
    pngOpts.interlaced = false;
    doc.saveAs(new File(png1080), pngOpts, true, Extension.LOWERCASE);

    // Duplicate & resize cleanly to YouTube recommended 1280x720 (<2MB PNG & high-quality JPG)
    var dup720 = doc.duplicate("YT_1280x720", true);
    dup720.resizeImage(new UnitValue(1280, "px"), new UnitValue(720, "px"), 72, ResampleMethod.BICUBICSHARPER);
    dup720.saveAs(new File(png720), pngOpts, true, Extension.LOWERCASE);

    var jpgOpts = new JPEGSaveOptions();
    jpgOpts.quality = 11;
    jpgOpts.embedColorProfile = true;
    jpgOpts.formatOptions = FormatOptions.OPTIMIZEDBASELINE;
    dup720.saveAs(new File(jpg720), jpgOpts, true, Extension.LOWERCASE);
    dup720.close(SaveOptions.DONOTSAVECHANGES);

    app.activeDocument = doc;

    var fPsd = new File(psdPath);
    var f1080 = new File(png1080);
    var f720p = new File(png720);
    var f720j = new File(jpg720);
    return {
        ok: true,
        docName: doc.name,
        width: W,
        height: H,
        layerSets: doc.layerSets.length,
        psdBytes: fPsd.length,
        png1080Bytes: f1080.length,
        png720Bytes: f720p.length,
        jpg720Bytes: f720j.length,
        png720Path: f720p.fsName,
        jpg720Path: f720j.fsName,
        png1080Path: f1080.fsName,
        psdPath: fPsd.fsName
    };
})();
