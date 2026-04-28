"""
patch_mw_v2.py — replaces Milky Way data + rendering with photorealistic version.

Changes:
1. Replace SG_MW_DATA (stride-4) with new SG_MW_DATA (stride-5) + SG_MW_DUST
2. Replace sgDrawMilkyWay function with 4-layer renderer + dark dust lanes
"""
import re, sys

HTML   = r"C:\Users\Owner\anya.github.io\index.html"
MW_JS  = r"C:\Users\Owner\anya.github.io\mw_data.js"

html = open(HTML,  encoding="utf-8").read()
mw   = open(MW_JS, encoding="utf-8").read().strip()

# ── 1. Replace old SG_MW_DATA block ──────────────────────────────────────────
# Find from "var SG_MW_DATA=[" to closing "];\n"
mw_start = html.find("var SG_MW_DATA=[")
if mw_start == -1:
    sys.exit("ERROR: SG_MW_DATA not found")
mw_end = html.find("];\n", mw_start) + 3
html = html[:mw_start] + mw + "\n" + html[mw_end:]
print(f"  SG_MW_DATA replaced ({len(mw):,} chars)", file=sys.stderr)

# ── 2. Replace sgDrawMilkyWay function ───────────────────────────────────────
# Find function boundaries
MW_FUNC_MARKER = "// ── Milky Way band"
mwf_start = html.find(MW_FUNC_MARKER)
if mwf_start == -1:
    sys.exit("ERROR: sgDrawMilkyWay marker not found")

# Walk braces to find end of function
brace = 0
opened = False
mwf_end = mwf_start
for i in range(mwf_start, min(mwf_start + 8000, len(html))):
    if html[i] == '{': brace += 1; opened = True
    elif html[i] == '}':
        brace -= 1
        if opened and brace == 0:
            mwf_end = i + 1
            break

OLD_FUNC = html[mwf_start:mwf_end]

NEW_FUNC = r"""// ── Milky Way band — photorealistic 4-layer renderer ─────────────────────────
function sgDrawMilkyWay(ctx, W, H) {
  if (typeof SG_MW_DATA === 'undefined') return;
  var d = SG_MW_DATA;
  var pxPerDeg = sgScale * Math.PI / 180;

  // Layer visual parameters [radiusScale, alphaScale, R, G, B]
  //   0=outerHalo  1=innerHalo  2=spine  3=GCbulge
  var LP = [
    [2.0, 0.050, 148, 162, 208],   // 0: outer halo — wide, cool blue-white
    [1.05,0.092, 188, 200, 228],   // 1: inner halo — blue-white
    [0.42,0.200, 228, 225, 212],   // 2: spine      — near-white, faint warm
    [1.00,0.110, 255, 232, 178],   // 3: GC bulge   — warm cream/golden
  ];

  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  // Draw layers in order: halo → inner → spine → GC (so bright parts are on top)
  for (var layer = 0; layer < 4; layer++) {
    var lp = LP[layer];
    var rScale = lp[0], aScale = lp[1], cr = lp[2], cg = lp[3], cb = lp[4];

    for (var i = 0; i < d.length; i += 5) {
      if (d[i + 4] !== layer) continue;
      var p = sgProject(d[i], d[i + 1]);
      if (!p.visible) continue;
      if (p.x < -W * 0.35 || p.x > W * 1.35 ||
          p.y < -H * 0.35 || p.y > H * 1.35) continue;

      var hw  = d[i + 2];
      var bri = d[i + 3];
      var r   = hw * pxPerDeg * rScale;
      if (r < 3) continue;

      var a0 = bri * aScale;
      var a1 = a0 * 0.48;
      var a2 = a0 * 0.14;
      var grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
      grd.addColorStop(0,    'rgba(' + cr + ',' + cg + ',' + cb + ',' + Math.min(1, a0) + ')');
      grd.addColorStop(0.38, 'rgba(' + cr + ',' + cg + ',' + cb + ',' + a1 + ')');
      grd.addColorStop(0.68, 'rgba(' + cr + ',' + cg + ',' + cb + ',' + a2 + ')');
      grd.addColorStop(1,    'rgba(' + cr + ',' + cg + ',' + cb + ',0)');
      ctx.fillStyle = grd;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  ctx.globalCompositeOperation = 'source-over';
  ctx.restore();

  // ── Dark dust lanes (Great Rift, Coal Sack) ────────────────────────────────
  if (typeof SG_MW_DUST === 'undefined') return;
  var dd = SG_MW_DUST;
  ctx.save();
  for (var i = 0; i < dd.length; i += 4) {
    var p = sgProject(dd[i], dd[i + 1]);
    if (!p.visible) continue;
    if (p.x < -80 || p.x > W + 80 || p.y < -80 || p.y > H + 80) continue;
    var r = dd[i + 2] * pxPerDeg;
    if (r < 2) continue;
    var op = dd[i + 3];
    var grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
    grd.addColorStop(0,    'rgba(1,1,16,' + (op * 0.90) + ')');
    grd.addColorStop(0.40, 'rgba(1,1,15,' + (op * 0.60) + ')');
    grd.addColorStop(0.70, 'rgba(1,1,14,' + (op * 0.25) + ')');
    grd.addColorStop(1,    'rgba(1,1,12,0)');
    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}"""

html = html[:mwf_start] + NEW_FUNC + html[mwf_end:]
print(f"  sgDrawMilkyWay replaced ({len(NEW_FUNC):,} chars)", file=sys.stderr)

# ── Write ─────────────────────────────────────────────────────────────────────
open(HTML, "w", encoding="utf-8").write(html)
print(f"\nDone — index.html {len(html):,} chars", file=sys.stderr)
