"""Penn Station props as MDL, built with make_models.Mesh and Garry's Mod's studiomdl.

    python tools/pm_models.py      # writes src/modelsrc/, compiles into src/models/pennmodern/

Models do not count against vbsp's 65,536 unique-vertex cap, so Moynihan's skylight trusses,
the secondary steel and the centre clock live here (origins in each builder's docstring).
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
SPAN = 155 * FT // 2     # half the N-S span of the hall (build_vmf.py HY)
RISE = 42 * FT           # truss springing ~50 ft to the 92 ft skylight crown
DEPTH = 4 * FT           # truss depth between its chords
LONG = 200 * FT          # hall length E-W (build_vmf.py 2*HX)

VMTS = {
    "steel": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.82 0.84 0.86]"\n'
             '\t"$surfaceprop" "metal"\n}\n',
    "clockcase": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.12 0.12 0.13]"\n'
                 '\t"$surfaceprop" "metal"\n}\n',
}


def arch(t, inset=0):
    """Point on the elliptical truss arch at angle t (0 = south springing, pi = north), y-z plane."""
    return (0, (SPAN - inset) * math.cos(t), (RISE - inset) * math.sin(t))


def truss():
    """Transverse arched truss (the kept 1912-14 Farley steel): two chords and a zigzag web,
    legs down to the balcony. Origin: hall centre line at springing height; spans y = -SPAN..SPAN."""
    m = Mesh()
    n = 28
    ts = [math.pi * k / n for k in range(n + 1)]
    for k in range(n):
        for ins in (0, DEPTH):
            m.tube("steel", arch(ts[k], ins), arch(ts[k + 1], ins), 5, 5, 6)
        m.tube("steel", arch(ts[k], 0), arch(ts[k + 1], DEPTH), 3, 3, 6)
        m.tube("steel", arch(ts[k], DEPTH), arch(ts[k], 0), 3, 3, 6)
    for sgn in (-1, 1):
        for ins in (0, DEPTH):
            m.tube("steel", (0, sgn * (SPAN - ins), 0), (0, sgn * (SPAN - ins), -30 * FT), 6, 6, 6)
    return m


def purlins():
    """Secondary steel: longitudinal ribs along the skylight between the transverse trusses.
    Origin as truss(); runs x = -LONG/2..LONG/2."""
    m = Mesh()
    for k in range(1, 12):
        y, z = arch(math.pi * k / 12)[1:]
        m.tube("steel", (-LONG / 2, y, z + 2), (LONG / 2, y, z + 2), 3, 3, 6)
    return m


def _box(m, mat, x0, y0, z0, x1, y1, z1, faces=None):
    faces = faces or {}
    sides = [((1, 0, 0), [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
             ((-1, 0, 0), [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)]),
             ((0, 1, 0), [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)]),
             ((0, -1, 0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),
             ((0, 0, 1), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
             ((0, 0, -1), [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)])]
    uv = ((0, 1), (1, 1), (1, 0), (0, 0))
    for nrm, q in sides:
        m.quad(faces.get(nrm, mat), *[(p, nrm, uv[i]) for i, p in enumerate(q)])


def clock():
    """The four-faced centre clock, 12 ft tall, about 6 ft a side, on a hanger rod.
    Origin: top of the rod (fixed to the centre truss crown)."""
    m = Mesh()
    h, a, rod = 12 * FT, 3 * FT, 30 * FT
    m.tube("clockcase", (0, 0, 0), (0, 0, -rod), 3, 3, 8)
    _box(m, "clockcase", -a, -a, -rod - h, a, a, -rod)
    f = a - 6
    for nrm in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
        sub = Mesh()
        _box(sub, "clockcase", -f, -f, -rod - h + 18, f, f, -rod - 18, faces={nrm: "clockface"})
        for mat, vs in sub.tris:
            if mat == "clockface":   # the dial face only, pushed just proud of the case
                m.tris.append((mat, [((p[0] + nrm[0] * 7, p[1] + nrm[1] * 7, p[2]), n_, uv) for p, n_, uv in vs]))
    return m


def skylight():
    """The glass vault over the trusses (skylight.vmt from pm_textures.py, translucent, 6 ft cells).
    Origin as purlins(); runs x = -LONG/2..LONG/2 just above the top chords."""
    m = Mesh()
    n, nx, cell = 24, 10, 12 * FT
    pts = [arch(math.pi * k / n, -10) for k in range(n + 1)]
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + math.dist(a, b))
    xs = [-LONG / 2 + LONG * i / nx for i in range(nx + 1)]
    for i in range(nx):
        for k in range(n):
            (_, y0, z0), (_, y1, z1) = pts[k], pts[k + 1]
            t = (math.pi * (k + .5) / n)
            nrm = (0, -math.cos(t), -math.sin(t))   # faces down into the hall ($nocull shows both)
            u0, u1, v0, v1 = xs[i] / cell, xs[i + 1] / cell, arc[k] / cell, arc[k + 1] / cell
            m.quad("skylight", ((xs[i], y0, z0), nrm, (u0, v0)), ((xs[i], y1, z1), nrm, (u0, v1)),
                   ((xs[i + 1], y1, z1), nrm, (u1, v1)), ((xs[i + 1], y0, z0), nrm, (u1, v0)))
    return m


MODELS = {"truss": truss, "purlins": purlins, "clock": clock, "skylight": skylight}


def build():
    SRC.mkdir(parents=True, exist_ok=True)
    MAT.mkdir(parents=True, exist_ok=True)
    gmat = G / "garrysmod" / "materials" / "models" / "pennmodern"
    gmat.mkdir(parents=True, exist_ok=True)
    for name, text in VMTS.items():
        (MAT / f"{name}.vmt").write_text(text, encoding="ascii", newline="\n")
    for f in MAT.glob("*.v[mt][tf]"):   # VMTS above plus pm_textures.py's model materials
        shutil.copy(f, gmat)
    out = ROOT / "src" / "models" / "pennmodern"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        (SRC / f"{name}.smd").write_text(fn().smd(), encoding="ascii", newline="\n")
        (SRC / f"{name}.qc").write_text(
            f'$modelname "pennmodern/{name}.mdl"\n$body body "{name}.smd"\n$cdmaterials "models/pennmodern/"\n'
            f'$staticprop\n$surfaceprop "metal"\n$sequence idle "{name}.smd"\n', encoding="ascii", newline="\n")
        r = subprocess.run([str(G / "bin" / "studiomdl.exe"), "-game", str(G / "garrysmod"), "-nop4",
                            str(SRC / f"{name}.qc")], capture_output=True, text=True)
        if r.returncode or "ERROR" in r.stdout:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-1000:])
        for f in (G / "garrysmod" / "models" / "pennmodern").glob(f"{name}.*"):
            shutil.copy(f, out)
        print("built", name, sorted(p.name for p in out.glob(f"{name}.*")))


if __name__ == "__main__":
    build()
