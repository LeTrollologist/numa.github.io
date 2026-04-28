"""
patch_stargazer_v3.py
1. Replaces entire star data block (SG_STAR_DATA…SG_CONSTELLATIONS) with v2 output
2. Defines sgShowStarName (was called but never defined)
3. Rewrites sgClickStar to show real catalogue info — no fictional name pool
4. Removes sgNamePool
5. Cleans up UI labels
"""
import re, sys

HTML = r"C:\Users\Owner\anya.github.io\index.html"
DATA = r"C:\Users\Owner\anya.github.io\star_data_v2.js"

html = open(HTML, encoding="utf-8").read()
data = open(DATA, encoding="utf-8").read().strip()

# ── 1. Replace star data block ────────────────────────────────────────────────
# Block spans from first "var SG_STAR_DATA=[" to the closing "];" of SG_CONSTELLATIONS
start_marker = "var SG_STAR_DATA=["
end_marker   = "var SG_CONSTELLATIONS=["
si = html.find(start_marker)
ei = html.find(end_marker)
if si == -1 or ei == -1:
    sys.exit("ERROR: cannot locate SG_STAR_DATA or SG_CONSTELLATIONS")

cons_end = html.find("];\n", ei) + 3     # skip past "];\n"
html = html[:si] + data + "\n" + html[cons_end:]
print(f"  Star data block replaced ({len(data):,} chars)", file=sys.stderr)

# ── 2. Remove sgNamePool ──────────────────────────────────────────────────────
# Find and remove the var sgNamePool = [...]; declaration
pool_re = re.compile(r"var sgNamePool\s*=\s*\[.*?\];\n", re.DOTALL)
if pool_re.search(html):
    html = pool_re.sub("", html, count=1)
    print("  sgNamePool removed", file=sys.stderr)
else:
    print("  WARNING: sgNamePool not found", file=sys.stderr)

# ── 3. Define sgShowStarName + rewrite sgClickStar ───────────────────────────
OLD_CLICK = '''// ── Click — reveal real name or assign pool name ────────────────────────────
function sgClickStar(cx, cy) {
  if (sgClickCooldown) return;
  var s = sgGetStarAt(cx, cy);
  if (!s) return;
  sgClickCooldown = true;
  setTimeout(function(){ sgClickCooldown = false; }, 400);
  var key = s.idx;
  if (sgNamed[key]) {
    sgShowStarName(sgNamed[key]);
  } else {
    var name;
    if (s.name) {
      name = s.name;
    } else {
      var usedNames = Object.values(sgNamed);
      var available = sgNamePool.filter(function(n){ return usedNames.indexOf(n) === -1; });
      if (!available.length) available = sgNamePool;
      name = available[Math.floor(Math.random() * available.length)];
    }
    sgNamed[key] = name;
    sgShowStarName(name);
    var nc = document.getElementById('sg-named-count');
    if (nc) nc.innerText = Object.keys(sgNamed).length;
  }
}'''

NEW_CLICK = '''// ── Star name card (auto-hides after 5 s) ────────────────────────────────────
var sgNameTimer;
function sgShowStarName(headline, detail) {
  var el = document.getElementById('sg-star-name');
  if (!el) return;
  el.innerHTML = '<div style="font-size:1.05em;font-weight:600;letter-spacing:.02em">'
    + headline + '</div>'
    + (detail ? '<div style="font-size:.76em;opacity:.68;margin-top:3px;letter-spacing:.03em">'
      + detail + '</div>' : '');
  el.classList.add('show');
  clearTimeout(sgNameTimer);
  sgNameTimer = setTimeout(function(){ el.classList.remove('show'); }, 5000);
}

// ── Click — identify star from real catalogue data ───────────────────────────
function sgClickStar(cx, cy) {
  if (sgClickCooldown) return;
  var s = sgGetStarAt(cx, cy);
  if (!s) return;
  sgClickCooldown = true;
  setTimeout(function(){ sgClickCooldown = false; }, 400);

  // Resolve identification: proper name > Bayer/Flamsteed > HIP number
  var proper = (typeof SG_STAR_NAMES !== 'undefined' && SG_STAR_NAMES[s.idx]) || '';
  var bayer  = (typeof SG_STAR_BAYER !== 'undefined' && SG_STAR_BAYER[s.idx]) || '';
  var infoRaw= (typeof SG_STAR_INFO  !== 'undefined' && SG_STAR_INFO[s.idx])  || '';
  var hip    = (typeof SG_STAR_HIP   !== 'undefined' && SG_STAR_HIP[s.idx])   || s.hip || 0;

  var headline;
  if (proper) {
    headline = proper + (bayer ? ' \u2014 ' + bayer : '');
  } else if (bayer) {
    headline = bayer;
  } else {
    headline = hip ? 'HIP\u00a0' + hip : 'Unknown star';
  }

  // Detail line: magnitude · spectral type · distance
  var parts   = infoRaw.split('|');
  var spect   = parts[0] || '';
  var distLy  = parts[1] || '';
  var detail  = 'Mag\u00a0' + s.vmag.toFixed(2);
  if (spect)  detail += '\u2002\u00b7\u2002' + spect;
  if (distLy) detail += '\u2002\u00b7\u2002' + distLy + '\u00a0ly';

  sgShowStarName(headline, detail);
  sgNamed[s.idx] = headline;  // mark as seen (for glow highlight in render loop)

  var nc = document.getElementById('sg-named-count');
  if (nc) nc.innerText = Object.keys(sgNamed).length;
}'''

