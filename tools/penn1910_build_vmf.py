"""Build src/gm_penn_modern.vmf: the 1910 Pennsylvania Station at 1 ft = 12 u.

Blockout stage: main waiting room. Run: python tools/build_vmf.py
Dimensions: ai-docs/notes/2026-11-26-dimensions.md.
"""
from pathlib import Path

import vmf_lib
from vmf_lib import box, prism, xprism, yprism, halfdisc, ngon, ent, groin, nid, _id

FT = 12
OUT = Path(__file__).resolve().parent.parent / "src" / "gm_penn_modern.vmf"

# Main waiting room: 314 ft 4 in x 108 ft 8 in, 150 ft to the crown. Long axis = x
# runs north-south in the station (+x toward 33rd St); +y is east, toward the arcade and Seventh Avenue;
# -y is west, toward the concourse.
HX, HY = 3772 // 2, 1304 // 2            # 1886, 652
CROWN = 150 * FT                          # 1800
RISE = HY                                 # groin barrels rise half the room width
SPRING = CROWN - RISE - 16                # 1132: groin() adds 16 u above the crown
BAYS = (-HX, -HX // 3, HX // 3, HX)       # three groin bays
T = 8 * FT                                # wall thickness
LUNETTE = 460                             # thermal window radius, 38 ft 4 in
PED = 14 * FT                             # column pedestal (session 5: taller, per the photos)
COL_TOP = PED + 60 * FT                   # capital top, 60 ft above the pedestal
ENT_Z0, ENT_Z1 = COL_TOP, COL_TOP + 14 * FT   # entablature over the columns
ARC_W, ARC_H, LAND = 40 * FT, 30 * FT, 16 * FT  # stair opening to the arcade, landing rise
ARCH_W, ARCH_SPRING = 30 * FT, 45 * FT    # round-headed arches in each long-wall bay, crown 60 ft
FACE = 4 * FT                             # arcade face layer standing proud of the long walls
NICHE, NICHE_H = 4 * FT, ARCH_SPRING + ARCH_W // 2   # recess behind the side arches, up to the crown
# Arcade (area 2): 45 ft x 225 ft at street level, east of the stair hall, five 45 ft groin bays
# lined with shops, Seventh Avenue at its east end.
AHX, AL, ABAY = 45 * FT // 2, 225 * FT, 45 * FT       # 270, 2700, 540
A_SPRING = LAND + 32 * FT                              # 576: vaults spring 32 ft above the arcade floor
YA = HY + T + 60 * FT                                  # 1468: west end of the arcade, top of the stair hall
YB = YA + AL                                           # 4168: Seventh Avenue end
VEST = 40 * FT                                         # entrance vestibule east of the arcade

TEX_FLOOR = "pennmodern/floor_travertine"
TEX_WALL = "pennmodern/travertine_ashlar"
TEX_VAULT = "pennmodern/vault_coffer"
TEX_TRIM = "pennmodern/travertine"
TEX_COL = "pennmodern/travertine"
# Texture scale: 512 px tiles. Ashlar 16 ft (4 ft courses), coffers 12 ft 10 in, floor slabs 10 ft 8 in.
vmf_lib.SCALE.update({TEX_WALL: 0.375, TEX_TRIM: 0.375, TEX_VAULT: 0.6, TEX_FLOOR: 0.5})
TEX_GLASS = "pennmodern/window_glass"
TEX_DOOR = "pennmodern/window_glow"
NODRAW = "tools/toolsnodraw"


def arcade(W, det, ents):
    """Area 2 blockout: the shopping arcade from the stair hall (y = YA) to Seventh Avenue (y = YB),
    floor at LAND, five groin bays, a shopfront in each bay on both sides, a vestibule at the east end."""
    z0, ztop = LAND, A_SPRING + AHX + 16 + 64
    W(box(-AHX - T, YA, z0 - 64, AHX + T, YB, z0, TEX_FLOOR))
    # West end wall over and beside the 40 ft stair hall opening (hall walls stop at YA).
    a, b = -ARC_W // 2, ARC_W // 2
    W(box(-AHX - T, YA - 32, ARC_H + LAND, AHX + T, YA, ztop, TEX_WALL))
    for x0, x1 in ((-AHX - T, a - 32), (b + 32, AHX + T)):
        W(box(x0, YA - 32, z0 - 64, x1, YA, ARC_H + LAND, TEX_WALL))
    # Side walls: per bay a shopfront 30 ft wide, 18 ft high, recessed the wall depth to a lit window.
    SW, SH = 30 * FT, 18 * FT
    for s in (-1, 1):
        x0, x1 = sorted((s * AHX, s * (AHX + T)))
        edges = [YA]
        for i in range(5):
            c = YA + i * ABAY + ABAY // 2
            edges += [c - SW // 2, c + SW // 2]
            W(box(x0, c - SW // 2, z0 + SH, x1, c + SW // 2, ztop, TEX_WALL))
            g0, g1 = sorted((s * (AHX + T), s * (AHX + T + 16)))
            W(box(g0, c - SW // 2, z0 - 64, g1, c + SW // 2, z0 + SH, TEX_DOOR))
            W(box(x0, c - SW // 2, z0 + SH - 16, x1, c + SW // 2, z0 + SH, TEX_TRIM))
        edges.append(YB)
        for i in range(0, len(edges), 2):
            W(box(x0, edges[i], z0 - 64, x1, edges[i + 1], ztop, TEX_WALL))
    for i in range(5):
        groin(W, -AHX, AHX, YA + i * ABAY, YA + (i + 1) * ABAY, A_SPRING, AHX, TEX_VAULT)
    # East end: a 40 ft x 30 ft opening into the entrance vestibule; the street doors glow for now.
    W(box(-AHX - T, YB, ARC_H + LAND, AHX + T, YB + T, ztop, TEX_WALL))
    for x0, x1 in ((-AHX - T, a), (b, AHX + T)):
        W(box(x0, YB, z0 - 64, x1, YB + T, ARC_H + LAND, TEX_WALL))
    v1 = YB + T + VEST
    W(box(a, YB, z0 - 64, b, v1, z0, TEX_FLOOR))
    W(box(a - 32, YB + T, z0 - 64, a, v1 + 32, ARC_H + LAND + 32, TEX_WALL))
    W(box(b, YB + T, z0 - 64, b + 32, v1 + 32, ARC_H + LAND + 32, TEX_WALL))
    W(box(a, YB + T, ARC_H + LAND, b, v1, ARC_H + LAND + 32, TEX_TRIM))
    W(box(a, v1, z0, b, v1 + 32, ARC_H + LAND, TEX_DOOR))
    for i in range(5):
        ents.append(ent("light", (0, YA + i * ABAY + ABAY // 2, A_SPRING), _light="250 225 190 30"))
    ents.append(ent("light", (0, YB + T + VEST // 2, LAND + 20 * FT), _light="250 225 190 15"))
    ents.append(ent("env_cubemap", (0, (YA + YB) // 2, LAND + 200)))


def build():
    world, ents = [], []
    W = world.append
    det = lambda s: ents.append(ent("func_detail", solids=s))

    top = SPRING + RISE + 16 + 64
    # Sealed nodraw hull around everything.
    X0, X1 = -HX - T - 256, HX + T + 256
    Y0, Y1 = -HY - T - 10 * FT - 256, YB + T + VEST + 256
    Z0, Z1 = -128, top + 128
    for b in ((X0, Y0, Z0 - 64, X1, Y1, Z0), (X0, Y0, Z1, X1, Y1, Z1 + 64),
              (X0 - 64, Y0, Z0, X0, Y1, Z1), (X1, Y0, Z0, X1 + 64, Y1, Z1),
              (X0, Y0 - 64, Z0, X1, Y0, Z1), (X0, Y1, Z0, X1, Y1 + 64, Z1)):
        W(box(*b, NODRAW))

    # Floor and end walls (x = +-HX, the 31st and 33rd St ends).
    W(box(-HX - T, -HY - T, -64, HX + T, HY + T, 0, TEX_FLOOR))
    for s in (-1, 1):
        x0, x1 = (HX, HX + T) if s > 0 else (-HX - T, -HX)
        W(box(x0, -HY - T, 0, x1, HY + T, top, TEX_WALL))

    def long_wall(y0, y1, ops, h):
        """Wall along x between y0 and y1 with openings [(x0, x1)] of height h."""
        edges = [-HX] + [v for o in ops for v in o] + [HX]
        for i in range(0, len(edges), 2):
            W(box(edges[i], y0, 0, edges[i + 1], y1, top, TEX_WALL))
        for a, b in ops:
            W(box(a, y0, h, b, y1, top, TEX_WALL))

    # Niches (session 8): behind each side arch the wall steps back 4 ft (NICHE) up to the arch
    # crown, so the arches read as openings into the side passages. The wall proper sits NICHE
    # back from the room face; filler brushes bring the face forward everywhere else.
    def niche_fill(s, gaps):
        """Face brushes between y = s*HY and s*(HY + NICHE), open over gaps [(x0, x1, z_top)]."""
        y0, y1 = sorted((s * HY, s * (HY + NICHE)))
        edges = [-HX] + [v for g in gaps for v in g[:2]] + [HX]
        for i in range(0, len(edges), 2):
            W(box(edges[i], y0, 0, edges[i + 1], y1, top, TEX_WALL))
        for x0, x1, zt in gaps:
            W(box(x0, y0, zt, x1, y1, top, TEX_WALL))
    side = lambda i: ((BAYS[i] + BAYS[i + 1]) // 2 - ARCH_W // 2, (BAYS[i] + BAYS[i + 1]) // 2 + ARCH_W // 2, NICHE_H)

    # West wall (y = -HY): one 20 ft opening per bay toward the concourse, sealed for now.
    ops = [((BAYS[i] + BAYS[i + 1]) // 2 - 120, (BAYS[i] + BAYS[i + 1]) // 2 + 120) for i in range(3)]
    long_wall(-HY - T, -HY - NICHE, ops, ARC_H)
    niche_fill(-1, [side(i) for i in range(3)])
    py = -HY - T - 10 * FT
    for a, b in ops:
        W(box(a - 32, py, 0, a, -HY - T, ARC_H, TEX_WALL))
        W(box(b, py, 0, b + 32, -HY - T, ARC_H, TEX_WALL))
        W(box(a, py, ARC_H, b, -HY - T, ARC_H + 32, TEX_WALL))
        W(box(a, py - 32, -64, b, -HY - T, 0, TEX_FLOOR))
        W(box(a, py - 32, 0, b, py, ARC_H, TEX_DOOR))

    # East wall (y = +HY): the 40 ft stair opening up to the arcade from Seventh Avenue.
    a, b = -ARC_W // 2, ARC_W // 2
    long_wall(HY + NICHE, HY + T, [(a, b)], ARC_H + LAND)
    niche_fill(1, [side(0), (a, b, ARC_H + LAND), side(2)])
    # Stair hall east of the opening: 16 steps up to a landing, sealed door at the arcade end.
    sy0, run, steps = HY, 32 * FT, 16
    sy1 = sy0 + T + 60 * FT
    W(box(a - 32, sy0 + T, -64, a, sy1, ARC_H + LAND + 32, TEX_WALL))
    W(box(b, sy0 + T, -64, b + 32, sy1, ARC_H + LAND + 32, TEX_WALL))
    W(box(a, sy0 + T, ARC_H + LAND, b, sy1, ARC_H + LAND + 32, TEX_TRIM))
    W(box(a, sy0, -64, b, sy0 + T, 0, TEX_FLOOR))
    for i in range(steps):
        y = sy0 + T + i * run // steps
        W(box(a, y, -64, b, y + run // steps, (i + 1) * LAND // steps, TEX_FLOOR))
    W(box(a, sy0 + T + run, -64, b, sy1, LAND, TEX_FLOOR))
    arcade(W, det, ents)

    # Groin vaults over the three bays.
    for i in range(3):
        groin(W, BAYS[i], BAYS[i + 1], -HY, HY, SPRING, RISE, TEX_VAULT)

    # Thermal windows in every lunette: long walls (per bay) and both ends.
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        for s in (-1, 1):
            y = s * HY
            det(yprism(halfdisc(cx, SPRING + 48, LUNETTE, 12), min(y, y - 8 * s), max(y, y - 8 * s), TEX_GLASS))
    for s in (-1, 1):
        x = s * HX
        det(xprism(halfdisc(0, SPRING + 48, LUNETTE, 12), min(x, x - 8 * s), max(x, x - 8 * s), TEX_GLASS))

    # Diocletian mullions: two stone piers split each lunette into three lights, a transom across.
    z0, mw, hz = SPRING + 48, 12, int(LUNETTE * 0.94)
    def mullions(c, wall, s, along_x):
        bars = [(c + d - mw, z0, c + d + mw, z0 + hz) for d in (-LUNETTE // 3, LUNETTE // 3)]
        bars.append((c - LUNETTE + 40, z0 + 168, c + LUNETTE - 40, z0 + 168 + 16))
        bars.append((c - LUNETTE, z0 - 24, c + LUNETTE, z0))
        d0, d1 = sorted((wall - 8 * s, wall - 24 * s))
        for u0, zz0, u1, zz1 in bars:
            det(box(u0, d0, zz0, u1, d1, zz1, TEX_TRIM) if along_x else box(d0, u0, zz0, d1, u1, zz1, TEX_TRIM))
    for i in range(3):
        for s in (-1, 1):
            mullions((BAYS[i] + BAYS[i + 1]) // 2, s * HY, s, True)
    for s in (-1, 1):
        mullions(0, s * HX, s, False)

    # Round-headed arches: one per bay in each long wall, a 4 ft face layer with the arch cut out;
    # the recess shows the wall behind. The east middle bay is the stair opening, so its arch is
    # 40 ft wide and springs at the opening head, with a glass tympanum.
    def arch_face(cx, s, w, zs):
        wy = s * HY
        d0, d1 = sorted((wy, wy - FACE * s))
        r = w // 2
        lo, hi = (BAYS[0], BAYS[1]) if cx < BAYS[1] else ((BAYS[1], BAYS[2]) if cx < BAYS[2] else (BAYS[2], BAYS[3]))
        det(box(lo, d0, 0, cx - r, d1, ENT_Z0, TEX_WALL))
        det(box(cx + r, d0, 0, hi, d1, ENT_Z0, TEX_WALL))
        arc = halfdisc(cx, zs, r, 10)
        for i in range(10):
            (xa, za), (xb, zb) = arc[i + 1], arc[i]          # left to right
            poly = [(xa, za), (xb, zb), (xb, ENT_Z0), (xa, ENT_Z0)]
            det(yprism(poly, d0, d1, TEX_WALL))
        # Archivolt: a plain travertine band round the arch, 6 u proud of the face.
        f0, f1 = (d0 - 6, d0) if s > 0 else (d1, d1 + 6)
        band = halfdisc(cx, zs, r + 18, 10)
        for i in range(10):
            det(yprism([arc[i + 1], arc[i], band[i], band[i + 1]], f0, f1, TEX_TRIM))
        # Impost blocks at the springing.
        for x in (cx - r - 16, cx + r - 2):
            det(box(x, min(d0, d1) - (12 if s > 0 else 0), zs - 24, x + 18, max(d0, d1) + (12 if s < 0 else 0), zs, TEX_TRIM))
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        arch_face(cx, -1, ARCH_W, ARCH_SPRING)
        if i == 1:
            arch_face(cx, 1, ARC_W, ARC_H + LAND)
            det(yprism(halfdisc(cx, ARC_H + LAND, ARC_W // 2, 10), HY - 4, HY, TEX_GLASS))
        else:
            arch_face(cx, 1, ARCH_W, ARCH_SPRING)

    # Entablature band round the room over the column tops.
    for s in (-1, 1):
        y0, y1 = (HY - 4 * FT, HY) if s > 0 else (-HY, -HY + 4 * FT)
        det(box(-HX, y0, ENT_Z0, HX, y1, ENT_Z1, TEX_TRIM))
        x0, x1 = (HX - 4 * FT, HX) if s > 0 else (-HX, -HX + 4 * FT)
        det(box(x0, -HY + 4 * FT, ENT_Z0, x1, HY - 4 * FT, ENT_Z1, TEX_TRIM))

    # Giant Corinthian columns (blockout: pedestal, 12-sided shaft, capital block) at the
    # bay piers and the room corners. The detail pass replaces them with MDL models.
    cols = [(x, s * (HY - 13 * FT)) for x in (BAYS[1], BAYS[2]) for s in (-1, 1)]
    cols += [(sx * (HX - 6 * FT), sy * (HY - 13 * FT)) for sx in (-1, 1) for sy in (-1, 1)]
    for cx, cy in cols:
        det(box(cx - 66, cy - 66, 0, cx + 66, cy + 66, PED, TEX_TRIM))
        ents.append(ent("prop_static", (cx, cy, PED), model="models/pennmodern/corinthian.mdl", solid="6"))
        # The entablature breaks forward over every column.
        wy = HY if cy > 0 else -HY
        det(box(cx - 7 * FT, min(wy, cy - 6 * FT * (1 if cy < 0 else -1)), ENT_Z0,
                cx + 7 * FT, max(wy, cy - 6 * FT * (1 if cy < 0 else -1)), ENT_Z1, TEX_TRIM))
        # Pier behind the column: a pilaster strip of the wall up to the entablature.
        wy = HY if cy > 0 else -HY
        if abs(cx) < HX - 8 * FT:
            det(box(cx - 8 * FT, min(wy, wy - 7 * FT * (1 if cy > 0 else -1)), 0,
                    cx + 8 * FT, max(wy, wy - 7 * FT * (1 if cy > 0 else -1)), ENT_Z0, TEX_WALL))

    # Lights (session 6). Daylight comes in through the thermal windows: the glass panes are texture
    # lights (src/lights.rad), morning sun from the east lunettes falls as light_spot shafts on the
    # floor of the west half, and a dim warm fill keeps the column shadows readable.
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        ents.append(ent("light", (cx, 0, SPRING), _light="235 220 195 35"))
        ents.append(ent("light", (cx, 0, 30 * FT), _light="250 220 180 18"))
        # Sun shaft: from just inside the east lunette, aimed down and west (pitch -50, yaw 270).
        ents.append(ent("light_spot", (cx, HY - 120, SPRING + 160), angles="-50 270 0", pitch="-50",
                        _light="255 236 200 260", _inner_cone="14", _cone="22", _exponent="1",
                        _constant_attn="1", _linear_attn="0", _quadratic_attn="0"))
        ents.append(ent("light", (cx, -(HY - 200), SPRING + 200), _light="195 210 235 25"))
    for s in (-1, 1):
        ents.append(ent("light", (s * (HX - 200), 0, SPRING + 200), _light="195 210 235 25"))
    ents.append(ent("light", (0, HY + T + 40 * FT, LAND + 20 * FT), _light="250 225 190 20"))

    NL = "\n"
    ents.append(ent("env_tonemap_controller", (0, 0, 64), targetname="tonemap"))
    conn = ['"OnMapSpawn" "tonemap,SetAutoExposureMin,0.6,0,-1"',
            '"OnMapSpawn" "tonemap,SetAutoExposureMax,1.6,0,-1"',
            '"OnMapSpawn" "tonemap,SetBloomScale,0.25,0,-1"']
    block = "\tconnections" + NL + "\t{" + NL + "".join("\t\t" + c + NL for c in conn) + "\t}" + NL + "}" + NL
    ents.append(ent("logic_auto", (0, 0, 96), spawnflags="1")[:-2] + block)
    ents.append(ent("info_player_start", (0, YB - 10 * FT, LAND + 8), angles="0 270 0"))
    ents.append(ent("info_player_start", (0, -300, 8), angles="0 0 0"))
    for x in (0, BAYS[1] - 600, BAYS[2] + 600):
        ents.append(ent("env_cubemap", (x, 0, 200)))

    world_s = ('world' + NL + '{' + NL + '\t"id" "%d"' + NL + '\t"mapversion" "1"' + NL + '\t"classname" "worldspawn"' + NL
               + '\t"skyname" "sky_day01_01"' + NL + '%s}' + NL) % (nid(), "".join(world))
    head = ('versioninfo' + NL + '{' + NL + '\t"editorversion" "400"' + NL + '\t"editorbuild" "8000"' + NL + '\t"mapversion" "1"' + NL
            + '\t"formatversion" "100"' + NL + '\t"prefab" "0"' + NL + '}' + NL)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + world_s + "".join(ents), encoding="ascii", newline=NL)
    print("wrote", OUT, _id[0], "ids")


if __name__ == "__main__":
    build()
