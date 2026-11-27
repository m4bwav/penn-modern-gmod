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
TEX_PYLON = "pennmodern/pylon_screen"     # 256 x 256 mapped once onto the pylon's 36 u screen
BOARDS = ("pennmodern/board_name", "pennmodern/board_info")
# Board textures are 1024 x 512 mapped once onto a 30 x 15 ft face (360 x 180 u): faces start on
# multiples of 360 in x and 180 in z so the texture origin lines up.
vmf_lib.SCALE.update({TEX_FLOOR: 0.375, TEX_WALL: 0.5, TEX_TRIM: 0.25, TEX_SHOP: 0.375,
                      BOARDS[0]: 0.3515625, BOARDS[1]: 0.3515625, TEX_PYLON: 0.140625})
TEX_GLASS = "glass/glasswindow007a"
STW, STL = 6 * FT, 22 * 16                # balcony stair: 6 ft wide, 22 risers of 12 u on 16 u treads
TEX_SKY = "tools/toolsskybox"
# Area 2, the LIRR concourse (2023 rebuild) east of Eighth Avenue at the West End Concourse level.
# Sizes: ai-docs/notes/lirr-dimensions.md. Long axis x, +x east toward Seventh Avenue.
CW, CH = 15 * FT, 12 * FT                 # passage under Eighth Avenue: 30 ft wide, 12 ft high (derived)
CX0 = 2040                                # concourse west wall (passage ~90 ft long, derived)
CX1 = CX0 + 400 * FT                      # 400 ft modelled (derived slice of the corridor)
CY = 342                                  # 57 ft wide (doubled in 2023, derived from 'doubled')
CC = LZ + 18 * FT                         # 18 ft ceiling (cited: 'at least 18 feet')
PX0, PX1 = 4200, 5400                     # 33rd Street entry pavilion, lit coffered ceiling (derived)
PZ = 10 * FT                              # pavilion ceiling, 40 ft over the concourse floor (derived)
MX = 5072                                 # street-level mezzanine x = MX..PX1 at z 0, escalator up to it
EY0, EY1 = -272, -128                     # escalator band (escalator.mdl, 12 ft wide)
COLY = 60                                 # column row, where the wood and white ceilings meet
TEX_GRANITE = "pennmodern/floor_granite"
TEX_WOOD = "pennmodern/ceil_wood"
TEX_CWHITE = "pennmodern/ceil_white"
TEX_LIGHTBOX = "pennmodern/lightbox"
TEX_COL = "pennmodern/column_blue"        # 512 tall, mapped once onto the 216 u column (col_uv)
TEX_WWHITE = "pennmodern/wall_white"
TEX_SIGN = "pennmodern/sign_band"         # 1024 x 128 overhead wayfinding band, 40 x 5 ft
vmf_lib.SCALE.update({TEX_GRANITE: 0.1875, TEX_LIGHTBOX: 0.46875, TEX_CWHITE: 0.375, TEX_WWHITE: 0.375})


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
    # No balustrade across the top end of each escalator (south well tops out east, north west).
    for (y0, y1), top_east in zip(WELLS, (True, False)):
        ends = [(-WX - 2, -WX)] if top_east else [(WX, WX + 2)]
        for x0, x1, ya, yb in [(-WX, WX, y0 - 2, y0), (-WX, WX, y1, y1 + 2)] + [(a, b, y0 - 2, y1 + 2) for a, b in ends]:
            W(box(x0, ya, 0, x1, yb, 42, TEX_GLASS))


