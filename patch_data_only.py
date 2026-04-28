"""Re-embeds star_data_v2.js into index.html (data block only)."""
import sys

HTML = r"C:\Users\Owner\anya.github.io\index.html"
DATA = r"C:\Users\Owner\anya.github.io\star_data_v2.js"

html = open(HTML, encoding="utf-8").read()
data = open(DATA, encoding="utf-8").read().strip()

start = "var SG_STAR_DATA=["
end   = "var SG_CONSTELLATIONS=["

si = html.find(start)
ei = html.find(end)
if si == -1 or ei == -1:
    sys.exit("Markers not found")

cons_end = html.find("];\n", ei) + 3
html = html[:si] + data + "\n" + html[cons_end:]

# Update tagline count
html = html.replace("1,638 real stars.", "1,637 real stars.")

open(HTML, "w", encoding="utf-8").write(html)
print(f"Done — {len(html):,} chars", file=sys.stderr)
