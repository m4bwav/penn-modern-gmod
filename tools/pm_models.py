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
DEPTH = 6 * FT           # truss depth between its chords
LONG = 200 * FT          # hall length E-W (build_vmf.py 2*HX)

VMTS = {
    "steel": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.42 0.44 0.47]"\n'
             '\t"$surfaceprop" "metal"\n}\n',
    "stainless": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.78 0.79 0.8]"\n'
                 '\t"$surfaceprop" "metal"\n}\n',
    "steptread": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.3 0.31 0.32]"\n'
                 '\t"$surfaceprop" "metal"\n}\n',
    "rubber": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.05 0.05 0.05]"\n'
              '\t"$surfaceprop" "rubber"\n}\n',
    "escglass": '"VertexLitGeneric"\n{\n\t"$basetexture" "glass/glasswindow007a"\n\t"$translucent" "1"\n'
                '\t"$nocull" "1"\n\t"$surfaceprop" "glass"\n}\n',
    "amblue": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.2 0.36 0.68]"\n'
              '\t"$surfaceprop" "metal"\n}\n',
    "seat": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.09 0.09 0.1]"\n'
            '\t"$surfaceprop" "plastic"\n}\n',
    "njwhite": '"UnlitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.9 0.92 0.9]"\n'
               '\t"$surfaceprop" "metal"\n}\n',
    "njstone": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.86 0.8 0.68]"\n'
               '\t"$surfaceprop" "stone"\n}\n',
    "clockcase": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.12 0.12 0.13]"\n'
                 '\t"$surfaceprop" "metal"\n}\n',
}


KNEE = 14 * FT            # straight legs above the springing before the knee
SLOPE_Y = 62 * FT         # where the knee meets the gable slope (|y|)
SLOPE_Z = 28 * FT


def _profile():
    """Half profile of the truss top chord, springing to ridge: leg, rounded knee, flat gable
    (the refs show a low gabled Pratt truss, not a round arch). Returns (y, z) from y = SPAN."""
    pts = [(SPAN, 0), (SPAN, KNEE)]
    for k in range(1, 6):   # quadratic knee from the leg top to the slope start
        u = k / 6
        a, b, c = (SPAN, KNEE), (SPAN, SLOPE_Z), (SLOPE_Y, SLOPE_Z + (RISE - SLOPE_Z) * (SPAN - SLOPE_Y) / SPAN)
        pts.append(tuple((1 - u) ** 2 * a[i] + 2 * u * (1 - u) * b[i] + u * u * c[i] for i in (0, 1)))
    pts += [(SLOPE_Y * (1 - k / 6), pts[-1][1] + (RISE - pts[-1][1]) * k / 6) for k in range(1, 7)]
    return pts


PROFILE = _profile()
_LEN = [0.0]
for _a, _b in zip(PROFILE, PROFILE[1:]):
    _LEN.append(_LEN[-1] + math.dist(_a, _b))


def _at(s):
    """Point and unit tangent on the full profile at s in [0, 1] (0 = south springing, 1 = north)."""
    south = s < .5
    d = (s * 2 if south else (1 - s) * 2) * _LEN[-1]
    i = max(j for j in range(len(_LEN) - 1) if _LEN[j] <= d) if d < _LEN[-1] else len(_LEN) - 2
    (y0, z0), (y1, z1) = PROFILE[i], PROFILE[i + 1]
    f = (d - _LEN[i]) / (_LEN[i + 1] - _LEN[i])
    y, z = y0 + (y1 - y0) * f, z0 + (z1 - z0) * f
    ty, tz = y1 - y0, z1 - z0
    if south:
        y, ty = -y, -ty
    else:
        ty, tz = ty, -tz
        ty = -ty
    n = math.hypot(ty, tz)
    return y, z, ty / n, tz / n


def arch(t, inset=0):
    """Point on the truss profile at t (0 = south springing, pi = north), y-z plane, moved inset
    units inward (down and toward the centre line; negative = outward)."""
    y, z, ty, tz = _at(t / math.pi)
    ny, nz = -tz, ty                       # left normal of the south-to-north tangent
    if ny * -y + nz * -z < 0 and abs(y) > 1:
        ny, nz = -ny, -nz
    if abs(y) <= 1:
        ny, nz = 0, -1
    return (0, y + ny * inset, z + nz * inset)


