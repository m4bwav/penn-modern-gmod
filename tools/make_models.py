"""Write props as SMD + QC and compile them to MDL with Garry's Mod's studiomdl.

Models do not count against vbsp's 65,536 unique-vertex cap, so round, many-sided
decoration (chandeliers, globes) belongs here instead of in brushes.

    python tools/make_models.py          # writes src/modelsrc/, compiles into src/models/

Output: src/models/gcs/<name>.{mdl,vvd,vtx...}, src/materials/models/gcs/*.vmt.
compile.sh copies both into garrysmod/ and packs them into the BSP.
"""
import math
import os
import random
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = Path(os.environ.get("GMOD", "D:/SteamLibrary/steamapps/common/GarrysMod"))
SRC = ROOT / "src" / "modelsrc"
MAT = ROOT / "src" / "materials" / "models" / "gcs"

FT = 12
SPRING = 125 * FT - 40 * FT     # concourse springline, matches build_vmf.py
CHAND_Z = 32 * FT               # chandelier body height above the concourse floor

# Model materials: VertexLitGeneric twins of the brush materials.
VMTS = {
    "gold": '"VertexLitGeneric"\n{\n\t"$basetexture" "stone/stonewall033a"\n\t"$color2" "[1.25 0.95 0.45]"\n'
            '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.25 0.2 0.1]"\n\t"$surfaceprop" "metal"\n}\n',
    "bronze": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.45 0.33 0.18]"\n'
              '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.25 0.2 0.12]"\n\t"$surfaceprop" "metal"\n}\n',
    "root": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.85 0.83 0.8]"\n'
            '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.3 0.3 0.3]"\n\t"$surfaceprop" "metal"\n}\n',
    "bulb": '"UnlitGeneric"\n{\n\t"$basetexture" "lights/white002"\n\t"$color2" "[1.0 0.86 0.6]"\n\t"$model" "1"\n}\n',
    "statue": '"VertexLitGeneric"\n{\n\t"$basetexture" "gcs/facade_stone"\n\t"$color2" "[0.8 0.76 0.7]"\n'
              '\t"$nocull" "1"\n\t"$surfaceprop" "stone"\n}\n',
    "taxi": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[1.5 1.1 0.12]"\n'
            '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.2 0.2 0.2]"\n\t"$surfaceprop" "metal"\n}\n',
    "car_glass": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.08 0.1 0.12]"\n'
                 '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.4 0.42 0.45]"\n\t"$surfaceprop" "glass"\n}\n',
    "tyre": '"VertexLitGeneric"\n{\n\t"$basetexture" "metal/metalwall001a"\n\t"$color2" "[0.05 0.05 0.05]"\n'
            '\t"$surfaceprop" "rubber"\n}\n',
}


def _cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _unit(a):
    ln = math.sqrt(sum(c * c for c in a)) or 1
    return tuple(c / ln for c in a)


