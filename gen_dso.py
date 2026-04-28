"""
gen_dso.py — generates dso_data.js
Outputs:
  SG_DSO_DATA   flat stride-8 array [ra,dec,vmag,majArcmin,minArcmin,pa,typeCode,nameIdx]
  SG_DSO_NAMES  {nameIdx: "M42 · Orion Nebula"}
  SG_MW_DATA    flat stride-4 array [ra,dec,halfWidthDeg,brightness] — Milky Way cloud points

Type codes: 0=galaxy 1=openCluster 2=globular 3=emissionNebula 4=planetaryNebula
            5=SNR 6=reflectionNebula 7=mixed(emission+reflection)

Run: python gen_dso.py > dso_data.js
"""
import math, sys

sys.stdout.reconfigure(encoding="utf-8")

# ── DSO catalogue ─────────────────────────────────────────────────────────────
# Fields: id, name (common), ra (deg J2000), dec (deg), vmag, maj (arcmin),
#         min (arcmin), pa (deg, N through E), type
DSOs = [
    # ── Supernova remnants ────────────────────────────────────────────────────
    {"id":"M1",      "name":"Crab Nebula",           "ra": 83.633, "dec": 22.015, "mag": 8.4, "maj": 7.0,   "min": 5.0,   "pa":  0, "type":5},
    # ── Open clusters ─────────────────────────────────────────────────────────
    {"id":"M6",      "name":"Butterfly Cluster",     "ra":265.083, "dec":-32.253, "mag": 4.2, "maj":25.0,   "min":25.0,   "pa":  0, "type":1},
    {"id":"M7",      "name":"Ptolemy Cluster",       "ra":268.463, "dec":-34.793, "mag": 3.3, "maj":80.0,   "min":80.0,   "pa":  0, "type":1},
    {"id":"M11",     "name":"Wild Duck Cluster",     "ra":282.771, "dec": -6.270, "mag": 6.3, "maj":14.0,   "min":14.0,   "pa":  0, "type":1},
    {"id":"M18",     "name":"",                      "ra":274.992, "dec":-17.102, "mag": 7.5, "maj": 9.0,   "min": 9.0,   "pa":  0, "type":1},
    {"id":"M21",     "name":"",                      "ra":271.054, "dec":-22.490, "mag": 6.5, "maj":13.0,   "min":13.0,   "pa":  0, "type":1},
    {"id":"M23",     "name":"",                      "ra":269.225, "dec":-19.020, "mag": 6.9, "maj":27.0,   "min":27.0,   "pa":  0, "type":1},
    {"id":"M24",     "name":"Sagittarius Star Cloud","ra":274.225, "dec":-18.483, "mag": 4.5, "maj":90.0,   "min":90.0,   "pa":  0, "type":1},
    {"id":"M25",     "name":"",                      "ra":277.946, "dec":-19.115, "mag": 4.6, "maj":32.0,   "min":32.0,   "pa":  0, "type":1},
    {"id":"M26",     "name":"",                      "ra":281.325, "dec": -9.384, "mag": 8.0, "maj":15.0,   "min":15.0,   "pa":  0, "type":1},
    {"id":"M29",     "name":"",                      "ra":305.989, "dec": 38.524, "mag": 7.1, "maj": 7.0,   "min": 7.0,   "pa":  0, "type":1},
    {"id":"M34",     "name":"",                      "ra": 40.521, "dec": 42.762, "mag": 5.5, "maj":35.0,   "min":35.0,   "pa":  0, "type":1},
    {"id":"M35",     "name":"",                      "ra": 92.225, "dec": 24.333, "mag": 5.3, "maj":28.0,   "min":28.0,   "pa":  0, "type":1},
    {"id":"M36",     "name":"",                      "ra": 84.050, "dec": 34.140, "mag": 6.3, "maj":12.0,   "min":12.0,   "pa":  0, "type":1},
    {"id":"M37",     "name":"",                      "ra": 88.075, "dec": 32.553, "mag": 6.2, "maj":24.0,   "min":24.0,   "pa":  0, "type":1},
    {"id":"M38",     "name":"",                      "ra": 82.175, "dec": 35.838, "mag": 7.4, "maj":21.0,   "min":21.0,   "pa":  0, "type":1},
    {"id":"M39",     "name":"",                      "ra":322.950, "dec": 48.433, "mag": 4.6, "maj":32.0,   "min":32.0,   "pa":  0, "type":1},
    {"id":"M41",     "name":"",                      "ra":101.496, "dec":-20.760, "mag": 4.5, "maj":38.0,   "min":38.0,   "pa":  0, "type":1},
    {"id":"M44",     "name":"Beehive Cluster",       "ra":130.100, "dec": 19.667, "mag": 3.7, "maj":95.0,   "min":95.0,   "pa":  0, "type":1},
    {"id":"M45",     "name":"Pleiades",              "ra": 56.750, "dec": 24.117, "mag": 1.6, "maj":110.0,  "min":110.0,  "pa":  0, "type":1},
    {"id":"M46",     "name":"",                      "ra":115.445, "dec":-14.810, "mag": 6.1, "maj":27.0,   "min":27.0,   "pa":  0, "type":1},
    {"id":"M47",     "name":"",                      "ra":114.146, "dec":-14.483, "mag": 5.2, "maj":30.0,   "min":30.0,   "pa":  0, "type":1},
    {"id":"M48",     "name":"",                      "ra":123.429, "dec": -5.750, "mag": 5.8, "maj":54.0,   "min":54.0,   "pa":  0, "type":1},
    {"id":"M50",     "name":"",                      "ra":105.675, "dec": -8.385, "mag": 5.9, "maj":16.0,   "min":16.0,   "pa":  0, "type":1},
    {"id":"M52",     "name":"",                      "ra":351.200, "dec": 61.593, "mag": 7.3, "maj":13.0,   "min":13.0,   "pa":  0, "type":1},
    {"id":"M67",     "name":"",                      "ra":132.825, "dec": 11.800, "mag": 6.1, "maj":30.0,   "min":30.0,   "pa":  0, "type":1},
    {"id":"M93",     "name":"",                      "ra":116.121, "dec":-23.853, "mag": 6.2, "maj":22.0,   "min":22.0,   "pa":  0, "type":1},
    {"id":"M103",    "name":"",                      "ra": 23.338, "dec": 60.655, "mag": 7.4, "maj": 6.0,   "min": 6.0,   "pa":  0, "type":1},
    {"id":"NGC 869", "name":"Double Cluster h Per",  "ra": 34.763, "dec": 57.133, "mag": 4.3, "maj":30.0,   "min":30.0,   "pa":  0, "type":1},
    {"id":"NGC 884", "name":"Double Cluster χ Per",  "ra": 35.604, "dec": 57.117, "mag": 4.4, "maj":30.0,   "min":30.0,   "pa":  0, "type":1},
    {"id":"NGC 752", "name":"",                      "ra": 28.997, "dec": 37.793, "mag": 5.7, "maj":50.0,   "min":50.0,   "pa":  0, "type":1},
    {"id":"NGC 2516","name":"",                      "ra":119.516, "dec":-60.752, "mag": 3.8, "maj":30.0,   "min":30.0,   "pa":  0, "type":1},
    {"id":"IC 4665", "name":"",                      "ra":267.654, "dec":  5.700, "mag": 4.2, "maj":41.0,   "min":41.0,   "pa":  0, "type":1},
    # ── Globular clusters ─────────────────────────────────────────────────────
    {"id":"M2",      "name":"",                      "ra":323.363, "dec": -0.823, "mag": 6.5, "maj":16.0,   "min":16.0,   "pa":  0, "type":2},
    {"id":"M3",      "name":"",                      "ra":205.548, "dec": 28.377, "mag": 6.2, "maj":18.0,   "min":18.0,   "pa":  0, "type":2},
    {"id":"M4",      "name":"",                      "ra":245.898, "dec":-26.525, "mag": 5.9, "maj":36.0,   "min":36.0,   "pa":  0, "type":2},
    {"id":"M5",      "name":"",                      "ra":229.638, "dec":  2.083, "mag": 5.7, "maj":23.0,   "min":23.0,   "pa":  0, "type":2},
    {"id":"M9",      "name":"",                      "ra":259.799, "dec":-18.516, "mag": 8.0, "maj":12.0,   "min":12.0,   "pa":  0, "type":2},
    {"id":"M10",     "name":"",                      "ra":254.287, "dec": -4.099, "mag": 6.4, "maj":20.0,   "min":20.0,   "pa":  0, "type":2},
    {"id":"M12",     "name":"",                      "ra":251.810, "dec": -1.948, "mag": 7.7, "maj":16.0,   "min":16.0,   "pa":  0, "type":2},
    {"id":"M13",     "name":"Hercules Cluster",      "ra":250.423, "dec": 36.460, "mag": 5.8, "maj":20.0,   "min":20.0,   "pa":  0, "type":2},
    {"id":"M14",     "name":"",                      "ra":264.400, "dec": -3.246, "mag": 8.0, "maj":12.0,   "min":12.0,   "pa":  0, "type":2},
    {"id":"M15",     "name":"Pegasus Cluster",       "ra":322.493, "dec": 12.167, "mag": 6.4, "maj":18.0,   "min":18.0,   "pa":  0, "type":2},
    {"id":"M19",     "name":"",                      "ra":255.657, "dec":-26.268, "mag": 7.5, "maj":17.0,   "min":17.0,   "pa":  0, "type":2},
    {"id":"M22",     "name":"Sagittarius Cluster",   "ra":279.100, "dec":-23.903, "mag": 5.1, "maj":32.0,   "min":32.0,   "pa":  0, "type":2},
    {"id":"M28",     "name":"",                      "ra":276.137, "dec":-24.870, "mag": 7.7, "maj":11.0,   "min":11.0,   "pa":  0, "type":2},
    {"id":"M30",     "name":"",                      "ra":325.093, "dec":-23.179, "mag": 7.5, "maj":12.0,   "min":12.0,   "pa":  0, "type":2},
    {"id":"M53",     "name":"",                      "ra":198.230, "dec": 18.168, "mag": 7.7, "maj":14.0,   "min":14.0,   "pa":  0, "type":2},
    {"id":"M54",     "name":"",                      "ra":283.763, "dec":-30.478, "mag": 7.7, "maj":12.0,   "min":12.0,   "pa":  0, "type":2},
    {"id":"M55",     "name":"",                      "ra":294.998, "dec":-30.962, "mag": 6.3, "maj":19.0,   "min":19.0,   "pa":  0, "type":2},
    {"id":"M56",     "name":"",                      "ra":289.148, "dec": 30.185, "mag": 8.4, "maj": 9.0,   "min": 9.0,   "pa":  0, "type":2},
    {"id":"M62",     "name":"",                      "ra":255.303, "dec":-30.113, "mag": 6.5, "maj":15.0,   "min":15.0,   "pa":  0, "type":2},
    {"id":"M68",     "name":"",                      "ra":189.867, "dec":-26.745, "mag": 8.0, "maj":12.0,   "min":12.0,   "pa":  0, "type":2},
    {"id":"M69",     "name":"",                      "ra":277.846, "dec":-32.348, "mag": 7.7, "maj":10.0,   "min":10.0,   "pa":  0, "type":2},
    {"id":"M70",     "name":"",                      "ra":280.803, "dec":-32.292, "mag": 8.0, "maj": 8.0,   "min": 8.0,   "pa":  0, "type":2},
    {"id":"M71",     "name":"",                      "ra":298.443, "dec": 18.779, "mag": 8.2, "maj": 7.0,   "min": 7.0,   "pa":  0, "type":2},
    {"id":"M72",     "name":"",                      "ra":313.365, "dec":-12.537, "mag": 9.3, "maj": 6.0,   "min": 6.0,   "pa":  0, "type":2},
    {"id":"M75",     "name":"",                      "ra":301.521, "dec":-21.922, "mag": 8.6, "maj": 6.0,   "min": 6.0,   "pa":  0, "type":2},
    {"id":"M79",     "name":"",                      "ra": 81.044, "dec":-24.524, "mag": 8.0, "maj":10.0,   "min":10.0,   "pa":  0, "type":2},
    {"id":"M80",     "name":"",                      "ra":244.260, "dec":-22.975, "mag": 7.2, "maj":10.0,   "min":10.0,   "pa":  0, "type":2},
    {"id":"M92",     "name":"",                      "ra":259.281, "dec": 43.136, "mag": 6.5, "maj":14.0,   "min":14.0,   "pa":  0, "type":2},
    {"id":"M107",    "name":"",                      "ra":248.133, "dec":-13.054, "mag": 8.0, "maj":13.0,   "min":13.0,   "pa":  0, "type":2},
    {"id":"NGC 104", "name":"47 Tucanae",            "ra":  6.022, "dec":-72.081, "mag": 4.9, "maj":50.0,   "min":50.0,   "pa":  0, "type":2},
    {"id":"NGC 5139","name":"Omega Centauri",        "ra":201.698, "dec":-47.480, "mag": 3.9, "maj":55.0,   "min":55.0,   "pa":  0, "type":2},
    {"id":"NGC 362", "name":"",                      "ra": 15.809, "dec":-70.849, "mag": 6.6, "maj":13.0,   "min":13.0,   "pa":  0, "type":2},
    {"id":"NGC 6752","name":"",                      "ra":287.716, "dec":-59.982, "mag": 5.4, "maj":20.0,   "min":20.0,   "pa":  0, "type":2},
    {"id":"NGC 6397","name":"",                      "ra":265.176, "dec":-53.674, "mag": 5.7, "maj":26.0,   "min":26.0,   "pa":  0, "type":2},
    # ── Emission nebulae ──────────────────────────────────────────────────────
    {"id":"M8",      "name":"Lagoon Nebula",         "ra":270.904, "dec":-24.387, "mag": 6.0, "maj":90.0,   "min":40.0,   "pa": 90, "type":3},
    {"id":"M16",     "name":"Eagle Nebula",          "ra":274.700, "dec":-13.790, "mag": 6.4, "maj":35.0,   "min":28.0,   "pa":  0, "type":3},
    {"id":"M17",     "name":"Omega Nebula",          "ra":275.108, "dec":-16.177, "mag": 6.0, "maj":46.0,   "min":37.0,   "pa":  0, "type":3},
    {"id":"M42",     "name":"Orion Nebula",          "ra": 83.822, "dec": -5.391, "mag": 4.0, "maj":65.0,   "min":60.0,   "pa":  0, "type":3},
    {"id":"M43",     "name":"De Mairan's Nebula",    "ra": 83.880, "dec": -5.267, "mag": 9.0, "maj":20.0,   "min":15.0,   "pa":  0, "type":3},
    {"id":"NGC 3372","name":"Eta Carinae Nebula",    "ra":160.950, "dec":-59.867, "mag": 1.0, "maj":120.0,  "min":120.0,  "pa":  0, "type":3},
    {"id":"NGC 2070","name":"Tarantula Nebula",      "ra": 84.658, "dec":-69.100, "mag": 5.0, "maj":40.0,   "min":25.0,   "pa":  0, "type":3},
    {"id":"NGC 7000","name":"North America Nebula",  "ra":314.700, "dec": 44.333, "mag": 4.0, "maj":120.0,  "min":100.0,  "pa":  0, "type":3},
    {"id":"NGC 2237","name":"Rosette Nebula",        "ra": 98.225, "dec":  4.867, "mag": 9.0, "maj":80.0,   "min":60.0,   "pa":  0, "type":3},
    {"id":"NGC 6334","name":"Cat's Paw Nebula",      "ra":260.113, "dec":-35.972, "mag": 9.0, "maj":35.0,   "min":20.0,   "pa":  0, "type":3},
    {"id":"NGC 6618","name":"",                      "ra":275.100, "dec":-16.183, "mag": 9.0, "maj":20.0,   "min":15.0,   "pa":  0, "type":3},
    {"id":"IC 1805", "name":"Heart Nebula",          "ra": 38.175, "dec": 61.450, "mag": 7.0, "maj":60.0,   "min":60.0,   "pa":  0, "type":3},
    {"id":"NGC 1499","name":"California Nebula",     "ra": 60.175, "dec": 36.417, "mag": 5.0, "maj":160.0,  "min":40.0,   "pa": 30, "type":3},
    {"id":"NGC 2024","name":"Flame Nebula",          "ra": 85.429, "dec": -1.850, "mag":10.0, "maj":30.0,   "min":30.0,   "pa":  0, "type":3},
    # ── Mixed emission+reflection ─────────────────────────────────────────────
    {"id":"M20",     "name":"Trifid Nebula",         "ra":270.596, "dec":-23.030, "mag": 6.3, "maj":28.0,   "min":28.0,   "pa":  0, "type":7},
    # ── Reflection nebulae ────────────────────────────────────────────────────
    {"id":"M78",     "name":"",                      "ra": 86.691, "dec":  0.050, "mag": 8.3, "maj": 8.0,   "min": 6.0,   "pa":  0, "type":6},
    # ── Planetary nebulae ─────────────────────────────────────────────────────
    {"id":"M27",     "name":"Dumbbell Nebula",       "ra":299.901, "dec": 22.721, "mag": 7.4, "maj": 8.0,   "min": 5.6,   "pa": 30, "type":4},
    {"id":"M57",     "name":"Ring Nebula",           "ra":283.396, "dec": 33.029, "mag": 8.8, "maj": 1.4,   "min": 1.0,   "pa":  0, "type":4},
    {"id":"M76",     "name":"Little Dumbbell",       "ra": 25.583, "dec": 51.576, "mag":10.1, "maj": 2.7,   "min": 1.8,   "pa": 45, "type":4},
    {"id":"M97",     "name":"Owl Nebula",            "ra":168.699, "dec": 55.019, "mag": 9.9, "maj": 3.4,   "min": 3.4,   "pa":  0, "type":4},
    {"id":"NGC 7293","name":"Helix Nebula",          "ra":337.411, "dec":-20.837, "mag": 7.3, "maj":16.0,   "min":12.0,   "pa":  0, "type":4},
    {"id":"NGC 3132","name":"Eight-Burst Nebula",    "ra":151.757, "dec":-40.436, "mag": 8.2, "maj": 1.5,   "min": 1.0,   "pa":  0, "type":4},
    {"id":"NGC 6543","name":"Cat's Eye Nebula",      "ra":269.639, "dec": 66.633, "mag": 8.1, "maj": 0.33,  "min": 0.33,  "pa":  0, "type":4},
    {"id":"NGC 7662","name":"Blue Snowball",         "ra":350.905, "dec": 42.545, "mag": 8.3, "maj": 0.5,   "min": 0.5,   "pa":  0, "type":4},
    {"id":"NGC 2392","name":"Eskimo Nebula",         "ra":112.291, "dec": 20.912, "mag": 9.2, "maj": 0.8,   "min": 0.8,   "pa":  0, "type":4},
    # ── Galaxies ──────────────────────────────────────────────────────────────
    {"id":"M31",     "name":"Andromeda Galaxy",      "ra": 10.685, "dec": 41.269, "mag": 3.4, "maj":178.0,  "min": 63.0,  "pa": 35, "type":0},
    {"id":"M32",     "name":"M32",                   "ra": 10.674, "dec": 40.866, "mag": 8.7, "maj": 8.0,   "min": 6.0,   "pa":170, "type":0},
    {"id":"M33",     "name":"Triangulum Galaxy",     "ra": 23.462, "dec": 30.660, "mag": 5.7, "maj": 73.0,  "min": 45.0,  "pa": 23, "type":0},
    {"id":"M49",     "name":"",                      "ra":187.444, "dec":  8.001, "mag": 8.4, "maj": 9.0,   "min": 7.5,   "pa":155, "type":0},
    {"id":"M51",     "name":"Whirlpool Galaxy",      "ra":202.469, "dec": 47.195, "mag": 8.4, "maj":11.0,   "min": 7.0,   "pa":  0, "type":0},
    {"id":"M58",     "name":"",                      "ra":189.431, "dec": 11.819, "mag": 9.7, "maj": 5.9,   "min": 4.7,   "pa":  0, "type":0},
    {"id":"M60",     "name":"",                      "ra":190.917, "dec": 11.553, "mag": 8.8, "maj": 7.6,   "min": 6.2,   "pa":  0, "type":0},
    {"id":"M63",     "name":"Sunflower Galaxy",      "ra":198.955, "dec": 42.029, "mag": 8.6, "maj":12.6,   "min": 7.2,   "pa":105, "type":0},
    {"id":"M64",     "name":"Black Eye Galaxy",      "ra":194.182, "dec": 21.683, "mag": 8.5, "maj":10.0,   "min": 5.0,   "pa": 65, "type":0},
    {"id":"M65",     "name":"",                      "ra":169.733, "dec": 13.092, "mag": 9.3, "maj": 9.8,   "min": 2.9,   "pa":171, "type":0},
    {"id":"M66",     "name":"",                      "ra":170.062, "dec": 12.992, "mag": 9.0, "maj": 9.1,   "min": 4.2,   "pa":173, "type":0},
    {"id":"M74",     "name":"Phantom Galaxy",        "ra": 24.174, "dec": 15.784, "mag": 9.4, "maj":10.5,   "min": 9.5,   "pa":  0, "type":0},
    {"id":"M77",     "name":"",                      "ra": 40.670, "dec": -0.013, "mag": 8.9, "maj": 7.0,   "min": 6.0,   "pa":  0, "type":0},
    {"id":"M81",     "name":"Bode's Galaxy",         "ra":148.888, "dec": 69.065, "mag": 6.9, "maj":26.9,   "min":14.1,   "pa":157, "type":0},
    {"id":"M82",     "name":"Cigar Galaxy",          "ra":148.967, "dec": 69.680, "mag": 8.4, "maj":11.2,   "min": 4.3,   "pa": 65, "type":0},
    {"id":"M83",     "name":"Southern Pinwheel",     "ra":204.254, "dec":-29.866, "mag": 7.6, "maj":12.9,   "min":11.5,   "pa": 45, "type":0},
    {"id":"M84",     "name":"",                      "ra":186.266, "dec": 12.887, "mag": 9.1, "maj": 6.5,   "min": 5.6,   "pa":  0, "type":0},
    {"id":"M86",     "name":"",                      "ra":186.550, "dec": 12.946, "mag": 8.9, "maj": 8.9,   "min": 5.8,   "pa":  0, "type":0},
    {"id":"M87",     "name":"Virgo A",               "ra":187.706, "dec": 12.391, "mag": 8.6, "maj": 8.3,   "min": 6.6,   "pa":  0, "type":0},
    {"id":"M94",     "name":"",                      "ra":192.721, "dec": 41.120, "mag": 8.2, "maj":11.0,   "min": 9.0,   "pa":  0, "type":0},
    {"id":"M96",     "name":"",                      "ra":161.694, "dec": 11.820, "mag": 9.2, "maj": 7.8,   "min": 5.2,   "pa":  5, "type":0},
    {"id":"M101",    "name":"Pinwheel Galaxy",       "ra":210.803, "dec": 54.349, "mag": 7.9, "maj":28.8,   "min":26.9,   "pa":  0, "type":0},
    {"id":"M104",    "name":"Sombrero Galaxy",       "ra":189.998, "dec":-11.623, "mag": 8.0, "maj": 8.7,   "min": 3.5,   "pa": 90, "type":0},
    {"id":"M106",    "name":"",                      "ra":184.739, "dec": 47.304, "mag": 8.4, "maj":18.6,   "min": 7.2,   "pa":150, "type":0},
    {"id":"M108",    "name":"",                      "ra":167.879, "dec": 55.674, "mag":10.0, "maj": 8.7,   "min": 2.2,   "pa": 79, "type":0},
    {"id":"M110",    "name":"M110",                  "ra": 10.092, "dec": 41.690, "mag": 8.1, "maj":19.5,   "min":11.5,   "pa":170, "type":0},
    {"id":"NGC 5128","name":"Centaurus A",           "ra":201.365, "dec":-43.019, "mag": 6.8, "maj":25.7,   "min":20.0,   "pa": 35, "type":0},
    {"id":"LMC",     "name":"Large Magellanic Cloud","ra": 80.894, "dec":-69.756, "mag": 0.9, "maj":650.0,  "min":550.0,  "pa":  0, "type":0},
    {"id":"SMC",     "name":"Small Magellanic Cloud","ra": 13.187, "dec":-72.829, "mag": 2.7, "maj":320.0,  "min":185.0,  "pa": 45, "type":0},
]

