"""Procedural waiting-room materials, tones judged by eye from the HABS photos
(refs/photos/WAITING_ROOM_FROM_SOUTHWEST..., NORTHWEST...): warm grey travertine ashlar,
a coffered vault of round coffers in square frames, pale travertine floor slabs.
Writes src/materials/pennmodern/<name>.vtf + .vmt and previews in shots/tex/.
Needs pip srctools pillow numpy."""
from pathlib import Path

import numpy as np
from PIL import Image
from srctools import vtf

N = 512
ROOT = Path(__file__).resolve().parent.parent
MAT = ROOT / "src" / "materials" / "pennmodern"
rng = np.random.default_rng(1910)


def fbm(n, octaves=5):
    # Seamless fbm: tile each random grid 3x3, resize, keep the middle tile.
    out = np.zeros((n, n))
    for o in range(octaves):
        k = 3 * 2**o
        g = np.tile(rng.random((k, k)), (3, 3))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((3*n, 3*n), Image.BICUBIC)
        out += (np.asarray(img, float)[n:2*n, n:2*n] / 255 - .5) / 2**o
    return out


def save(img, name, surf="stone"):
    rgb = np.clip(img, 0, 255).astype(np.uint8)
    (ROOT / "shots" / "tex").mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(ROOT / "shots" / "tex" / f"{name}.png")
    tex = vtf.VTF(N, N, fmt=vtf.ImageFormats.RGB888)
    tex.get().copy_from(np.dstack([rgb, np.full((N, N), 255, np.uint8)]).tobytes(), vtf.ImageFormats.RGBA8888)
    tex.compute_mipmaps()
    MAT.mkdir(parents=True, exist_ok=True)
    with open(MAT / f"{name}.vtf", "wb") as f:
        tex.save(f)
    (MAT / f"{name}.vmt").write_text('"LightmappedGeneric"\n{\n\t"$basetexture" "pennmodern/%s"\n\t"$surfaceprop" "%s"\n}\n'
                                     % (name, surf), encoding="ascii", newline="\n")
    print("wrote", name)


def pits(img, count, tone):
    # Travertine voids: small dark elongated pits along the bedding.
    y, x = np.mgrid[0:N, 0:N]
    for _ in range(count):
        cx, cy = rng.integers(0, N, 2)
        rx, ry = rng.uniform(2, 7), rng.uniform(0.8, 1.8)
        d = ((x - cx + N/2) % N - N/2)**2 / rx**2 + ((y - cy + N/2) % N - N/2)**2 / ry**2
        img[d < 1] *= tone
    return img


TRAV = np.array([122, 112, 98], float)   # session 5: photos read mid-grey, darker than 150
yy, xx = np.mgrid[0:N, 0:N]
bed = np.sin(yy / N * 2*np.pi * 18 + fbm(N, 4) * 6)

# Ashlar: 4 courses x 2 blocks per tile, half-block offset, thin light joints, horizontal bedding.
img = np.zeros((N, N, 3))
ch, bw = N // 4, N // 2
for c in range(4):
    off = (bw // 2) * (c % 2)
    for b in range(3):
        x0, x1 = max(0, b*bw - off), min(N, (b+1)*bw - off)
        if x1 > x0:
            img[c*ch:(c+1)*ch, x0:x1] = TRAV * (1 + rng.uniform(-.05, .05)) * [1, 1 + rng.uniform(-.02, .02), 1 + rng.uniform(-.04, .02)]
img *= (1 + fbm(N, 6) * 0.10 + bed * 0.025)[..., None]
img = pits(img, 260, 0.78)
for c in range(4):
    img[c*ch:c*ch+3] = img[c*ch:c*ch+3] * 0.55 + TRAV * 1.1 * 0.45
    off = (bw // 2) * (c % 2)
    for b in range(3):
        x = (b*bw - off) % N
        img[c*ch:(c+1)*ch, x:x+3] = img[c*ch:(c+1)*ch, x:x+3] * 0.55 + TRAV * 1.1 * 0.45
save(img, "travertine_ashlar")

# Plain dressed travertine for trim, entablature and pedestals: no joints.
img = TRAV * 1.05 * (1 + fbm(N, 6) * 0.08 + bed * 0.02)[..., None]
save(pits(img, 160, 0.8), "travertine")

# Vault: round coffers in octagonal frames on a diagonal lattice (session 5, matching the
# HABS photos), four per tile at the square corners and centre, rosette in each.
PLAS = np.array([170, 160, 144], float)
img = PLAS * (1 + fbm(N, 5) * 0.06)[..., None]
cell = N // 2
u, w = (xx + cell/2) % cell - cell/2, (yy + cell/2) % cell - cell/2
u2, w2 = xx % cell - cell/2, yy % cell - cell/2
pick = np.hypot(u, w) > np.hypot(u2, w2)
u, w = np.where(pick, u2, u), np.where(pick, w2, w)
r = np.hypot(u, w)
octo = np.maximum(np.maximum(abs(u), abs(w)), (abs(u) + abs(w)) / np.sqrt(2))
shade = np.ones_like(r)
shade = np.where(octo < 84, 0.86, shade)              # octagonal frame, first step
shade = np.where(r < 70, 0.62, shade)                 # deep round coffer
shade = np.where((r < 70) & (r > 62), 0.78, shade)
shade = np.where((r < 62) & (r > 55), 0.9, shade)
shade = np.where((octo >= 84) & (octo < 90), 1.12, shade)  # lit rib edge
img *= shade[..., None]
img[(r < 70) & (w < -0.3 * r)] *= 0.9                # top lip casts shadow downward
ros = np.clip((16 - r) / 4, 0, 1) * (0.8 + 0.2 * np.cos(np.arctan2(w, u) * 8))
img = img * (1 - ros[..., None]) + PLAS * 1.15 * ros[..., None]
save(img, "vault_coffer", "plaster")

# Floor: 2x2 pale travertine slabs with dark joints.
FL = np.array([168, 160, 146], float)
img = np.zeros((N, N, 3))
for i in range(2):
    for j in range(2):
        img[i*cell:(i+1)*cell, j*cell:(j+1)*cell] = FL * (1 + rng.uniform(-.04, .04))
img *= (1 + fbm(N, 6) * 0.08 + bed * 0.015)[..., None]
img = pits(img, 120, 0.85)
for k in (0, cell):
    img[k:k+2] *= 0.6
    img[:, k:k+2] *= 0.6
save(img, "floor_travertine")
