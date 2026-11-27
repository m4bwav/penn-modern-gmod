"""Rough top-down plan of gm_penn_modern from the VMF: brushes at chest height on the hall floor
(z 0) dark, on the Amtrak concourse (z -20 ft) green, on the West End Concourse below (z -30 ft) blue, the escalator clips grey, plus the
spawn and labels. +x (east, toward Eighth Avenue) to the right, +y (north) up.

python tools/make_map.py [out.png]
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VMF = Path(__file__).resolve().parent.parent / "src" / "gm_penn_modern.vmf"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/level-map.png")
FT = 12
LEVELS = ((0, (70, 62, 56)), (-30 * FT, (60, 110, 170)))
txt = VMF.read_text()
hall, lower, amtrak, clip = [], [], [], []
for blk in re.split(r"(?m)^\s*solid$", txt)[1:]:
    blk = re.split(r"(?m)^\s*(?:entity|editor)$", blk)[0]
    pts = [tuple(map(float, p)) for p in re.findall(r"\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)", blk)]
    tex = [t.lower() for t in re.findall(r'"material" "([^"]+)"', blk)]
    if not pts or all("skybox" in t or "nodraw" in t for t in tex):
        continue
    xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    r = (min(xs), min(ys), max(xs), max(ys))
    if any("playerclip" in t for t in tex):
        clip.append(r)
    elif min(zs) <= 48 <= max(zs) and max(zs) - min(zs) < 2000 or min(zs) <= 48 < max(zs) and (r[2] - r[0] < 200 or r[3] - r[1] < 200):
        hall.append(r)
    elif min(zs) <= -30 * FT + 48 <= max(zs):
        lower.append(r)
    elif min(zs) <= -20 * FT and -20 * FT + 48 <= max(zs):
        amtrak.append(r)
spawn = [(float(x), float(y)) for x, y in re.findall(r'info_player_start"[^}]*?"origin" "([-\d.]+) ([-\d.]+)', txt, re.S)]
allr = hall + lower + amtrak
x0, y0 = min(r[0] for r in allr), min(r[1] for r in allr)
x1, y1 = max(r[2] for r in allr), max(r[3] for r in allr)
W = 1600; s = (W - 120) / (x1 - x0)
H = int((y1 - y0) * s) + 260
img = Image.new("RGB", (W, H), (244, 242, 236)); d = ImageDraw.Draw(img)
try: f, fb = ImageFont.truetype("arial.ttf", 22), ImageFont.truetype("arialbd.ttf", 34)
except OSError: f = fb = ImageFont.load_default()
P = lambda x, y: (60 + (x - x0) * s, 170 + (y1 - y) * s)
for g in range(0, int((x1 - x0) / FT) + 1, 50):
    X = P(x0 + g * FT, 0)[0]; d.line((X, 160, X, H - 70), fill=(220, 216, 206))
def rect(r, fill):
    a, b = P(r[0], r[3]), P(r[2], r[1]); d.rectangle((a[0], a[1], b[0], b[1]), fill=fill)
for r in lower: rect(r, LEVELS[1][1])
for r in amtrak: rect(r, (70, 140, 90))
for r in clip: rect(r, (175, 175, 175))
for r in hall: rect(r, LEVELS[0][1])
for x, y in spawn:
    cx, cy = P(x, y); d.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(200, 40, 40)); d.text((cx+14, cy-12), "spawn", fill=(200, 40, 40), font=f)
for lbl, x, y in (("Moynihan Train Hall", 0, 520), ("Escalators down", 0, 0), ("Stairs to balcony", -700, -640),
                  ("Side hall and shops (balcony over)", 300, -800), ("Side hall and shops", 300, 800),
                  ("West End Concourse below (blue)", 0, -420), ("Under Eighth Avenue", 1620, 330), ("LIRR concourse (blue)", 3000, 250),
                  ("33rd St pavilion, escalator up", 4800, -500), ("Amtrak concourse (green)", 3440, -1100),
                  ("Stair up from LIRR", 3024, -540), ("Waiting room", 2360, -2230), ("Escalator to tracks", 4036, -1760)):
    cx, cy = P(x, y); w = d.textlength(lbl, font=f); d.rectangle((cx-w/2-6, cy-16, cx+w/2+6, cy+14), fill=(255, 255, 255)); d.text((cx-w/2, cy-13), lbl, fill=(30, 30, 30), font=f)
d.text((60, 30), "gm_penn_modern: rough plan", fill=(30, 30, 30), font=fb)
d.text((60, 78), f"dark = hall level at chest height, green = Amtrak 20 ft below, blue = concourses 30 ft below, grey = escalators   |   grid 50 ft   |   {round((x1-x0)/FT)} x {round((y1-y0)/FT)} ft   |   N up", fill=(80, 80, 80), font=f)
d.text((60, H-45), "Generated from src/gm_penn_modern.vmf by tools/make_map.py", fill=(120, 120, 120), font=f)
OUT.parent.mkdir(parents=True, exist_ok=True); img.save(OUT); print("wrote", OUT, len(hall), len(lower), len(clip))