class Mesh:
    def __init__(self):
        self.tris = []      # (material, [(pos, normal, uv)] * 3)

    def quad(self, mat, a, b, c, d):
        # Corners counter-clockwise seen from outside; each item (pos, normal, uv).
        self.tris.append((mat, [a, b, c]))
        self.tris.append((mat, [a, c, d]))

    def lathe(self, mat, prof, cx, cy, cz, n=16):
        """Revolve a profile [(r, z)] from bottom to top about the vertical axis at (cx, cy)."""
        for i in range(len(prof) - 1):
            (r0, z0), (r1, z1) = prof[i], prof[i + 1]
            dr, dz = r1 - r0, z1 - z0
            ln = math.hypot(dr, dz) or 1
            nr, nz = dz / ln, -dr / ln            # outward normal of this band in (r, z)
            for j in range(n):
                t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                def v(r, z, t, u):
                    p = (cx + r * math.cos(t), cy + r * math.sin(t), cz + z)
                    nrm = (nr * math.cos(t), nr * math.sin(t), nz)
                    return (p, nrm, (u, z / 64.0))
                self.quad(mat, v(r0, z0, t0, j / n), v(r0, z0, t1, (j + 1) / n),
                          v(r1, z1, t1, (j + 1) / n), v(r1, z1, t0, j / n))

    def cyl(self, mat, cx, cy, r, z0, z1, n=16):
        # Closed cylinder: bottom cap, side, top cap as a lathe profile.
        self.lathe(mat, [(0, z0), (r, z0), (r, z1), (0, z1)], cx, cy, 0, n)

    def sphere(self, mat, cx, cy, cz, r, n=10):
        prof = [(r * math.sin(math.pi * k / n), -r * math.cos(math.pi * k / n)) for k in range(n + 1)]
        self.lathe(mat, prof, cx, cy, cz, 2 * n)

    def tube(self, mat, a, b, r0, r1, n=10):
        """Tapered tube from point a (radius r0) to b (radius r1), domed ends, any direction."""
        ax = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ln = math.sqrt(sum(c * c for c in ax)) or 1
        w = tuple(c / ln for c in ax)
        u = _unit(_cross(w, (1, 0, 0) if abs(w[0]) < 0.9 else (0, 1, 0)))
        v = _cross(w, u)
        prof = [(0, -r0 * 0.6), (r0 * 0.7, -r0 * 0.4), (r0, 0), (r1, ln), (r1 * 0.7, ln + r1 * 0.4), (0, ln + r1 * 0.6)]
        self.frame(mat, prof, a, u, v, w, n)

    def blob(self, mat, c, rx, ry, rz, n=8):
        """Ellipsoid centred at c with radii along x, y, z."""
        prof = [(math.sin(math.pi * k / n), -math.cos(math.pi * k / n)) for k in range(n + 1)]
        for i in range(n):
            (r0, z0), (r1, z1) = prof[i], prof[i + 1]
            for j in range(2 * n):
                t0, t1 = math.pi * j / n, math.pi * (j + 1) / n
                def v(r, z, t):
                    nx, ny, nz = r * math.cos(t), r * math.sin(t), z
                    p = (c[0] + rx * nx, c[1] + ry * ny, c[2] + rz * nz)
                    return (p, _unit((nx / rx, ny / ry, nz / rz)), (p[0] / 128.0, p[2] / 128.0))
                self.quad(mat, v(r0, z0, t0), v(r0, z0, t1), v(r1, z1, t1), v(r1, z1, t0))

    def frame(self, mat, prof, o, u, v, w, n):
        """Lathe a profile [(r, h)] about axis w through o; (u, v) span the ring plane."""
        for i in range(len(prof) - 1):
            (r0, h0), (r1, h1) = prof[i], prof[i + 1]
            dr, dh = r1 - r0, h1 - h0
            ln = math.hypot(dr, dh) or 1
            nr, nh = dh / ln, -dr / ln
            for j in range(n):
                t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                def vt(r, h, t):
                    ct, st = math.cos(t), math.sin(t)
                    p = tuple(o[k] + r * (ct * u[k] + st * v[k]) + h * w[k] for k in range(3))
                    nrm = tuple(nr * (ct * u[k] + st * v[k]) + nh * w[k] for k in range(3))
                    return (p, nrm, (p[0] / 128.0, p[2] / 128.0))
                self.quad(mat, vt(r0, h0, t0), vt(r0, h0, t1), vt(r1, h1, t1), vt(r1, h1, t0))

    def slab(self, mat, poly, y0, y1):
        """Flat plate: convex-ish polygon [(x, z)], counter-clockwise seen from -y, from y0 to y1."""
        cx, cz = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
        uv = lambda x, z: (x / 128.0, z / 128.0)
        for i in range(len(poly)):
            (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % len(poly)]
            self.tris.append((mat, [((cx, y0, cz), (0, -1, 0), uv(cx, cz)), ((x1, y0, z1), (0, -1, 0), uv(x1, z1)),
                                    ((x0, y0, z0), (0, -1, 0), uv(x0, z0))]))
            self.tris.append((mat, [((cx, y1, cz), (0, 1, 0), uv(cx, cz)), ((x0, y1, z0), (0, 1, 0), uv(x0, z0)),
                                    ((x1, y1, z1), (0, 1, 0), uv(x1, z1))]))
            nn = _unit((z1 - z0, 0, x0 - x1))
            self.quad(mat, ((x0, y0, z0), nn, uv(x0, z0)), ((x1, y0, z1), nn, uv(x1, z1)),
                      ((x1, y1, z1), nn, uv(x1, z1)), ((x0, y1, z0), nn, uv(x0, z0)))

    def smd(self):
        out = ["version 1", "nodes", '0 "root" -1', "end", "skeleton", "time 0", "0 0 0 0 0 0 0", "end", "triangles"]
        for mat, vs in self.tris:
            out.append(mat)
            for p, nrm, uv in vs:
                out.append("0 %.3f %.3f %.3f %.4f %.4f %.4f %.4f %.4f" % (*p, *nrm, *uv))
        out.append("end")
        return "\n".join(out) + "\n"


