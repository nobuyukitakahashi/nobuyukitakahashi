// build_furusato2026_cm.jsx
// 2026 30CM3SMPTE36 / 1920x1080 / 30fps
// ES3 compatible ExtendScript for Adobe After Effects 2027

app.beginUndoGroup("Build Furusato 2026 CM (36sec Master)");

var __buildResult = (function () {
    var PARTS_DIR = "C:/Users/nobuy/OneDrive/My Documents/\u30af\u30e9\u30a4\u30a2\u30f3\u30c8\u5225/\u98ef\u7530\u5546\u5de5\u4f1a\u8b70\u6240_\u98ef\u7530\u8077\u696d\u5b89\u5b9a\u5354\u4f1a/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a_\u30d1\u30fc\u30c4";
    var GEN_DIR   = "g:/\u30de\u30a4\u30c9\u30e9\u30a4\u30d6/git/nobuyukitakahashi/02_Creative_Dept/aftereffects/drafts/furusato2026_cm/assets";

    var W = 1920;
    var H = 1080;
    var FPS = 30.0;
    var MAIN_DUR = 30.0;
    var BAR_DUR = 3.0;
    var MASTER_DUR = 36.0;

    // Verified PostScript font names on this machine
    var FONT_BLACK  = "NotoSansJP-Black";
    var FONT_BOLD   = "NotoSansJP-Bold";
    var FONT_MEDIUM = "NotoSansJP-Medium";

    // Brand color palette (normalized 0..1 RGB) from 2026 Leaflet
    var COL = {
        blueMain:    [0.000, 0.624, 0.890], // #009FE3
        blueDeep:    [0.000, 0.408, 0.718], // #0068B7
        blueDark:    [0.000, 0.286, 0.561], // #00498F
        blueLight:   [0.886, 0.953, 0.988], // #E2F3FC
        bluePale:    [0.953, 0.984, 1.000], // #F3FBFF
        cyanBright:  [0.078, 0.761, 0.965], // #14C2F6
        orangeMain:  [0.941, 0.541, 0.294], // #F08A4B
        orangeVivid: [0.953, 0.439, 0.129], // #F37021
        orangeDeep:  [0.863, 0.341, 0.047], // #DC570C
        orangeWarm:  [1.000, 0.580, 0.259], // #FF9442
        yellowMain:  [0.976, 0.918, 0.278], // #F9EA47
        yellowSoft:  [1.000, 0.957, 0.486], // #FFF47C
        navy:        [0.078, 0.157, 0.294], // #14284B
        slate:       [0.275, 0.369, 0.471], // #465E78
        white:       [1.000, 1.000, 1.000],
        igPink:      [0.867, 0.165, 0.482], // #DD2A7B
        igPurple:    [0.506, 0.204, 0.686], // #8134AF
        igOrange:    [0.961, 0.522, 0.161]  // #F58529
    };

    // Start fresh project
    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    var proj = app.newProject();
    var folderAssets = proj.items.addFolder("01_Assets");
    var folderComps  = proj.items.addFolder("02_Comps");

    // Helper: import file safely
    var imported = {};
    function imp(key, fullPath) {
        var f = new File(fullPath);
        if (!f.exists) {
            throw new Error("Missing asset file [" + key + "]: " + fullPath);
        }
        var io = new ImportOptions(f);
        var item = proj.importFile(io);
        item.parentFolder = folderAssets;
        imported[key] = item;
        return item;
    }

    // Import all 2026 official parts & generated assets
    imp("logo",         PARTS_DIR + "/furusato2027_logo.png");
    imp("char1_tl",     PARTS_DIR + "/01_\u4e0a\u90e8\u5de6_\u5973\u6027.png");
    imp("char2_tcl",    PARTS_DIR + "/02_\u4e0a\u90e8\u4e2d\u592e\u5de6_\u5973\u6027.png");
    imp("char3_tcr",    PARTS_DIR + "/03_\u4e0a\u90e8\u4e2d\u592e\u53f3_\u7537\u6027.png");
    imp("char4_tr",     PARTS_DIR + "/04_\u4e0a\u90e8\u53f3_\u7537\u6027.png");
    imp("char5_ml",     PARTS_DIR + "/05_\u4e2d\u6bb5\u5de6_\u8003\u3048\u308b\u4eba\u7269.png");
    imp("char6_mr",     PARTS_DIR + "/06_\u4e2d\u6bb5\u53f3_\u30ce\u30fc\u30c8\u3068\u30da\u30f3\u3092\u6301\u3064\u7537\u6027.png");
    imp("char7_pair",   PARTS_DIR + "/07_\u53f3\u4e0b_\u5973\u5b50\u5b66\u751f\u3068\u5973\u6027\u30da\u30a2.png");
    imp("companies100", PARTS_DIR + "/03_\u53c2\u52a0\u4f01\u696d\u6570_100\u793e\u4ee5\u4e0a.png");
    imp("datetime",     PARTS_DIR + "/04_\u65e5\u6642.png");
    imp("venue",        PARTS_DIR + "/05_\u4f1a\u5834_\u5834\u6240.png");
    imp("seminar",      PARTS_DIR + "/02_\u540c\u6642\u958b\u50ac_\u5c31\u6d3b\u30bb\u30df\u30ca\u30fc.png");
    imp("bubble_l",     PARTS_DIR + "/06_\u5439\u304d\u51fa\u3057\u5de6_\u3069\u3093\u306a\u4f01\u696d\u304c\u3042\u308b\u304b\u77e5\u308a\u305f\u3044.png");
    imp("bubble_c",     GEN_DIR   + "/bubble_c_ui_turn.png");
    imp("bubble_r",     PARTS_DIR + "/08_\u5439\u304d\u51fa\u3057\u53f3_\u5c31\u8077\u6d3b\u52d5\u306e\u60c5\u5831\u3092\u96c6\u3081\u305f\u3044.png");
    imp("quocard",      PARTS_DIR + "/01_\u30af\u30aa\u30ab\u30fc\u30c9\u30d7\u30ec\u30bc\u30f3\u30c8.png");
    imp("navi_logo",    PARTS_DIR + "/logo_976_88.png");
    imp("qr_code",      PARTS_DIR + "/iidajob_qr_code.png");
    imp("search_bar",   GEN_DIR   + "/search_bar_only.png");
    imp("color_bars",   GEN_DIR   + "/smpte_hd_bars_1920x1080.png");
    imp("ma_mix",       GEN_DIR   + "/ma_30sec_prod_bgm_google_tts.wav");
    imp("prod_bgm",     GEN_DIR   + "/prod_bgm_30sec.wav");
    imp("gtts_narr",    GEN_DIR   + "/google_tts_narration_only_30sec.wav");

    // ------------------------------------------------------------------
    // Utility helpers for sleek motion graphics
    // ------------------------------------------------------------------
    function applyEase(prop, kIdx, inInf, outInf) {
        var dims = 1;
        var pvt = prop.propertyValueType;
        if (pvt === PropertyValueType.TwoD_SPATIAL || pvt === PropertyValueType.ThreeD_SPATIAL || pvt === PropertyValueType.OneD) {
            dims = 1;
        } else if (pvt === PropertyValueType.TwoD) {
            dims = 2;
        } else if (pvt === PropertyValueType.ThreeD) {
            dims = 3;
        } else {
            var v = prop.keyValue(kIdx);
            if (v instanceof Array) { dims = v.length; }
        }
        var inArr = [];
        var outArr = [];
        for (var i = 0; i < dims; i++) {
            inArr.push(new KeyframeEase(0, inInf));
            outArr.push(new KeyframeEase(0, outInf));
        }
        prop.setTemporalEaseAtKey(kIdx, inArr, outArr);
    }

    function setKeysEaseOut(prop, t0, v0, t1, v1, inInf, outInf) {
        prop.setValueAtTime(t0, v0);
        prop.setValueAtTime(t1, v1);
        var k1 = prop.nearestKeyIndex(t0);
        var k2 = prop.nearestKeyIndex(t1);
        applyEase(prop, k1, 33, outInf || 20);
        applyEase(prop, k2, inInf || 85, 33);
    }

    function popScale(layer, t0, targetScale, dur, overshoot) {
        var sc = layer.property("ADBE Transform Group").property("ADBE Scale");
        var ov = overshoot || 1.08;
        var d = dur || 0.42;
        var tMid = t0 + d * 0.62;
        var tEnd = t0 + d;
        sc.setValueAtTime(t0, [0, 0]);
        sc.setValueAtTime(tMid, [targetScale * ov, targetScale * ov]);
        sc.setValueAtTime(tEnd, [targetScale, targetScale]);
        applyEase(sc, sc.nearestKeyIndex(t0), 33, 25);
        applyEase(sc, sc.nearestKeyIndex(tMid), 75, 45);
        applyEase(sc, sc.nearestKeyIndex(tEnd), 80, 33);
    }

    function slideIn(layer, t0, dur, targetPos, dx, dy, withOpacity) {
        var tr = layer.property("ADBE Transform Group");
        var pos = tr.property("ADBE Position");
        var startPos = [targetPos[0] + dx, targetPos[1] + dy];
        setKeysEaseOut(pos, t0, startPos, t0 + dur, targetPos, 86, 18);
        if (withOpacity !== false) {
            var op = tr.property("ADBE Opacity");
            op.setValueAtTime(t0, 0);
            op.setValueAtTime(t0 + Math.min(dur * 0.55, 0.22), 100);
        }
        layer.motionBlur = true;
    }

    function fadeOpacity(layer, t0, t1, v0, v1) {
        var op = layer.property("ADBE Transform Group").property("ADBE Opacity");
        op.setValueAtTime(t0, v0);
        op.setValueAtTime(t1, v1);
    }

    function addDropShadow(layer, opacity255, distance, softness, direction, color) {
        var fx = layer.property("ADBE Effect Parade").addProperty("ADBE Drop Shadow");
        if (color) { fx.property("ADBE Drop Shadow-0001").setValue(color); }
        fx.property("ADBE Drop Shadow-0002").setValue(opacity255 || 55);
        fx.property("ADBE Drop Shadow-0003").setValue(direction || 140);
        fx.property("ADBE Drop Shadow-0004").setValue(distance || 14);
        fx.property("ADBE Drop Shadow-0005").setValue(softness || 28);
        return fx;
    }

    function addGradientBg(comp, name, inT, outT, cStart, cEnd, pStart, pEnd) {
        var solid = comp.layers.addSolid(cStart, name, W, H, 1.0, MAIN_DUR);
        solid.inPoint = inT;
        solid.outPoint = outT;
        var ramp = solid.property("ADBE Effect Parade").addProperty("ADBE Ramp");
        ramp.property("ADBE Ramp-0001").setValue(pStart || [0, 0]);
        ramp.property("ADBE Ramp-0002").setValue(cStart);
        ramp.property("ADBE Ramp-0003").setValue(pEnd || [W, H]);
        ramp.property("ADBE Ramp-0004").setValue(cEnd);
        return solid;
    }

    function addRectShape(comp, name, w, h, roundness, fillCol, strokeCol, strokeW, pos, inT, outT) {
        var layer = comp.layers.addShape();
        layer.name = name;
        layer.inPoint = inT;
        layer.outPoint = outT;
        var contents = layer.property("ADBE Root Vectors Group");
        var grp = contents.addProperty("ADBE Vector Group");
        var v = grp.property("ADBE Vectors Group");
        var rect = v.addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue([w, h]);
        rect.property("ADBE Vector Rect Roundness").setValue(roundness || 0);
        if (fillCol) {
            var fill = v.addProperty("ADBE Vector Graphic - Fill");
            fill.property("ADBE Vector Fill Color").setValue(fillCol);
        }
        if (strokeCol && strokeW > 0) {
            var stroke = v.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeCol);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeW);
        }
        layer.property("ADBE Transform Group").property("ADBE Position").setValue(pos);
        return layer;
    }

    function addCircleShape(comp, name, diam, fillCol, strokeCol, strokeW, pos, inT, outT) {
        var layer = comp.layers.addShape();
        layer.name = name;
        layer.inPoint = inT;
        layer.outPoint = outT;
        var contents = layer.property("ADBE Root Vectors Group");
        var grp = contents.addProperty("ADBE Vector Group");
        var v = grp.property("ADBE Vectors Group");
        var ell = v.addProperty("ADBE Vector Shape - Ellipse");
        ell.property("ADBE Vector Ellipse Size").setValue([diam, diam]);
        if (fillCol) {
            var fill = v.addProperty("ADBE Vector Graphic - Fill");
            fill.property("ADBE Vector Fill Color").setValue(fillCol);
        }
        if (strokeCol && strokeW > 0) {
            var stroke = v.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeCol);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeW);
        }
        layer.property("ADBE Transform Group").property("ADBE Position").setValue(pos);
        return layer;
    }

    function addStarSparkle(comp, name, outerR, innerR, pts, fillCol, pos, inT, outT, phase) {
        var layer = comp.layers.addShape();
        layer.name = name;
        layer.inPoint = inT;
        layer.outPoint = outT;
        var grp = layer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        var v = grp.property("ADBE Vectors Group");
        var star = v.addProperty("ADBE Vector Shape - Star");
        star.property("ADBE Vector Star Type").setValue(1); // Star
        star.property("ADBE Vector Star Points").setValue(pts || 4);
        star.property("ADBE Vector Star Outer Radius").setValue(outerR);
        star.property("ADBE Vector Star Inner Radius").setValue(innerR);
        var fill = v.addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(fillCol);
        var tr = layer.property("ADBE Transform Group");
        tr.property("ADBE Position").setValue(pos);
        var ph = phase || 0;
        tr.property("ADBE Rotate Z").expression = "(time * 55) + " + (ph * 40);
        tr.property("ADBE Scale").expression = "var s = 75 + 35 * Math.sin(time * 5.2 + " + ph + "); [s, s];";
        return layer;
    }

    function addTextLayer(comp, name, txt, fontPS, fontSize, fillCol, pos, inT, outT, tracking, just) {
        var layer = comp.layers.addText(txt);
        layer.name = name;
        layer.inPoint = inT;
        layer.outPoint = outT;
        var textProp = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var td = textProp.value;
        td.text = txt;
        td.font = fontPS || FONT_BOLD;
        td.fontSize = fontSize;
        td.fillColor = fillCol;
        td.applyFill = true;
        td.applyStroke = false;
        td.tracking = tracking || 0;
        td.justification = just || ParagraphJustification.CENTER_JUSTIFY;
        textProp.setValue(td);

        // Center anchor precisely via sourceRectAtTime
        var sampleT = Math.min(outT - 0.05, inT + 0.25);
        var rect = layer.sourceRectAtTime(sampleT, false);
        var tr = layer.property("ADBE Transform Group");
        tr.property("ADBE Anchor Point").setValue([rect.left + rect.width / 2, rect.top + rect.height / 2]);
        tr.property("ADBE Position").setValue(pos);
        return layer;
    }

    function addFootage(comp, key, name, pos, scalePct, inT, outT) {
        var layer = comp.layers.add(imported[key]);
        layer.name = name;
        layer.inPoint = inT;
        layer.outPoint = outT;
        var tr = layer.property("ADBE Transform Group");
        tr.property("ADBE Position").setValue(pos);
        tr.property("ADBE Scale").setValue([scalePct, scalePct]);
        return layer;
    }

    function addAliveFloat(layer, ampY, speedY, ampRot, speedRot, phase) {
        var tr = layer.property("ADBE Transform Group");
        var ph = phase || 0;
        tr.property("ADBE Position").expression = "value + [0, Math.sin((time + " + ph + ") * " + speedY + ") * " + ampY + "];";
        if (ampRot && ampRot > 0) {
            tr.property("ADBE Rotate Z").expression = "value + Math.sin((time + " + ph + ") * " + speedRot + ") * " + ampRot + ";";
        }
    }

    function addCircularAvatar(comp, name, assetKey, centerPos, diam, bgCol, ringCol, ringW, imgScale, imgDx, imgDy, tPop, inT, outT, phase) {
        var grpNull = comp.layers.addNull();
        grpNull.name = name + "_CTRL";
        grpNull.inPoint = inT;
        grpNull.outPoint = outT;
        var nTr = grpNull.property("ADBE Transform Group");
        nTr.property("ADBE Anchor Point").setValue([50, 50]);
        nTr.property("ADBE Position").setValue(centerPos);
        nTr.property("ADBE Scale").setValue([100, 100]);

        var bg = addCircleShape(comp, name + "_BG", diam, bgCol, null, 0, centerPos, inT, outT);
        addDropShadow(bg, 58, 12, 24, 140);
        bg.parent = grpNull;
        bg.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);

        var img = addFootage(comp, assetKey, name + "_IMG", [centerPos[0] + imgDx, centerPos[1] + imgDy], imgScale, inT, outT);
        img.parent = grpNull;
        img.property("ADBE Transform Group").property("ADBE Position").setValue([50 + imgDx, 50 + imgDy]);

        var matte = addCircleShape(comp, name + "_MATTE", diam - 4, COL.white, null, 0, centerPos, inT, outT);
        matte.parent = grpNull;
        matte.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);
        matte.enabled = false;
        if (typeof img.setTrackMatte === "function") {
            img.setTrackMatte(matte, TrackMatteType.ALPHA);
        } else {
            img.trackMatteType = TrackMatteType.ALPHA;
        }

        if (ringCol && ringW > 0) {
            var ring = addCircleShape(comp, name + "_RING", diam, null, ringCol, ringW, centerPos, inT, outT);
            ring.parent = grpNull;
            ring.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);
        }

        // Apply pop-in & float animation AFTER all children are cleanly parented at 100% scale!
        popScale(grpNull, tPop, 100, 0.46, 1.09);
        addAliveFloat(grpNull, 6, 2.8, 1.4, 1.8, phase || 0);
        return grpNull;
    }

    function addDiagonalWipe(comp, name, tCenter, col1, col2) {
        // Two overlapping slanted panels sweeping cleanly across 1920x1080
        var p1 = addRectShape(comp, name + "_A", 2800, 1900, 0, col1, null, 0, [-1600, H / 2], tCenter - 0.45, tCenter + 0.45);
        p1.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-14);
        setKeysEaseOut(p1.property("ADBE Transform Group").property("ADBE Position"), tCenter - 0.40, [-1650, H / 2], tCenter + 0.36, [3600, H / 2], 70, 70);
        p1.motionBlur = true;

        var p2 = addRectShape(comp, name + "_B", 2400, 1900, 0, col2, null, 0, [-1600, H / 2], tCenter - 0.38, tCenter + 0.50);
        p2.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-14);
        setKeysEaseOut(p2.property("ADBE Transform Group").property("ADBE Position"), tCenter - 0.30, [-1700, H / 2], tCenter + 0.42, [3650, H / 2], 72, 72);
        p2.motionBlur = true;
    }

    // ------------------------------------------------------------------
    // COMP 1: 01_MainCM_30sec (1920x1080, 29.97fps, 30.0s)
    // ------------------------------------------------------------------
    var mainComp = proj.items.addComp("01_MainCM_30sec", W, H, 1.0, MAIN_DUR, FPS);
    mainComp.parentFolder = folderComps;
    mainComp.motionBlur = true;
    mainComp.shutterAngle = 180;

    // Audio tracks (0.0s .. 30.0s): Active Google TTS + Prod BGM MA mix + muted separate stems
    var narrStem = mainComp.layers.add(imported["gtts_narr"]);
    narrStem.name = "[GOOGLE_TTS_NARR_STEM_MUTED] google_tts_narration_only_30sec.wav";
    narrStem.startTime = 0;
    narrStem.audioEnabled = false;

    var bgmStem = mainComp.layers.add(imported["prod_bgm"]);
    bgmStem.name = "[PROD_BGM_STEM_MUTED] prod_bgm_30sec.wav";
    bgmStem.startTime = 0;
    bgmStem.audioEnabled = false;

    var maLayer = mainComp.layers.add(imported["ma_mix"]);
    maLayer.name = "[MA_ACTIVE] ma_30sec_prod_bgm_google_tts.wav";
    maLayer.startTime = 0;
    maLayer.audioEnabled = true;

    // ==================================================================
    // SCENE 1: HOOK / OPENING (0.0s .. 2.2s  ultra-speedy & passionate!)
    // ==================================================================
    var s1In = 0.0, s1Out = 2.25;
    addGradientBg(mainComp, "S1_BG", s1In, s1Out, COL.blueDark, COL.blueMain, [0, 0], [W, H]);

    // Animated kinetic diagonal ribbons in S1 background
    var s1Rib1 = addRectShape(mainComp, "S1_DiagRibbon1", 320, 1800, 0, COL.cyanBright, null, 0, [260, 540], s1In, s1Out);
    s1Rib1.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-22);
    s1Rib1.property("ADBE Transform Group").property("ADBE Opacity").setValue(22);
    setKeysEaseOut(s1Rib1.property("ADBE Transform Group").property("ADBE Position"), 0.0, [120, 540], 2.2, [380, 540], 50, 50);

    var s1Rib2 = addRectShape(mainComp, "S1_DiagRibbon2", 180, 1800, 0, COL.white, null, 0, [1680, 540], s1In, s1Out);
    s1Rib2.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-22);
    s1Rib2.property("ADBE Transform Group").property("ADBE Opacity").setValue(14);
    setKeysEaseOut(s1Rib2.property("ADBE Transform Group").property("ADBE Position"), 0.0, [1840, 540], 2.2, [1540, 540], 50, 50);

    // Expanding geometric rings
    var s1Ring1 = addCircleShape(mainComp, "S1_Ring1", 680, null, COL.white, 3, [260, 210], s1In, s1Out);
    s1Ring1.property("ADBE Transform Group").property("ADBE Opacity").setValue(24);
    setKeysEaseOut(s1Ring1.property("ADBE Transform Group").property("ADBE Scale"), 0.0, [45, 45], 2.2, [118, 118], 65, 25);

    var s1Ring2 = addCircleShape(mainComp, "S1_Ring2", 860, null, COL.yellowMain, 4, [1680, 880], s1In, s1Out);
    s1Ring2.property("ADBE Transform Group").property("ADBE Opacity").setValue(30);
    setKeysEaseOut(s1Ring2.property("ADBE Transform Group").property("ADBE Scale"), 0.05, [40, 40], 2.2, [112, 112], 65, 25);

    // Top orange pill label
    var s1Pill = addRectShape(mainComp, "S1_TopPill", 680, 58, 29, COL.orangeVivid, null, 0, [960, 250], 0.02, s1Out);
    popScale(s1Pill, 0.02, 100, 0.24, 1.08);
    addDropShadow(s1Pill, 60, 10, 20, 140);
    var s1PillTxt = addTextLayer(mainComp, "S1_TopPillTxt", "IIDA\u30fbSHIMOINA CAREER EVENT 2026", FONT_BOLD, 27, COL.white, [960, 250], 0.04, s1Out, 50);
    popScale(s1PillTxt, 0.04, 100, 0.24, 1.08);

    // Main Hook Line 1: 
    var s1Line1 = addTextLayer(mainComp, "S1_HookLine1", "\u3042\u306a\u305f\u306e\u672a\u6765\u304c\u3001", FONT_BLACK, 106, COL.white, [960, 415], 0.08, s1Out, 25);
    slideIn(s1Line1, 0.08, 0.28, [960, 415], -180, 0, true);
    addDropShadow(s1Line1, 90, 12, 22, 140);

    // Accent Orange Ribbon behind Line 2
    var s1AccBar = addRectShape(mainComp, "S1_AccentBar", 1120, 146, 18, COL.orangeVivid, null, 0, [960, 585], 0.62, s1Out);
    s1AccBar.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-1.5);
    addDropShadow(s1AccBar, 95, 16, 28, 140);
    setKeysEaseOut(s1AccBar.property("ADBE Transform Group").property("ADBE Scale"), 0.62, [0, 100], 0.90, [100, 100], 88, 20);
    s1AccBar.motionBlur = true;

    // Main Hook Line 2: 
    var s1Line2 = addTextLayer(mainComp, "S1_HookLine2", "\u3053\u3053\u304b\u3089\u52d5\u304d\u51fa\u3059\u3002", FONT_BLACK, 114, COL.white, [960, 583], 0.68, s1Out, 30);
    s1Line2.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-1.5);
    slideIn(s1Line2, 0.68, 0.28, [960, 583], 170, 0, true);
    addDropShadow(s1Line2, 75, 8, 16, 140);

    // Sub Copy
    var s1Sub = addTextLayer(mainComp, "S1_SubCopy", "\u98ef\u7530\u30fb\u4e0b\u4f0a\u90a3\u5730\u533a \u6700\u5927\u7d1a\u306e\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a", FONT_BOLD, 42, COL.yellowSoft, [960, 760], 1.08, s1Out, 40);
    slideIn(s1Sub, 1.08, 0.30, [960, 760], 0, 40, true);
    addDropShadow(s1Sub, 80, 6, 14, 140);

    // Subtle zoom-in energy on sub-elements via sparkles
    addStarSparkle(mainComp, "S1_Star1", 28, 10, 4, COL.yellowMain, [345, 510], 0.80, s1Out, 0.5);
    addStarSparkle(mainComp, "S1_Star2", 24, 9, 4, COL.white, [1585, 645], 0.85, s1Out, 2.2);

    // ==================================================================
    // SCENE 2: TITLE LOGO & 100 (103) IMPACT (2.2s .. 6.0s  punchy 3.8s!)
    // ==================================================================
    var s2In = 2.2, s2Out = 6.05;
    addGradientBg(mainComp, "S2_BG", s2In, s2Out, COL.white, COL.blueLight, [960, 0], [960, H]);

    // Decorative slanted top/bottom brand frame bands
    var s2TopBand = addRectShape(mainComp, "S2_TopBand", 2200, 140, 0, COL.blueMain, null, 0, [960, 26], s2In, s2Out);
    s2TopBand.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-1.2);
    var s2BotBand = addRectShape(mainComp, "S2_BotBand", 2200, 90, 0, COL.blueMain, null, 0, [960, 1068], s2In, s2Out);
    s2BotBand.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-1.2);

    // Soft floating background circles
    var s2Deco1 = addCircleShape(mainComp, "S2_DecoC1", 520, null, COL.blueMain, 4, [150, 920], s2In, s2Out);
    s2Deco1.property("ADBE Transform Group").property("ADBE Opacity").setValue(14);
    var s2Deco2 = addCircleShape(mainComp, "S2_DecoC2", 440, null, COL.orangeMain, 4, [1780, 190], s2In, s2Out);
    s2Deco2.property("ADBE Transform Group").property("ADBE Opacity").setValue(16);

    // Top welcome pill badge
    var s2WelPill = addRectShape(mainComp, "S2_WelPill", 1080, 62, 31, COL.blueDeep, null, 0, [960, 140], 2.28, s2Out);
    addDropShadow(s2WelPill, 45, 8, 18, 140);
    slideIn(s2WelPill, 2.28, 0.32, [960, 140], 0, -55, true);
    var s2WelTxt = addTextLayer(mainComp, "S2_WelTxt", "\u5730\u5143\u3067\u5c31\u8077\u3092\u304a\u8003\u3048\u306e\u65b9\u306e\u53c2\u52a0\u3092\u304a\u5f85\u3061\u3057\u3066\u3044\u307e\u3059\uff01", FONT_BOLD, 32, COL.white, [960, 140], 2.30, s2Out, 20);
    slideIn(s2WelTxt, 2.30, 0.32, [960, 140], 0, -55, true);

    // Official Logo: furusato2027_logo.png (3016x749 -> scale 36% = 1086x270)
    var s2Logo = addFootage(mainComp, "logo", "S2_MainLogo", [960, 405], 36, 2.26, s2Out);
    popScale(s2Logo, 2.26, 36, 0.38, 1.09);
    addDropShadow(s2Logo, 40, 10, 22, 140);

    // Left & Right energetic characters cleanly framed in circular avatars
    addCircularAvatar(mainComp, "S2_CharLeft",  "char1_tl", [220, 425],  300, COL.white, COL.blueMain,   7, 37, 0, 36, 2.40, 2.40, s2Out, 0.2);
    addCircularAvatar(mainComp, "S2_CharRight", "char4_tr", [1700, 425], 300, COL.white, COL.orangeMain, 7, 33, 0, 36, 2.48, 2.48, s2Out, 1.6);

    // Sparkles around title
    addStarSparkle(mainComp, "S2_Star1", 26, 10, 4, COL.orangeVivid, [400, 250], 2.50, s2Out, 0.0);
    addStarSparkle(mainComp, "S2_Star2", 22, 8, 4, COL.blueMain, [1525, 255], 2.55, s2Out, 1.5);

    // Bottom Impact Card: " 100" + "103!" count-up badge
    var s2Card = addRectShape(mainComp, "S2_CompanyCard", 1560, 252, 28, COL.white, COL.blueMain, 4, [960, 770], 2.95, s2Out);
    addDropShadow(s2Card, 55, 14, 30, 140);
    slideIn(s2Card, 2.95, 0.38, [960, 770], 0, 120, true);

    // Left inside card: Official 100 PNG
    var s2Comp100 = addFootage(mainComp, "companies100", "S2_Companies100", [675, 770], 47, 3.10, s2Out);
    popScale(s2Comp100, 3.10, 47, 0.36, 1.09);

    // Right inside card: Vibrant Orange Badge for "103"
    var s2Badge = addRectShape(mainComp, "S2_Badge103", 500, 184, 24, COL.orangeVivid, null, 0, [1435, 770], 3.22, s2Out);
    popScale(s2Badge, 3.22, 100, 0.36, 1.10);
    addDropShadow(s2Badge, 65, 10, 20, 140);

    var s2BadgeTop = addTextLayer(mainComp, "S2_Badge103_Label", "\u6700\u65b0 \u53c2\u52a0\u4e88\u5b9a", FONT_BOLD, 28, COL.white, [1435, 718], 3.28, s2Out, 35);
    fadeOpacity(s2BadgeTop, 3.28, 3.45, 0, 100);

    // Animated Count-up 0 -> 103 (3.28s .. 4.18s)
    var s2CountTxt = addTextLayer(mainComp, "S2_Count103", "103\u793e", FONT_BLACK, 84, COL.yellowSoft, [1435, 792], 3.28, s2Out, 10);
    s2CountTxt.property("ADBE Text Properties").property("ADBE Text Document").expression =
        "var t0 = 3.28; var t1 = 4.18;\n" +
        "var p = Math.max(0, Math.min(1, (time - t0) / (t1 - t0)));\n" +
        "var e = 1 - Math.pow(1 - p, 3);\n" +
        "Math.round(e * 103) + '\u793e';";
    var s2CntSc = s2CountTxt.property("ADBE Transform Group").property("ADBE Scale");
    s2CntSc.setValueAtTime(3.28, [92, 92]);
    s2CntSc.setValueAtTime(4.16, [100, 100]);
    s2CntSc.setValueAtTime(4.30, [116, 116]);
    s2CntSc.setValueAtTime(4.52, [100, 100]);
    applyEase(s2CntSc, s2CntSc.nearestKeyIndex(4.30), 75, 45);
    applyEase(s2CntSc, s2CntSc.nearestKeyIndex(4.52), 80, 33);
    addDropShadow(s2CountTxt, 70, 6, 12, 140);

    // Subtle official footnote under card
    var s2Note = addTextLayer(mainComp, "S2_Footnote", "\u203b\u53c2\u52a0\u4e8b\u696d\u6240\u306f\u5909\u66f4\u3068\u306a\u308b\u5834\u5408\u304c\u3042\u308a\u307e\u3059\u3002", FONT_MEDIUM, 22, COL.slate, [1460, 932], 3.40, s2Out, 15);
    fadeOpacity(s2Note, 3.40, 3.65, 0, 100);

    // ==================================================================
    // SCENE 3: SCHEDULE, VENUE & SEMINAR DASHBOARD (6.0s .. 13.8s  generous 7.8s!)
    // ==================================================================
    var s3In = 6.0, s3Out = 13.85;
    addGradientBg(mainComp, "S3_BG", s3In, s3Out, COL.blueMain, COL.blueDeep, [0, 0], [W, H]);

    // Drifting geometric light bands in S3 background
    var s3Band1 = addRectShape(mainComp, "S3_BgBand1", 260, 1800, 0, COL.white, null, 0, [320, 540], s3In, s3Out);
    s3Band1.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-20);
    s3Band1.property("ADBE Transform Group").property("ADBE Opacity").setValue(10);
    setKeysEaseOut(s3Band1.property("ADBE Transform Group").property("ADBE Position"), s3In, [240, 540], s3Out, [480, 540], 50, 50);

    var s3Band2 = addRectShape(mainComp, "S3_BgBand2", 380, 1800, 0, COL.cyanBright, null, 0, [1600, 540], s3In, s3Out);
    s3Band2.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-20);
    s3Band2.property("ADBE Transform Group").property("ADBE Opacity").setValue(22);

    // Top persistent mini header
    var s3Hdr = addRectShape(mainComp, "S3_HeaderPill", 540, 50, 25, COL.navy, null, 0, [410, 76], 6.08, s3Out);
    s3Hdr.property("ADBE Transform Group").property("ADBE Opacity").setValue(85);
    var s3HdrTxt = addTextLayer(mainComp, "S3_HeaderTxt", "\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a 2026  \u958b\u50ac\u6982\u8981", FONT_BOLD, 24, COL.white, [410, 76], 6.10, s3Out, 20);
    fadeOpacity(s3HdrTxt, 6.10, 6.32, 0, 100);

    // Card 1: Date & Time (6.20s  synced with "1227")
    var s3C1 = addRectShape(mainComp, "S3_Card1_DateTime", 1220, 316, 26, COL.white, null, 0, [750, 282], 6.20, s3Out);
    addDropShadow(s3C1, 65, 14, 28, 140);
    slideIn(s3C1, 6.20, 0.44, [750, 282], -260, 0, true);
    var s3C1Bar = addRectShape(mainComp, "S3_Card1_Accent", 18, 260, 9, COL.orangeVivid, null, 0, [172, 282], 6.20, s3Out);
    slideIn(s3C1Bar, 6.20, 0.44, [172, 282], -260, 0, true);
    var s3DateImg = addFootage(mainComp, "datetime", "S3_Img_DateTime", [770, 282], 39, 6.28, s3Out);
    slideIn(s3DateImg, 6.28, 0.44, [770, 282], -220, 0, true);

    // Card 2: Venue (7.65s  synced with "")
    var s3C2 = addRectShape(mainComp, "S3_Card2_Venue", 1220, 204, 26, COL.white, null, 0, [750, 582], 7.65, s3Out);
    addDropShadow(s3C2, 65, 14, 28, 140);
    slideIn(s3C2, 7.65, 0.44, [750, 582], -260, 0, true);
    var s3C2Bar = addRectShape(mainComp, "S3_Card2_Accent", 18, 152, 9, COL.blueMain, null, 0, [172, 582], 7.65, s3Out);
    slideIn(s3C2Bar, 7.65, 0.44, [172, 582], -260, 0, true);
    var s3VenueImg = addFootage(mainComp, "venue", "S3_Img_Venue", [770, 582], 48, 7.73, s3Out);
    slideIn(s3VenueImg, 7.73, 0.44, [770, 582], -220, 0, true);

    // Card 3: Concurrent Seminar (9.65s  synced with "")
    var s3C3 = addRectShape(mainComp, "S3_Card3_Seminar", 1220, 204, 26, COL.white, null, 0, [750, 828], 9.65, s3Out);
    addDropShadow(s3C3, 65, 14, 28, 140);
    slideIn(s3C3, 9.65, 0.44, [750, 828], -260, 0, true);
    var s3C3Bar = addRectShape(mainComp, "S3_Card3_Accent", 18, 152, 9, COL.yellowMain, null, 0, [172, 828], 9.65, s3Out);
    slideIn(s3C3Bar, 9.65, 0.44, [172, 828], -260, 0, true);
    var s3SemImg = addFootage(mainComp, "seminar", "S3_Img_Seminar", [770, 828], 48, 9.73, s3Out);
    slideIn(s3SemImg, 9.73, 0.44, [770, 828], -220, 0, true);

    // Right side cheering characters clipped cleanly inside circular avatars
    addCircularAvatar(mainComp, "S3_CharUpper", "char2_tcl", [1615, 325], 348, COL.bluePale, COL.white, 8, 27, 0, 78, 6.55, 6.52, s3Out, 0.4);
    addCircularAvatar(mainComp, "S3_CharLower", "char3_tcr", [1615, 760], 348, COL.bluePale, COL.white, 8, 25, 0, 76, 8.15, 8.12, s3Out, 2.1);

    // ==================================================================
    // SCENE 4: TARGET & EMPATHY   (13.8s .. 20.2s  BIG & BOLD MOTION!)
    // ==================================================================
    var s4In = 13.8, s4Out = 20.25;
    addGradientBg(mainComp, "S4_BG", s4In, s4Out, COL.white, COL.bluePale, [0, 0], [W, H]);

    // Soft side blue accents with lively drift
    var s4SideL = addRectShape(mainComp, "S4_SideL", 340, 1600, 0, COL.blueLight, null, 0, [60, 540], s4In, s4Out);
    s4SideL.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(12);
    var s4SideR = addRectShape(mainComp, "S4_SideR", 340, 1600, 0, COL.blueLight, null, 0, [1860, 540], s4In, s4Out);
    s4SideR.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(12);

    // Header badge:  (BIGGER & BOLDER, clean clearance above center bubble!)
    var s4TitleBg = addRectShape(mainComp, "S4_TitleBg", 680, 84, 42, COL.orangeVivid, null, 0, [960, 96], 13.88, s4Out);
    popScale(s4TitleBg, 13.88, 100, 0.36, 1.15);
    addDropShadow(s4TitleBg, 60, 12, 22, 140);
    var s4TitleTxt = addTextLayer(mainComp, "S4_TitleTxt", "\u3053\u3093\u306a\u65b9\u306b\u304a\u3059\u3059\u3081\uff01", FONT_BLACK, 50, COL.white, [960, 96], 13.92, s4Out, 30);
    popScale(s4TitleTxt, 13.92, 100, 0.36, 1.15);

    // Helper for bold, bouncy, rotating speech bubble entrance + lively rhythmic sway
    function animateBoldBubble(layer, t0, targetScale, targetPos, rotStart, phase, pulseTime) {
        var tr = layer.property("ADBE Transform Group");
        var sc = tr.property("ADBE Scale");
        var pos = tr.property("ADBE Position");
        var rot = tr.property("ADBE Rotate Z");
        // Bold elastic overshoot scale bounce
        sc.setValueAtTime(t0, [0, 0]);
        sc.setValueAtTime(t0 + 0.24, [targetScale * 1.20, targetScale * 1.20]);
        sc.setValueAtTime(t0 + 0.38, [targetScale * 0.94, targetScale * 0.94]);
        sc.setValueAtTime(t0 + 0.50, [targetScale, targetScale]);
        applyEase(sc, sc.nearestKeyIndex(t0), 33, 20);
        applyEase(sc, sc.nearestKeyIndex(t0 + 0.24), 78, 45);
        applyEase(sc, sc.nearestKeyIndex(t0 + 0.38), 75, 45);
        applyEase(sc, sc.nearestKeyIndex(t0 + 0.50), 82, 33);
        if (pulseTime) {
            sc.setValueAtTime(pulseTime, [targetScale, targetScale]);
            sc.setValueAtTime(pulseTime + 0.16, [targetScale * 1.10, targetScale * 1.10]);
            sc.setValueAtTime(pulseTime + 0.36, [targetScale, targetScale]);
            applyEase(sc, sc.nearestKeyIndex(pulseTime + 0.16), 72, 60);
            applyEase(sc, sc.nearestKeyIndex(pulseTime + 0.36), 82, 33);
        }
        // Bold jump-up position from below + lively rhythmic float expression
        setKeysEaseOut(pos, t0, [targetPos[0], targetPos[1] + 190], t0 + 0.44, targetPos, 88, 16);
        pos.expression = "var amp = linear(time, " + (t0 + 0.42) + ", " + (t0 + 0.72) + ", 0, 15); value + [Math.sin((time + " + phase + ") * 2.2) * (amp * 0.35), Math.sin((time + " + phase + ") * 3.8) * amp];";
        // Dynamic tilt swing entrance + playful rocking
        setKeysEaseOut(rot, t0, rotStart, t0 + 0.46, 0, 84, 18);
        rot.expression = "var ramp = linear(time, " + (t0 + 0.44) + ", " + (t0 + 0.75) + ", 0, 4.0); value + Math.sin((time + " + phase + ") * 2.9) * ramp;";
        layer.motionBlur = true;
    }

    // Three LARGE yellow speech bubbles (46% / 49% / 46%  ~1.65x area!) popping & bouncing boldly!
    var s4BubL = addFootage(mainComp, "bubble_l", "S4_BubbleLeft", [395, 456], 46, 14.12, s4Out);
    animateBoldBubble(s4BubL, 14.12, 46, [395, 456], -16, 0.0, 16.20);
    addDropShadow(s4BubL, 52, 16, 30, 140);

    var s4BubC = addFootage(mainComp, "bubble_c", "S4_BubbleCenter", [960, 446], 49, 14.52, s4Out);
    animateBoldBubble(s4BubC, 14.52, 49, [960, 446], 12, 1.3, 15.25);
    addDropShadow(s4BubC, 58, 18, 34, 140);

    var s4BubR = addFootage(mainComp, "bubble_r", "S4_BubbleRight", [1525, 456], 46, 14.92, s4Out);
    animateBoldBubble(s4BubR, 14.92, 46, [1525, 456], 16, 2.6, 17.20);
    addDropShadow(s4BubR, 52, 16, 30, 140);

    // Energetic sparkles around the giant speech bubbles
    addStarSparkle(mainComp, "S4_Spark1", 30, 11, 4, COL.orangeVivid, [165, 252], 14.35, s4Out, 0.2);
    addStarSparkle(mainComp, "S4_Spark2", 26, 9,  4, COL.blueMain,    [682, 212], 14.70, s4Out, 1.4);
    addStarSparkle(mainComp, "S4_Spark3", 28, 10, 4, COL.orangeMain,  [1238, 212], 15.05, s4Out, 2.5);
    addStarSparkle(mainComp, "S4_Spark4", 30, 11, 4, COL.blueMain,    [1755, 252], 15.15, s4Out, 3.4);

    // Thinking characters at bottom-left and bottom-right (tucked cleanly beside larger banner)
    var s4CharL = addFootage(mainComp, "char5_ml", "S4_ThinkLeft", [145, 822], 38, 14.00, s4Out);
    slideIn(s4CharL, 14.00, 0.44, [145, 822], -160, 90, true);
    addAliveFloat(s4CharL, 8, 3.0, 2.5, 2.0, 0.5);

    var s4CharR = addFootage(mainComp, "char6_mr", "S4_ThinkRight", [1772, 822], 34, 14.10, s4Out);
    slideIn(s4CharR, 14.10, 0.44, [1772, 822], 160, 90, true);
    addAliveFloat(s4CharR, 8, 2.9, 2.5, 1.9, 1.9);

    // Bottom Navy Welcome Banner (BIGGER & BOLDER TEXT + dynamic bounce!)
    var s4Ban = addRectShape(mainComp, "S4_WelcomeBanner", 1320, 206, 26, COL.navy, null, 0, [960, 858], 16.15, s4Out);
    addDropShadow(s4Ban, 72, 16, 28, 140);
    slideIn(s4Ban, 16.15, 0.42, [960, 858], 0, 150, true);
    var s4BanTop = addRectShape(mainComp, "S4_BannerTopBar", 1320, 12, 6, COL.blueMain, null, 0, [960, 761], 16.15, s4Out);
    slideIn(s4BanTop, 16.15, 0.42, [960, 761], 0, 150, true);

    var s4BanTxt1 = addTextLayer(mainComp, "S4_BanTxt1", "\u5730\u5143\u5c31\u8077\u30fbUI\u30bf\u30fc\u30f3\u3092\u8003\u3048\u308b\u65b0\u5352\u30fb\u65e2\u5352\u306e\u65b9\u306f\u3082\u3061\u308d\u3093", FONT_BLACK, 38, COL.yellowSoft, [960, 816], 16.22, s4Out, 15);
    slideIn(s4BanTxt1, 16.22, 0.40, [960, 816], -120, 0, true);

    var s4BanTxt2 = addTextLayer(mainComp, "S4_BanTxt2", "\u4e2d\u9ad8\u751f\u30fb\u4fdd\u8b77\u8005\u30fb\u5b66\u6821\u95a2\u4fc2\u8005\u306e\u65b9\u3082\u5927\u6b53\u8fce\uff01", FONT_BLACK, 53, COL.white, [960, 894], 16.32, s4Out, 18);
    slideIn(s4BanTxt2, 16.32, 0.40, [960, 894], 120, 0, true);
    // Bold emphasis bounce right when narration says "" (~18.3s)
    var s4T2Sc = s4BanTxt2.property("ADBE Transform Group").property("ADBE Scale");
    s4T2Sc.setValueAtTime(18.15, [100, 100]);
    s4T2Sc.setValueAtTime(18.34, [108, 108]);
    s4T2Sc.setValueAtTime(18.58, [100, 100]);
    applyEase(s4T2Sc, s4T2Sc.nearestKeyIndex(18.34), 75, 55);
    applyEase(s4T2Sc, s4T2Sc.nearestKeyIndex(18.58), 82, 33);

    // ==================================================================
    // SCENE 5: QUO CARD PRESENT & AGGRESSIVE WELCOME GRADUATES (20.2s .. 25.0s  DYNAMIC IMPACT!)
    // ==================================================================
    var s5In = 20.2, s5Out = 25.05;
    addGradientBg(mainComp, "S5_BG", s5In, s5Out, COL.orangeVivid, COL.orangeDeep, [0, 0], [W, H]);

    // Kinetic rotating golden sunburst rays radiating energy across the frame
    var s5BurstLayer = mainComp.layers.addShape();
    s5BurstLayer.name = "S5_SunburstRays";
    s5BurstLayer.inPoint = s5In;
    s5BurstLayer.outPoint = s5Out;
    var s5BurstRoot = s5BurstLayer.property("ADBE Root Vectors Group");
    for (var ri = 0; ri < 12; ri++) {
        var rGrp = s5BurstRoot.addProperty("ADBE Vector Group");
        rGrp.name = "Ray_" + ri;
        var rv = rGrp.property("ADBE Vectors Group");
        var rPath = rv.addProperty("ADBE Vector Shape - Group");
        var shp = new Shape();
        shp.vertices = [[0, 0], [1600, -125], [1600, 125]];
        shp.closed = true;
        rPath.property("ADBE Vector Shape").setValue(shp);
        var rFill = rv.addProperty("ADBE Vector Graphic - Fill");
        rFill.property("ADBE Vector Fill Color").setValue(COL.yellowMain);
        rGrp.property("ADBE Vector Transform Group").property("ADBE Vector Rotation").setValue(ri * 30);
    }
    var s5BurstTr = s5BurstLayer.property("ADBE Transform Group");
    s5BurstTr.property("ADBE Position").setValue([920, 480]);
    s5BurstTr.property("ADBE Opacity").setValue(18);
    s5BurstTr.property("ADBE Rotate Z").expression = "(time - 20.2) * 14;";

    // Bold diagonal dark-orange speed-slash stripes for poster-grade dynamism
    var s5Slash1 = addRectShape(mainComp, "S5_BgSlash1", 2600, 190, 0, COL.orangeDeep, null, 0, [960, 505], s5In, s5Out);
    s5Slash1.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-5);
    s5Slash1.property("ADBE Transform Group").property("ADBE Opacity").setValue(28);
    var s5Slash2 = addRectShape(mainComp, "S5_BgSlash2", 2600, 54, 0, COL.yellowMain, null, 0, [960, 472], s5In, s5Out);
    s5Slash2.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-5);
    s5Slash2.property("ADBE Transform Group").property("ADBE Opacity").setValue(22);

    // ------------------------------------------------------------------
    // S5 TOP HERO GROUP: Tilted (-2.2 deg) High-Impact QUO Card Card + Hard Navy Shadow
    // ------------------------------------------------------------------
    var s5TopNull = mainComp.layers.addNull();
    s5TopNull.name = "S5_TopGroup_CTRL";
    s5TopNull.inPoint = 20.28;
    s5TopNull.outPoint = s5Out;
    var s5TopTr = s5TopNull.property("ADBE Transform Group");
    s5TopTr.property("ADBE Anchor Point").setValue([50, 50]);
    s5TopTr.property("ADBE Position").setValue([900, 266]);
    s5TopTr.property("ADBE Scale").setValue([100, 100]);
    s5TopTr.property("ADBE Rotate Z").setValue(0);

    // Hard graphic navy offset shadow (replaces generic soft PowerPoint shadow)
    var s5TopHardSh = addRectShape(mainComp, "S5_QuoHardShadow", 1460, 294, 24, COL.navy, null, 0, [900, 266], 20.28, s5Out);
    s5TopHardSh.parent = s5TopNull;
    s5TopHardSh.property("ADBE Transform Group").property("ADBE Position").setValue([66, 66]);

    // Bold white card with vivid yellow graphic border
    var s5CardTop = addRectShape(mainComp, "S5_QuoCardBg", 1460, 294, 24, COL.white, COL.yellowMain, 8, [900, 266], 20.28, s5Out);
    s5CardTop.parent = s5TopNull;
    s5CardTop.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);

    // Official QUO Card PNG scaled boldly to 77% (fills the tilted hero card edge-to-edge)
    var s5QuoImg = addFootage(mainComp, "quocard", "S5_Img_QuoCard", [900, 276], 77, 20.32, s5Out);
    s5QuoImg.parent = s5TopNull;
    s5QuoImg.property("ADBE Transform Group").property("ADBE Position").setValue([50, 62]);

    // Punchy top-left ribbon badge breaking the card's upper border
    var s5BadgeSh = addRectShape(mainComp, "S5_PresentPillSh", 564, 70, 35, COL.navy, null, 0, [560, 118], 20.42, s5Out);
    s5BadgeSh.parent = s5TopNull;
    s5BadgeSh.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 332, 50 - 140]);
    s5BadgeSh.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-2.2);
    popScale(s5BadgeSh, 20.42, 100, 0.34, 1.24);

    var s5BadgeTop = addRectShape(mainComp, "S5_PresentPill", 564, 70, 35, COL.blueMain, COL.white, 5, [560, 118], 20.42, s5Out);
    s5BadgeTop.parent = s5TopNull;
    s5BadgeTop.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 340, 50 - 148]);
    s5BadgeTop.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-2.2);
    popScale(s5BadgeTop, 20.42, 100, 0.34, 1.24);

    var s5BadgeTxt = addTextLayer(mainComp, "S5_PresentPillTxt", "\u3046\u308c\u3057\u3044\u6765\u5834\u8005\u30d7\u30ec\u30bc\u30f3\u30c8\uff01", FONT_BLACK, 35, COL.white, [560, 118], 20.45, s5Out, 20);
    s5BadgeTxt.parent = s5TopNull;
    s5BadgeTxt.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 340, 50 - 148]);
    s5BadgeTxt.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-2.2);
    popScale(s5BadgeTxt, 20.45, 100, 0.34, 1.24);

    // Now animate S5_TopGroup_CTRL: aggressive slam-in + tilt snap + narration peak beat pulse + live rock
    setKeysEaseOut(s5TopTr.property("ADBE Position"), 20.28, [560, 180], 20.68, [900, 266], 88, 16);
    s5TopTr.property("ADBE Position").expression = "var amp = linear(time, 20.68, 20.95, 0, 6); value + [0, Math.sin((time - 20.2) * 3.4) * amp];";
    setKeysEaseOut(s5TopTr.property("ADBE Rotate Z"), 20.28, -9.5, 20.72, -2.2, 84, 18);
    s5TopTr.property("ADBE Rotate Z").expression = "var r = linear(time, 20.72, 21.00, 0, 0.8); value + Math.sin((time - 20.2) * 2.5) * r;";
    var s5TopSc = s5TopTr.property("ADBE Scale");
    s5TopSc.setValueAtTime(20.28, [72, 72]);
    s5TopSc.setValueAtTime(20.54, [109, 109]);
    s5TopSc.setValueAtTime(20.72, [100, 100]);
    // Beat-synced impact pulse when narration says "500"
    s5TopSc.setValueAtTime(21.62, [100, 100]);
    s5TopSc.setValueAtTime(21.78, [107, 107]);
    s5TopSc.setValueAtTime(22.02, [100, 100]);
    applyEase(s5TopSc, s5TopSc.nearestKeyIndex(20.54), 78, 45);
    applyEase(s5TopSc, s5TopSc.nearestKeyIndex(20.72), 82, 33);
    applyEase(s5TopSc, s5TopSc.nearestKeyIndex(21.78), 72, 55);
    applyEase(s5TopSc, s5TopSc.nearestKeyIndex(22.02), 82, 33);
    s5CardTop.motionBlur = true;
    s5QuoImg.motionBlur = true;

    // Top-right 14-point Golden Starburst Promo Seal ("") overlapping card corner
    var s5SealNull = mainComp.layers.addNull();
    s5SealNull.name = "S5_StarSeal_CTRL";
    s5SealNull.inPoint = 20.52;
    s5SealNull.outPoint = s5Out;
    var s5SealTr = s5SealNull.property("ADBE Transform Group");
    s5SealTr.property("ADBE Anchor Point").setValue([50, 50]);
    s5SealTr.property("ADBE Position").setValue([1718, 174]);
    s5SealTr.property("ADBE Scale").setValue([100, 100]);

    var s5SealShape = mainComp.layers.addShape();
    s5SealShape.name = "S5_StarSeal_Bg";
    s5SealShape.inPoint = 20.52;
    s5SealShape.outPoint = s5Out;
    var s5SGrp = s5SealShape.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
    var s5SV = s5SGrp.property("ADBE Vectors Group");
    var s5Star = s5SV.addProperty("ADBE Vector Shape - Star");
    s5Star.property("ADBE Vector Star Type").setValue(1);
    s5Star.property("ADBE Vector Star Points").setValue(14);
    s5Star.property("ADBE Vector Star Outer Radius").setValue(108);
    s5Star.property("ADBE Vector Star Inner Radius").setValue(88);
    var s5SFill = s5SV.addProperty("ADBE Vector Graphic - Fill");
    s5SFill.property("ADBE Vector Fill Color").setValue(COL.yellowMain);
    var s5SStrk = s5SV.addProperty("ADBE Vector Graphic - Stroke");
    s5SStrk.property("ADBE Vector Stroke Color").setValue(COL.white);
    s5SStrk.property("ADBE Vector Stroke Width").setValue(7);
    addDropShadow(s5SealShape, 85, 10, 18, 140);
    s5SealShape.parent = s5SealNull;
    s5SealShape.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);
    s5SealShape.property("ADBE Transform Group").property("ADBE Rotate Z").expression = "(time - 20.52) * 18;";

    var s5SealTxt = addTextLayer(mainComp, "S5_StarSeal_Txt", "\u6765\u5834\n\u7279\u5178\uff01", FONT_BLACK, 42, COL.navy, [1718, 174], 20.52, s5Out, 10);
    s5SealTxt.parent = s5SealNull;
    s5SealTxt.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);
    s5SealTxt.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(10);

    popScale(s5SealNull, 20.52, 100, 0.40, 1.28);
    s5SealTr.property("ADBE Scale").expression = "var p = linear(time, 20.95, 21.15, 0, 5); var w = Math.sin((time - 20.5) * 6.0) * p; value + [w, w];";

    // ------------------------------------------------------------------
    // S5 BOTTOM HERO GROUP: AGGRESSIVE Counter-Tilted (+1.6 deg) Deep Navy Impact Block
    // ------------------------------------------------------------------
    var s5BotNull = mainComp.layers.addNull();
    s5BotNull.name = "S5_BotGroup_CTRL";
    s5BotNull.inPoint = 21.02;
    s5BotNull.outPoint = s5Out;
    var s5BotTr = s5BotNull.property("ADBE Transform Group");
    s5BotTr.property("ADBE Anchor Point").setValue([50, 50]);
    s5BotTr.property("ADBE Position").setValue([728, 758]);
    s5BotTr.property("ADBE Scale").setValue([100, 100]);
    s5BotTr.property("ADBE Rotate Z").setValue(0);

    // Bold vivid-yellow hard offset shadow behind Deep Navy hero block
    var s5BotHardSh = addRectShape(mainComp, "S5_WelcomeHardShadow", 1290, 412, 24, COL.yellowMain, null, 0, [728, 758], 21.02, s5Out);
    s5BotHardSh.parent = s5BotNull;
    s5BotHardSh.property("ADBE Transform Group").property("ADBE Position").setValue([66, 66]);

    // Deep Navy Hero Container with crisp 9px bright cyan border
    var s5CardBot = addRectShape(mainComp, "S5_WelcomeCard", 1290, 412, 24, COL.navy, COL.cyanBright, 9, [728, 758], 21.02, s5Out);
    s5CardBot.parent = s5BotNull;
    s5CardBot.property("ADBE Transform Group").property("ADBE Position").setValue([50, 50]);

    // Sub-tag pill:  (bold high-contrast white on vivid blue)
    var s5SubPill = addRectShape(mainComp, "S5_SubGradPill", 640, 56, 28, COL.blueMain, null, 0, [860, 616], 21.24, s5Out);
    s5SubPill.parent = s5BotNull;
    s5SubPill.property("ADBE Transform Group").property("ADBE Position").setValue([50 + 145, 50 - 142]);
    popScale(s5SubPill, 21.24, 100, 0.34, 1.14);

    var s5T2 = addTextLayer(mainComp, "S5_TxtGradSub", "\u5927\u5b66\u30fb\u77ed\u5927\u30fb\u5c02\u4fee\u5b66\u6821\u7b49", FONT_BLACK, 34, COL.white, [860, 616], 21.27, s5Out, 25);
    s5T2.parent = s5BotNull;
    s5T2.property("ADBE Transform Group").property("ADBE Position").setValue([50 + 145, 50 - 142]);
    popScale(s5T2, 21.27, 100, 0.34, 1.14);

    // MASSIVE HERO HEADLINE GROUP: 103(106pt Yellow) + (94pt White)
    // Unified under S5_GradHeadline_CTRL so both parts scale/pulse together with ZERO character overlap!
    var s5HeadNull = mainComp.layers.addNull();
    s5HeadNull.name = "S5_GradHeadline_CTRL";
    s5HeadNull.inPoint = 21.34;
    s5HeadNull.outPoint = s5Out;
    var s5HeadTr = s5HeadNull.property("ADBE Transform Group");
    s5HeadTr.property("ADBE Anchor Point").setValue([50, 50]);
    s5HeadTr.property("ADBE Scale").setValue([100, 100]);
    s5HeadNull.parent = s5BotNull;
    s5HeadTr.property("ADBE Position").setValue([50, 50 - 18]);

    var s5T1A = addTextLayer(mainComp, "S5_TxtGradYear", "\u4ee4\u548c10\u5e743\u6708", FONT_BLACK, 106, COL.yellowMain, [728, 740], 21.34, s5Out, -20);
    var s5T1B = addTextLayer(mainComp, "S5_TxtGradRole", "\u5352\u696d\u4e88\u5b9a\u8005", FONT_BLACK, 94, COL.white, [728, 740], 21.34, s5Out, -15);
    var rT1A = s5T1A.sourceRectAtTime(22.0, false);
    var rT1B = s5T1B.sourceRectAtTime(22.0, false);
    var gapT1 = 24;
    var rawTotalW = rT1A.width + gapT1 + rT1B.width;
    var fitScale = (rawTotalW > 1180) ? Math.floor((1180 / rawTotalW) * 100) : 100;
    var xLocA = -rawTotalW / 2 + rT1A.width / 2;
    var xLocB =  rawTotalW / 2 - rT1B.width / 2;

    // Animated bright cyan marker slash cleanly below "103"
    var s5MarkW = Math.round(rT1A.width + 16);
    var s5MarkBar = addRectShape(mainComp, "S5_GradUnderline", s5MarkW, 13, 6, COL.cyanBright, null, 0, [728, 795], 21.46, s5Out);
    s5MarkBar.parent = s5HeadNull;
    s5MarkBar.property("ADBE Transform Group").property("ADBE Position").setValue([50 + xLocA, 50 + 66]);
    var s5MarkSc = s5MarkBar.property("ADBE Transform Group").property("ADBE Scale");
    setKeysEaseOut(s5MarkSc, 21.46, [0, 100], 21.82, [100, 100], 86, 18);

    // Parent headline texts to unified S5_GradHeadline_CTRL before scaling the controller
    s5T1A.parent = s5HeadNull;
    s5T1A.property("ADBE Transform Group").property("ADBE Position").setValue([50 + xLocA, 50 - 2]);
    fadeOpacity(s5T1A, 21.34, 21.46, 0, 100);

    s5T1B.parent = s5HeadNull;
    s5T1B.property("ADBE Transform Group").property("ADBE Position").setValue([50 + xLocB, 50 + 2]);
    fadeOpacity(s5T1B, 21.36, 21.48, 0, 100);

    // Unified slam-in (1.42x -> 0.94x -> 1.00x) + climax pulse at 23.94s (ZERO overlap guaranteed!)
    var s5HeadSc = s5HeadTr.property("ADBE Scale");
    s5HeadSc.setValueAtTime(21.34, [fitScale * 1.42, fitScale * 1.42]);
    s5HeadSc.setValueAtTime(21.56, [fitScale * 0.94, fitScale * 0.94]);
    s5HeadSc.setValueAtTime(21.70, [fitScale, fitScale]);
    s5HeadSc.setValueAtTime(23.78, [fitScale, fitScale]);
    s5HeadSc.setValueAtTime(23.94, [fitScale * 1.07, fitScale * 1.07]);
    s5HeadSc.setValueAtTime(24.18, [fitScale, fitScale]);
    applyEase(s5HeadSc, s5HeadSc.nearestKeyIndex(21.56), 80, 45);
    applyEase(s5HeadSc, s5HeadSc.nearestKeyIndex(21.70), 82, 33);
    applyEase(s5HeadSc, s5HeadSc.nearestKeyIndex(23.94), 74, 55);
    applyEase(s5HeadSc, s5HeadSc.nearestKeyIndex(24.18), 82, 33);

    // High-contrast crisp white callout ribbon for parent message (46pt Bold Orange-Deep!)
    var s5BotRib = addRectShape(mainComp, "S5_ParentRibbon", 1200, 84, 16, COL.white, null, 0, [728, 886], 21.58, s5Out);
    s5BotRib.parent = s5BotNull;
    slideIn(s5BotRib, 21.58, 0.38, [50, 50 + 126], 200, 0, true);

    var s5T3 = addTextLayer(mainComp, "S5_TxtParent", "\u5e74\u672b\u306b\u5e30\u7701\u3055\u308c\u308b\u304a\u5b50\u3055\u3093\u3068\u305c\u3072\u3054\u4e00\u7dd2\u306b\uff01", FONT_BLACK, 46, COL.orangeDeep, [728, 886], 21.62, s5Out, 12);
    s5T3.parent = s5BotNull;
    slideIn(s5T3, 21.62, 0.38, [50, 50 + 126], 200, 0, true);

    // EXPLOSIVE STAMP BADGE:  breaking aggressively over top-left corner (-7 deg)!
    var s5WelSh = addRectShape(mainComp, "S5_TagDaiSh", 326, 88, 18, COL.orangeDeep, null, 0, [285, 568], 21.22, s5Out);
    s5WelSh.parent = s5BotNull;
    s5WelSh.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 442, 50 - 188]);
    s5WelSh.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-7.2);

    var s5WelTag = addRectShape(mainComp, "S5_TagDai", 326, 88, 18, COL.yellowMain, COL.white, 6, [278, 560], 21.22, s5Out);
    s5WelTag.parent = s5BotNull;
    s5WelTag.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 450, 50 - 196]);
    s5WelTag.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-7.2);

    var s5WelTagTxt = addTextLayer(mainComp, "S5_TagDaiTxt", "\u5927\u6b53\u8fce\uff01", FONT_BLACK, 54, COL.navy, [278, 560], 21.22, s5Out, 25);
    s5WelTagTxt.parent = s5BotNull;
    s5WelTagTxt.property("ADBE Transform Group").property("ADBE Position").setValue([50 - 450, 50 - 196]);
    s5WelTagTxt.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-7.2);

    // Rubber-stamp slam-down animation (185% -> 92% -> 100% + climax pulse at 23.78s)
    var stampLayers = [s5WelSh, s5WelTag, s5WelTagTxt];
    for (var si = 0; si < stampLayers.length; si++) {
        var stSc = stampLayers[si].property("ADBE Transform Group").property("ADBE Scale");
        stSc.setValueAtTime(21.22, [185, 185]);
        stSc.setValueAtTime(21.42, [92, 92]);
        stSc.setValueAtTime(21.56, [100, 100]);
        stSc.setValueAtTime(23.74, [100, 100]);
        stSc.setValueAtTime(23.90, [113, 113]);
        stSc.setValueAtTime(24.12, [100, 100]);
        applyEase(stSc, stSc.nearestKeyIndex(21.42), 82, 42);
        applyEase(stSc, stSc.nearestKeyIndex(21.56), 82, 33);
        applyEase(stSc, stSc.nearestKeyIndex(23.90), 75, 55);
        applyEase(stSc, stSc.nearestKeyIndex(24.12), 82, 33);
        fadeOpacity(stampLayers[si], 21.22, 21.30, 0, 100);
    }

    // Now animate S5_BotGroup_CTRL: aggressive slam-up from bottom-left + counter-tilt (+1.6 deg) + live kinetic rock
    setKeysEaseOut(s5BotTr.property("ADBE Position"), 21.02, [540, 960], 21.44, [728, 758], 88, 16);
    s5BotTr.property("ADBE Position").expression = "var amp = linear(time, 21.44, 21.72, 0, 6); value + [0, Math.sin((time - 21.0 + 1.4) * 3.2) * amp];";
    setKeysEaseOut(s5BotTr.property("ADBE Rotate Z"), 21.02, 7.5, 21.46, 1.6, 84, 18);
    s5BotTr.property("ADBE Rotate Z").expression = "var r = linear(time, 21.46, 21.75, 0, 0.7); value + Math.sin((time - 21.0 + 1.2) * 2.4) * r;";
    var s5BotSc = s5BotTr.property("ADBE Scale");
    s5BotSc.setValueAtTime(21.02, [76, 76]);
    s5BotSc.setValueAtTime(21.30, [106, 106]);
    s5BotSc.setValueAtTime(21.48, [100, 100]);
    applyEase(s5BotSc, s5BotSc.nearestKeyIndex(21.30), 78, 45);
    applyEase(s5BotSc, s5BotSc.nearestKeyIndex(21.48), 82, 33);
    s5CardBot.motionBlur = true;

    // Right-side Student & Woman Pair Character (enlarged 456px circular avatar with lively upbeat motion)
    var s5CharRingHalo = addCircleShape(mainComp, "S5_CharHaloRing", 506, null, COL.yellowSoft, 4, [1645, 735], 21.28, s5Out);
    s5CharRingHalo.property("ADBE Transform Group").property("ADBE Opacity").setValue(45);
    popScale(s5CharRingHalo, 21.28, 100, 0.44, 1.15);
    addCircularAvatar(mainComp, "S5_CharPair", "char7_pair", [1645, 735], 456, COL.white, COL.yellowMain, 10, 58, 0, 126, 21.34, 21.30, s5Out, 0.8);

    // Energetic dynamic sparkles around both hero blocks (clean clearance outside card borders)
    addStarSparkle(mainComp, "S5_Spark1", 28, 10, 4, COL.yellowMain, [84, 185], 20.55, s5Out, 0.0);
    addStarSparkle(mainComp, "S5_Spark2", 30, 11, 4, COL.cyanBright, [1495, 445], 20.75, s5Out, 1.2);
    addStarSparkle(mainComp, "S5_Spark3", 32, 11, 4, COL.white,      [1835, 448], 21.35, s5Out, 2.3);
    addStarSparkle(mainComp, "S5_Spark4", 34, 12, 4, COL.yellowMain, [1428, 975], 21.45, s5Out, 3.1);

    // ==================================================================
    // SCENE 6: END CARD   + QR + Instagram (25.0s .. 30.0s)
    // ==================================================================
    var s6In = 25.0, s6Out = 30.0;
    addGradientBg(mainComp, "S6_BG", s6In, s6Out, COL.white, COL.bluePale, [960, 0], [960, H]);

    // Subtle animated watermark band
    var s6Wm = addRectShape(mainComp, "S6_Watermark", 460, 1800, 0, COL.blueMain, null, 0, [1620, 540], s6In, s6Out);
    s6Wm.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(-22);
    s6Wm.property("ADBE Transform Group").property("ADBE Opacity").setValue(5);

    // Top & bottom thin brand accent bars
    addRectShape(mainComp, "S6_TopLine", W, 14, 0, COL.blueMain, null, 0, [W / 2, 7], s6In, s6Out);
    addRectShape(mainComp, "S6_BotLine", W, 14, 0, COL.orangeVivid, null, 0, [W / 2, H - 7], s6In, s6Out);

    // Top Event Reminder Pill
    var s6RemBg = addRectShape(mainComp, "S6_RemPill", 1580, 62, 31, COL.blueMain, null, 0, [960, 98], 25.12, s6Out);
    addDropShadow(s6RemBg, 40, 8, 16, 140);
    slideIn(s6RemBg, 25.12, 0.38, [960, 98], 0, -50, true);
    var s6RemTxt = addTextLayer(mainComp, "S6_RemTxt", "12.27(\u65e5) 13:00\u301c16:00 \u30a8\u30b9\u30fb\u30d0\u30fc\u30c9  \uff5c  \u53c2\u52a0\u4e88\u5b9a\u4f01\u696d 100\u793e\u4ee5\u4e0a\uff08103\u793e\uff09  \uff5c  \u4e8b\u524d\u7533\u8fbc\u307f\u4e0d\u8981\u30fb\u670d\u88c5\u81ea\u7531", FONT_BOLD, 28, COL.white, [960, 98], 25.16, s6Out, 15);
    slideIn(s6RemTxt, 25.16, 0.38, [960, 98], 0, -50, true);

    // Organization & Single Hero Search Bar
    var s6OrgTxt = addTextLayer(mainComp, "S6_OrgTxt", "\u8a73\u3057\u304f\u306f  \u98ef\u7530\u8077\u696d\u5b89\u5b9a\u5354\u4f1a \u516c\u5f0f\u30b5\u30a4\u30c8", FONT_BLACK, 38, COL.navy, [960, 198], 25.26, s6Out, 30);
    slideIn(s6OrgTxt, 25.26, 0.36, [960, 198], 0, 30, true);

    // Clean Hero Search Bar Only + click pulse animation!
    var s6Search = addFootage(mainComp, "search_bar", "S6_SearchBar", [960, 326], 94, 25.42, s6Out);
    addDropShadow(s6Search, 38, 10, 20, 140);
    var s6SSc = s6Search.property("ADBE Transform Group").property("ADBE Scale");
    s6SSc.setValueAtTime(25.42, [0, 0]);
    s6SSc.setValueAtTime(25.70, [100, 100]);
    s6SSc.setValueAtTime(25.86, [94, 94]);
    s6SSc.setValueAtTime(26.48, [94, 94]);
    s6SSc.setValueAtTime(26.62, [100, 100]);
    s6SSc.setValueAtTime(26.80, [94, 94]);
    applyEase(s6SSc, s6SSc.nearestKeyIndex(25.70), 75, 45);
    applyEase(s6SSc, s6SSc.nearestKeyIndex(25.86), 80, 33);
    applyEase(s6SSc, s6SSc.nearestKeyIndex(26.62), 70, 70);
    applyEase(s6SSc, s6SSc.nearestKeyIndex(26.80), 80, 33);

    // Middle 2-Column Action Cards (symmetrical: left 220..920, right 1000..1700, y=622, height=286 -> 479..765)
    // LEFT CARD: Official Website QR Code
    var s6QrCard = addRectShape(mainComp, "S6_QrCard", 700, 286, 26, COL.white, COL.blueMain, 4, [570, 622], 25.66, s6Out);
    addDropShadow(s6QrCard, 48, 12, 24, 140);
    slideIn(s6QrCard, 25.66, 0.42, [570, 622], -90, 36, true);

    var s6QrImg = addFootage(mainComp, "qr_code", "S6_QrCode", [375, 622], 112, 25.78, s6Out);
    popScale(s6QrImg, 25.78, 112, 0.38, 1.06);

    var s6QrPill = addRectShape(mainComp, "S6_QrPill", 340, 44, 22, COL.blueMain, null, 0, [708, 540], 25.82, s6Out);
    fadeOpacity(s6QrPill, 25.82, 26.02, 0, 100);
    var s6QrPillTxt = addTextLayer(mainComp, "S6_QrPillTxt", "\u30b9\u30de\u30db\u3067\u53c2\u52a0\u4f01\u696d\u3092\u30c1\u30a7\u30c3\u30af\uff01", FONT_BOLD, 22, COL.white, [708, 540], 25.84, s6Out, 10);
    fadeOpacity(s6QrPillTxt, 25.84, 26.04, 0, 100);

    var s6QrT1 = addTextLayer(mainComp, "S6_QrT1", "QR\u30b3\u30fc\u30c9\u304b\u3089\n\u8a73\u7d30\u30da\u30fc\u30b8\u3078\u30a2\u30af\u30bb\u30b9", FONT_BLACK, 33, COL.navy, [708, 634], 25.88, s6Out, 10);
    fadeOpacity(s6QrT1, 25.88, 26.10, 0, 100);
    var s6QrUrl = addTextLayer(mainComp, "S6_QrUrl", "\u30a4\u30a4\u30c0\u30ab\u30a4\u30b7\u30e3\u30ca\u30d3\u516c\u5f0f\u30b5\u30a4\u30c8", FONT_BOLD, 22, COL.blueDeep, [708, 718], 25.92, s6Out, 10);
    fadeOpacity(s6QrUrl, 25.92, 26.14, 0, 100);

    // RIGHT CARD: Instagram  (@IIDAJOB)
    var s6IgCard = addRectShape(mainComp, "S6_IgCard", 700, 286, 26, COL.white, COL.igPink, 4, [1350, 622], 25.74, s6Out);
    addDropShadow(s6IgCard, 48, 12, 24, 140);
    slideIn(s6IgCard, 25.74, 0.42, [1350, 622], 90, 36, true);

    var s6IgIconBg = addRectShape(mainComp, "S6_IgIconBg", 144, 144, 34, COL.igPink, null, 0, [1138, 622], 25.84, s6Out);
    var igRamp = s6IgIconBg.property("ADBE Effect Parade").addProperty("ADBE Ramp");
    igRamp.property("ADBE Ramp-0001").setValue([1066, 694]);
    igRamp.property("ADBE Ramp-0002").setValue(COL.igOrange);
    igRamp.property("ADBE Ramp-0003").setValue([1210, 550]);
    igRamp.property("ADBE Ramp-0004").setValue(COL.igPurple);
    popScale(s6IgIconBg, 25.84, 100, 0.38, 1.10);

    var s6IgFrame = addRectShape(mainComp, "S6_IgCamFrame", 94, 94, 25, null, COL.white, 8, [1138, 622], 25.84, s6Out);
    popScale(s6IgFrame, 25.84, 100, 0.38, 1.10);
    var s6IgLens = addCircleShape(mainComp, "S6_IgCamLens", 45, null, COL.white, 8, [1138, 622], 25.84, s6Out);
    popScale(s6IgLens, 25.84, 100, 0.38, 1.10);
    var s6IgDot = addCircleShape(mainComp, "S6_IgCamDot", 13, COL.white, null, 0, [1164, 595], 25.84, s6Out);
    popScale(s6IgDot, 25.84, 100, 0.38, 1.10);

    var s6IgT1 = addTextLayer(mainComp, "S6_IgTitle", "Instagram\n\u306f\u3058\u3081\u307e\u3057\u305f\uff01", FONT_BLACK, 38, COL.igPink, [1455, 580], 25.90, s6Out, 15);
    fadeOpacity(s6IgT1, 25.90, 26.12, 0, 100);
    var s6IgSub = addTextLayer(mainComp, "S6_IgSub", "\u30d5\u30a9\u30ed\u30fc\u30fb\u3044\u3044\u306d\uff01\u304a\u5f85\u3061\u3057\u3066\u3044\u307e\u3059", FONT_BOLD, 22, COL.slate, [1455, 656], 25.94, s6Out, 10);
    fadeOpacity(s6IgSub, 25.94, 26.16, 0, 100);

    var s6IgPill = addRectShape(mainComp, "S6_IgIdPill", 240, 46, 23, COL.igPink, null, 0, [1455, 716], 25.96, s6Out);
    fadeOpacity(s6IgPill, 25.96, 26.18, 0, 100);
    var s6IgId = addTextLayer(mainComp, "S6_IgIdTxt", "@IIDAJOB", FONT_BLACK, 26, COL.white, [1455, 716], 25.98, s6Out, 40);
    fadeOpacity(s6IgId, 25.98, 26.20, 0, 100);

    // LARGE, HIGH-VISIBILITY CONTACT BAR (y=892, height 140 -> 822..962, symmetrical & dominant on TV!)
    var s6ConCard = addRectShape(mainComp, "S6_ContactCard", 1520, 140, 26, COL.navy, null, 0, [960, 892], 25.48, s6Out);
    addDropShadow(s6ConCard, 60, 12, 24, 140);
    slideIn(s6ConCard, 25.48, 0.42, [960, 892], 0, 90, true);

    var s6ConPill = addRectShape(mainComp, "S6_ContactPill", 260, 70, 35, COL.orangeVivid, null, 0, [362, 892], 25.56, s6Out);
    popScale(s6ConPill, 25.56, 100, 0.36, 1.08);
    var s6ConPillTxt = addTextLayer(mainComp, "S6_ContactPillTxt", "\u304a\u554f\u3044\u5408\u308f\u305b", FONT_BLACK, 34, COL.white, [362, 892], 25.58, s6Out, 20);
    popScale(s6ConPillTxt, 25.58, 100, 0.36, 1.08);

    var s6ConOrg = addTextLayer(mainComp, "S6_ContactOrg", "\u98ef\u7530\u8077\u696d\u5b89\u5b9a\u5354\u4f1a", FONT_BLACK, 46, COL.white, [800, 870], 25.60, s6Out, 20);
    fadeOpacity(s6ConOrg, 25.60, 25.86, 0, 100);
    var s6ConSub = addTextLayer(mainComp, "S6_ContactSub", "\uff08\u98ef\u7530\u5546\u5de5\u4f1a\u8b70\u6240\u5185\uff09", FONT_BOLD, 30, COL.blueLight, [800, 922], 25.62, s6Out, 15);
    fadeOpacity(s6ConSub, 25.62, 25.88, 0, 100);

    var s6ConTel = addTextLayer(mainComp, "S6_ContactTel", "TEL. 0265-24-1234", FONT_BLACK, 58, COL.yellowSoft, [1396, 892], 25.64, s6Out, 15);
    popScale(s6ConTel, 25.64, 100, 0.38, 1.07);

    // ==================================================================
    // DYNAMIC DIAGONAL SWIPE TRANSITIONS BETWEEN ALL 6 SCENES (TOP LAYERS)
    // ==================================================================
    addDiagonalWipe(mainComp, "TR_S1_to_S2", 2.20,  COL.orangeVivid, COL.white);
    addDiagonalWipe(mainComp, "TR_S2_to_S3", 6.00,  COL.yellowMain,  COL.blueMain);
    addDiagonalWipe(mainComp, "TR_S3_to_S4", 13.80, COL.orangeMain,  COL.white);
    addDiagonalWipe(mainComp, "TR_S4_to_S5", 20.20, COL.blueMain,    COL.orangeVivid);
    addDiagonalWipe(mainComp, "TR_S5_to_S6", 25.00, COL.blueMain,    COL.white);

    // ------------------------------------------------------------------
    // COMP 2: 00_MASTER_36sec_ColorBars (3s Bars + 30s MainCM + 3s Bars)
    // ------------------------------------------------------------------
    var masterComp = proj.items.addComp("00_MASTER_36sec_ColorBars", W, H, 1.0, MASTER_DUR, FPS);
    masterComp.parentFolder = folderComps;

    // Head 3.0s SMPTE HD Color Bars (silent)
    var barHead = masterComp.layers.add(imported["color_bars"]);
    barHead.name = "HEAD_3sec_SMPTE_ColorBars";
    barHead.startTime = 0.0;
    barHead.inPoint = 0.0;
    barHead.outPoint = BAR_DUR;

    // Main 30.0s CM (3.0s .. 33.0s)
    var mainLayer = masterComp.layers.add(mainComp);
    mainLayer.name = "MAIN_CM_30sec";
    mainLayer.startTime = BAR_DUR;
    mainLayer.inPoint = BAR_DUR;
    mainLayer.outPoint = BAR_DUR + MAIN_DUR;

    // Tail 3.0s SMPTE HD Color Bars (silent)
    var barTail = masterComp.layers.add(imported["color_bars"]);
    barTail.name = "TAIL_3sec_SMPTE_ColorBars";
    barTail.startTime = BAR_DUR + MAIN_DUR;
    barTail.inPoint = BAR_DUR + MAIN_DUR;
    barTail.outPoint = MASTER_DUR;

    masterComp.openInViewer();

    // Ensure final_outputs directory exists
    var finalDir = "g:/\u30de\u30a4\u30c9\u30e9\u30a4\u30d6/git/nobuyukitakahashi/02_Creative_Dept/aftereffects/final_outputs/furusato2026_cm";
    var finalFolder = new Folder(finalDir);
    if (!finalFolder.exists) { finalFolder.create(); }

    // Save final master .aep
    var masterAep = new File(finalDir + "/furusato2026_cm_master.aep");
    proj.save(masterAep);

    // Render 36sec master MP4 via H.264 15 Mbps template (30fps, 1920x1080, 48kHz stereo)
    while (proj.renderQueue.numItems > 0) { proj.renderQueue.item(1).remove(); }
    var rq = proj.renderQueue.items.add(masterComp);
    var om = rq.outputModule(1);
    om.applyTemplate("H.264 - \u30ec\u30f3\u30c0\u30ea\u30f3\u30b0\u8a2d\u5b9a\u3092\u4e00\u81f4 - 15 Mbps");
    var masterMp4 = new File(finalDir + "/2026-12-27_\u3075\u308b\u3055\u3068\u5408\u540c\u4f01\u696d\u8aac\u660e\u4f1a2026_CM_36sec.mp4");
    if (masterMp4.exists) { try { masterMp4.remove(); } catch(_) {} }
    om.file = masterMp4;
    proj.renderQueue.render();

    return JSON.stringify({
        ok: true,
        masterAep: masterAep.fsName,
        masterMp4: masterMp4.fsName,
        mp4Exists: masterMp4.exists,
        mp4Size: masterMp4.length,
        renderStatus: rq.status,
        masterComp: masterComp.name,
        masterDuration: masterComp.duration,
        masterFps: masterComp.frameRate,
        mainComp: mainComp.name,
        mainDuration: mainComp.duration,
        mainLayers: mainComp.numLayers
    });
})();

app.endUndoGroup();
return __buildResult;
