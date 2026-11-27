"""Side-by-side sheet: each screenshot beside the reference photo from about the same viewpoint.
Usage: python tools/compare.py shots/<stamp> [set]  -> shots/<stamp>/compare.jpg (compare_<set>.jpg)"""
import os
import sys
from PIL import Image, ImageDraw

PAIRS = {  # shot -> refs/photos file (HABS NY-5471, waiting room)
    "from_sw": "WAITING_ROOM_FROM_SOUTHWEST_Pennsylvania_Station.jpg",
    "from_nw": "WAITING_ROOM_FROM_NORTHWEST_Pennsylvania_Station.jpg",
    "stair_east": "STAIRWAY_FROM_WAITING_ROOM_TO_ARCADE_Pennsylvania_Station.jpg",
}
LOWER, PLAT, CHAMBERS = {}, {}, {}  # later areas add their pairs here
d, W, H = sys.argv[1], 640, 400
lower = sys.argv[2:3] and sys.argv[2]
if lower:
    PAIRS = {"lower": LOWER, "plat": PLAT, "chambers": CHAMBERS}[lower]
PAIRS = {k: v for k, v in PAIRS.items() if os.path.exists(f"{d}/{k}.jpg")}  # shots.sh CAMS= may shoot only some
sheet = Image.new("RGB", (W * 2, (H + 18) * len(PAIRS)))
draw = ImageDraw.Draw(sheet)
for i, (shot, ref) in enumerate(PAIRS.items()):
    for j, path in enumerate((f"{d}/{shot}.jpg", f"refs/photos/{ref}")):
        im = Image.open(path).convert("RGB")
        im.thumbnail((W, H))
        sheet.paste(im, (j * W, i * (H + 18)))
        draw.text((j * W + 4, i * (H + 18) + H + 3), path, fill="white")
out = f"{d}/compare_{lower}.jpg" if lower else f"{d}/compare.jpg"
sheet.save(out, quality=85)
print(out)
