"""
patch_dso.py — embeds DSO/MW data and rendering code into index.html
1. Inserts SG_DSO_NAMES, SG_DSO_DATA, SG_MW_DATA after SG_STAR_HIP block
2. Injects sgDrawMilkyWay(), individual DSO draw functions, sgDrawDSOs()
   and DSO hit detection into the Stargazer JS
3. Calls sgDrawMilkyWay() in sgLoop (after background, before cache build)
4. Calls sgDrawDSOs() in sgLoop (after projection cache, before constellation lines)
5. Updates identifiedcount label to include DSOs
"""
import sys, re

HTML    = r"C:\Users\Owner\anya.github.io\index.html"
DSO_JS  = r"C:\Users\Owner\anya.github.io\dso_data.js"

html = open(HTML, encoding="utf-8").read()
dso  = open(DSO_JS, encoding="utf-8").read().strip()

# ── 1. Inject DSO data after SG_STAR_HIP block ───────────────────────────────
HIP_END = "};\n\nvar SG_CONSTELLATIONS=["
if HIP_END in html:
    html = html.replace(HIP_END, "};\n\n" + dso + "\n\nvar SG_CONSTELLATIONS=[", 1)
    print("  DSO data injected after SG_STAR_HIP", file=sys.stderr)
else:
    # fallback: look for SG_CONSTELLATIONS
    CON_MARK = "var SG_CONSTELLATIONS=["
    if CON_MARK in html:
        html = html.replace(CON_MARK, dso + "\n\n" + CON_MARK, 1)
        print("  DSO data injected before SG_CONSTELLATIONS (fallback)", file=sys.stderr)
    else:
        sys.exit("ERROR: cannot locate injection point for DSO data")