def chandelier():
    """Concourse chandelier, origin at the body centre: gold rod up to the cornice, a gold drum
    with two tiers of eight glowing globes, a finial and a big bottom globe."""
    m = Mesh()
    m.cyl("gold", 0, 0, 2, 48, SPRING - CHAND_Z, 8)
    m.lathe("gold", [(0, -36), (5, -36), (5, -30), (8, -30), (8, -6), (22, -6), (24, 0), (22, 6),
                     (12, 6), (12, 44), (14, 48), (0, 48)], 0, 0, 0, 24)
    for tier, (r, z) in enumerate(((30, 11), (18, 35))):
        for a in range(8):
            t = 2 * math.pi * (a + 0.5 * tier) / 8
            x, y = r * math.cos(t), r * math.sin(t)
            m.cyl("gold", x * 0.5, y * 0.5, 1.2, z - 6, z - 4, 6)   # arm stub under each globe
            m.sphere("bulb", x, y, z, 5, 6)
    m.sphere("bulb", 0, 0, -46, 10, 10)
    return m


VH_TOP = 30 * FT   # Vanderbilt Hall: ceiling above the chandelier centre (VH_H - zc in build_vmf.py)


def vh_chandelier():
    """Vanderbilt Hall chandelier, origin at the middle bulb ring: chain from a ceiling rosette,
    a tall bronze cage of eight bars with gold bands, then three rings of globes narrowing
    downward round a bronze bowl core to a gold finial (photo: GCT_Vanderbilt_hall_chandeliers)."""
    m = Mesh()
    cage0, cage1 = 34, 13 * FT
    m.cyl("gold", 0, 0, 30, VH_TOP - 4, VH_TOP, 24)                 # ceiling rosette
    m.cyl("bronze", 0, 0, 2, cage1 + 18, VH_TOP - 4, 8)              # chain
    m.lathe("gold", [(0, cage1), (10, cage1), (12, cage1 + 9), (10, cage1 + 18), (0, cage1 + 18)], 0, 0, 0, 16)
    m.cyl("bronze", 0, 0, 4, cage0, cage1, 8)                        # stem
    for i in range(8):
        a = i * math.pi / 4
        m.cyl("bronze", 16 * math.cos(a), 16 * math.sin(a), 1.5, cage0, cage1 - 10, 6)   # cage bars
    for z, r in ((cage1 - 10, 16), (cage0 + 3 * FT, 22), (cage0, 30)):
        m.cyl("gold", 0, 0, r + 1, z - 4, z, 24)                     # cage bands
    for r, z in ((54, 24), (40, 0), (26, -24)):
        m.lathe("bronze", [(r - 10, z - 4), (r + 2, z - 4), (r + 2, z), (r - 10, z)], 0, 0, 0, 24)
        m.cyl("gold", 0, 0, r - 10, z - 4, z + 3, 24)
        k = max(10, int(r / 3.2))
        for i in range(k):
            t = 2 * math.pi * i / k
            m.sphere("bulb", r * math.cos(t), r * math.sin(t), z + 5, 4.5, 5)
    m.lathe("bronze", [(0, -30), (8, -26), (12, 0), (10, 30), (0, 30)], 0, 0, 0, 16)   # bowl core
    m.lathe("gold", [(0, -54), (3, -50), (6, -40), (5, -30), (0, -30)], 0, 0, 0, 12)   # finial
    return m