def lower(W):
    # West End Concourse stub, sealed on its own; open to the hall only through the wells.
    W(box(-LX - T, -LY - T, LZ - T, LX + T, LY + T, LZ, TEX_FLOOR))
    W(box(-LX - T, -LY - T, LZ, -LX, LY + T, -SLAB, TEX_WALL))
    # East wall with the opening to the passage under Eighth Avenue (lirr()).
    W(box(LX, -LY - T, LZ, LX + T, -CW, -SLAB, TEX_WALL))
    W(box(LX, CW, LZ, LX + T, LY + T, -SLAB, TEX_WALL))
    W(box(LX, -CW, LZ + CH, LX + T, CW, -SLAB, TEX_WALL))
    W(box(-LX, -LY - T, LZ, LX, -LY, -SLAB, TEX_WALL))
    W(box(-LX, LY, LZ, LX, LY + T, -SLAB, TEX_WALL))
    # Escalators blocked out as ramps (about 27 degrees): the south well climbs west to east,
    # the north well east to west, so both ends of the hall reach the concourse.
    for (y0, y1), up_east in zip(WELLS, (True, False)):
        poly = [(-WX, LZ), (WX, LZ), (WX, 0)] if up_east else [(-WX, LZ), (WX, LZ), (-WX, 0)]
        W(yprism(poly, y0, y1, "tools/toolsplayerclip"))   # walkable clip under escalator.mdl


def col_uv(n, s=216 / 512):
    if abs(n[2]) > 0.5:
        return vmf_lib.axes_for(n, s)
    u = "[%d %d 0 0] %g" % (((0, 1) if abs(n[0]) > 0.5 else (1, 0)) + (s,))
    return u, "[0 0 -1 %g] %g" % (CC / s, s)


def sign_uv(n, s=480 / 1024):
    # Band spans y = -CY..-CY + 480; read left to right from the west (normal -x) and the east (+x).
    if abs(n[0]) < 0.5:
        return vmf_lib.axes_for(n, 0.25)
    if n[0] < 0:
        u = "[0 -1 0 %g] %g" % ((-CY + 480) / s, s)
    else:
        u = "[0 1 0 %g] %g" % (CY / s, s)
    return u, "[0 0 -1 %g] %g" % ((PZ - 60) / s, s)


