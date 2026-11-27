"""Contact sheet of stock HL2 materials: python tools/texsheet.py out.jpg <regex> [more regexes]."""
import io
import re
import sys

from PIL import Image, ImageDraw
from srctools.keyvalues import Keyvalues
from srctools.vpk import VPK
from srctools.vtf import VTF

G = "D:/SteamLibrary/steamapps/common/GarrysMod/sourceengine/"
paks = [VPK(G + "hl2_misc_dir.vpk"), VPK(G + "hl2_textures_dir.vpk")]


def find(path):
    for p in paks:
        if path in p:
            return p[path].read()
    return None


out, pats = sys.argv[1], [re.compile(x, re.I) for x in sys.argv[2:]]
names = sorted({f.filename for p in paks for f in p
                if f.filename.endswith(".vmt") and any(r.search(f.filename) for r in pats)})
tiles = []
for n in names:
    try:
        kv = Keyvalues.parse(find(n).decode("latin-1"))
        mat = next(iter(kv))
        base = mat["$basetexture", None]
        if not base:
            continue
        raw = find("materials/" + base.replace("\\", "/").lower() + ".vtf")
        img = VTF.read(io.BytesIO(raw)).get().to_PIL().convert("RGB").resize((160, 160))
        tiles.append((n[10:-4], img))
    except Exception as e:
        print("skip", n, e)
cols = 8
sheet = Image.new("RGB", (cols * 170, ((len(tiles) + cols - 1) // cols) * 185), "black")
d = ImageDraw.Draw(sheet)
for i, (n, img) in enumerate(tiles):
    x, y = (i % cols) * 170, (i // cols) * 185
    sheet.paste(img, (x + 5, y + 5))
    d.text((x + 5, y + 168), n[-26:], fill="white")
sheet.save(out, quality=85)
print(len(tiles), "tiles")
