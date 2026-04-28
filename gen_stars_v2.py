"""
gen_stars_v2.py — Real star data generator for Stargazer
Sources:
  Stars       : HYG v3.8 (Hipparcos/Yale/Gliese), GitHub
  Const. lines: Stellarium modern_iau sky culture (JSON, HIP-ID polylines)
  Star names  : Stellarium common_star_names.fab (HIP-ID -> proper name)

Outputs per star:
  SG_STAR_DATA   flat [ra,dec,vmag,bv,  ...] for 1638 real stars
  SG_STAR_NAMES  {idx:"Sirius"}              IAU/Stellarium proper names
  SG_STAR_BAYER  {idx:"alpha CMa"}           Bayer/Flamsteed designations
  SG_STAR_INFO   {idx:"A1V|8.6"}            spectral class | distance (ly)
  SG_STAR_HIP    {idx:32349}                Hipparcos catalogue number
  SG_CONSTELLATIONS [[name,cRA,cDec,[segs]]]

Run: python gen_stars_v2.py 2>gen_log.txt > star_data_v2.js
"""

import csv, gzip, io, json, re, sys, urllib.request

MAG_LIMIT = 6.5   # full naked-eye sky + all constellation endpoint stars (incl. Mira)

HYG_URL   = ("https://raw.githubusercontent.com/astronexus/"
             "HYG-Database/main/hyg/v3/hyg_v38.csv.gz")
IAU_URL   = ("https://raw.githubusercontent.com/Stellarium/stellarium/"
             "master/skycultures/modern_iau/index.json")
NAMES_URL = ("https://raw.githubusercontent.com/Stellarium/stellarium/"
             "master/skycultures/common_star_names.fab")

# Greek letter lookup (HYG bayer column 3-letter codes)
GREEK = {
    "Alp":"α","Bet":"β","Gam":"γ","Del":"δ","Eps":"ε","Zet":"ζ",
    "Eta":"η","The":"θ","Iot":"ι","Kap":"κ","Lam":"λ","Mu" :"μ",
    "Nu" :"ν","Xi" :"ξ","Omi":"ο","Pi" :"π","Rho":"ρ","Sig":"σ",
    "Tau":"τ","Ups":"υ","Phi":"φ","Chi":"χ","Psi":"ψ","Ome":"ω",
}
SUP = {"1":"¹","2":"²","3":"³","4":"⁴","5":"⁵","6":"⁶","7":"⁷","8":"⁸","9":"⁹"}

def bayer_str(bayer_col, flam_col, con_col):
    """Return a compact designation like 'α CMa' or '61 Cyg', or '' if none."""
    con = con_col.strip()
    if not con:
        return ""
    b = bayer_col.strip()
    if b:
        m = re.match(r"([A-Za-z]+)(\d?)", b)
        if m:
            code, sup = m.group(1)[:3], m.group(2)
            greek = GREEK.get(code, "")
            if greek:
                return greek + SUP.get(sup, "") + " " + con
    f = flam_col.strip()
    if f.isdigit():
        return f + " " + con
    return ""