# ── 2. Inject DSO rendering functions before sgDrawConstellations ─────────────
DSO_FUNCTIONS = r"""
// ── Deep-Sky Object rendering ─────────────────────────────────────────────────
var sgDSOCache = [];

function sgBVtoAlpha(mag, base, scale) {
  return Math.max(0.06, Math.min(1, base - (mag - 4) * scale));
}

// Galaxy: warm elliptical gradient, oriented by position angle
function sgDrawGalaxy(ctx, x, y, a, b, pa, mag) {
  ctx.save();
  ctx.translate(x, y);
  // PA is degrees from N through E; in our projection N=-y, E=+x
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, Math.max(0.15, b / a));
  var alpha = sgBVtoAlpha(mag, 0.92, 0.10);
  var grd = ctx.createRadialGradient(0, 0, 0, 0, 0, a);
  grd.addColorStop(0,    'rgba(255,242,205,' + Math.min(1, alpha * 1.25) + ')');
  grd.addColorStop(0.10, 'rgba(255,228,175,' + (alpha * 0.92) + ')');
  grd.addColorStop(0.28, 'rgba(240,210,150,' + (alpha * 0.58) + ')');
  grd.addColorStop(0.52, 'rgba(215,188,130,' + (alpha * 0.24) + ')');
  grd.addColorStop(0.75, 'rgba(185,162,110,' + (alpha * 0.08) + ')');
  grd.addColorStop(1,    'rgba(160,140, 95,0)');
  ctx.beginPath();
  ctx.arc(0, 0, a, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  ctx.restore();
}

// Globular cluster: dense bright core with seeded dot halo
function sgDrawGlobular(ctx, x, y, r, mag, seed) {
  var alpha = sgBVtoAlpha(mag, 0.95, 0.09);
  var grd = ctx.createRadialGradient(x, y, 0, x, y, r);
  grd.addColorStop(0,    'rgba(255,252,225,' + Math.min(1, alpha * 1.15) + ')');
  grd.addColorStop(0.07, 'rgba(255,248,210,' + (alpha * 0.90) + ')');
  grd.addColorStop(0.22, 'rgba(245,235,185,' + (alpha * 0.60) + ')');
  grd.addColorStop(0.45, 'rgba(225,215,165,' + (alpha * 0.30) + ')');
  grd.addColorStop(0.70, 'rgba(200,190,140,' + (alpha * 0.11) + ')');
  grd.addColorStop(1,    'rgba(175,165,120,0)');
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  // Crosshair
  var hl = r * 0.32;
  ctx.strokeStyle = 'rgba(255,252,220,' + (alpha * 0.45) + ')';
  ctx.lineWidth = 0.7;
  ctx.beginPath();
  ctx.moveTo(x - hl, y); ctx.lineTo(x + hl, y);
  ctx.moveTo(x, y - hl); ctx.lineTo(x, y + hl);
  ctx.stroke();
  // Outer ring
  ctx.strokeStyle = 'rgba(230,225,190,' + (alpha * 0.28) + ')';
  ctx.lineWidth = 0.5;
  ctx.beginPath(); ctx.arc(x, y, r * 0.85, 0, Math.PI * 2); ctx.stroke();
}

// Emission nebula: pinkish-red H-alpha glow
function sgDrawEmissionNebula(ctx, x, y, a, b, pa, mag) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, Math.max(0.2, b / a));
  var alpha = sgBVtoAlpha(mag, 0.88, 0.09);
  var grd = ctx.createRadialGradient(0, 0, 0, 0, 0, a);
  grd.addColorStop(0,    'rgba(255,105,130,' + Math.min(1, alpha * 1.10) + ')');
  grd.addColorStop(0.20, 'rgba(235, 75,110,' + (alpha * 0.72) + ')');
  grd.addColorStop(0.45, 'rgba(205, 60, 95,' + (alpha * 0.38) + ')');
  grd.addColorStop(0.70, 'rgba(170, 45, 80,' + (alpha * 0.14) + ')');
  grd.addColorStop(1,    'rgba(140, 30, 65,0)');
  ctx.beginPath();
  ctx.arc(0, 0, a, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  ctx.restore();
}

// Planetary nebula: blue-green ring with central glow
function sgDrawPlanetaryNebula(ctx, x, y, r, pa, mag) {
  r = Math.max(r, 4);
  var alpha = sgBVtoAlpha(mag, 0.95, 0.07);
  // Inner disc glow
  var grd = ctx.createRadialGradient(x, y, 0, x, y, r);
  grd.addColorStop(0,    'rgba(100,215,235,' + (alpha * 0.55) + ')');
  grd.addColorStop(0.35, 'rgba( 70,190,220,' + (alpha * 0.35) + ')');
  grd.addColorStop(0.68, 'rgba( 50,165,205,' + (alpha * 0.18) + ')');
  grd.addColorStop(1,    'rgba( 30,140,185,0)');
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  // Bright ring outline
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, 0.72);
  ctx.strokeStyle = 'rgba(90,210,230,' + (alpha * 0.85) + ')';
  ctx.lineWidth = Math.max(0.9, r * 0.32);
  ctx.beginPath();
  ctx.arc(0, 0, r * 0.78, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// Supernova remnant: filamentary reddish ring
function sgDrawSNR(ctx, x, y, a, b, pa, mag) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, Math.max(0.5, b / a));
  a = Math.max(a, 5);
  var alpha = sgBVtoAlpha(mag, 0.90, 0.07);
  var grd = ctx.createRadialGradient(0, 0, a * 0.35, 0, 0, a);
  grd.addColorStop(0,    'rgba(210,140, 80,' + (alpha * 0.12) + ')');
  grd.addColorStop(0.55, 'rgba(190,100, 55,' + (alpha * 0.22) + ')');
  grd.addColorStop(0.82, 'rgba(210,120, 60,' + (alpha * 0.55) + ')');
  grd.addColorStop(1,    'rgba(170, 80, 40,0)');
  ctx.beginPath();
  ctx.arc(0, 0, a, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  ctx.strokeStyle = 'rgba(205,125, 65,' + (alpha * 0.65) + ')';
  ctx.lineWidth = Math.max(0.8, a * 0.14);
  ctx.beginPath();
  ctx.arc(0, 0, a * 0.82, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// Reflection nebula: blue haze
function sgDrawReflectionNebula(ctx, x, y, a, b, pa, mag) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, Math.max(0.2, b / a));
  var alpha = sgBVtoAlpha(mag, 0.82, 0.09);
  var grd = ctx.createRadialGradient(0, 0, 0, 0, 0, a);
  grd.addColorStop(0,    'rgba(130,180,255,' + Math.min(1, alpha * 1.1) + ')');
  grd.addColorStop(0.30, 'rgba( 95,155,245,' + (alpha * 0.65) + ')');
  grd.addColorStop(0.58, 'rgba( 70,130,230,' + (alpha * 0.28) + ')');
  grd.addColorStop(1,    'rgba( 50,110,215,0)');
  ctx.beginPath();
  ctx.arc(0, 0, a, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  ctx.restore();
}

// Mixed emission+reflection (Trifid-type): red centre, blue halo
function sgDrawMixedNebula(ctx, x, y, a, b, pa, mag) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((pa - 90) * Math.PI / 180);
  ctx.scale(1, Math.max(0.2, b / a));
  var alpha = sgBVtoAlpha(mag, 0.88, 0.09);
  var grd = ctx.createRadialGradient(0, 0, 0, 0, 0, a);
  grd.addColorStop(0,    'rgba(240,100,120,' + Math.min(1, alpha * 1.1) + ')');
  grd.addColorStop(0.22, 'rgba(210, 80,105,' + (alpha * 0.70) + ')');
  grd.addColorStop(0.45, 'rgba(160, 80,160,' + (alpha * 0.40) + ')');
  grd.addColorStop(0.68, 'rgba(100,120,220,' + (alpha * 0.20) + ')');
  grd.addColorStop(1,    'rgba( 70, 90,200,0)');
  ctx.beginPath();
  ctx.arc(0, 0, a, 0, Math.PI * 2);
  ctx.fillStyle = grd;
  ctx.fill();
  ctx.restore();
}

// Open cluster: dashed circle + seeded stars
function sgDrawOpenCluster(ctx, x, y, r, mag, seed) {
  r = Math.max(r, 5);
  var alpha = sgBVtoAlpha(mag, 0.85, 0.07);
  ctx.save();
  ctx.strokeStyle = 'rgba(185,205,255,' + (alpha * 0.32) + ')';
  ctx.lineWidth = 0.7;
  ctx.setLineDash([2.5, 3.5]);
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
  ctx.setLineDash([]);
  // Seeded scatter of star dots
  var s = (seed * 1664525 + 1013904223) >>> 0;
  function rnd() { s = (s * 1664525 + 1013904223) >>> 0; return (s >>> 0) / 4294967296; }
  var n = Math.floor(10 + rnd() * 18);
  ctx.fillStyle = 'rgba(205,220,255,' + (alpha * 0.88) + ')';
  for (var k = 0; k < n; k++) {
    var ang = rnd() * Math.PI * 2;
    var dst = Math.pow(rnd(), 0.55) * r * 0.88;
    var sr  = 0.6 + rnd() * 1.6;
    ctx.beginPath();
    ctx.arc(x + Math.cos(ang) * dst, y + Math.sin(ang) * dst, sr, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

// ── Main DSO draw pass ────────────────────────────────────────────────────────
function sgDrawDSOs(ctx, W, H) {
  if (typeof SG_DSO_DATA === 'undefined') return;
  var d = SG_DSO_DATA;
  var pxPerArcmin = sgScale * Math.PI / (180 * 60);
  for (var i = 0; i < d.length; i += 8) {
    var p = sgDSOCache[i / 8];
    if (!p || !p.visible) continue;
    if (p.x < -120 || p.x > W + 120 || p.y < -120 || p.y > H + 120) continue;
    var mag  = d[i + 2];
    var majA = d[i + 3], minA = d[i + 4], pa = d[i + 5], type = d[i + 6];
    var a    = Math.max(majA * pxPerArcmin / 2, 3);
    var b    = Math.max(minA * pxPerArcmin / 2, 2);
    var nidx = d[i + 7];
    ctx.globalAlpha = 1;
    switch (type) {
      case 0: sgDrawGalaxy(ctx, p.x, p.y, a, b, pa, mag);                     break;
      case 1: sgDrawOpenCluster(ctx, p.x, p.y, a, mag, nidx * 7919);          break;
      case 2: sgDrawGlobular(ctx, p.x, p.y, a, mag, nidx * 6271);             break;
      case 3: sgDrawEmissionNebula(ctx, p.x, p.y, a, b, pa, mag);             break;
      case 4: sgDrawPlanetaryNebula(ctx, p.x, p.y, a, pa, mag);               break;
      case 5: sgDrawSNR(ctx, p.x, p.y, a, b, pa, mag);                        break;
      case 6: sgDrawReflectionNebula(ctx, p.x, p.y, a, b, pa, mag);           break;
      case 7: sgDrawMixedNebula(ctx, p.x, p.y, a, b, pa, mag);                break;
    }
  }
  ctx.globalAlpha = 1;
}

// ── DSO hit detection ─────────────────────────────────────────────────────────
function sgGetDSOAt(cx, cy) {
  if (typeof SG_DSO_DATA === 'undefined' || !sgDSOCache.length) return null;
  var d = SG_DSO_DATA;
  var pxPerArcmin = sgScale * Math.PI / (180 * 60);
  var best = null, bestDist = Infinity;
  for (var i = 0; i < d.length; i += 8) {
    var p = sgDSOCache[i / 8];
    if (!p || !p.visible) continue;
    var a = Math.max(d[i + 3] * pxPerArcmin / 2, 8);
    var dx = cx - p.x, dy = cy - p.y;
    var dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < a * 1.1 && dist < bestDist) { bestDist = dist; best = i / 8; }
  }
  return best !== null ? best : null;
}

// ── Milky Way band ────────────────────────────────────────────────────────────
function sgDrawMilkyWay(ctx, W, H) {
  if (typeof SG_MW_DATA === 'undefined') return;
  var d = SG_MW_DATA;
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for (var i = 0; i < d.length; i += 4) {
    var p = sgProject(d[i], d[i + 1]);
    if (!p.visible) continue;
    if (p.x < -W * 0.3 || p.x > W * 1.3 || p.y < -H * 0.3 || p.y > H * 1.3) continue;
    var hw  = d[i + 2]; // half-width in degrees
    var bri = d[i + 3];
    var r   = hw * sgScale * Math.PI / 180;
    if (r < 4) continue;
    var grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
    var a0  = bri * 0.038, a1 = bri * 0.022, a2 = bri * 0.008;
    grd.addColorStop(0,   'rgba(210,218,240,' + a0  + ')');
    grd.addColorStop(0.38,'rgba(195,205,230,' + a1  + ')');
    grd.addColorStop(0.65,'rgba(175,185,220,' + a2  + ')');
    grd.addColorStop(1,   'rgba(155,165,210,0)');
    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalCompositeOperation = 'source-over';
  ctx.restore();
}
"""

