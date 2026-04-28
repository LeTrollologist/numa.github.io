"""
gen_mw.py — regenerates only the Milky Way section of dso_data.js
Outputs SG_MW_DATA (stride-5) and SG_MW_DUST (stride-4)

SG_MW_DATA stride-5: [ra, dec, halfWidthDeg, brightness, layerType]
  layerType 0 = outer halo   (wide, cool blue-white)
  layerType 1 = inner halo   (medium, blue-white)
  layerType 2 = spine / plane (narrow, near-white, slightly warm)
  layerType 3 = GC bulge     (warm cream / yellow-white)

SG_MW_DUST stride-4: [ra, dec, halfWidthDeg, opacity]
  Dark dust lane patches (Great Rift + Coal Sack region)

Run: python gen_mw.py > mw_data.js
"""
import math, sys
sys.stdout.reconfigure(encoding="utf-8")

# IAU galactic to J2000 equatorial
RA_NGP  = math.radians(192.859508)
DEC_NGP = math.radians(27.128336)
L_NCP   = math.radians(122.932)

def gal_to_eq(l_deg, b_deg):
    l = math.radians(l_deg)
    b = math.radians(b_deg)
    sin_d = math.sin(DEC_NGP)*math.sin(b) + math.cos(DEC_NGP)*math.cos(b)*math.cos(L_NCP - l)
    sin_d = max(-1.0, min(1.0, sin_d))
    dec   = math.asin(sin_d)
    cos_d = math.cos(dec)
    if cos_d < 1e-9:
        return 0.0, math.degrees(dec)
    sin_x = math.cos(b)*math.sin(L_NCP - l) / cos_d
    cos_x = (math.cos(DEC_NGP)*math.sin(b) - math.sin(DEC_NGP)*math.cos(b)*math.cos(L_NCP - l)) / cos_d
    ra = RA_NGP + math.atan2(sin_x, cos_x)
    return (math.degrees(ra) % 360), math.degrees(dec)

# ── Brightness profile ─────────────────────────────────────────────────────────
def mw_brightness(l):
    l = l % 360
    lc = l if l < 180 else 360 - l   # degrees from GC
    gc  = math.exp(-(lc / 50)**2) * 1.00
    scu = math.exp(-((l -  30) / 20)**2) * 0.80   # Scutum arm
    cyg = math.exp(-((l -  80) / 16)**2) * 0.74   # Cygnus
    per = math.exp(-((l - 140) / 26)**2) * 0.48   # Perseus
    vel = math.exp(-((l - 255) / 22)**2) * 0.60   # Vela/Puppis
    cen = math.exp(-((l - 310) / 20)**2) * 0.84   # Centaurus
    nor = math.exp(-((l - 332) / 18)**2) * 0.90   # Norma/Scorpius
    return max(0.20, gc + scu + cyg + per + vel + cen + nor)

def mw_half_width(l):
    """Half-width of the full band in degrees."""
    l = l % 360
    lc = l if l < 180 else 360 - l
    base = 5.5 + 10.5 * math.exp(-(lc / 52)**2)
    cyg_w = 3.5 * math.exp(-((l - 80) / 22)**2)
    return min(base + cyg_w, 20.0)

# ── Build MW cloud data ────────────────────────────────────────────────────────
MW = []  # list of [ra, dec, halfWidthDeg, brightness, layerType]

STEP = 2   # degrees galactic longitude per sample

for l_int in range(0, 360, STEP):
    l   = float(l_int)
    bri = mw_brightness(l)
    hw  = mw_half_width(l)

    # ── Layer 2: spine (on the galactic plane b=0) ────────────────────────────
    ra, dec = gal_to_eq(l, 0.0)
    MW.append([round(ra,2), round(dec,2), round(hw * 0.38, 2), round(bri, 3), 2])

    # ── Layer 1: inner halo (b = ±0.42 * hw) ─────────────────────────────────
    for sign in [1, -1]:
        b_off = sign * hw * 0.42
        scale = math.exp(-(0.42 * 2.0)**2) * 0.88
        ra2, dec2 = gal_to_eq(l, b_off)
        MW.append([round(ra2,2), round(dec2,2), round(hw * 0.72, 2),
                   round(bri * scale, 3), 1])

    # ── Layer 0: outer halo (b = ±0.78 * hw) ─────────────────────────────────
    for sign in [1, -1]:
        b_off = sign * hw * 0.78
        scale = math.exp(-(0.78 * 1.7)**2) * 0.55
        ra2, dec2 = gal_to_eq(l, b_off)
        MW.append([round(ra2,2), round(dec2,2), round(hw * 1.10, 2),
                   round(bri * scale, 3), 0])