# Constellation display centres (RA°, Dec°)
CON_CENTERS = {
    "Andromeda"         : ( 17.0,  38.0),
    "Aquarius"          : (335.0, -12.0),
    "Aquila"            : (297.0,   5.0),
    "Ara"               : (264.0, -57.0),
    "Aries"             : ( 33.0,  20.0),
    "Auriga"            : ( 90.0,  42.0),
    "Boötes"            : (220.0,  30.0),
    "Cancer"            : (130.0,  20.0),
    "Canes Venatici"    : (195.0,  40.0),
    "Canis Major"       : (105.0, -22.0),
    "Canis Minor"       : (114.0,   6.0),
    "Capricornus"       : (308.0, -18.0),
    "Carina"            : (155.0, -62.0),
    "Cassiopeia"        : ( 10.0,  60.0),
    "Centaurus"         : (210.0, -50.0),
    "Cepheus"           : (340.0,  70.0),
    "Cetus"             : ( 25.0, -10.0),
    "Columba"           : ( 84.0, -35.0),
    "Corona Australis"  : (284.0, -42.0),
    "Corona Borealis"   : (240.0,  28.0),
    "Corvus"            : (187.0, -18.0),
    "Crux"              : (187.0, -60.0),
    "Cygnus"            : (310.0,  45.0),
    "Delphinus"         : (309.0,  13.0),
    "Draco"             : (270.0,  65.0),
    "Eridanus"          : ( 55.0, -28.0),
    "Gemini"            : (113.0,  22.0),
    "Hercules"          : (258.0,  28.0),
    "Hydra"             : (180.0, -20.0),
    "Leo"               : (152.0,  15.0),
    "Lepus"             : ( 82.0, -20.0),
    "Libra"             : (230.0, -15.0),
    "Lupus"             : (232.0, -45.0),
    "Lyra"              : (283.0,  36.0),
    "Ophiuchus"         : (267.0,  -8.0),
    "Orion"             : ( 83.8,   5.0),
    "Pegasus"           : (340.0,  20.0),
    "Perseus"           : ( 57.0,  45.0),
    "Phoenix"           : (  6.6, -42.3),
    "Pisces"            : ( 10.0,  12.0),
    "Piscis Austrinus"  : (344.0, -28.0),
    "Puppis"            : (121.0, -30.0),
    "Sagitta"           : (298.0,  19.0),
    "Sagittarius"       : (285.0, -28.0),
    "Scorpius"          : (253.0, -30.0),
    "Serpens"           : (238.0,   5.0),
    "Taurus"            : ( 65.0,  20.0),
    "Triangulum"        : ( 31.0,  32.0),
    "Ursa Major"        : (165.0,  55.0),
    "Ursa Minor"        : (230.0,  78.0),
    "Virgo"             : (200.0,  -5.0),
    "Vela"              : (135.0, -45.0),
    "Vulpecula"         : (299.0,  24.0),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_bytes(url, label):
    print(f"  Downloading {label} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()

# ── 1. Stars from HYG v3.8 ───────────────────────────────────────────────────
raw_gz = fetch_bytes(HYG_URL, "HYG v3.8 star catalogue")
raw    = gzip.decompress(raw_gz).decode("utf-8")
reader = csv.DictReader(io.StringIO(raw))

all_stars  = []
hip_to_idx = {}

for row in reader:
    try:
        mag = float(row["mag"])
    except (ValueError, KeyError):
        continue
    if mag > MAG_LIMIT:
        continue
    # Exclude the Sun (mag -26.7, stored at RA/Dec 0,0 as a placeholder)
    # and any other non-stellar objects that sneak into the catalogue
    if mag < -2.0:
        continue

    hip_str = row.get("hip", "").strip()
    hip     = int(hip_str) if hip_str.isdigit() else 0

    try:
        ra_deg = float(row["ra"]) * 15.0
        dec    = float(row["dec"])
    except (ValueError, KeyError):
        continue

    try:
        bv = round(float(row["ci"]), 2)
    except (ValueError, KeyError):
        bv = 0.6

    # Distance: parsecs -> light-years (0 or > 100000 = unknown)
    try:
        dist_pc = float(row.get("dist", "0") or "0")
        dist_ly = round(dist_pc * 3.26156, 1) if 0 < dist_pc < 100000 else 0
    except (ValueError, TypeError):
        dist_ly = 0

    # Spectral type — trim to ≤ 6 chars for compactness
    spect = (row.get("spect") or "").strip()[:6]

    # Bayer/Flamsteed designation
    bay = bayer_str(row.get("bayer",""), row.get("flam",""), row.get("con",""))

    all_stars.append({
        "ra"    : round(ra_deg, 4),
        "dec"   : round(dec,    4),
        "mag"   : round(mag,    2),
        "bv"    : bv,
        "hip"   : hip,
        "name"  : "",
        "bayer" : bay,
        "spect" : spect,
        "dist"  : dist_ly,
    })

all_stars.sort(key=lambda s: s["mag"])
for i, s in enumerate(all_stars):
    if s["hip"]:
        hip_to_idx[s["hip"]] = i

print(f"  {len(all_stars)} stars (mag ≤ {MAG_LIMIT})", file=sys.stderr)

# ── 2. Star names from Stellarium common_star_names.fab ──────────────────────
names_raw = fetch_bytes(NAMES_URL, "star names").decode("utf-8")
for line in names_raw.splitlines():
    m = re.match(r"\s*(\d+)\|_\(\"([^\"]+)\"\)", line)
    if not m:
        continue
    hip, name = int(m.group(1)), m.group(2)
    if hip in hip_to_idx:
        all_stars[hip_to_idx[hip]]["name"] = name

named_count  = sum(1 for s in all_stars if s["name"])
bayer_count  = sum(1 for s in all_stars if s["bayer"])
print(f"  {named_count} proper names, {bayer_count} Bayer/Flamsteed designations",
      file=sys.stderr)

# ── 3. Constellation lines from Stellarium modern_iau ────────────────────────
iau_data = json.loads(fetch_bytes(IAU_URL, "IAU constellation lines"))

constellations = []
for con in iau_data.get("constellations", []):
    cn   = con.get("common_name", {})
    name = cn.get("native", "").strip()
    if not name or name not in CON_CENTERS:
        continue

    segs = []
    for polyline in con.get("lines", []):
        for k in range(len(polyline) - 1):
            ha, hb = int(polyline[k]), int(polyline[k + 1])
            if ha in hip_to_idx and hb in hip_to_idx:
                segs.extend([hip_to_idx[ha], hip_to_idx[hb]])

    if not segs:
        print(f"  WARNING: no matched stars for {name}", file=sys.stderr)
        continue

    cra, cdec = CON_CENTERS[name]
    constellations.append([name, cra, cdec, segs])

constellations.sort(key=lambda c: c[1])
print(f"  {len(constellations)} constellations", file=sys.stderr)

# ── 4. Emit JS ────────────────────────────────────────────────────────────────
out = []
out.append("// AUTO-GENERATED by gen_stars_v2.py")
out.append(f"// {len(all_stars)} REAL stars · HYG v3.8 (Hipparcos) · mag ≤ {MAG_LIMIT}")
out.append(f"// {len(constellations)} IAU constellations · Stellarium modern_iau")
out.append("")

# SG_STAR_DATA: flat [ra,dec,vmag,bv, ...]
vals = []
for s in all_stars:
    vals.extend([s["ra"], s["dec"], s["mag"], s["bv"]])

out.append("var SG_STAR_DATA=[")
COLS = 8  # stars per text line
for i in range(0, len(vals), COLS * 4):
    out.append("  " + ",".join(str(v) for v in vals[i:i + COLS * 4]) + ",")
out.append("];")
out.append("")

# SG_STAR_NAMES: {idx:"Sirius", ...}  — IAU proper names only
out.append("var SG_STAR_NAMES={")
for i, s in enumerate(all_stars):
    if s["name"]:
        out.append(f'  {i}:"{s["name"].replace(chr(34), chr(92)+chr(34))}",')
out.append("};")
out.append("")

# SG_STAR_BAYER: {idx:"α CMa", ...}  — Bayer/Flamsteed for stars lacking a proper name
out.append("var SG_STAR_BAYER={")
for i, s in enumerate(all_stars):
    if s["bayer"] and not s["name"]:
        safe = s["bayer"].replace('"', '\\"')
        out.append(f'  {i}:"{safe}",')
out.append("};")
out.append("")

# SG_STAR_INFO: {idx:"A1V|8.6", ...}  — spectral|dist(ly), only where both known
out.append("var SG_STAR_INFO={")
for i, s in enumerate(all_stars):
    sp, d = s["spect"], s["dist"]
    if sp or d:
        val = sp + "|" + (str(d) if d else "")
        out.append(f'  {i}:"{val}",')
out.append("};")
out.append("")

# SG_STAR_HIP: {idx:hip_id, ...}  — Hipparcos numbers (non-zero only)
out.append("var SG_STAR_HIP={")
for i, s in enumerate(all_stars):
    if s["hip"]:
        out.append(f"  {i}:{s['hip']},")
out.append("};")
out.append("")

# SG_CONSTELLATIONS: [[name,cRA,cDec,[segs]], ...]
out.append("var SG_CONSTELLATIONS=[")
for con in constellations:
    seg_str = ",".join(str(x) for x in con[3])
    out.append(f'  ["{con[0]}",{con[1]},{con[2]},[{seg_str}]],')
out.append("];")
out.append("")

sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.write("\n".join(out))
print(f"\nDone — {len(all_stars)} stars, {len(constellations)} constellations.",
      file=sys.stderr)
