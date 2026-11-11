// Test script for Adobe Illustrator 2027 MCP verification
// Creates a CMYK document (800 x 500 pt) with CVN Brand Green (C:90 M:0 Y:70 K:0) vector badge & typography

while (app.documents.length > 0) {
  app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
}

var preset = new DocumentPreset();
preset.title = "CVN_Illustrator_MCP_Verify";
preset.width = 800;
preset.height = 500;
preset.colorMode = DocumentColorSpace.CMYK;
preset.units = RulerUnits.Points;

var doc = app.documents.addDocument(DocumentColorSpace.CMYK, preset);
var abRect = doc.artboards[0].artboardRect; // [left, top, right, bottom]
var L = abRect[0];
var T = abRect[1];
var W = abRect[2] - abRect[0];
var H = abRect[1] - abRect[3];

function makeCMYK(c, m, y, k) {
  var col = new CMYKColor();
  col.cyan = c;
  col.magenta = m;
  col.yellow = y;
  col.black = k;
  return col;
}

var cvnGreen = makeCMYK(90, 0, 70, 0);
var cvnDark = makeCMYK(85, 65, 55, 70);
var cvnLightBg = makeCMYK(8, 0, 6, 0);
var pureWhite = makeCMYK(0, 0, 0, 0);

// Create named Swatches in document
function addNamedSwatch(name, cmykCol) {
  try {
    var existing = doc.swatches.getByName(name);
    if (existing) return existing;
  } catch (e) {}
  var sw = doc.swatches.add();
  sw.name = name;
  sw.color = cmykCol;
  return sw;
}
addNamedSwatch("CVN_Brand_Green_C90M0Y70K0", cvnGreen);
addNamedSwatch("CVN_Dark_Charcoal", cvnDark);

// Layer setup
var bgLayer = doc.layers[0];
bgLayer.name = "Background_Layer";
var badgeLayer = doc.layers.add();
badgeLayer.name = "Vector_Badge_Layer";
var textLayer = doc.layers.add();
textLayer.name = "Typography_Layer";

// 1. Soft card background on Background_Layer
var bgCard = bgLayer.pathItems.roundedRectangle(T - 24, L + 24, W - 48, H - 48, 28, 28);
bgCard.filled = true;
bgCard.fillColor = pureWhite;
bgCard.stroked = true;
bgCard.strokeWidth = 3;
bgCard.strokeColor = cvnGreen;

// Header accent band
var topBand = bgLayer.pathItems.roundedRectangle(T - 44, L + 44, W - 88, 96, 18, 18);
topBand.filled = true;
topBand.fillColor = cvnLightBg;
topBand.stroked = false;

// 2. Vector Capsule Badge & Geometric Emblem on Vector_Badge_Layer
var pillBadge = badgeLayer.pathItems.roundedRectangle(T - 175, L + 68, 260, 120, 60, 60);
pillBadge.filled = true;
pillBadge.fillColor = cvnGreen;
pillBadge.stroked = false;

// White geometric "+" emblem inside left of pill badge
var cx = L + 132;
var cy = T - 235;
var vBar = badgeLayer.pathItems.roundedRectangle(cy + 34, cx - 10, 20, 68, 10, 10);
vBar.filled = true;
vBar.fillColor = pureWhite;
vBar.stroked = false;

var hBar = badgeLayer.pathItems.roundedRectangle(cy + 10, cx - 34, 68, 20, 10, 10);
hBar.filled = true;
hBar.fillColor = pureWhite;
hBar.stroked = false;

// 3. Typography helper
function addPointText(contents, x, y, sizePt, fillCol) {
  var tf = textLayer.textFrames.add();
  tf.contents = contents;
  var attr = tf.textRange.characterAttributes;
  attr.size = sizePt;
  attr.fillColor = fillCol;
  try {
    attr.textFont = app.textFonts.getByName("Arial-BoldMT");
  } catch (e) {
    try {
      attr.textFont = app.textFonts.getByName("KozGoPr6N-Bold");
    } catch (e2) {}
  }
  tf.left = x;
  tf.top = y;
  return tf;
}

// Decorative CMYK registration chips & individually aligned labels
var barSpecs = [
  { label: "Cyan: 90%",        col: makeCMYK(90, 0, 0, 0),  txtCol: pureWhite },
  { label: "Magenta: 0%",      col: makeCMYK(0, 0, 0, 12),  txtCol: cvnDark   },
  { label: "Yellow: 70%",      col: makeCMYK(0, 0, 75, 0),  txtCol: cvnDark   },
  { label: "CMYK(90,0,70,0)",  col: cvnGreen,               txtCol: pureWhite }
];
for (var b = 0; b < barSpecs.length; b++) {
  var bx = L + 68 + b * 168;
  var by = T - 392;
  var chip = badgeLayer.pathItems.roundedRectangle(by, bx, 152, 40, 10, 10);
  chip.filled = true;
  chip.fillColor = barSpecs[b].col;
  chip.stroked = false;
  addPointText(barSpecs[b].label, bx + 18, by - 11, 13, barSpecs[b].txtCol);
}

addPointText("ADOBE ILLUSTRATOR 2027 MCP VERIFIED", L + 72, T - 62, 24, cvnGreen);
addPointText("CMYK Vector & Print Automation Pipeline (02_Creative_Dept)", L + 72, T - 98, 14, cvnDark);
addPointText("cvn", L + 184, T - 202, 54, pureWhite);
addPointText("plus mobile", L + 356, T - 184, 52, cvnGreen);
addPointText("Primary CMYK: C90 M0 Y70 K0  |  Outlines & Artboard Export Ready", L + 358, T - 262, 12.5, cvnDark);

return JSON.stringify({
  created: true,
  docName: doc.name,
  colorSpace: String(doc.documentColorSpace),
  layersCount: doc.layers.length,
  pathItemsCount: doc.pathItems.length,
  textFramesCount: doc.textFrames.length
});
