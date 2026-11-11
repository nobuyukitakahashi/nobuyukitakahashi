// Test script for Adobe Photoshop 2027 (v28.0) MCP verification
// Creates a 1600 x 1000 px (300 dpi, RGB 8-bit) multi-layer PSD composition
// featuring CVN Brand Green (#00a273) visual badge, cards, color chips, and typography layers

app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.POINTS;

while (app.documents.length > 0) {
  app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
}

var W = 1600;
var H = 1000;
var doc = app.documents.add(
  UnitValue(W, "px"),
  UnitValue(H, "px"),
  300,
  "CVN_Photoshop_MCP_Verify",
  NewDocumentMode.RGB,
  DocumentFill.WHITE,
  1.0,
  BitsPerChannelType.EIGHT
);

function makeRGB(r, g, b) {
  var c = new SolidColor();
  c.rgb.red = r;
  c.rgb.green = g;
  c.rgb.blue = b;
  return c;
}

var colDarkBg     = makeRGB(14, 29, 26);    // Deep emerald dark background
var colCardWhite  = makeRGB(255, 255, 255); // Crisp card white
var colHeaderMint = makeRGB(232, 247, 242); // Soft mint header band
var colCvnGreen   = makeRGB(0, 162, 115);   // CVN Primary Brand Green (#00a273)
var colCvnTeal    = makeRGB(0, 198, 148);   // Bright teal accent
var colDarkText   = makeRGB(20, 42, 38);    // Deep charcoal-green text
var colSubText    = makeRGB(70, 102, 95);   // Muted slate subtext
var colCyanChip   = makeRGB(0, 168, 232);   // Cyan chip
var colDarkChip   = makeRGB(32, 48, 45);    // Charcoal chip
var colGoldChip   = makeRGB(245, 196, 35);  // Warm yellow/gold chip

function fillRectSelection(layer, left, top, right, bottom, solidCol) {
  doc.activeLayer = layer;
  var region = [[left, top], [right, top], [right, bottom], [left, bottom]];
  doc.selection.select(region);
  doc.selection.fill(solidCol);
  doc.selection.deselect();
}

// 1. Background Layer Set
var bgSet = doc.layerSets.add();
bgSet.name = "01_Background_Group";

var bgBase = bgSet.artLayers.add();
bgBase.name = "Dark_Emerald_Backdrop";
fillRectSelection(bgBase, 0, 0, W, H, colDarkBg);

// Outer accent frame border
var outerFrame = bgSet.artLayers.add();
outerFrame.name = "Brand_Green_Outer_Card";
fillRectSelection(outerFrame, 44, 44, W - 44, H - 44, colCvnGreen);

var innerCard = bgSet.artLayers.add();
innerCard.name = "Main_White_Canvas_Card";
fillRectSelection(innerCard, 52, 52, W - 52, H - 52, colCardWhite);

var headerBand = bgSet.artLayers.add();
headerBand.name = "Top_Mint_Header_Band";
fillRectSelection(headerBand, 88, 88, W - 88, 280, colHeaderMint);

// Left accent bar in header
var headerAccent = bgSet.artLayers.add();
headerAccent.name = "Header_Left_Accent_Bar";
fillRectSelection(headerAccent, 88, 88, 106, 280, colCvnGreen);

// 2. Visual Badge & Color Chips Layer Set
var badgeSet = doc.layerSets.add();
badgeSet.name = "02_Visual_Badge_and_Chips";

var badgeShadow = badgeSet.artLayers.add();
badgeShadow.name = "Badge_Soft_Accent_Backing";
fillRectSelection(badgeShadow, 144, 356, 668, 604, colHeaderMint);

var badgeMain = badgeSet.artLayers.add();
badgeMain.name = "CVN_Green_Hero_Badge";
fillRectSelection(badgeMain, 136, 348, 660, 596, colCvnGreen);