# ── Milky Way cloud data ──────────────────────────────────────────────────────
# IAU galactic coordinate transformation to J2000 equatorial
RA_NGP  = math.radians(192.859508)   # RA of North Galactic Pole
DEC_NGP = math.radians(27.128336)    # Dec of NGP
L_NCP   = math.radians(122.932)      # Galactic longitude of North Celestial Pole

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

# Brightness profile along the galactic plane (empirical, matches photographic appearance)
def mw_brightness(l):
    l = l % 360
    lr = math.radians(l)
    # Galactic center bulge (l=0, b=0 is brightest region)
    l_c = l if l < 180 else 360 - l   # distance from GC in degrees
    gc  = math.exp(-(l_c / 48)**2) * 1.00
    # Scutum-Centaurus arm peak ~l=30
    scu = math.exp(-((l -  30) / 22)**2) * 0.78
    # Cygnus arm peak ~l=80
    cyg = math.exp(-((l -  80) / 18)**2) * 0.72
    # Perseus arm ~l=140
    per = math.exp(-((l - 140) / 28)**2) * 0.45
    # Vela / Puppis ~l=255
    vel = math.exp(-((l - 255) / 22)**2) * 0.58
    # Centaurus arm ~l=310
    cen = math.exp(-((l - 310) / 22)**2) * 0.82
    # Norma/Scorpius ~l=330
    nor = math.exp(-((l - 330) / 20)**2) * 0.88
    return max(0.18, gc + scu + cyg + per + vel + cen + nor)

