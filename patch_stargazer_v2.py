"""
patch_stargazer_v2.py
1. Replaces the SG_STAR_DATA / SG_STAR_NAMES / SG_CONSTELLATIONS block in index.html
   with the new real-data version from star_data_v2.js
2. Adds computeLST() for real-time sky orientation
3. Narrows FOV from 110 degrees to 80 degrees
4. Adds sidereal tracking so the sky rotates with Earth in real time
"""

import re, sys

HTML  = r"C:\Users\Owner\anya.github.io\index.html"
DATA  = r"C:\Users\Owner\anya.github.io\star_data_v2.js"

html = open(HTML,  encoding="utf-8").read()
data = open(DATA,  encoding="utf-8").read().strip()

# ── 1. Replace star data block ───────────────────────────────────────────────
# The block starts with "var SG_STAR_DATA=[" and ends after "SG_CONSTELLATIONS" closing "];"
start_marker = "var SG_STAR_DATA=["
end_marker   = "var SG_CONSTELLATIONS=["

si = html.find(start_marker)
ei = html.find(end_marker)
if si == -1 or ei == -1:
    print("ERROR: Could not find SG_STAR_DATA or SG_CONSTELLATIONS in index.html", file=sys.stderr)
    sys.exit(1)

# Find the closing "];" after SG_CONSTELLATIONS
cons_start = ei
cons_end   = html.find("];", cons_start) + 2   # include "];"

html = html[:si] + data + "\n" + html[cons_end:]
print(f"  Star data block replaced ({len(data)} chars)", file=sys.stderr)

# ── 2. FOV: 110° -> 80° ──────────────────────────────────────────────────────
html = html.replace(
    "// 110° vertical FOV\n  sgScale = (H / 2) / Math.tan(55 * Math.PI / 180);",
    "// 80° vertical FOV — less gnomonic distortion at edges\n  sgScale = (H / 2) / Math.tan(40 * Math.PI / 180);"
)
print("  FOV updated 110° → 80°", file=sys.stderr)

# ── 3. Add computeLST() + tracking vars after the sgClickCooldown line ───────
LST_BLOCK = """
// ── Local Sidereal Time + real-time sky tracking ────────────────────────────
// computeLST() returns the RA (degrees) currently on the meridian.
// IAU formula for Greenwich Mean Sidereal Time, corrected for observer longitude.
function computeLST() {
  var JD   = Date.now() / 86400000.0 + 2440587.5;  // Julian Date
  var T    = (JD - 2451545.0) / 36525.0;           // Julian centuries from J2000
  var GMST = 280.46061837
             + 360.98564736629 * (JD - 2451545.0)
             + T * T * 0.000387933
             - T * T * T / 38710000.0;
  return ((GMST + LNG + 360000) % 360 + 360) % 360;
}
// Earth sidereal rotation: 360° / 86164.1 s
var SG_SIDEREAL_RATE = 360 / 86164.1; // degrees per second
var sgTrackRA   = 180;   // RA anchor set on init / drag-end
var sgTrackTime = 0;     // timestamp of anchor"""

COOLDOWN_LINE = "var sgClickCooldown = false;"
if COOLDOWN_LINE in html:
    html = html.replace(COOLDOWN_LINE, COOLDOWN_LINE + "\n" + LST_BLOCK)
    print("  computeLST() + tracking vars injected", file=sys.stderr)
else:
    print("  WARNING: could not find cooldown line, LST block NOT injected", file=sys.stderr)

# ── 4. Update initStargazer() to start from LST ──────────────────────────────
OLD_INIT = "  sgCanvas = document.getElementById('stargazer-canvas');\n  if (!sgCanvas) return;\n  sgCtx = sgCanvas.getContext('2d');\n  resizeSG();\n  if (!sgStars.length) generateSGStars();"
NEW_INIT = """  sgCanvas = document.getElementById('stargazer-canvas');
  if (!sgCanvas) return;
  sgCtx = sgCanvas.getContext('2d');
  resizeSG();
  if (!sgStars.length) generateSGStars();
  // Initialise view to current sky (LST = meridian RA, observer latitude)
  sgTrackRA   = computeLST();
  sgTrackTime = Date.now();
  sgViewRA    = sgTrackRA;
  sgViewDec   = LAT;"""