def lirr(W, E):
    # Passage under Eighth Avenue from the West End Concourse stub to the LIRR concourse.
    W(box(LX + T, -CW - T, LZ - T, CX0, CW + T, LZ, TEX_GRANITE))
    W(box(LX + T, -CW - T, LZ, CX0 - T, -CW, LZ + CH, TEX_WWHITE))
    W(box(LX + T, CW, LZ, CX0 - T, CW + T, LZ + CH, TEX_WWHITE))
    W(box(LX + T, -CW - T, LZ + CH, CX0 - T, CW + T, LZ + CH + T, TEX_CWHITE))
    # Concourse shell: floor, side walls and roof over the full height of the pavilion.
    top = PZ + T
    W(box(CX0 - T, -CY - T, LZ - T, CX1 + T, CY + T, LZ, TEX_GRANITE))
    W(box(CX0 - T, -CY - T, LZ, CX1 + T, -CY, top, TEX_WWHITE))
    W(box(CX0 - T, CY, LZ, CX1 + T, CY + T, top, TEX_WWHITE))
    W(box(CX0 - T, -CY, PZ, CX1 + T, CY, top, TEX_LIGHTBOX))
    W(box(CX1, -CY, LZ, CX1 + T, CY, PZ, TEX_WWHITE))
    W(box(CX0 - T, -CY, LZ, CX0, -CW, PZ, TEX_WWHITE))
    W(box(CX0 - T, CW, LZ, CX0, CY, PZ, TEX_WWHITE))
    W(box(CX0 - T, -CW, LZ + CH, CX0, CW, PZ, TEX_WWHITE))
    # 18 ft ceilings either side of the pavilion: wood slats south of the column row, white north.
    for x0, x1 in ((CX0, PX0 - T), (PX1 + T, CX1)):
        W(box(x0, -CY, CC, x1, COLY, CC + T, TEX_WOOD))
        W(box(x0, COLY, CC, x1, CY, CC + T, TEX_CWHITE))
    # Bulkheads where the ceiling steps up into the pavilion.
    W(box(PX0 - T, -CY, CC, PX0, CY, PZ, TEX_WWHITE))
    W(box(PX1, -CY, CC, PX1 + T, CY, PZ, TEX_WWHITE))
    # Column row: white-and-blue columns every 30 ft; in the pavilion they run white to the ceiling.
    vmf_lib.FACEUV[TEX_COL] = col_uv
    for x in range(CX0 + 360, CX1, 360):
        if MX - 24 < x < PX1 + 24:
            continue
        W(box(x - 15, COLY - 15, LZ, x + 15, COLY + 15, CC, TEX_COL))
        if PX0 < x < PX1:
            W(box(x - 15, COLY - 15, CC, x + 15, COLY + 15, PZ, TEX_WWHITE))
    # Street-level mezzanine at the east end of the pavilion (33rd Street entrance, sealed until area 6),
    # reached by the escalator; glass rail on its open edge except over the escalator.
    W(box(MX, -CY, -18, PX1, CY, 0, TEX_GRANITE))
    for ya, yb in ((-CY, EY0), (EY1, CY)):
        W(box(MX, ya, 0, MX + 2, yb, 42, TEX_GLASS))
    W(yprism([(MX - 672, LZ), (MX, LZ), (MX, 0)], EY0, EY1, "tools/toolsplayerclip"))
    E(ent("prop_static", (MX - 336, (EY0 + EY1) // 2, 0), model="models/pennmodern/escalator.mdl",
          angles="0 90 0", solid="0", disableshadows="1"))
    # Shops along the north wall of the pavilion and a wayfinding band hung across it.
    W(box(PX0, CY - 4, LZ, MX, CY, LZ + 14 * FT, TEX_SHOP))
    vmf_lib.FACEUV[TEX_SIGN] = sign_uv
    W(box(PX0 + 300, -CY, PZ - 120, PX0 + 304, -CY + 480, PZ - 60, TEX_SIGN))
    # Lights: a row down each ceiling, cool fill under the light box.
    for x in range(CX0 + 180, CX1, 360):
        if PX0 < x < PX1:
            continue
        for y in (-170, 200):
            E(ent("light", (x, y, CC - 24), _light="235 240 250 40"))
    for x in (PX0 + 300, PX0 + 700, MX - 100):
        for y in (-180, 180):
            E(ent("light", (x, y, PZ - 80), _light="200 225 255 120"))
    for x in (1200, 1700):
        E(ent("light", (x, 0, LZ + CH - 20), _light="235 240 250 50"))
    E(ent("light", ((MX + PX1) // 2, 0, 100), _light="235 240 250 50"))
    E(ent("env_cubemap", (3000, 0, LZ + 100)))
    E(ent("env_cubemap", (4700, 0, LZ + 100)))


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
        # Balcony slab with an opening at the west end for the stair (band in front of the upper wall).
        sa_, sb_ = sorted((sgn * (HY - 8 * FT - STW), sgn * (HY - 8 * FT)))
        W(box(-HX + STL, y0, BALC, HX, y1, BALC + 18, TEX_TRIM))
        for ya, yb in ((y0, sa_), (sb_, y1)):
            if yb > ya:
                W(box(-HX, ya, BALC, -HX + STL, yb, BALC + 18, TEX_TRIM))
        ra, rb = sorted((edge, edge - sgn * 2))
        W(box(-HX, ra, BALC + 18, HX, rb, BALC + 18 + 42, TEX_GLASS))
        # Stair up to the balcony, climbing east from the west wall; glass rail on the hall side of the opening.
        n = (BALC + 18) // 12
        for i in range(n):
            W(box(-HX + i * 16, sa_, 0, -HX + (i + 1) * 16, sb_, (i + 1) * 12 if i < n - 1 else BALC + 18, TEX_TRIM))
        ga, gb = (sa_ - 2, sa_) if sgn > 0 else (sb_, sb_ + 2)
        W(box(-HX, ga, BALC + 18, -HX + STL, gb, BALC + 18 + 42, TEX_GLASS))
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
        # Warm downlights under the balcony, one per bay between the piers.
        for k in range(-3, 3):
            E(ent("light", (k * 25 * FT + 150, sgn * (HY - SIDE // 2), BALC - 16), _light="255 214 160 45"))
        E(ent("light", (0, sgn * (HY - 4 * FT), BALC + 8 * FT), _light="255 240 215 80"))


def pylon_uv(n, s=0.140625):
    # One 256 texel screen per 36 u face, read left to right, top edge at 8 ft + 36 u.
    if abs(n[1]) > 0.5:
        u = "[%d 0 0 0] %g" % (-1 if n[1] > 0 else 1, s)
    else:
        u = "[0 %d 0 0] %g" % (1 if n[0] > 0 else -1, s)
    return u, "[0 0 -1 %g] %g" % ((8 * FT + 36) / s, s)


def pylons(W):
    # Freestanding black departure pylons at the well ends (the 11/12 track signs), lit screen band on top.
    # x - 18 on a multiple of 36 so pylon_uv starts the screen texture on the face's left edge.
    vmf_lib.FACEUV[TEX_PYLON] = pylon_uv
    for x in (-450, 450):
        for y in (-20 * FT, 20 * FT):
            W(box(x - 18, y - 9, 0, x + 18, y + 9, 8 * FT, TEX_TRIM))
            W(box(x - 18, y - 10, 8 * FT, x + 18, y + 10, 8 * FT + 36, TEX_PYLON))
            W(box(x - 18, y - 9, 8 * FT + 36, x + 18, y + 9, 8 * FT + 42, TEX_TRIM))


def props(E):
    # Escalators: yaw 90 keeps SMD axes = world axes (+x up), yaw 270 climbs toward -x.
    for (y0, y1), yaw in zip(WELLS, (90, 270)):
        E(ent("prop_static", (0, (y0 + y1) // 2, 0), model="models/pennmodern/escalator.mdl", angles="0 %d 0" % yaw,
              solid="0", disableshadows="1"))
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
    pylons(W)
    lirr(W, E)
    props(E)
    ents += [
        ent("light_environment", (0, 0, H - 64), angles="-60 30 0", pitch="-60",
            _light="255 240 215 220", _ambient="170 190 220 35"),
        ent("light", (0, 0, SPRING), _light="240 235 225 40"),
        ent("light", (0, 0, LZ + 9 * FT), _light="240 240 235 90"),
        ent("light", (-50 * FT, 0, LZ + 9 * FT), _light="240 240 235 60"),
        ent("light", (50 * FT, 0, LZ + 9 * FT), _light="240 240 235 60"),
        ent("info_player_start", (-HX + 200, 0, 8), angles="0 0 0"),
        ent("env_cubemap", (0, 0, 200)),
        ent("env_cubemap", (0, 0, LZ + 100)),
    ]
    NL = "\n"
    ents.append(ent("env_tonemap_controller", (0, 0, 64), targetname="tonemap"))
    conn = ['"OnMapSpawn" "tonemap,SetAutoExposureMin,0.5,0,-1"',
            '"OnMapSpawn" "tonemap,SetAutoExposureMax,1.2,0,-1"',
            '"OnMapSpawn" "tonemap,SetBloomScale,0.2,0,-1"']
    block = "\tconnections" + NL + "\t{" + NL + "".join("\t\t" + c + NL for c in conn) + "\t}" + NL + "}" + NL
    ents.append(ent("logic_auto", (0, 0, 96), spawnflags="1")[:-2] + block)
    world_s = ('world' + NL + '{' + NL + '\t"id" "%d"' + NL + '\t"mapversion" "1"' + NL + '\t"classname" "worldspawn"' + NL
               + '\t"skyname" "sky_day01_01"' + NL + '%s}' + NL) % (nid(), "".join(world))
    head = ('versioninfo' + NL + '{' + NL + '\t"editorversion" "400"' + NL + '\t"editorbuild" "8000"' + NL + '\t"mapversion" "1"' + NL
            + '\t"formatversion" "100"' + NL + '\t"prefab" "0"' + NL + '}' + NL)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + world_s + "".join(ents), encoding="ascii", newline=NL)
    print("wrote", OUT, _id[0], "ids")


if __name__ == "__main__":
    build()