if OLD_CLICK in html:
    html = html.replace(OLD_CLICK, NEW_CLICK)
    print("  sgClickStar + sgShowStarName injected", file=sys.stderr)
else:
    print("  WARNING: sgClickStar pattern not matched — trying fuzzy replace",
          file=sys.stderr)
    # Fuzzy: just prepend the new function before the old one
    fallback_marker = "function sgClickStar"
    if fallback_marker in html:
        html = html.replace(fallback_marker,
                            NEW_CLICK + "\n\n// (legacy stub)\nfunction __old_sgClickStar",
                            1)

# ── 4. Update sgShuffle to use random RA but keep sidereal anchor ─────────────
OLD_SHUFFLE = """function sgShuffle() {
  sgNamed = {};
  var nc = document.getElementById('sg-named-count');
  if (nc) nc.innerText = '0';
  sgViewRA  = Math.random() * 360;
  sgViewDec = (Math.random() - 0.5) * 80;
}"""
NEW_SHUFFLE = """function sgShuffle() {
  sgNamed = {};
  var nc = document.getElementById('sg-named-count');
  if (nc) nc.innerText = '0';
  sgTrackRA   = Math.random() * 360;
  sgTrackTime = Date.now();
  sgViewRA    = sgTrackRA;
  sgViewDec   = (Math.random() - 0.5) * 60;
}"""
if OLD_SHUFFLE in html:
    html = html.replace(OLD_SHUFFLE, NEW_SHUFFLE)
    print("  sgShuffle updated", file=sys.stderr)
else:
    print("  WARNING: sgShuffle pattern not matched", file=sys.stderr)

# ── 5. Update Stargazer overlay UI text ───────────────────────────────────────
OLD_INFO = """    <div id="sg-info">
      <strong>🌌 Stargazer</strong><br>
      Click a star to name it<br>
      Drag to rotate the sky<br>
      <span id="sg-named-count">0</span> stars named
    </div>"""
NEW_INFO = """    <div id="sg-info">
      <strong>🌌 Stargazer</strong><br>
      Click a star to identify it<br>
      Drag to explore the sky<br>
      <span id="sg-named-count">0</span> stars identified
    </div>"""
if OLD_INFO in html:
    html = html.replace(OLD_INFO, NEW_INFO)
    print("  Overlay info text updated", file=sys.stderr)
else:
    print("  WARNING: overlay info text not matched", file=sys.stderr)

OLD_TAGLINE = "Every star has a name. Click one to find it."
NEW_TAGLINE = "1,638 real stars. Click one to identify it."
if OLD_TAGLINE in html:
    html = html.replace(OLD_TAGLINE, NEW_TAGLINE)
    print("  Tagline updated", file=sys.stderr)
else:
    print("  WARNING: tagline not matched", file=sys.stderr)

# ── Write ──────────────────────────────────────────────────────────────────────
open(HTML, "w", encoding="utf-8").write(html)
print(f"\nDone — index.html {len(html):,} chars", file=sys.stderr)