# Width profile (half-width in degrees)
def mw_half_width(l):
    l = l % 360
    l_c = l if l < 180 else 360 - l
    base = 5.5 + 11.0 * math.exp(-(l_c / 55)**2)   # wider at GC
    # Cygnus is also wider
    cyg_w = 3.5 * math.exp(-((l - 80) / 25)**2)
    return min(base + cyg_w, 20.0)

MW_CLOUDS = []

# Main galactic plane — sample every 3 degrees
for l_int in range(0, 360, 3):
    l = float(l_int)
    bri = mw_brightness(l)
    hw  = mw_half_width(l)
    # Plane point
    ra, dec = gal_to_eq(l, 0.0)
    MW_CLOUDS.append([round(ra, 2), round(dec, 2), round(hw * 0.90, 1), round(bri, 3)])
    # Upper/lower halo layers  at b = ±hw/2 and ±hw
    for boff_frac in [0.45, 0.85]:
        for sign in [1, -1]:
            b = sign * hw * boff_frac
            scale = math.exp(-(boff_frac * 1.4)**2)
            ra2, dec2 = gal_to_eq(l, b)
            MW_CLOUDS.append([round(ra2, 2), round(dec2, 2),
                              round(hw * 0.55, 1), round(bri * scale * 0.55, 3)])

