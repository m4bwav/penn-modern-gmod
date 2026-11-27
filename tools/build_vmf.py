"""Build src/gm_penn_modern.vmf: today's New York Penn Station and Moynihan Train Hall at 1 ft = 12 u.

Blockout stage (session 2): Moynihan Train Hall with escalator wells down to a stub of the West End
Concourse, two-storey side halls with the 20 ft balcony, the wall band up to the truss springing,
and the skylight as a sky ceiling. The transverse trusses, secondary steel and clock are MDL
(tools/pm_models.py) placed as prop_static. Sizes: ai-docs/notes/moynihan-dimensions.md.
Patterns for vaults, bays, arches, lights and the tonemap: tools/penn1910_build_vmf.py.
Run: python tools/build_vmf.py
"""
from pathlib import Path

import vmf_lib
from vmf_lib import box, ent, nid, yprism, _id

FT = 12
OUT = Path(__file__).resolve().parent.parent / "src" / "gm_penn_modern.vmf"

# Moynihan Train Hall, inside the Farley Building's former mail-sorting room. Long axis = x
# (east-west, +x toward Eighth Avenue and Penn Station across it).
HX, HY = 200 * FT // 2, 155 * FT // 2     # 200 x 155 ft = 31,000 sq ft (cited area, derived aspect)
H = 92 * FT                               # skylight 92 ft (cited)
SPRING = 50 * FT                          # truss springing (derived)
BALC = 20 * FT                            # balcony level (cited)
SIDE = 25 * FT                            # depth of each side hall under the balcony (derived)
T = 64                                    # shell thickness
SLAB = 24                                 # hall floor slab over the lower concourse
# West End Concourse stub under the hall: the escalators land here (derived, ~30 ft down).
LZ = -30 * FT
LX, LY = 70 * FT, 40 * FT
WX = 28 * FT                              # escalator wells run x = -WX..WX
WELLS = ((-26 * FT, -14 * FT), (14 * FT, 26 * FT))   # y ranges of the two wells
TRUSS_X = (-50 * FT, 0, 50 * FT)          # 3 transverse trusses, 4 bays (counted in the CC0 wide shots)
TEX_FLOOR = "pennmodern/floor_marble"     # tools/pm_textures.py
TEX_WALL = "pennmodern/wall_stone"
TEX_TRIM = "pennmodern/trim_dark"
TEX_SHOP = "pennmodern/storefront"
BOARDS = ("pennmodern/board_name", "pennmodern/board_info")
# Board textures are 1024 x 512 mapped once onto a 30 x 15 ft face (360 x 180 u): faces start on
# multiples of 360 in x and 180 in z so the texture origin lines up.
vmf_lib.SCALE.update({TEX_FLOOR: 0.375, TEX_WALL: 0.5, TEX_TRIM: 0.25, TEX_SHOP: 0.375,
                      BOARDS[0]: 0.3515625, BOARDS[1]: 0.3515625})
TEX_GLASS = "glass/glasswindow007a"
TEX_SKY = "tools/toolsskybox"


def hall(W):
    # Shell: walls from the lower concourse floor up, sky ceiling (the skylight for now).
    W(box(-HX - T, -HY - T, H, HX + T, HY + T, H + T, TEX_SKY))
    W(box(-HX - T, -HY - T, -SLAB, -HX, HY + T, H, TEX_WALL))
    W(box(HX, -HY - T, -SLAB, HX + T, HY + T, H, TEX_WALL))
    W(box(-HX, -HY - T, -SLAB, HX, -HY, H, TEX_WALL))
    W(box(-HX, HY, -SLAB, HX, HY + T, H, TEX_WALL))
    # Floor slab with the two escalator wells cut out of the middle strip.
    W(box(-HX, -HY, -SLAB, -WX, HY, 0, TEX_FLOOR))
    W(box(WX, -HY, -SLAB, HX, HY, 0, TEX_FLOOR))
    ys = [-HY] + [v for w in WELLS for v in w] + [HY]
    for y0, y1 in zip(ys[::2], ys[1::2]):
        W(box(-WX, y0, -SLAB, WX, y1, 0, TEX_FLOOR))
    # Glass balustrades round the wells, 42 in.
    for y0, y1 in WELLS:
        for x0, x1, ya, yb in ((-WX, WX, y0 - 2, y0), (-WX, WX, y1, y1 + 2), (-WX - 2, -WX, y0 - 2, y1 + 2),
                               (WX, WX + 2, y0 - 2, y1 + 2)):
            W(box(x0, ya, 0, x1, yb, 42, TEX_GLASS))


def lower(W):
    # West End Concourse stub, sealed on its own; open to the hall only through the wells.
    W(box(-LX - T, -LY - T, LZ - T, LX + T, LY + T, LZ, TEX_FLOOR))
    W(box(-LX - T, -LY - T, LZ, -LX, LY + T, -SLAB, TEX_WALL))
    W(box(LX, -LY - T, LZ, LX + T, LY + T, -SLAB, TEX_WALL))
    W(box(-LX, -LY - T, LZ, LX, -LY, -SLAB, TEX_WALL))
    W(box(-LX, LY, LZ, LX, LY + T, -SLAB, TEX_WALL))
    # Escalators blocked out as ramps (about 27 degrees): the south well climbs west to east,
    # the north well east to west, so both ends of the hall reach the concourse.
    for (y0, y1), up_east in zip(WELLS, (True, False)):
        poly = [(-WX, LZ), (WX, LZ), (WX, 0)] if up_east else [(-WX, LZ), (WX, LZ), (-WX, 0)]
        W(yprism(poly, y0, y1, TEX_TRIM))