# ── Layer 3: Galactic Centre bulge (dense warm cluster) ───────────────────────
# The bulge dominates the inner ~20° around the GC
for dl in range(-22, 23, 3):
    for db in range(-14, 15, 3):
        dist = math.sqrt((dl/26)**2 + (db/17)**2)
        bri_c = 1.05 * math.exp(-dist**2)
        if bri_c < 0.04: continue
        ra, dec = gal_to_eq(dl % 360, db)
        MW.append([round(ra,2), round(dec,2), 4.5, round(bri_c, 3), 3])

# ── SG_MW_DUST: dark dust lanes (Great Rift + Coal Sack) ─────────────────────
DUST = []  # [ra, dec, halfWidthDeg, opacity]

# Great Rift — runs roughly l=5° to l=88°, slightly north of galactic plane
# Most prominent in the Cygnus (l=70-85°) and Aquila (l=30-50°) regions
for l in range(5, 89, 3):
    # The rift sits slightly above the plane (toward positive b)
    b_peak = 1.8 + 3.5 * math.exp(-((l - 68) / 28)**2)  # peaks in Cygnus
    # Width of the dark lane
    hw_dust = 1.8 + 2.0 * math.exp(-((l - 70) / 30)**2)
    opacity = 0.52 + 0.32 * math.exp(-((l - 58) / 26)**2)
    ra, dec = gal_to_eq(l, b_peak)
    DUST.append([round(ra,2), round(dec,2), round(hw_dust,1), round(opacity,2)])
    # A secondary narrower lane slightly below
    if l < 70:
        ra2, dec2 = gal_to_eq(l, b_peak * 0.4)
        DUST.append([round(ra2,2), round(dec2,2), round(hw_dust*0.55,1), round(opacity*0.45,2)])

# Dark lane in Ophiuchus / Scorpius near GC (l=0-25°, b=+1 to +5°)
for l in range(-8, 26, 3):
    b_off = 2.5 + 1.5 * math.exp(-((l - 8) / 15)**2)
    hw_dust = 2.2
    opacity = 0.40 + 0.18 * math.exp(-((l - 10) / 18)**2)
    ra, dec = gal_to_eq(l % 360, b_off)
    DUST.append([round(ra,2), round(dec,2), round(hw_dust,1), round(opacity,2)])

# Coal Sack (southern sky) — l≈300-303°, b≈-2° to -4°
for dl in range(-4, 5, 2):
    for db in [-1, -2, -3, -4]:
        ra, dec = gal_to_eq((301 + dl) % 360, db)
        DUST.append([round(ra,2), round(dec,2), 2.2, 0.58])

# ── Emit JS ───────────────────────────────────────────────────────────────────
out = []
out.append("// AUTO-GENERATED by gen_mw.py")
out.append(f"// {len(MW)} Milky Way cloud points (stride-5) · {len(DUST)} dust lane points")
out.append("")

# SG_MW_DATA stride-5
out.append("var SG_MW_DATA=[")
COLS = 5  # points per line
for i in range(0, len(MW), COLS):
    chunk = MW[i:i+COLS]
    line = ",".join(f"{p[0]},{p[1]},{p[2]},{p[3]},{p[4]}" for p in chunk)
    out.append(f"  {line},")
out.append("];")
out.append("")

# SG_MW_DUST stride-4
out.append("var SG_MW_DUST=[")
COLS = 6
for i in range(0, len(DUST), COLS):
    chunk = DUST[i:i+COLS]
    line = ",".join(f"{p[0]},{p[1]},{p[2]},{p[3]}" for p in chunk)
    out.append(f"  {line},")
out.append("];")
out.append("")

sys.stdout.write("\n".join(out))
print(f"\nDone — {len(MW)} MW points, {len(DUST)} dust points.", file=sys.stderr)