def truss():
    """Transverse gabled Pratt truss (the kept 1912-14 Farley steel): two chords and a zigzag web,
    legs down to the balcony. Origin: hall centre line at springing height; spans y = -SPAN..SPAN."""
    m = Mesh()
    n = 28
    ts = [math.pi * k / n for k in range(n + 1)]
    for k in range(n):
        for ins in (0, DEPTH):
            m.tube("steel", arch(ts[k], ins), arch(ts[k + 1], ins), 9, 9, 6)
        a, b = (k, k + 1) if k < n // 2 else (k + 1, k)   # Pratt: diagonals fall toward mid-span
        m.tube("steel", arch(ts[a], 0), arch(ts[b], DEPTH), 3, 3, 6)
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
    uv = ((0, 0), (1, 0), (1, 1), (0, 1))   # SMD v runs up: v 0 at z0 (was flipped: boards read upside down)
    for nrm, q in sides:
        m.quad(faces.get(nrm, mat), *[(p, nrm, uv[i]) for i, p in enumerate(q)])


def clock():
    """The four-faced centre clock, 12 ft tall, about 6 ft a side, on a hanger rod.
    Origin: top of the rod (fixed to the centre truss crown)."""
    m = Mesh()
    h, a, rod = 12 * FT, 3 * FT, 30 * FT
    m.tube("clockcase", (0, 0, 0), (0, 0, -rod), 3, 3, 8)
    _box(m, "clockcase", -a, -a, -rod - h, a, a, -rod)
    for z0, z1, w in ((-rod - 10, -rod, a + 6), (-rod - h, -rod - h + 10, a + 6), (-rod + 0, -rod + 14, a - 10)):
        _box(m, "clockcase", -w, -w, z0, w, w, z1)   # stepped art-deco caps
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
            c = arch(math.pi * (k + .5) / n, 0)
            nrm = tuple(p - q for p, q in zip(arch(math.pi * (k + .5) / n, 1), c))   # into the hall ($nocull shows both)
            u0, u1, v0, v1 = xs[i] / cell, xs[i + 1] / cell, arc[k] / cell, arc[k + 1] / cell
            m.quad("skylight", ((xs[i], y0, z0), nrm, (u0, v0)), ((xs[i], y1, z1), nrm, (u0, v1)),
                   ((xs[i + 1], y1, z1), nrm, (u1, v1)), ((xs[i + 1], y0, z0), nrm, (u1, v0)))
    return m


ESC_RUN, ESC_RISE = 56 * FT, 30 * FT   # build_vmf.py: wells run 2*WX, down to LZ


def escalator():
    """A pair of escalators side by side in one 12 ft well, climbing toward +x: steps on a
    stainless truss, glass balustrades with black handrails. Origin: top end at the hall floor
    (z 0, x = +ESC_RUN/2), bottom end at x = -ESC_RUN/2, z = -ESC_RISE; spans y = -63..63."""
    m = Mesh()
    L, R = ESC_RUN / 2, ESC_RISE
    z = lambda x: (x + L) * R / ESC_RUN - R
    n = R // 8                                    # 8 u (8 in) risers
    d = ESC_RUN / n
    for yc in (-33, 33):
        a, b = yc - 20, yc + 20                   # 40 in step width
        for i in range(n):
            x0 = -L + i * d
            _box(m, "steptread", x0, a, -R + i * 8 - 2, x0 + d, b, -R + (i + 1) * 8)
        for y0, y1 in ((a - 10, a), (b, b + 10)):     # inner deck and skirt on each side, sloped
            pts = [(-L, z(-L) - 30), (L, z(L) - 30), (L, z(L) + 6), (-L, z(-L) + 6)]
            m.quad("stainless", *[((x, y0, zz), (0, -1, 0), (x / 96, zz / 96)) for x, zz in pts])
            m.quad("stainless", *[((x, y1, zz), (0, 1, 0), (x / 96, zz / 96)) for x, zz in pts[::-1]])
            m.quad("stainless", ((-L, y0, z(-L) + 6), (0, 0, 1), (0, 0)), ((L, y0, z(L) + 6), (0, 0, 1), (1, 0)),
                   ((L, y1, z(L) + 6), (0, 0, 1), (1, 1)), ((-L, y1, z(-L) + 6), (0, 0, 1), (0, 1)))
            ym = (y0 + y1) / 2
            m.quad("escglass", *[((x, ym, zz), (0, 1, 0), (x / 96, zz / 96)) for x, zz in
                                 ((-L, z(-L) + 6), (L, z(L) + 6), (L, z(L) + 36), (-L, z(-L) + 36))])
            m.tube("rubber", (-L - 12, ym, z(-L) + 38), (L + 12, ym, z(L) + 38), 2.5, 2.5, 6)
        # cladding under the run, seen from the concourse below
        m.quad("stainless", ((-L, b + 10, z(-L) - 30), (0, 0, -1), (0, 0)), ((-L, a - 10, z(-L) - 30), (0, 0, -1), (1, 0)),
               ((L, a - 10, z(L) - 30), (0, 0, -1), (1, 1)), ((L, b + 10, z(L) - 30), (0, 0, -1), (0, 1)))
    return m