TARGET_BEFORE_CONSTELLATIONS = "function sgDrawConstellations("
if TARGET_BEFORE_CONSTELLATIONS in html:
    html = html.replace(TARGET_BEFORE_CONSTELLATIONS,
                        DSO_FUNCTIONS + "\n" + TARGET_BEFORE_CONSTELLATIONS, 1)
    print("  DSO rendering functions injected", file=sys.stderr)
else:
    sys.exit("ERROR: cannot find sgDrawConstellations to inject before")

# ── 3. Add MW draw call in sgLoop — after background, before cache ─────────────
# Target: right after the purple gradient fillRect, before sgFrame++
OLD_FRAME = "  sgFrame++;\n"
NEW_FRAME = "  sgFrame++;\n  sgDrawMilkyWay(ctx, W, H);\n"
if OLD_FRAME in html:
    html = html.replace(OLD_FRAME, NEW_FRAME, 1)
    print("  sgDrawMilkyWay() call injected in sgLoop", file=sys.stderr)
else:
    print("  WARNING: sgFrame++ not found, MW call not injected", file=sys.stderr)

# ── 4. Build DSO cache + draw DSOs after star projection cache is built ───────
OLD_CALL_CONS = "  // Constellation lines + labels\n  sgDrawConstellations("
NEW_CALL_CONS = (
    "  // Build DSO projection cache\n"
    "  sgDSOCache = [];\n"
    "  if (typeof SG_DSO_DATA !== 'undefined') {\n"
    "    var _dD = SG_DSO_DATA;\n"
    "    for (var _di = 0; _di < _dD.length; _di += 8) {\n"
    "      sgDSOCache.push(sgProject(_dD[_di], _dD[_di + 1]));\n"
    "    }\n"
    "  }\n"
    "  sgDrawDSOs(ctx, W, H);\n\n"
    "  // Constellation lines + labels\n"
    "  sgDrawConstellations("
)
if OLD_CALL_CONS in html:
    html = html.replace(OLD_CALL_CONS, NEW_CALL_CONS, 1)
    print("  sgDrawDSOs() call + DSO cache build injected in sgLoop", file=sys.stderr)