// White "+" emblem inside left of badge
var plusEmblem = badgeSet.artLayers.add();
plusEmblem.name = "Plus_Cross_Emblem";
fillRectSelection(plusEmblem, 240, 404, 280, 540, colCardWhite);
fillRectSelection(plusEmblem, 192, 452, 328, 492, colCardWhite);

// Horizontal divider line under hero section
var dividerLine = badgeSet.artLayers.add();
dividerLine.name = "Section_Divider_Line";
fillRectSelection(dividerLine, 136, 676, W - 136, 682, colHeaderMint);

// 4 Color Chips at bottom
var chipSpecs = [
  { name: "Chip_1_CVN_Green",  col: colCvnGreen, left: 136,  right: 446 },
  { name: "Chip_2_Bright_Teal", col: colCvnTeal,  left: 476,  right: 786 },
  { name: "Chip_3_Cyan_Accent", col: colCyanChip, left: 816,  right: 1126 },
  { name: "Chip_4_Dark_Slate",  col: colDarkChip, left: 1156, right: 1464 }
];

for (var i = 0; i < chipSpecs.length; i++) {
  var cs = chipSpecs[i];
  var chipLy = badgeSet.artLayers.add();
  chipLy.name = cs.name;
  fillRectSelection(chipLy, cs.left, 740, cs.right, 860, cs.col);
}

// 3. Typography Layer Set
var textSet = doc.layerSets.add();
textSet.name = "03_Typography_Group";

function addTextLayer(layerName, contents, xPx, yPx, sizePx, rgbCol) {
  var tl = textSet.artLayers.add();
  tl.kind = LayerKind.TEXT;
  tl.name = layerName;
  var ti = tl.textItem;
  ti.contents = contents;
  try {
    ti.font = "Arial-BoldMT";
  } catch (_f) {}
  // In Photoshop DOM, textItem.size is evaluated at 72 pt/inch relative to doc.resolution.
  // Scaling by (72 / doc.resolution) guarantees exact pixel typography regardless of DPI.
  var sizePt = sizePx * (72.0 / doc.resolution);
  ti.size = new UnitValue(sizePt, "pt");
  ti.color = rgbCol;
  ti.position = [new UnitValue(xPx, "px"), new UnitValue(yPx, "px")];
  return tl;
}

addTextLayer(
  "Title_Header",
  "ADOBE PHOTOSHOP 2027 MCP VERIFIED",
  140,
  168,
  46,
  colCvnGreen
);

addTextLayer(
  "Subtitle_Header",
  "Multi-Layer PSD Composition & Automated Retouching Pipeline (02_Creative_Dept)",
  142,
  232,
  26,
  colDarkText
);

addTextLayer(
  "Badge_CVN_Text",
  "cvn",
  368,
  508,
  108,
  colCardWhite
);

addTextLayer(
  "Hero_Brand_Title",
  "plus mobile",
  716,
  486,
  102,
  colCvnGreen
);

addTextLayer(
  "Hero_Specs_Caption",
  "1600x1000px @ 300dpi | RGB 8-bit | Layered PSD & PNG Visual Audit Ready",
  716,
  564,
  20,
  colSubText
);

addTextLayer("Chip_Label_1", "HEX #00A273", 182, 812, 26, colCardWhite);
addTextLayer("Chip_Label_2", "RGB(0,198,148)", 506, 812, 26, colCardWhite);
addTextLayer("Chip_Label_3", "CYAN ACCENT", 856, 812, 26, colCardWhite);
addTextLayer("Chip_Label_4", "PSD LAYERED", 1196, 812, 26, colCardWhite);

return JSON.stringify({
  created: true,
  docName: doc.name,
  widthPx: Number(doc.width.as("px")),
  heightPx: Number(doc.height.as("px")),
  resolutionDpi: Number(doc.resolution),
  layerSetsCount: Number(doc.layerSets.length),
  topLevelLayersCount: Number(doc.layers.length)
});
