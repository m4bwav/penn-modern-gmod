"""Side-by-side sheet: each screenshot beside the reference photo from about the same viewpoint.
Usage: python tools/compare.py shots/<stamp> [set]  -> shots/<stamp>/compare.jpg (compare_<set>.jpg)"""
import os
import sys
from PIL import Image, ImageDraw

PAIRS = {  # shot -> refs/photos file (Moynihan Train Hall, Commons, refs/SOURCES.md)
    "hall_west": "Moynihan_Train_Hall_viewed_from_center_of_floor_Dec_27_2022.jpg",
    "hall_up": "The_92_Foot_High_Skylight_supported_by_the_original_steel_tr.jpg",
    "side_south": "Moynihan_Train_Hall_interior_Dec_27_2022.jpg",
}
LIRR = {  # LIRR concourse (area 2)
    "lirr_west": "Penn_Station_LIRR_concourse_renovated_high_ceiling.jpg",
    "pavilion": "LIRR_Penn_Station_2025a.jpg",
    "lirr_east": "Penn_Station_LIRR_concourse_2.jpg",
}
SETS = {"lirr": LIRR}  # later areas add their sets here
d, W, H = sys.argv[1], 640, 400
lower = sys.argv[2:3] and sys.argv[2]
if lower:
    if lower not in SETS:
        raise SystemExit(f"unknown set {lower!r}; known: {', '.join(SETS)}")
    PAIRS = SETS[lower]
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