if OLD_INIT in html:
    html = html.replace(OLD_INIT, NEW_INIT)
    print("  initStargazer() updated with LST init", file=sys.stderr)
else:
    print("  WARNING: initStargazer() pattern not matched", file=sys.stderr)

# ── 5. Update drag end handlers to re-anchor the tracker ─────────────────────
# mouseup: after "sgDrag = false;"  inside the sgCanvas.addEventListener block
OLD_MOUSEUP = """    sgDrag = false;
  });

  sgCanvas.addEventListener('touchstart',"""
NEW_MOUSEUP = """    sgDrag = false;
    sgTrackRA = sgViewRA; sgTrackTime = Date.now(); // re-anchor sidereal tracker
  });

  sgCanvas.addEventListener('touchstart',"""
if OLD_MOUSEUP in html:
    html = html.replace(OLD_MOUSEUP, NEW_MOUSEUP)
    print("  mouseup re-anchor injected", file=sys.stderr)
else:
    print("  WARNING: mouseup pattern not matched", file=sys.stderr)

OLD_TOUCHEND = """    sgDrag = false;
  });
}

function resizeSG()"""
NEW_TOUCHEND = """    sgDrag = false;
    sgTrackRA = sgViewRA; sgTrackTime = Date.now(); // re-anchor sidereal tracker
  });
}

function resizeSG()"""
if OLD_TOUCHEND in html:
    html = html.replace(OLD_TOUCHEND, NEW_TOUCHEND)
    print("  touchend re-anchor injected", file=sys.stderr)
else:
    print("  WARNING: touchend pattern not matched", file=sys.stderr)

# ── 6. Update sgLoop to advance RA with Earth's rotation ─────────────────────
OLD_CACHE = """  // Build projection cache
  sgProjectCache = [];
  for (var i = 0; i < sgStars.length; i++) {
    var s = sgStars[i];
    sgProjectCache[i] = sgProject(s.ra, s.dec);
  }"""
NEW_CACHE = """  // Advance view RA with Earth's sidereal rotation (sky drifts westward in real time)
  if (!sgDrag) {
    sgViewRA = ((sgTrackRA + (Date.now() - sgTrackTime) / 1000 * SG_SIDEREAL_RATE) % 360 + 360) % 360;
  }

  // Build projection cache
  sgProjectCache = [];
  for (var i = 0; i < sgStars.length; i++) {
    var s = sgStars[i];
    sgProjectCache[i] = sgProject(s.ra, s.dec);
  }"""
if OLD_CACHE in html:
    html = html.replace(OLD_CACHE, NEW_CACHE)
    print("  sgLoop sidereal advance injected", file=sys.stderr)
else:
    print("  WARNING: sgLoop projection cache pattern not matched", file=sys.stderr)

# ── 7. Update sgReset() to snap back to current LST ─────────────────────────
OLD_RESET = "  sgViewRA = 180; sgViewDec = 25;"
NEW_RESET = """  sgTrackRA   = computeLST();
  sgTrackTime = Date.now();
  sgViewRA    = sgTrackRA;
  sgViewDec   = LAT;"""
if OLD_RESET in html:
    html = html.replace(OLD_RESET, NEW_RESET)
    print("  sgReset() updated to current LST", file=sys.stderr)
else:
    print("  WARNING: sgReset pattern not matched", file=sys.stderr)

# ── Write ─────────────────────────────────────────────────────────────────────
open(HTML, "w", encoding="utf-8").write(html)
print(f"\nindex.html updated — {len(html)} chars.", file=sys.stderr)