else:
    print("  WARNING: constellation call pattern not found", file=sys.stderr)

# ── 5. Patch sgClickStar to also test DSO hits ────────────────────────────────
OLD_CLICK_START = (
    "function sgClickStar(cx, cy) {\n"
    "  if (sgClickCooldown) return;\n"
    "  var s = sgGetStarAt(cx, cy);\n"
    "  if (!s) return;"
)
NEW_CLICK_START = (
    "function sgClickStar(cx, cy) {\n"
    "  if (sgClickCooldown) return;\n"
    "  // Check DSOs first (they are larger targets)\n"
    "  var dsoIdx = sgGetDSOAt(cx, cy);\n"
    "  if (dsoIdx !== null && typeof SG_DSO_DATA !== 'undefined') {\n"
    "    sgClickCooldown = true;\n"
    "    setTimeout(function(){ sgClickCooldown = false; }, 400);\n"
    "    var dName  = (SG_DSO_NAMES && SG_DSO_NAMES[dsoIdx]) || 'DSO';\n"
    "    var dD     = SG_DSO_DATA;\n"
    "    var dMag   = dD[dsoIdx * 8 + 2];\n"
    "    var dMajA  = dD[dsoIdx * 8 + 3];\n"
    "    var dType  = dD[dsoIdx * 8 + 6];\n"
    "    var typeStr = ['Galaxy','Open Cluster','Globular Cluster',\n"
    "      'Emission Nebula','Planetary Nebula','Supernova Remnant',\n"
    "      'Reflection Nebula','Emission/Reflection Nebula'][dType] || 'Deep-Sky Object';\n"
    "    var detail = typeStr\n"
    "      + '\\u2002\\u00b7\\u2002Mag\\u00a0' + dMag.toFixed(1)\n"
    "      + '\\u2002\\u00b7\\u2002' + dMajA.toFixed(1) + '\\u2019 span';\n"
    "    sgShowStarName(dName, detail);\n"
    "    sgNamed['dso_' + dsoIdx] = dName;\n"
    "    var nc = document.getElementById('sg-named-count');\n"
    "    if (nc) nc.innerText = Object.keys(sgNamed).length;\n"
    "    return;\n"
    "  }\n"
    "  var s = sgGetStarAt(cx, cy);\n"
    "  if (!s) return;"
)
if OLD_CLICK_START in html:
    html = html.replace(OLD_CLICK_START, NEW_CLICK_START, 1)
    print("  sgClickStar patched for DSO hit detection", file=sys.stderr)
else:
    print("  WARNING: sgClickStar pattern not matched", file=sys.stderr)

# ── Write ─────────────────────────────────────────────────────────────────────
open(HTML, "w", encoding="utf-8").write(html)
print(f"\nDone — index.html {len(html):,} chars", file=sys.stderr)
