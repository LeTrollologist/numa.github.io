#!/usr/bin/env python3
# patch_stargazer.py — Embeds real star data + rewrites Stargazer JS in index.html
import re, sys

# ── 1. Read files ────────────────────────────────────────────────────────────
with open('index.html', encoding='utf-8') as f:
    html = f.read()

with open('star_data_utf8.js', encoding='utf-8') as f:
    star_data = f.read()

# ── 2. Build the replacement Stargazer JS block ──────────────────────────────
NEW_SG = r"""// ══════════════════════════════════════════════════════════
// STARGAZER — Real astronomical data (Yale BSC + IAU constellations)
// ══════════════════════════════════════════════════════════

// ── Projection helpers ──────────────────────────────────────────────────────
function sgInitProjection() {
  if (!sgCanvas) return;
  var H = sgCanvas.height;
  // 110° vertical FOV
  sgScale = (H / 2) / Math.tan(55 * Math.PI / 180);
}

function sgProject(ra_deg, dec_deg) {
  var W = sgCanvas.width, H = sgCanvas.height;
  var ra0  = sgViewRA  * Math.PI / 180;
  var dec0 = sgViewDec * Math.PI / 180;
  var ra   = ra_deg    * Math.PI / 180;
  var dec  = dec_deg   * Math.PI / 180;
  var dra  = ra - ra0;
  var cos_c = Math.sin(dec0) * Math.sin(dec) + Math.cos(dec0) * Math.cos(dec) * Math.cos(dra);
  if (cos_c < 0.001) return {x: 0, y: 0, visible: false};
  var x_tan = Math.cos(dec) * Math.sin(dra) / cos_c;
  var y_tan = (Math.cos(dec0) * Math.sin(dec) - Math.sin(dec0) * Math.cos(dec) * Math.cos(dra)) / cos_c;
  return {
    x: W / 2 + sgScale * x_tan,
    y: H / 2 - sgScale * y_tan,
    visible: true
  };
}

// ── B-V index → RGB colour ──────────────────────────────────────────────────
function sgBVtoColor(bv) {
  var stops = [
    [-0.4, 155, 176, 255],
    [-0.1, 180, 200, 255],
    [ 0.0, 255, 255, 255],
    [ 0.4, 255, 252, 230],
    [ 0.8, 255, 244, 200],
    [ 1.5, 255, 210, 130],
    [ 2.0, 255, 160,  80]
  ];
  if (bv <= stops[0][0]) return 'rgb('+stops[0][1]+','+stops[0][2]+','+stops[0][3]+')';
  if (bv >= stops[stops.length-1][0]) {
    var s = stops[stops.length-1];
    return 'rgb('+s[1]+','+s[2]+','+s[3]+')';
  }
  for (var i = 1; i < stops.length; i++) {
    if (bv <= stops[i][0]) {
      var t = (bv - stops[i-1][0]) / (stops[i][0] - stops[i-1][0]);
      var r = Math.round(stops[i-1][1] + t * (stops[i][1] - stops[i-1][1]));
      var g = Math.round(stops[i-1][2] + t * (stops[i][2] - stops[i-1][2]));
      var b = Math.round(stops[i-1][3] + t * (stops[i][3] - stops[i-1][3]));
      return 'rgb('+r+','+g+','+b+')';
    }
  }
  return 'rgb(255,255,255)';
}

// ── Build star objects from flat data array ─────────────────────────────────
function generateSGStars() {
  sgStars = [];
  var d = SG_STAR_DATA;
  for (var i = 0; i < d.length; i += 4) {
    var ra = d[i], dec = d[i+1], vmag = d[i+2], bv = d[i+3];
    var idx = i / 4;
    sgStars.push({
      ra: ra, dec: dec, vmag: vmag, bv: bv,
      color: sgBVtoColor(bv),
      r: Math.max(0.8, 4.5 - vmag * 0.7),
      name: SG_STAR_NAMES[idx] || null,
      idx: idx,
      twinklePhase: Math.random() * Math.PI * 2,
      twinkleSpeed: 0.008 + Math.random() * 0.015
    });
  }
}

// ── Draw IAU constellation stick figures ────────────────────────────────────
function sgDrawConstellations(ctx, W, H) {
  if (!sgShowLines || !SG_CONSTELLATIONS) return;
  ctx.strokeStyle = 'rgba(150,160,220,0.22)';
  ctx.lineWidth = 0.8;
  ctx.fillStyle = 'rgba(180,180,220,0.40)';
  ctx.font = '10px sans-serif';
  ctx.textAlign = 'center';

  for (var c = 0; c < SG_CONSTELLATIONS.length; c++) {
    var con = SG_CONSTELLATIONS[c];
    var name = con[0], cra = con[1], cdec = con[2], segs = con[3];
    // Draw segments
    ctx.beginPath();
    for (var s = 0; s < segs.length - 1; s += 2) {
      var sa = sgStars[segs[s]],   pa = sgProjectCache[segs[s]];
      var sb = sgStars[segs[s+1]], pb = sgProjectCache[segs[s+1]];
      if (!sa || !sb || !pa || !pb) continue;
      if (!pa.visible || !pb.visible) continue;
      if (Math.abs(pa.x - pb.x) > W * 0.5) continue;
      ctx.moveTo(pa.x, pa.y);
      ctx.lineTo(pb.x, pb.y);
    }
    ctx.stroke();
    // Label at centroid
    var cp = sgProject(cra, cdec);
    if (cp.visible && cp.x > 0 && cp.x < W && cp.y > 0 && cp.y < H) {
      ctx.fillText(name, cp.x, cp.y);
    }
  }
}

// ── Hit-testing ─────────────────────────────────────────────────────────────
function sgGetStarAt(cx, cy) {
  if (!sgCanvas || !sgStars.length || !sgProjectCache.length) return null;
  var best = null, bestDist = Infinity;
  for (var i = 0; i < sgStars.length; i++) {
    var p = sgProjectCache[i];
    if (!p || !p.visible) continue;
    var dx = cx - p.x, dy = cy - p.y;
    var dist = Math.sqrt(dx*dx + dy*dy);
    var hitR = Math.max(8, 12 - sgStars[i].vmag * 1.5);
    if (dist < hitR && dist < bestDist) {
      bestDist = dist;
      best = sgStars[i];
    }
  }
  return best;
}

// ── Click — reveal real name or assign pool name ────────────────────────────
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
}

// ── Shuffle / Reset ─────────────────────────────────────────────────────────
function sgShuffle() {
  sgNamed = {};
  var nc = document.getElementById('sg-named-count');
  if (nc) nc.innerText = '0';
  sgViewRA  = Math.random() * 360;
  sgViewDec = (Math.random() - 0.5) * 80;
}

function sgReset() {
  sgNamed = {};
  var nc = document.getElementById('sg-named-count');
  if (nc) nc.innerText = '0';
  sgViewRA = 180; sgViewDec = 25;
}

function sgToggleLines() { sgShowLines = !sgShowLines; }

// ── Init (called once when navigating to Stargazer tab) ─────────────────────
function initStargazer() {
  sgCanvas = document.getElementById('stargazer-canvas');
  if (!sgCanvas) return;
  sgCtx = sgCanvas.getContext('2d');
  resizeSG();
  if (!sgStars.length) generateSGStars();

  var _dragStartX = 0, _dragStartY = 0;

  sgCanvas.addEventListener('mousedown', function(e) {
    sgDrag = true; sgDragX = e.clientX; sgDragY = e.clientY;
    _dragStartX = e.clientX; _dragStartY = e.clientY;
  });
  sgCanvas.addEventListener('mousemove', function(e) {
    if (sgDrag) {
      sgViewRA -= (e.clientX - sgDragX) / sgScale * (180 / Math.PI);
      sgViewRA = ((sgViewRA % 360) + 360) % 360;
      sgViewDec = Math.max(-85, Math.min(85, sgViewDec + (e.clientY - sgDragY) / sgScale * (180 / Math.PI)));
      sgDragX = e.clientX; sgDragY = e.clientY;
    }
    var rect = sgCanvas.getBoundingClientRect();
    sgHover = sgGetStarAt(e.clientX - rect.left, e.clientY - rect.top);
    sgCanvas.style.cursor = sgHover ? 'pointer' : 'crosshair';
  });
  sgCanvas.addEventListener('mouseup', function(e) {
    if (Math.abs(e.clientX - _dragStartX) < 5 && Math.abs(e.clientY - _dragStartY) < 5) {
      var rect = sgCanvas.getBoundingClientRect();
      sgClickStar(e.clientX - rect.left, e.clientY - rect.top);
    }
    sgDrag = false;
  });

  sgCanvas.addEventListener('touchstart', function(e) {
    sgDrag = true;
    sgDragX = e.touches[0].clientX; sgDragY = e.touches[0].clientY;
    _dragStartX = sgDragX; _dragStartY = sgDragY;
  }, {passive: true});
  sgCanvas.addEventListener('touchmove', function(e) {
    if (!sgDrag) return;
    sgViewRA -= (e.touches[0].clientX - sgDragX) / sgScale * (180 / Math.PI);
    sgViewRA = ((sgViewRA % 360) + 360) % 360;
    sgViewDec = Math.max(-85, Math.min(85, sgViewDec + (e.touches[0].clientY - sgDragY) / sgScale * (180 / Math.PI)));
    sgDragX = e.touches[0].clientX; sgDragY = e.touches[0].clientY;
  }, {passive: true});
  sgCanvas.addEventListener('touchend', function(e) {
    var t = e.changedTouches[0];
    if (t && Math.abs(t.clientX - _dragStartX) < 10 && Math.abs(t.clientY - _dragStartY) < 10) {
      var rect = sgCanvas.getBoundingClientRect();
      sgClickStar(t.clientX - rect.left, t.clientY - rect.top);
    }
    sgDrag = false;
  });
}

function resizeSG() {
  if (!sgCanvas) return;
  var cont = document.getElementById('page-stargazer');
  if (!cont) return;
  sgCanvas.width  = cont.clientWidth  || innerWidth;
  sgCanvas.height = cont.clientHeight || innerHeight;
  sgInitProjection();
}

// ── Render loop ─────────────────────────────────────────────────────────────
var sgFrame = 0;
function sgLoop() {
  if (!sgCanvas || currentPage !== 'stargazer') {
    requestAnimationFrame(sgLoop);
    return;
  }
  var ctx = sgCtx || sgCanvas.getContext('2d');
  var W = sgCanvas.width, H = sgCanvas.height;

  // Background
  ctx.fillStyle = '#010110';
  ctx.fillRect(0, 0, W, H);
  var grad = ctx.createRadialGradient(W*0.6, H*0.4, 0, W*0.6, H*0.4, W*0.55);
  grad.addColorStop(0, 'rgba(80,40,140,0.12)');
  grad.addColorStop(0.5, 'rgba(40,20,80,0.06)');
  grad.addColorStop(1, 'transparent');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  sgFrame++;

  // Build projection cache
  sgProjectCache = [];
  for (var i = 0; i < sgStars.length; i++) {
    var s = sgStars[i];
    sgProjectCache[i] = sgProject(s.ra, s.dec);
  }

  // Constellation lines + labels
  sgDrawConstellations(ctx, W, H);

  // Batch draw by colour bucket
  var buckets = {};
  for (var i = 0; i < sgStars.length; i++) {
    var p = sgProjectCache[i];
    if (!p || !p.visible) continue;
    if (p.x < -20 || p.x > W+20 || p.y < -20 || p.y > H+20) continue;
    var s = sgStars[i];
    var col = sgNamed[s.idx] ? '__named__' : s.color;
    if (!buckets[col]) buckets[col] = [];
    buckets[col].push(i);
  }

  ctx.shadowBlur = 0;
  for (var col in buckets) {
    if (col === '__named__') continue;
    ctx.fillStyle = col;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    var list = buckets[col];
    for (var j = 0; j < list.length; j++) {
      var idx = list[j];
      var p = sgProjectCache[idx];
      var s = sgStars[idx];
      s.twinklePhase += s.twinkleSpeed;
      var alpha = 0.65 + 0.35 * Math.sin(s.twinklePhase);
      var r = s.r * (0.85 + 0.15 * alpha);
      ctx.moveTo(p.x + r, p.y);
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    }
    ctx.fill();
  }

  // Glow for bright stars (vmag < 1.5)
  for (var i = 0; i < sgStars.length; i++) {
    var s = sgStars[i];
    if (s.vmag >= 1.5) continue;
    var p = sgProjectCache[i];
    if (!p || !p.visible) continue;
    ctx.shadowBlur = 12 - s.vmag * 4;
    ctx.shadowColor = s.color;
    ctx.fillStyle = s.color;
    ctx.globalAlpha = 0.9;
    ctx.beginPath();
    ctx.arc(p.x, p.y, s.r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.shadowBlur = 0;

  // Named stars
  if (buckets['__named__']) {
    var namedList = buckets['__named__'];
    for (var j = 0; j < namedList.length; j++) {
      var idx = namedList[j];
      var p = sgProjectCache[idx];
      var s = sgStars[idx];
      s.twinklePhase += s.twinkleSpeed;
      ctx.shadowBlur = 14;
      ctx.shadowColor = '#c9b8ff';
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = '#e0d0ff';
      ctx.beginPath();
      ctx.arc(p.x, p.y, s.r + 1.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 0.8;
      ctx.fillStyle = '#c9b8ff';
      ctx.font = '10px "DM Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(sgNamed[s.idx], p.x, p.y - s.r - 5);
    }
  }

  ctx.globalAlpha = 1;
  ctx.shadowBlur = 0;

  // Hover ring
  if (sgHover) {
    var hp = sgProjectCache[sgHover.idx];
    if (hp && hp.visible) {
      ctx.strokeStyle = 'rgba(200,180,255,0.6)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(hp.x, hp.y, sgHover.r + 8, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  requestAnimationFrame(sgLoop);
}"""