class Figure:
    """Pose a figure in body inches (6 ft tall, feet at 0, facing -y), scaled by k and moved
    to base in model space (x right as seen from the street, y back, z up)."""
    def __init__(self, m, base, k):
        self.m, self.b, self.k = m, base, k

    def P(self, p):
        return tuple(self.b[i] + p[i] * self.k for i in range(3))

    def limb(self, a, b, r0, r1, n=10):
        self.m.tube("statue", self.P(a), self.P(b), r0 * self.k, r1 * self.k, n)

    def blob(self, c, rx, ry, rz):
        self.m.blob("statue", self.P(c), rx * self.k, ry * self.k, rz * self.k)

    def head(self, c):
        self.limb((c[0], c[1], c[2] - 9), (c[0], c[1], c[2] - 4), 2.6, 2.4)   # neck
        self.blob(c, 3.6, 4.2, 4.8)

    def plate(self, pts, y, t=1.0):
        # Thin plate through body points [(x, z)] at depth y (wings on hats and wands).
        self.m.slab("statue", [(self.b[0] + x * self.k, self.b[2] + z * self.k) for x, z in pts],
                    self.b[1] + (y - t / 2) * self.k, self.b[1] + (y + t / 2) * self.k)


def statue_group():
    """Glory of Commerce (Coutan, 1914) over the 42nd Street clock. Origin on the pedestal top
    at the facade axis, facing -y. Mercury strides with his right arm flung out and the
    caduceus raised in his left, an eagle's wings spread behind him; Hercules reclines on the
    viewer's left, Minerva sits on the right with helmet and shield (photo:
    42nd_Street_Facade_Grand_Central_Terminal_October_2025). About 48 ft high."""
    m = Mesh()
    # Mercury, 26 ft, on the clock surround's crown (19 ft), weight on his left leg.
    f = Figure(m, (0, 2 * FT, 19 * FT), 26 * FT / 72)
    f.blob((-5, -3, 2), 2.6, 5.5, 2)
    f.blob((4, 1, 2), 2.6, 5.5, 2)
    f.limb((-5, -2, 3), (-5, -4, 19), 2.6, 3.4)            # shins
    f.limb((4, 1, 3), (4.5, 0, 19), 2.6, 3.4)
    f.limb((-5, -4, 19), (-4, 0, 36), 3.8, 5.4)            # thighs
    f.limb((4.5, 0, 19), (4, 0, 36), 3.8, 5.4)
    f.blob((0, 0, 37), 8, 5, 6)                            # hips
    f.limb((0, 0, 37), (0.5, 0, 52), 6.5, 8)               # torso
    f.blob((0.5, -1, 50), 8.5, 5.5, 7.5)                   # chest
    f.head((1, -0.5, 66))
    f.limb((-2.5, -0.5, 69), (4.5, -0.5, 69), 4.4, 4.4, 12)   # petasos
    for s in (-1, 1):
        f.plate([(s * 3, 69), (s * 6, 71), (s * 10, 77)][::s], -0.5)   # its wings
    f.limb((-8.5, 0, 55), (-20, -2, 60), 2.8, 2.2)         # right arm flung out
    f.limb((-20, -2, 60), (-31, -3, 66), 2.2, 1.8)
    f.blob((-33, -3, 67), 2, 1.2, 2.2)
    f.limb((9, 0, 55), (13, -1, 44), 2.8, 2.2)             # left arm bent up to the caduceus
    f.limb((13, -1, 44), (15, -3, 58), 2.2, 1.8)
    f.limb((15, -3, 30), (15.5, -3, 84), 0.7, 0.7, 8)      # caduceus staff
    f.blob((15.5, -3, 85), 1.6, 1.6, 1.6)
    for s in (-1, 1):
        f.plate([(15.5, 80), (15.5 + s * 5, 81), (15.5 + s * 6, 84)][::s], -3)
        for z in (68, 74):                                 # serpent coils
            f.blob((15.5 + s * 1.4, -3, z), 1.2, 1.2, 2.4)
    f.blob((-6, 4, 46), 9, 3, 14)                          # cloak off the shoulder
    # Eagle behind Mercury, wings spread up and out.
    ey = 5 * FT
    m.blob("statue", (0, ey, 21 * FT), 3 * FT, 3 * FT, 5 * FT)
    m.blob("statue", (0, ey - 2 * FT, 27 * FT), 1.4 * FT, 1.8 * FT, 1.4 * FT)
    for s in (-1, 1):
        wing = [(3, 19), (8, 20), (14, 22), (13, 23), (18, 27), (16, 27), (19, 31), (17, 32), (9, 25), (2, 22)]
        # Wing as a fan of convex quads from the shoulder so the slab stays convex.
        for i in range(1, len(wing) - 2, 2):
            q = [wing[0], wing[i], wing[i + 1], wing[i + 2]]
            m.slab("statue", [(s * x * FT, z * FT) for x, z in (q if s < 0 else q[::-1])], ey - 8, ey + 8)
    # Hercules, reclining on the left, propped on his left elbow, club along his side.
    h = Figure(m, (-15 * FT, 0, 0), 30 * FT / 72)
    h.blob((-2, 0, 22), 10, 7, 6)
    h.limb((-2, 0, 22), (12, 0, 40), 7, 8.5)               # torso rising toward the centre
    h.blob((10, -1, 37), 9, 6.5, 8)
    h.head((17, -2, 53))
    h.limb((-6, 0, 21), (-26, -6, 18), 5.5, 4)             # far leg stretched out
    h.limb((-26, -6, 18), (-42, -8, 6), 4, 3)
    h.limb((2, -2, 22), (-16, -12, 26), 5.5, 4.2)          # near leg drawn up
    h.limb((-16, -12, 26), (-30, -14, 10), 4.2, 3)
    h.limb((5, 2, 40), (0, 4, 28), 3.6, 3)                 # left arm propping
    h.limb((19, -3, 41), (24, -8, 30), 3.6, 3)             # right arm on the knee
    h.limb((-36, -10, 4), (24, -10, 28), 2, 3.4)           # club
    h.blob((4, 5, 30), 14, 5, 7)                           # lion skin
    # Minerva, seated on the right: robe over the knees, helmet and crest, shield at her side.
    mi = Figure(m, (16 * FT, 0, 0), 30 * FT / 72)
    rx, ry, _ = mi.P((6, -8, 0))
    k = mi.k
    m.lathe("statue", [(0, 0), (11 * k, 0), (10 * k, 4 * k), (9 * k, 14 * k), (7 * k, 20 * k), (0, 22 * k)], rx, ry, 0, 14)
    mi.blob((0, 0, 22), 9, 7, 6)
    mi.limb((0, 0, 22), (-4, 0, 40), 6.5, 7.5)             # torso leaning toward the centre
    mi.blob((-4, -1, 37), 8, 6, 7.5)
    mi.head((-7, -1, 53))
    mi.limb((-9.5, -1, 57), (-1, -1, 57), 4.6, 4.6, 12)    # helmet
    mi.limb((-7, 1, 58), (-7, 4, 63), 1.2, 3)              # crest
    mi.limb((4, 0, 40), (14, -4, 34), 3.4, 2.8)            # right arm on the shield
    mi.limb((-12, -1, 40), (-20, -6, 46), 3.4, 2.8)        # left arm toward Mercury
    m.frame("statue", [(0, 0), (16 * k, 0), (16 * k, 2 * k), (6 * k, 4 * k), (0, 4 * k)],
            mi.P((22, -2, 22)), (0, 1, 0), (0, 0, 1), (-1, 0, 0), 16)   # round shield
    return m


