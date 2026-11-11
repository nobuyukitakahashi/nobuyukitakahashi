Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap("C:/Users/nobuy/.gemini/antigravity/brain/cf440cba-1843-494a-be0f-dcf6ae9d7919/.user_uploaded/media_1793863159631_a5a50c12.png")

$script = @"
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;

public class ContourExtractor {
    private static double[] GetPt(int edge, int x, int y, double a00, double a10, double a11, double a01) {
        if (edge == 0) return new double[]{ x + (128.0 - a00)/(a10 - a00), y };
        if (edge == 1) return new double[]{ x + 1, y + (128.0 - a10)/(a11 - a10) };
        if (edge == 2) return new double[]{ x + (128.0 - a01)/(a11 - a01), y + 1 };
        return new double[]{ x, y + (128.0 - a00)/(a01 - a00) };
    }

    public static string Trace(Bitmap bmp, int xMin, int xMax) {
        int H = bmp.Height;
        var segs = new List<double[]>();
        int[,] table = new int[,] {
            {-1,-1,-1,-1}, {3,0,-1,-1}, {0,1,-1,-1}, {3,1,-1,-1},
            {1,2,-1,-1}, {3,0,1,2}, {0,2,-1,-1}, {3,2,-1,-1},
            {2,3,-1,-1}, {2,0,-1,-1}, {0,1,2,3}, {2,1,-1,-1},
            {1,3,-1,-1}, {1,0,-1,-1}, {0,3,-1,-1}, {-1,-1,-1,-1}
        };
        for (int y = -1; y < H; y++) {
            for (int x = xMin - 1; x <= xMax + 1; x++) {
                double a00 = (x >= 0 && x < bmp.Width && y >= 0 && y < H) ? bmp.GetPixel(x, y).A : 0;
                double a10 = (x+1 >= 0 && x+1 < bmp.Width && y >= 0 && y < H) ? bmp.GetPixel(x+1, y).A : 0;
                double a11 = (x+1 >= 0 && x+1 < bmp.Width && y+1 >= 0 && y+1 < H) ? bmp.GetPixel(x+1, y+1).A : 0;
                double a01 = (x >= 0 && x < bmp.Width && y+1 >= 0 && y+1 < H) ? bmp.GetPixel(x, y+1).A : 0;
                int mask = (a00 >= 128 ? 1 : 0) | (a10 >= 128 ? 2 : 0) | (a11 >= 128 ? 4 : 0) | (a01 >= 128 ? 8 : 0);
                if (mask == 0 || mask == 15) continue;
                var p1 = GetPt(table[mask, 0], x, y, a00, a10, a11, a01);
                var p2 = GetPt(table[mask, 1], x, y, a00, a10, a11, a01);
                segs.Add(new double[]{ p1[0], p1[1], p2[0], p2[1] });
                if (table[mask, 2] != -1) {
                    var p3 = GetPt(table[mask, 2], x, y, a00, a10, a11, a01);
                    var p4 = GetPt(table[mask, 3], x, y, a00, a10, a11, a01);
                    segs.Add(new double[]{ p3[0], p3[1], p4[0], p4[1] });
                }
            }
        }
        var pts = new List<double[]>();
        var used = new bool[segs.Count];
        pts.Add(new double[]{ segs[0][0], segs[0][1] });
        pts.Add(new double[]{ segs[0][2], segs[0][3] });
        used[0] = true;
        while (true) {
            var last = pts[pts.Count - 1];
            int nextIdx = -1;
            for (int i = 0; i < segs.Count; i++) {
                if (used[i]) continue;
                if (Math.Abs(segs[i][0] - last[0]) < 1e-4 && Math.Abs(segs[i][1] - last[1]) < 1e-4) {
                    nextIdx = i; break;
                }
            }
            if (nextIdx == -1) break;
            used[nextIdx] = true;
            pts.Add(new double[]{ segs[nextIdx][2], segs[nextIdx][3] });
        }
        // Two passes of Gaussian smoothing on the closed contour
        int N = pts.Count - 1;
        var cur = new List<double[]>();
        for (int i = 0; i < N; i++) cur.Add(pts[i]);
        for (int pass = 0; pass < 2; pass++) {
            var next = new List<double[]>();
            for (int i = 0; i < N; i++) {
                var pPrev = cur[(i - 1 + N) % N];
                var pCurr = cur[i];
                var pNext = cur[(i + 1) % N];
                next.Add(new double[]{ (pPrev[0] + 2*pCurr[0] + pNext[0])/4.0, (pPrev[1] + 2*pCurr[1] + pNext[1])/4.0 });
            }
            cur = next;
        }
        var sb = new StringBuilder();
        for (int i = 0; i < N; i += 3) {
            sb.Append(i == 0 ? "M " : "L ");
            sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0:F1},{1:F1} ", cur[i][0], cur[i][1]);
        }
        sb.Append("Z");
        return sb.ToString();
    }
}
"@
Add-Type -TypeDefinition $script -ReferencedAssemblies System.Drawing
$dc = [ContourExtractor]::Trace($bmp, 0, 205)
$dv = [ContourExtractor]::Trace($bmp, 215, 430)
$dn = [ContourExtractor]::Trace($bmp, 448, 662)
$bmp.Dispose()

# Save paths to JSON for reuse
$obj = @{ c = $dc; v = $dv; n = $dn } | ConvertTo-Json
$outPath = Join-Path $PSScriptRoot "cvn_paths.json"
[System.IO.File]::WriteAllText($outPath, $obj, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Saved $outPath successfully. Lengths: c=$($dc.Length), v=$($dv.Length), n=$($dn.Length)"