# Galactic center extra bulge detail
for dl in range(-20, 21, 5):
    for db in range(-15, 16, 5):
        bri_c = 0.95 * math.exp(-(dl/25)**2 - (db/18)**2)
        if bri_c < 0.05: continue
        ra, dec = gal_to_eq(dl % 360, db)
        MW_CLOUDS.append([round(ra, 2), round(dec, 2), 4.5, round(bri_c, 3)])

# ── Emit JS ───────────────────────────────────────────────────────────────────
out = []
out.append("// AUTO-GENERATED by gen_dso.py")
out.append(f"// {len(DSOs)} deep-sky objects · Messier + key NGC/IC · J2000")
out.append(f"// {len(MW_CLOUDS)} Milky Way cloud points · IAU galactic coordinates")
out.append("")

# SG_DSO_NAMES
names = {}
for i, d in enumerate(DSOs):
    cname = d["name"]
    label = d["id"] + (" · " + cname if cname else "")
    names[i] = label
out.append("var SG_DSO_NAMES={")
for i, label in names.items():
    safe = label.replace('"', '\\"')
    out.append(f'  {i}:"{safe}",')
out.append("};")
out.append("")

# SG_DSO_DATA  stride-8: ra,dec,vmag,maj,min,pa,type,nameIdx
out.append("var SG_DSO_DATA=[")
for i, d in enumerate(DSOs):
    out.append(f"  {d['ra']},{d['dec']},{d['mag']},{d['maj']},{d['min']},{d['pa']},{d['type']},{i},")
out.append("];")
out.append("")

# SG_MW_DATA  stride-4: ra,dec,halfWidthDeg,brightness
out.append("var SG_MW_DATA=[")
COLS = 6  # cloud points per line
for i in range(0, len(MW_CLOUDS), COLS):
    chunk = MW_CLOUDS[i:i+COLS]
    line = ",".join(f"{p[0]},{p[1]},{p[2]},{p[3]}" for p in chunk)
    out.append(f"  {line},")
out.append("];")
out.append("")

sys.stdout.write("\n".join(out))
print(f"\nDone — {len(DSOs)} DSOs, {len(MW_CLOUDS)} MW cloud points.", file=sys.stderr)