def eagle():
    """Bronze eagle on a corner of the 42nd Street facade (one of the 1898 Grand Central Station
    eagles re-set on the terminal, about 13 ft across the wings). Origin at the plinth foot,
    facing -y, wings half raised."""
    m = Mesh()
    m.slab("statue", [(-30, 0), (30, 0), (30, 14), (-30, 14)], -30, 30)          # plinth
    m.blob("statue", (0, 0, 22), 14, 14, 10)                                      # globe it grips
    for s in (-1, 1):
        m.tube("statue", (s * 8, -4, 26), (s * 9, -8, 34), 2.2, 2.6, 8)           # legs
    m.blob("statue", (0, 4, 58), 18, 16, 26)                                      # body
    m.blob("statue", (0, -6, 70), 15, 12, 14)                                     # breast
    m.tube("statue", (0, -4, 80), (0, -14, 96), 8, 7, 10)                         # neck
    m.blob("statue", (0, -18, 100), 8, 10, 8)                                     # head
    m.tube("statue", (0, -26, 100), (0, -34, 94), 3.5, 1, 8)                      # beak, hooked down
    m.slab("statue", [(-14, 40), (14, 40), (10, 34), (0, 18), (-10, 34)][::-1], 18, 26)   # tail
    for s in (-1, 1):
        # Wing as a fan of convex quads from the shoulder: up and out, primaries spread at the tip.
        wing = [(10, 74), (40, 96), (70, 112), (78, 106), (84, 96), (80, 88), (82, 74), (72, 70), (60, 62), (34, 56), (12, 58)]
        for i in range(1, len(wing) - 2, 2):
            q = [wing[0], wing[i], wing[i + 1], wing[i + 2]]
            m.slab("statue", [(s * x, z) for x, z in (q if s < 0 else q[::-1])], 2, 10)
    return m


