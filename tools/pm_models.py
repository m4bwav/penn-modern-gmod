"""Penn Station props as MDL, built with make_models.Mesh and Garry's Mod's studiomdl.

    python tools/pm_models.py      # writes src/modelsrc/, compiles into src/models/pennmodern/

Models do not count against vbsp's 65,536 unique-vertex cap, so the waiting room's giant
fluted Corinthian columns live here. Origin of each column is the top of its pedestal.
"""
import math
import os
import shutil
import subprocess
from pathlib import Path

from make_models import Mesh

ROOT = Path(__file__).resolve().parent.parent
G = Path(os.environ.get("GMOD", "D:/SteamLibrary/steamapps/common/GarrysMod"))
SRC = ROOT / "src" / "modelsrc"
MAT = ROOT / "src" / "materials" / "models" / "pennmodern"
FT = 12
COL_H = 60 * FT          # base to abacus top, matches build_vmf.py COL_TOP - PED
COL_R = 42               # shaft radius at the base (7 ft diameter)

VMTS = {
    "travertine": '"VertexLitGeneric"\n{\n\t"$basetexture" "pennmodern/travertine"\n\t"$surfaceprop" "stone"\n}\n',
}


def fluted(m, mat, r0, r1, z0, z1, flutes=24, depth=4, rings=6):
    """Tapered shaft with concave flutes: each flute is 4 facets dipping to `depth`."""
    n = flutes * 4
    dip = [0, depth * 0.7, depth, depth * 0.7]
    for k in range(rings):
        za, zb = z0 + (z1 - z0) * k / rings, z0 + (z1 - z0) * (k + 1) / rings
        ra, rb = r0 + (r1 - r0) * k / rings, r0 + (r1 - r0) * (k + 1) / rings
        for j in range(n):
            t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            d0, d1 = dip[j % 4], dip[(j + 1) % 4]
            def v(r, d, z, t, u):
                return ((math.cos(t) * (r - d), math.sin(t) * (r - d), z),
                        (math.cos(t), math.sin(t), 0), (u, z / 128.0))
            m.quad(mat, v(ra, d0, za, t0, j / n * 4), v(ra, d1, za, t1, (j + 1) / n * 4),
                   v(rb, d1, zb, t1, (j + 1) / n * 4), v(rb, d0, zb, t0, j / n * 4))


def corinthian():
    m = Mesh()
    rt = COL_R * 0.86                       # entasis: shaft narrows to the top
    cap_h = 8 * FT
    shaft_top = COL_H - cap_h
    # Attic base: plinth ring, lower torus, scotia, upper torus, fillet.
    m.lathe("travertine", [(0, 0), (COL_R + 14, 0), (COL_R + 14, 10), (COL_R + 12, 12), (COL_R + 14, 18),
                           (COL_R + 10, 24), (COL_R + 4, 26), (COL_R + 4, 30), (COL_R + 9, 33),
                           (COL_R + 6, 38), (COL_R, 40)], 0, 0, 0, 32)
    fluted(m, "travertine", COL_R, rt, 40, shaft_top - 6)
    m.lathe("travertine", [(rt, shaft_top - 6), (rt + 4, shaft_top - 4), (rt + 4, shaft_top), (rt, shaft_top)], 0, 0, 0, 32)
    # Capital: bell flaring to the abacus, two rows of acanthus leaves, corner volutes.
    bell = [(rt, shaft_top), (rt + 2, shaft_top + cap_h * 0.5), (rt + 14, shaft_top + cap_h * 0.85),
            (rt + 20, shaft_top + cap_h * 0.85), (0, shaft_top + cap_h * 0.85)]
    m.lathe("travertine", bell, 0, 0, 0, 32)
    for row, (h, n, r, off) in enumerate(((cap_h * 0.22, 8, rt + 6, 0.0), (cap_h * 0.45, 8, rt + 9, 0.5))):
        for k in range(n):
            t = 2 * math.pi * (k + off) / n
            c = (r * math.cos(t), r * math.sin(t), shaft_top + h)
            m.blob("travertine", c, 9 + 3 * abs(math.cos(t)), 9 + 3 * abs(math.sin(t)), cap_h * 0.2, 6)
    for k in range(4):
        t = math.pi / 4 + k * math.pi / 2
        rv = rt + 20
        m.blob("travertine", (rv * math.cos(t), rv * math.sin(t), shaft_top + cap_h * 0.72), 10, 10, 10, 6)
    # Abacus: square slab with concave-cut sides approximated by a flat square.
    a, z0, z1 = rt + 28, shaft_top + cap_h * 0.85, COL_H
    up, dn = (0, 0, 1), (0, 0, -1)
    uv = lambda x, y: (x / 128.0, y / 128.0)
    c = [(-a, -a), (a, -a), (a, a), (-a, a)]
    m.quad("travertine", *[((x, y, z1), up, uv(x, y)) for x, y in c])
    m.quad("travertine", *[((x, y, z0), dn, uv(x, y)) for x, y in reversed(c)])
    for i in range(4):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % 4]
        nn = ((y1 - y0) / (2 * a), (x0 - x1) / (2 * a), 0)
        m.quad("travertine", ((x0, y0, z0), nn, (0, 0)), ((x1, y1, z0), nn, (1, 0)),
               ((x1, y1, z1), nn, (1, 0.3)), ((x0, y0, z1), nn, (0, 0.3)))
    return m


MODELS = {"corinthian": corinthian}


def build():
    SRC.mkdir(parents=True, exist_ok=True)
    MAT.mkdir(parents=True, exist_ok=True)
    gmat = G / "garrysmod" / "materials" / "models" / "pennmodern"
    gmat.mkdir(parents=True, exist_ok=True)
    for name, text in VMTS.items():
        (MAT / f"{name}.vmt").write_text(text, encoding="ascii", newline="\n")
        shutil.copy(MAT / f"{name}.vmt", gmat)
    out = ROOT / "src" / "models" / "pennmodern"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        (SRC / f"{name}.smd").write_text(fn().smd(), encoding="ascii", newline="\n")
        (SRC / f"{name}.qc").write_text(
            f'$modelname "pennmodern/{name}.mdl"\n$body body "{name}.smd"\n$cdmaterials "models/pennmodern/"\n'
            f'$staticprop\n$surfaceprop "stone"\n$sequence idle "{name}.smd"\n', encoding="ascii", newline="\n")
        r = subprocess.run([str(G / "bin" / "studiomdl.exe"), "-game", str(G / "garrysmod"), "-nop4",
                            str(SRC / f"{name}.qc")], capture_output=True, text=True)
        if r.returncode or "ERROR" in r.stdout:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-1000:])
        for f in (G / "garrysmod" / "models" / "pennmodern").glob(f"{name}.*"):
            shutil.copy(f, out)
        print("built", name, sorted(p.name for p in out.glob(f"{name}.*")))


if __name__ == "__main__":
    build()