def colboard():
    """Two LIRR departure boards (2.5 x 5 ft) back to back on a 30 in column, facing +-x along the
    corridor (place yaw 90). Origin: column centre at the floor; boards span z 6.5..11.5 ft."""
    m = Mesh()
    for sx in (1, -1):
        x0, x1 = sorted((sx * 15, sx * 21))
        _box(m, "clockcase", x0, -15, 78, x1, 15, 138, faces={(sx, 0, 0): "depboard"})
    return m


def tvm():
    """An LIRR ticket machine, 30 in wide, 18 in deep, 66 in tall, its screen facing +y
    (place yaw 90). Origin: back of the machine at the floor, centred."""
    m = Mesh()
    _box(m, "stainless", -15, 0, 0, 15, 18, 66, faces={(0, 1, 0): "tvm_front"})
    _box(m, "clockcase", -16, 0, 66, 16, 20, 70)
    return m


def amcol():
    """An Amtrak concourse column: 3 ft round, pale blue, 14 ft to the ceiling, with the ring of
    lights (halo) round it just under the ceiling. Origin: column centre at the floor."""
    m = Mesh()
    m.cyl("amblue", 0, 0, 18, 0, 168, 16)
    m.lathe("halo", [(26, 150), (44, 150), (44, 156), (26, 156)], 0, 0, 0, 24)
    m.lathe("clockcase", [(18, 156), (46, 156), (46, 166), (18, 166)], 0, 0, 0, 24)
    return m


def seats():
    """A row of six black waiting-room seats on a steel beam, facing -y.
    Origin: middle of the row at the floor; spans x = -72..72."""
    m = Mesh()
    _box(m, "stainless", -74, -4, 10, 74, 4, 14)
    for k in (-60, 60):
        _box(m, "stainless", k - 2, -8, 0, k + 2, 8, 14)
    for i in range(6):
        x = -72 + i * 24
        _box(m, "seat", x + 1, -10, 14, x + 23, 10, 18)
        _box(m, "seat", x + 1, 9, 18, x + 23, 12, 36)
    return m


def njtruss():
    """One white arched truss across the NJ Transit vault (VY0..VY1 in build_vmf.py, 280 u wide):
    elliptical top and bottom chords with a zigzag web, springing 12 ft up, crown 20 ft.
    Origin: vault centre line at springing height; spans y = -140..140 (place yaw 90: studiomdl turns SMD y to the prop's -x)."""
    m = Mesh()
    n = 14
    pt = lambda k, r, h: (0, -r * math.cos(math.pi * k / n), h * math.sin(math.pi * k / n))
    for k in range(n):
        m.tube("njwhite", pt(k, 140, 92), pt(k + 1, 140, 92), 3, 3, 6)
        m.tube("njwhite", pt(k, 124, 70), pt(k + 1, 124, 70), 3, 3, 6)
        m.tube("njwhite", pt(k, 140, 92), pt(k + 1, 124, 70), 1.5, 1.5, 4)
    return m


def njcol():
    """A flared NJ Transit concourse column, cream stone, 3 ft round, its capital spreading to
    8 ft under the 12 ft side ceiling. Origin: column centre at the floor."""
    m = Mesh()
    m.lathe("njstone", [(18, 0), (18, 100), (24, 116), (36, 132), (48, 140), (48, 144), (0, 144)], 0, 0, 0, 20)
    return m


def pmcar():
    """A Bombardier MultiLevel coach, 85 ft long, 10.5 ft wide, 15.5 ft over the rail (cited): stainless
    body with the two-level window band (mlside), dark underframe and two trucks. Origin: top of
    rail at the car's centre; place yaw 90 to run along world x."""
    m = Mesh()
    L, Wd = 510, 63
    _box(m, "stainless", -L, -Wd, 22, L, Wd, 176, faces={(0, 1, 0): "mlside", (0, -1, 0): "mlside",
                                                          (1, 0, 0): "mlend", (-1, 0, 0): "mlend"})
    _box(m, "stainless", -L + 6, -Wd + 6, 176, L - 6, Wd - 6, 186)
    _box(m, "clockcase", -L + 40, -Wd + 8, 10, L - 40, Wd - 8, 22)
    for x in (-380, 380):
        _box(m, "rubber", x - 60, -32, 0, x + 60, 32, 22)
    return m


MODELS = {"pmcar": pmcar, "njtruss": njtruss, "njcol": njcol, "amcol": amcol, "seats": seats, "colboard": colboard, "tvm": tvm, "escalator": escalator, "truss": truss, "purlins": purlins, "clock": clock, "skylight": skylight}


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