def taxi():
    """New York yellow cab, a generic sedan about 16 ft long. Origin on the road under its
    centre, length along x (front +x)."""
    m = Mesh()
    L, W = 96, 36
    body = [(-L, 10), (L, 10), (L, 30), (L - 6, 36), (L - 40, 38), (-L + 30, 38), (-L, 34)]
    m.slab("taxi", body[::-1], -W, W)
    m.slab("car_glass", [(-L + 34, 38), (L - 46, 38), (L - 62, 56), (-L + 46, 56)][::-1], -W + 3, W - 3)
    m.slab("taxi", [(-L + 46, 56), (L - 62, 56), (L - 62, 58), (-L + 46, 58)][::-1], -W + 4, W - 4)   # roof
    m.slab("taxi", [(-12, 58), (12, 58), (10, 66), (-10, 66)][::-1], -10, 10)                        # roof sign
    m.slab("car_glass", [(-L - 1, 14), (L + 1, 14), (L + 1, 18), (-L - 1, 18)][::-1], -W - 1, W + 1)   # bumpers
    for x in (-L + 26, L - 26):
        for y in (-W + 4, W - 4):
            m.tube("tyre", (x, y - 5, 13), (x, y + 5, 13), 13, 13, 12)
    for y in (-W + 8, W - 8):
        m.tube("bulb", (L + 1, y, 30), (L + 2, y, 30), 4, 4, 8)                       # headlamps
    return m


def lex_pendant():
    """Lexington Passage pendant, origin at the ceiling: gold canopy and rod, a brass dome
    shade with a rim, a glowing bowl under it."""
    m = Mesh()
    m.lathe("gold", [(0, -4), (8, -4), (9, -1), (7, 0), (0, 0)], 0, 0, 0, 16)       # canopy
    m.cyl("gold", 0, 0, 1, -30, -4, 8)                                              # rod
    m.lathe("gold", [(0, -48), (16, -48), (18, -46), (17, -44), (13, -38), (7, -32), (3, -30), (0, -30)],
            0, 0, 0, 24)                                                            # dome shade
    m.lathe("bulb", [(0, -53), (10, -51), (15, -48), (0, -48)], 0, 0, 0, 24)        # glowing bowl
    return m


def mk_rail():
    """Brass guard rail for the Market display window, origin at its west end on the floor,
    running 332 u along +x: turned posts, top rail and a lower rail."""
    m = Mesh()
    L = 332
    for i in range(5):
        x = L * i / 4
        m.lathe("gold", [(0, 0), (3, 0), (3, 2), (1.2, 4), (1.2, 34), (2, 36), (0, 37)], x, 0, 0, 10)
    m.tube("gold", (0, 0, 36), (L, 0, 36), 1.6, 1.6, 10)
    m.tube("gold", (0, 0, 12), (L, 0, 12), 0.9, 0.9, 8)
    return m


