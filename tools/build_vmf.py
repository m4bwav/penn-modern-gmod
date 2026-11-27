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
# Area 3, the Amtrak (main) concourse: one level below the street and one above the LIRR concourse
# (cited), south of the LIRR corridor under Madison Square Garden. Sizes: ai-docs/notes/amtrak-dimensions.md.
AZ = -20 * FT                             # floor 20 ft below the street, 10 ft above the LIRR floor (derived)
AC = AZ + 14 * FT                         # 14 ft louvred ceiling (derived)
RZ = AZ + 18 * FT                         # raised centre ceiling over the escalator atrium (derived)
AX0, AX1 = 2000, 2000 + 240 * FT          # 240 x 150 ft hall (derived)
AY1 = -CY - T - 256                       # north wall: a 21 ft stair passage up from the LIRR corridor
AY0 = AY1 - 150 * FT
SX0, SX1 = 2928, 3120                     # 16 ft stair opening in the LIRR south wall (clear of the TVM banks)
RX0, RX1, RY0, RY1 = 2720, 4160, -1920, -1200   # raised ceiling
EX0, EX1 = 3700, 3700 + 56 * FT           # escalator well (escalator.mdl run), down 30 ft toward the tracks
EYC = -1560
WRX, WRY = 2720, -2000                    # glazed ticketed waiting room in the south-west corner
TEX_TERRAZZO = "pennmodern/floor_terrazzo"
TEX_CAM = "pennmodern/ceil_amtrak"
TEX_AMBOARD = "pennmodern/amboard"        # 1024 x 256, mapped once onto a 40 x 10 ft face
vmf_lib.SCALE.update({TEX_TERRAZZO: 0.5, TEX_CAM: 0.75})


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
    # South wall with the stair opening up to the Amtrak concourse (amtrak()).
    W(box(CX0 - T, -CY - T, LZ, SX0, -CY, top, TEX_WWHITE))
    W(box(SX1, -CY - T, LZ, CX1 + T, -CY, top, TEX_WWHITE))
    W(box(SX0, -CY - T, CC, SX1, -CY, top, TEX_WWHITE))
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
        if not PX0 < x < PX1:
            E(ent("prop_static", (x, COLY, LZ), model="models/pennmodern/colboard.mdl", angles="0 90 0",
                  disableshadows="1"))
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
    # Ticket machines in banks of four on the south wall, screens facing into the concourse.
    for xb in (CX0 + 600, CX0 + 2400, PX0 + 120):
        for k in range(4):
            E(ent("prop_static", (xb + k * 40, -CY + 20, LZ), model="models/pennmodern/tvm.mdl", angles="0 270 0",
                  disableshadows="1"))
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


def amboard_uv(x0, top, s=480 / 1024):
    # Board face looks -y (seen from the hall looking north, its right is +x).
    def uv(n):
        if n[1] > -0.5:
            return vmf_lib.axes_for(n, 0.25)
        return "[1 0 0 %g] %g" % (-x0 / s, s), "[0 0 -1 %g] %g" % (top / s, s)
    return uv


