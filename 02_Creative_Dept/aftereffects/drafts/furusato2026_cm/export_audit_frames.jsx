// export_audit_frames.jsx
// Export key frames from 00_MASTER_36sec_ColorBars for visual inspection
var outDir = "g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/aftereffects/drafts/furusato2026_cm/audit_frames";
var folder = new Folder(outDir);
if (!folder.exists) { folder.create(); }

var proj = app.project;
var comp = null;
for (var i = 1; i <= proj.numItems; i++) {
    var it = proj.item(i);
    if (it instanceof CompItem && it.name === "00_MASTER_36sec_ColorBars") {
        comp = it;
        break;
    }
}
if (!comp) {
    throw new Error("Comp 00_MASTER_36sec_ColorBars not found");
}

var shots = [
    { name: "01_head_bar_1.5s.png",        t: 1.50 },
    { name: "02_scene1_hook_5.5s.png",     t: 5.50 },
    { name: "03_trans1_6.5s.png",          t: 6.50 },
    { name: "04_scene2_count_9.0s.png",    t: 9.00 },
    { name: "05_scene2_title_10.5s.png",   t: 10.50 },
    { name: "06_scene3_sched_16.8s.png",   t: 16.80 },
    { name: "07_scene4_recom_22.2s.png",   t: 22.20 },
    { name: "08_scene5_quocard_26.5s.png", t: 26.50 },
    { name: "09_scene6_endcard_31.0s.png", t: 31.00 },
    { name: "10_tail_bar_34.5s.png",       t: 34.50 }
];

var exported = [];
for (var j = 0; j < shots.length; j++) {
    var s = shots[j];
    var f = new File(outDir + "/" + s.name);
    comp.saveFrameToPng(s.t, f);
    exported.push({ name: s.name, t: s.t, exists: f.exists, length: f.length });
}

return JSON.stringify({ ok: true, count: exported.length, files: exported });