def pit_rail(L):
    """Brass railing across a track pit end, origin at its west end on the platform floor,
    running L u along +x: turned posts every 48 u or so, top rail and a lower rail."""
    def build():
        m = Mesh()
        n = max(2, round(L / 48))
        for i in range(n + 1):
            x = L * i / n
            m.lathe("gold", [(0, 0), (2.4, 0), (2.4, 2), (1, 4), (1, 40), (1.8, 42), (0, 43)], x, 0, 0, 8)
        m.tube("gold", (0, 0, 42), (L, 0, 42), 1.8, 1.8, 10)
        m.tube("gold", (0, 0, 21), (L, 0, 21), 1, 1, 8)
        return m
    return build


def root_chandelier():
    """Grand Central Market's Root Chandelier (Donald Lipski, 1999): an upturned tree's roots in
    pale silver spreading from the dome crown, crystal drops on the tips. Origin at the ceiling,
    about 25 ft across and 9 ft deep. Seeded, so every build is the same."""
    rnd = random.Random(1999)
    m = Mesh()
    m.lathe("root", [(0, -6), (14, -6), (16, -2), (12, 0), (0, 0)], 0, 0, 0, 16)    # crown plate
    m.tube("root", (0, 0, -4), (0, 0, -30), 9, 7, 8)                               # trunk
    m.lathe("bulb", [(0, -10), (18, -10), (18, -8), (0, -8)], 0, 0, 0, 16)        # uplight ring

    def grow(p, yaw, pitch, ln, r, depth):
        d = (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch))
        q = (p[0] + d[0] * ln, p[1] + d[1] * ln, p[2] + d[2] * ln)
        m.tube("root", p, q, r, r * 0.65, 6)
        if depth == 0 or math.hypot(q[0], q[1]) > 150:
            # Crystal drop on a short wire under each tip.
            m.blob("bulb", (q[0], q[1], q[2] - 5), 1.6, 1.6, 3.2, 4)
            return
        for _ in range(2 if depth < 3 else rnd.choice((2, 3))):
            grow(q, yaw + rnd.uniform(-0.6, 0.6), max(-1.3, pitch + rnd.uniform(-0.45, 0.15)),
                 ln * rnd.uniform(0.6, 0.8), r * 0.65, depth - 1)

    for k in range(9):
        yaw = 2 * math.pi * k / 9 + rnd.uniform(-0.15, 0.15)
        grow((0, 0, -24), yaw, rnd.uniform(-0.35, -0.15), rnd.uniform(48, 60), 5, 4)
    return m


MODELS = {"pit_rail_240": pit_rail(240), "pit_rail_420": pit_rail(420), "mk_rail": mk_rail, "root_chandelier": root_chandelier, "lex_pendant": lex_pendant, "eagle": eagle, "taxi": taxi, "statue_group": statue_group, "chandelier": chandelier, "vh_chandelier": vh_chandelier}


def build():
    SRC.mkdir(parents=True, exist_ok=True)
    MAT.mkdir(parents=True, exist_ok=True)
    for name, text in VMTS.items():
        (MAT / f"{name}.vmt").write_text(text, encoding="ascii", newline="\n")
    gmat = G / "garrysmod" / "materials" / "models" / "gcs"
    gmat.mkdir(parents=True, exist_ok=True)
    for f in MAT.glob("*.vmt"):
        shutil.copy(f, gmat)
    out = ROOT / "src" / "models" / "gcs"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        (SRC / f"{name}.smd").write_text(fn().smd(), encoding="ascii", newline="\n")
        (SRC / f"{name}.qc").write_text(
            f'$modelname "gcs/{name}.mdl"\n$body body "{name}.smd"\n$cdmaterials "models/gcs/"\n'
            f'$staticprop\n$surfaceprop "metal"\n$sequence idle "{name}.smd"\n', encoding="ascii", newline="\n")
        r = subprocess.run([str(G / "bin" / "studiomdl.exe"), "-game", str(G / "garrysmod"), "-nop4",
                            str(SRC / f"{name}.qc")], capture_output=True, text=True)
        if r.returncode or "ERROR" in r.stdout:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-1000:])
        built = G / "garrysmod" / "models" / "gcs"
        for f in built.glob(f"{name}.*"):
            shutil.copy(f, out)
        print("built", name, sorted(p.name for p in out.glob(f"{name}.*")))


if __name__ == "__main__":
    build()