# ── 3. Find the old Stargazer section boundaries ────────────────────────────
start_marker = '// ══════════════════════════════════════════════════════════\n// STARGAZER'
end_marker   = '// ══════════════════════════════════════════════════════════\n// INIT'

start_idx = html.find(start_marker)
end_idx   = html.find(end_marker)
if start_idx == -1 or end_idx == -1:
    print('ERROR: Could not find Stargazer section markers!')
    sys.exit(1)

print(f'Stargazer section: chars {start_idx}–{end_idx}')

# ── 4. Find where to inject star data (just before the STARGAZER section) ───
# We'll inject the star data inline as a <script>-less block right above the
# STARGAZER comment, within the same inline <script>.

# Build data injection block
data_block = '\n// ── Star catalogue data (auto-generated) ─────────────────────────────────\n'
data_block += star_data.strip() + '\n\n'

# ── 5. Check if data already injected ────────────────────────────────────────
if 'var SG_STAR_DATA=' in html:
    # Already injected — just replace the Stargazer functions section
    print('Star data already present, replacing functions only...')
    new_html = html[:start_idx] + NEW_SG + '\n\n' + html[end_idx:]
else:
    # Inject data + new functions, replacing old Stargazer section
    print('Injecting star data + new Stargazer functions...')
    new_html = html[:start_idx] + data_block + NEW_SG + '\n\n' + html[end_idx:]

# ── 6. Write output ───────────────────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Done. index.html updated.')
# Sanity checks
checks = ['SG_STAR_DATA', 'SG_STAR_NAMES', 'SG_CONSTELLATIONS', 'sgInitProjection', 'sgProject', 'sgBVtoColor', 'sgDrawConstellations', 'sgGetStarAt']
for c in checks:
    print(f'  {"OK" if c in new_html else "MISSING"}: {c}')