def board_uv(x0, s=0.3515625):
    # Read left to right from the hall: a face with normal +y is seen looking -y, so its right is -x.
    # Shift puts the board's left edge on the texture's left edge. Built per face, so the end faces
    # (x normals) just get a sliver of it.
    def uv(n):
        sx = -1 if n[1] > 0 else 1
        left = x0 if sx > 0 else -(x0 + 360)
        return "[%d 0 0 %g] %g" % (sx, -left / s, s), "[0 0 -1 0] %g" % s
    return uv


def side_halls(W, E):
    # Under each balcony: piers every 25 ft along the edge, the balcony slab, a glass rail,
    # storefront back wall; above it the wall band runs up to the truss springing.
    for sgn in (-1, 1):
        edge = sgn * (HY - SIDE)
        y0, y1 = sorted((edge, sgn * HY))
        for k in range(-3, 4):
            x = k * 25 * FT
            W(box(x - 18, edge - 18, 0, x + 18, edge + 18, BALC, TEX_TRIM))
        W(box(-HX, y0, BALC, HX, y1, BALC + 18, TEX_TRIM))
        ra, rb = sorted((edge, edge - sgn * 2))
        W(box(-HX, ra, BALC + 18, HX, rb, BALC + 18 + 42, TEX_GLASS))
        # Over the balcony: a lit, glazed upper floor (shop and office fronts), then the wall band
        # up to the truss springing, both set back 8 ft.
        wa, wb = sorted((sgn * (HY - 8 * FT), sgn * HY))
        up = BALC + 18 + 14 * FT
        W(box(-HX, wa, BALC + 18, HX, wb, up, TEX_SHOP))
        W(box(-HX, wa, up, HX, wb, SPRING, TEX_WALL))
        # Lit shop fronts on the back wall under the balcony, between the end walls.
        sa, sb = sorted((sgn * (HY - 4), sgn * HY))
        W(box(-HX, sa, 0, HX, sb, BALC, TEX_SHOP))
        # LED boards hung in front of the wall band, 30 x 15 ft.
        ba, bb = sorted((sgn * (HY - 8 * FT - 8), sgn * (HY - 8 * FT)))
        for x0, tex in ((-720, BOARDS[0]), (360, BOARDS[1])):
            vmf_lib.FACEUV[tex] = board_uv(x0)
            W(box(x0, ba, 360, x0 + 360, bb, 540, tex))
        E(ent("light", (0, sgn * (HY - SIDE // 2), BALC - 24), _light="255 240 215 120"))
        E(ent("light", (0, sgn * (HY - 4 * FT), BALC + 8 * FT), _light="255 240 215 80"))


def props(E):
    # studiomdl turns SMD +x to the prop's +y: yaw 90 puts the trusses across the hall (N-S).
    for x in TRUSS_X:
        E(ent("prop_static", (x, 0, SPRING), model="models/pennmodern/truss.mdl", angles="0 90 0", solid="0",
              disableshadows="1"))
    E(ent("prop_static", (0, 0, SPRING), model="models/pennmodern/purlins.mdl", angles="0 90 0", solid="0",
          disableshadows="1"))
    E(ent("prop_static", (0, 0, SPRING), model="models/pennmodern/skylight.mdl", angles="0 90 0", solid="0",
          disableshadows="1"))
    E(ent("prop_static", (0, 0, H - 4 * FT), model="models/pennmodern/clock.mdl", angles="0 0 0",
          solid="6"))


def build():
    world, ents = [], []
    W, E = world.append, ents.append
    hall(W)
    lower(W)
    side_halls(W, E)
    props(E)
    ents += [
        ent("light_environment", (0, 0, H - 64), angles="-60 30 0", pitch="-60",
            _light="255 245 225 300", _ambient="170 190 220 60"),
        ent("light", (0, 0, SPRING), _light="240 235 225 80"),
        ent("light", (0, 0, LZ + 9 * FT), _light="240 240 235 90"),
        ent("light", (-50 * FT, 0, LZ + 9 * FT), _light="240 240 235 60"),
        ent("light", (50 * FT, 0, LZ + 9 * FT), _light="240 240 235 60"),
        ent("info_player_start", (-HX + 200, 0, 8), angles="0 0 0"),
        ent("env_cubemap", (0, 0, 200)),
        ent("env_cubemap", (0, 0, LZ + 100)),
    ]
    NL = "\n"
    world_s = ('world' + NL + '{' + NL + '\t"id" "%d"' + NL + '\t"mapversion" "1"' + NL + '\t"classname" "worldspawn"' + NL
               + '\t"skyname" "sky_day01_01"' + NL + '%s}' + NL) % (nid(), "".join(world))
    head = ('versioninfo' + NL + '{' + NL + '\t"editorversion" "400"' + NL + '\t"editorbuild" "8000"' + NL + '\t"mapversion" "1"' + NL
            + '\t"formatversion" "100"' + NL + '\t"prefab" "0"' + NL + '}' + NL)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + world_s + "".join(ents), encoding="ascii", newline=NL)
    print("wrote", OUT, _id[0], "ids")


if __name__ == "__main__":
    build()