def amtrak(W, E):
    top = RZ + T
    py0 = -CY - T                          # passage from the LIRR south wall to the hall's north wall
    # Stair passage: 10 risers of 12 u on 16 u treads from the LIRR floor up to AZ, then a landing.
    W(box(SX0 - T, AY1, LZ - T, SX0, py0, -56, TEX_WWHITE))
    W(box(SX1, AY1, LZ - T, SX1 + T, py0, -56, TEX_WWHITE))
    W(box(SX0, AY1, -120, SX1, py0, -56, TEX_CWHITE))
    for i in range(10):
        W(box(SX0, py0 - 16 * (i + 1), LZ - T, SX1, py0 - 16 * i, LZ + 12 * (i + 1), TEX_GRANITE))
    W(box(SX0, AY1 - T, LZ - T, SX1, py0 - 160, AZ, TEX_TERRAZZO))
    # Hall shell: walls to the raised roof; the north wall is open over the stair landing.
    W(box(AX0 - T, AY0 - T, AZ - T, AX0, AY1 + T, top, TEX_WWHITE))
    W(box(AX1, AY0 - T, AZ - T, AX1 + T, AY1 + T, top, TEX_WWHITE))
    W(box(AX0, AY0 - T, AZ - T, AX1, AY0, top, TEX_WWHITE))
    W(box(AX0, AY1, AZ - T, SX0, AY1 + T, top, TEX_WWHITE))
    W(box(SX1, AY1, AZ - T, AX1, AY1 + T, top, TEX_WWHITE))
    W(box(SX0, AY1, -120, SX1, AY1 + T, top, TEX_WWHITE))
    # Floor with the escalator well cut out.
    wy0, wy1 = EYC - 72, EYC + 72
    W(box(AX0, AY0, AZ - T, EX0, AY1, AZ, TEX_TERRAZZO))
    W(box(EX1, AY0, AZ - T, AX1, AY1, AZ, TEX_TERRAZZO))
    W(box(EX0, AY0, AZ - T, EX1, wy0, AZ, TEX_TERRAZZO))
    W(box(EX0, wy1, AZ - T, EX1, AY1, AZ, TEX_TERRAZZO))
    # Louvred 14 ft ceiling round the raised centre, which steps up 4 ft over the atrium.
    for x0, y0, x1, y1 in ((AX0, AY0, RX0, AY1), (RX1, AY0, AX1, AY1), (RX0, AY0, RX1, RY0), (RX0, RY1, RX1, AY1)):
        W(box(x0, y0, AC, x1, y1, top, TEX_CAM))
    W(box(RX0, RY0, RZ, RX1, RY1, top, TEX_CWHITE))
    # Escalator down toward the tracks: sealed landing 30 ft below until area 5 adds the platforms.
    lz = AZ - 30 * FT
    lx0, ly0, ly1 = EX0 - 240, EYC - 140, EYC + 140
    W(box(lx0 - T, ly0 - T, lz - T, EX1 + T, ly1 + T, lz, TEX_GRANITE))
    W(box(lx0 - T, ly0 - T, lz, lx0, ly1 + T, AZ - T, TEX_WWHITE))
    W(box(EX1, ly0 - T, lz, EX1 + T, ly1 + T, AZ - T, TEX_WWHITE))
    W(box(lx0, ly0 - T, lz, EX1, ly0, AZ - T, TEX_WWHITE))
    W(box(lx0, ly1, lz, EX1, ly1 + T, AZ - T, TEX_WWHITE))
    W(yprism([(EX0, lz), (EX1, lz), (EX1, AZ)], EYC - 63, EYC + 63, "tools/toolsplayerclip"))
    E(ent("prop_static", ((EX0 + EX1) // 2, EYC, AZ), model="models/pennmodern/escalator.mdl", angles="0 90 0",
          solid="0", disableshadows="1"))
    # Glass rail round the well, open at the top (east) end of the escalator.
    for x0, x1, ya, yb in ((EX0, EX1, wy0 - 2, wy0), (EX0, EX1, wy1, wy1 + 2), (EX0 - 2, EX0, wy0 - 2, wy1 + 2)):
        W(box(x0, ya, AZ, x1, yb, AZ + 42, TEX_GLASS))
    # Blue columns with light halos (amcol.mdl) on a 30 ft grid north and south of the atrium.
    for x in range(AX0 + 360, AX1, 360):
        for y in (AY1 - 360, AY0 + 360):
            if not (x < WRX + 40 and y < WRY):
                E(ent("prop_static", (x, y, AZ), model="models/pennmodern/amcol.mdl", angles="0 0 0"))
    # Departures board on the north wall, east of the stair.
    bx = 3360
    vmf_lib.FACEUV[TEX_AMBOARD] = amboard_uv(bx, AZ + 160)
    W(box(bx, AY1 - 8, AZ + 40, bx + 480, AY1, AZ + 160, TEX_AMBOARD))
    # Ticket counters along the west wall: lit back office, counter, glass screen above it.
    W(box(AX0, -1900, AZ, AX0 + 4, -1100, AC, TEX_SHOP))
    W(box(AX0 + 60, -1900, AZ, AX0 + 96, -1100, AZ + 42, TEX_TRIM))
    W(box(AX0 + 60, -1900, AZ + 42, AX0 + 62, -1100, AZ + 96, TEX_GLASS))
    # Shops along the south wall east of the waiting room.
    W(box(WRX + 120, AY0, AZ, AX1, AY0 + 4, AZ + 12 * FT, TEX_SHOP))
    # Ticketed waiting room: glazed walls to the ceiling with a 10 ft door, rows of black seats.
    W(box(WRX, AY0, AZ, WRX + 4, WRY, AC, TEX_GLASS))
    W(box(AX0, WRY, AZ, 2400, WRY + 4, AC, TEX_GLASS))
    W(box(2520, WRY, AZ, WRX + 4, WRY + 4, AC, TEX_GLASS))
    for y in (-2120, -2260, -2400):
        for x in (2150, 2350, 2560):
            E(ent("prop_static", (x, y, AZ), model="models/pennmodern/seats.mdl", angles="0 90 0"))
    # Lights: a grid under the ceiling, brighter in the atrium.
    for x in range(AX0 + 180, AX1, 360):
        for y in range(AY1 - 180, AY0, -360):
            atrium = RX0 < x < RX1 and RY0 < y < RY1
            E(ent("light", (x, y, (RZ if atrium else AC) - 20), _light="250 245 235 %d" % (70 if atrium else 45)))
    E(ent("light", ((lx0 + EX1) // 2, EYC, lz + 120), _light="240 240 235 50"))
    E(ent("light", ((SX0 + SX1) // 2, py0 - 100, -150), _light="240 240 235 30"))
    E(ent("env_cubemap", (3000, -1300, AZ + 100)))
    E(ent("env_cubemap", (4200, -1800, AZ + 100)))


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
    amtrak(W, E)
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
