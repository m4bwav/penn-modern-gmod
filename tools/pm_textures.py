"""Procedural Moynihan Train Hall materials, tones judged by eye from the CC0 wide shots
(refs/photos/Moynihan_Train_Hall_viewed_from_center_of_floor_Dec_27_2022.jpg and _interior_*):
pale grey-beige marble floor in long slabs, pale grey stone wall panels, charcoal metal trim,
lit storefront glazing, the skylight's glass grid (translucent, for the skylight model),
the clock dial and the blue LED boards on the side walls.
Brush materials -> src/materials/pennmodern/, model materials -> src/materials/models/pennmodern/,
previews in shots/tex/. Needs pip srctools pillow numpy. Run through tools/compile.sh."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from srctools import vtf

N = 512
ROOT = Path(__file__).resolve().parent.parent
MAT = ROOT / "src" / "materials" / "pennmodern"
MMAT = ROOT / "src" / "materials" / "models" / "pennmodern"
rng = np.random.default_rng(2021)


def fbm(n, octaves=5, m=None):
    # Seamless fbm: tile each random grid 3x3, resize, keep the middle tile.
    m = m or n
    out = np.zeros((m, n))
    for o in range(octaves):
        k = 3 * 2**o
        g = np.tile(rng.random((k, k)), (3, 3))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((3*n, 3*m), Image.BICUBIC)
        out += (np.asarray(img, float)[m:2*m, n:2*n] / 255 - .5) / 2**o
    return out


def save(img, name, vmt=None, surf="stone", alpha=None, model=False):
    rgb = np.clip(img, 0, 255).astype(np.uint8)
    h, w = rgb.shape[:2]
    (ROOT / "shots" / "tex").mkdir(parents=True, exist_ok=True)
    a = np.full((h, w), 255, np.uint8) if alpha is None else np.clip(alpha, 0, 255).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, a]) if alpha is not None else rgb).save(ROOT / "shots" / "tex" / f"{name}.png")
    tex = vtf.VTF(w, h, fmt=vtf.ImageFormats.DXT5 if alpha is not None else vtf.ImageFormats.DXT1)   # DXT cuts the BSP ~6x
    tex.get().copy_from(np.dstack([rgb, a]).tobytes(), vtf.ImageFormats.RGBA8888)
    if alpha is not None:
        tex.flags |= vtf.VTFFlags.EIGHTBITALPHA   # Source reads translucency from this flag, not the format
    tex.compute_mipmaps()
    d, path = (MMAT, "models/pennmodern") if model else (MAT, "pennmodern")
    d.mkdir(parents=True, exist_ok=True)
    with open(d / f"{name}.vtf", "wb") as f:
        tex.save(f)
    vmt = vmt or '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n}\n'
    (d / f"{name}.vmt").write_text(vmt % (f"{path}/{name}", surf), encoding="ascii", newline="\n")
    print("wrote", name)


yy, xx = np.mgrid[0:N, 0:N]


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


# Floor: long pale grey-beige marble slabs, 4 across x 2 down per tile, running bond, soft veins.
FL = np.array([176, 170, 160], float)
img = np.zeros((N, N, 3))
sw, sh = N // 2, N // 4
for r in range(4):
    off = (sw // 2) * (r % 2)
    for b in range(3):
        x0, x1 = max(0, b*sw - off), min(N, (b+1)*sw - off)
        if x1 > x0:
            img[r*sh:(r+1)*sh, x0:x1] = FL * (1 + rng.uniform(-.05, .05))
vein = np.abs(np.sin((xx * 0.6 + yy) / N * 2*np.pi * 3 + fbm(N, 5) * 9))
img *= (1 + fbm(N, 6) * 0.06 - (vein < 0.06) * 0.08)[..., None]
for r in range(4):
    img[r*sh:r*sh+2] *= 0.72
    off = (sw // 2) * (r % 2)
    for b in range(3):
        x = (b*sw - off) % N
        img[r*sh:(r+1)*sh, x:x+2] *= 0.72
save(img, "floor_marble", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.12 0.12 0.12]"\n}\n')

# Wall: pale grey stone panels, 2 x 2 per tile, fine joints.
ST = np.array([168, 166, 160], float)
img = ST * (1 + fbm(N, 6) * 0.07)[..., None]
for k in range(0, N, N // 2):
    img[k:k+2] *= 0.7
    img[:, k:k+2] *= 0.7
save(img, "wall_stone")

# Trim: charcoal painted steel / metal panel, the colour of the trusses' surrounds and piers.
img = np.array([78, 80, 84], float) * (1 + fbm(N, 6) * 0.05)[..., None]
for k in range(0, N, N // 4):
    img[k:k+2] *= 0.75
save(img, "trim_dark", surf="metal")

# Storefront: warm lit shops behind glass, 2 bays per tile with mullions and a dark fascia band.
img = np.zeros((N, N, 3))
img[:] = [214, 190, 150]
img *= (0.88 + 0.12 * fbm(N, 3)[..., None] + 0.12 * (yy / N)[..., None])   # even shop glow, no blotches
for k in (N // 4, 3 * N // 4):
    img[N // 3:N - 40, k - 50:k + 50] *= 0.86   # shelving shadow in each bay
img[: N // 6] = [40, 42, 46]                               # fascia
img[N // 6: N // 6 + 6] = [235, 220, 190]                  # cove light strip
for k in (0, N // 2):
    img[:, k:k+10] = [55, 57, 60]                          # mullions
img[N - 12:] = [55, 57, 60]
save(img, "storefront", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$selfillum" "1"\n\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.2 0.2 0.2]"\n}\n', surf="glass")

# Skylight glass for the skylight model: one 6 ft square cell per half tile with a thin diagonal
# grid, steel mullions opaque, glass mostly clear and slightly blue-white.
img = np.zeros((N, N, 3)) + [205, 220, 235]
al = np.full((N, N), 70.0)
c = N // 2
mul = ((xx % c) < 8) | ((yy % c) < 8)
diag = (np.abs((xx % c) - (yy % c)) < 2) | (np.abs((xx % c) + (yy % c) - c) < 2)
img[mul] = [92, 95, 100]
al[mul] = 255
img[diag & ~mul] = [130, 134, 140]
al[diag & ~mul] = 200
save(img, "skylight", '"VertexLitGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$translucent" "1"\n\t"$nocull" "1"\n\t"$model" "1"\n}\n', surf="glass", alpha=al, model=True)

# Clock dial: cream face, black hour marks and hands at 10:08.
img = np.zeros((N, N, 3)) + [236, 230, 212]
im = Image.fromarray(img.astype(np.uint8))
dr = ImageDraw.Draw(im)
cx = N / 2
dr.ellipse((14, 14, N - 14, N - 14), outline=(30, 30, 32), width=10)
for k in range(60):
    a = np.pi * 2 * k / 60
    r0 = cx - 50 if k % 5 == 0 else cx - 36
    dr.line((cx + r0*np.sin(a), cx - r0*np.cos(a), cx + (cx-26)*np.sin(a), cx - (cx-26)*np.cos(a)),
            fill=(25, 25, 28), width=12 if k % 5 == 0 else 3)
for frac, ln, wd in ((10/12 + 8/720, 0.5, 16), (8/60, 0.75, 10)):
    a = 2 * np.pi * frac
    dr.line((cx, cx, cx + ln*cx*np.sin(a), cx - ln*cx*np.cos(a)), fill=(20, 20, 22), width=wd)
dr.ellipse((cx - 14, cx - 14, cx + 14, cx + 14), fill=(20, 20, 22))
save(np.asarray(im, float), "clockface", '"UnlitGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$model" "1"\n}\n', surf="metal", model=True)

# LED boards on the side walls (the big blue screens over the balcony): one 1024 x 512 board per
# face, mapped once by build_vmf.py's SCALE (30 x 15 ft).
for name, text in (("board_name", "MOYNIHAN\nTRAIN HALL"), ("board_info", "Ticketed Waiting Room")):
    W2 = 1024
    g = np.linspace(0, 1, W2)[None, :, None]
    img = np.zeros((N, W2, 3)) + [28, 52, 120] * (0.85 + 0.3 * g)
    img[:10] = img[-10:] = img[:, :10] = img[:, -10:] = [20, 20, 22]
    im = Image.fromarray(img.astype(np.uint8))
    dr = ImageDraw.Draw(im)
    f = font(120 if "\n" in text else 80)
    dr.multiline_text((W2 / 2, N / 2), text, font=f, fill=(240, 240, 245), anchor="mm", align="center", spacing=20)
    save(np.asarray(im, float), name, '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
         '\t"$selfillum" "1"\n}\n', surf="glass")

# Pylon screen: black departure pylon head, amber "TRACKS" over white track numbers.
img = np.zeros((256, 256, 3)) + [14, 15, 18]
im = Image.fromarray(img.astype(np.uint8))
dr = ImageDraw.Draw(im)
dr.rectangle((6, 6, 249, 249), outline=(60, 62, 66), width=4)
dr.text((128, 70), "TRACKS", font=font(40), fill=(255, 176, 40), anchor="mm")
dr.text((128, 160), "11  12", font=font(84), fill=(245, 245, 245), anchor="mm")
save(np.asarray(im, float), "pylon_screen", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$selfillum" "1"\n}\n', surf="glass")

# --- Area 2, the LIRR concourse (refs/photos/Penn_Station_LIRR_concourse_renovated_high_ceiling.jpg,
# LIRR_Penn_Station_2025a.jpg): grey granite tiles, warm wood-slat ceiling, white ceiling panels with
# downlights, the 33rd Street pavilion's lit blue coffer grid, white columns fading to blue, signage.
SL = '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n\t"$selfillum" "1"\n}\n'

# Floor: speckled grey granite, 2 x 2 ft tiles (4 per tile row), with a darker band every other row.
img = np.array([128, 130, 134], float) * (1 + fbm(N, 6) * 0.05)[..., None]
img *= (1 + (rng.random((N, N)) - .5) * 0.18)[..., None]
for k in range(0, N, N // 4):
    img[k:k+2] *= 0.8
    img[:, k:k+2] *= 0.8
save(img, "floor_granite", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.08 0.08 0.08]"\n}\n')

# Wood-slat ceiling: honey wood slats with dark gaps and a lit line every 8 slats.
img = np.zeros((N, N, 3)) + [186, 140, 92]
img *= (1 + fbm(N, 5) * 0.08)[..., None]
img[(yy % 32) < 6] = [60, 44, 32]
img[(yy % 256) < 6] = [255, 240, 205]
save(img, "ceil_wood", surf="wood")

# White ceiling: large pale panels, dark reveal joints, small downlight dots.
img = np.zeros((N, N, 3)) + [222, 224, 226]
img *= (1 + fbm(N, 4) * 0.03)[..., None]
img[(yy % 256) < 4] = [90, 92, 96]
img[(xx % 512) < 4] = [90, 92, 96]
dots = (((xx + 64) % 128 - 64) ** 2 + ((yy + 128) % 256 - 128) ** 2) < 25
img[dots] = [255, 252, 240]
img[(yy % 128 > 60) & (yy % 128 < 68)] = [255, 253, 246]   # long linear light strips, as in the refs
UL = '"UnlitGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n}\n'
save(img, "ceil_white", UL)   # $selfillum on LightmappedGeneric left it dark grey in game; unlit reads as lit panels

# Light box: the pavilion's coffer grid, glowing sky-blue panels in dark steel frames, 2 x 2 per tile.
img = np.zeros((N, N, 3)) + [24, 26, 30]
c = N // 2
inner = ((xx % c) > 22) & ((xx % c) < c - 22) & ((yy % c) > 22) & ((yy % c) < c - 22)
glow = 1 - 0.25 * ((((xx % c) - c / 2) ** 2 + ((yy % c) - c / 2) ** 2) / (c / 2) ** 2)
img[inner] = (np.array([130, 190, 245]) * glow[..., None])[inner]
img[((xx % c) - 11) ** 2 + ((yy % c) - 11) ** 2 < 16] = [255, 220, 150]
save(img, "lightbox", UL, surf="glass")

# Column: white enamel, a band at 9 ft, deep blue gradient toward the floor (512 tall, mapped once).
img = np.zeros((N, 256, 3)) + [228, 230, 232]
t = np.linspace(0, 1, N)[:, None, None]
blue = np.array([28, 48, 140]) * (0.7 + 0.3 * t) + np.array([228, 230, 232]) * 0
mix = np.clip((t - 0.45) / 0.3, 0, 1)
img = img * (1 - mix) + blue * mix
img[:, :4] *= 0.8
save(img, "column_blue", surf="metal")

# White wall panels.
img = np.array([215, 216, 218], float) * (1 + fbm(N, 5) * 0.03)[..., None]
img[(yy % 256) < 3] *= 0.82
img[(xx % 256) < 3] *= 0.82
save(img, "wall_white")

# Overhead wayfinding band: green Exit, blue street exit, black subway/LIRR, yellow Tracks.
W2 = 1024
im = Image.new("RGB", (W2, 128), (18, 18, 20))
dr = ImageDraw.Draw(im)
for x0, x1, col in ((0, 110, (0, 150, 70)), (112, 470, (20, 40, 160)), (472, 800, (22, 22, 24)), (802, 1024, (250, 190, 20))):
    dr.rectangle((x0, 4, x1, 123), fill=col)
dr.text((55, 64), "Exit", font=font(40), fill=(255, 255, 255), anchor="mm")
dr.text((290, 64), "7th Av & 33rd St", font=font(36), fill=(255, 255, 255), anchor="mm")
dr.text((636, 64), "LIRR  Subway  NJ Transit", font=font(30), fill=(255, 255, 255), anchor="mm")
dr.text((913, 64), "Tracks 13-21", font=font(30), fill=(20, 20, 20), anchor="mm")
save(np.asarray(im, float), "sign_band", SL, surf="metal")

# LIRR departure board for the columns: black screen, amber train rows, blue header (model material).
UNLIT = '"UnlitGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n\t"$model" "1"\n}\n'
im = Image.new("RGB", (256, 512), (8, 8, 10))
dr = ImageDraw.Draw(im)
dr.rectangle((0, 0, 255, 52), fill=(20, 40, 150))
dr.text((128, 27), "Departures", font=font(30), fill=(255, 255, 255), anchor="mm")
rows = (("5:12", "Babylon", "19"), ("5:18", "Port Wash", "13"), ("5:21", "Ronkonkoma", "20"),
        ("5:26", "Hempstead", "17"), ("5:31", "Huntington", "21"), ("5:34", "Far Rockaway", "14"),
        ("5:40", "Long Beach", "18"), ("5:43", "Montauk", "16"), ("5:49", "Oyster Bay", "15"))
for i, (t, dest, trk) in enumerate(rows):
    y = 80 + i * 48
    dr.text((8, y), t, font=font(22), fill=(255, 190, 40), anchor="lm")
    dr.text((70, y), dest, font=font(20), fill=(255, 190, 40), anchor="lm")
    dr.text((246, y), trk, font=font(22), fill=(255, 255, 255), anchor="rm")
    dr.line((6, y + 22, 250, y + 22), fill=(40, 40, 44), width=2)
save(np.asarray(im, float), "depboard", UNLIT, surf="metal", model=True)

# Ticket machine front: brushed steel, a blue touch screen, card slot and ticket tray.
im = Image.new("RGB", (256, 512), (150, 154, 160))
dr = ImageDraw.Draw(im)
dr.rectangle((0, 0, 255, 40), fill=(20, 40, 150))
dr.text((128, 21), "LIRR Tickets", font=font(24), fill=(255, 255, 255), anchor="mm")
dr.rectangle((28, 70, 228, 230), fill=(25, 25, 28))
dr.rectangle((36, 78, 220, 222), fill=(40, 110, 200))
dr.text((128, 120), "Touch to start", font=font(20), fill=(255, 255, 255), anchor="mm")
dr.rectangle((60, 260, 196, 276), fill=(30, 30, 32))
dr.rectangle((150, 300, 220, 340), fill=(40, 40, 44))
dr.rectangle((50, 380, 206, 430), fill=(35, 35, 38))
save(np.asarray(im, float), "tvm_front", UNLIT, surf="metal", model=True)

# --- Area 3, the Amtrak concourse (refs: Amtrak_terminal_New_York_Penn_December_27_2022.jpg,
# NY_Penn_Station_Amtrak_Terminal.jpg, Penn_Station_concourse.jpg) ---
# Terrazzo floor: pale grey with fine dark and white chips, faint slab joints every 256 texels.
img = np.zeros((N, N, 3)) + [196, 198, 200]
img *= (1 + fbm(N, 5) * 0.05)[..., None]
chips = rng.random((N, N))
img[chips < 0.03] *= 0.6
img[chips > 0.985] = [238, 238, 236]
img[((yy % 256) < 2) | ((xx % 256) < 2)] *= 0.85
save(img, "floor_terrazzo", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.12 0.12 0.12]"\n}\n')

# Amtrak ceiling: charcoal louvre slats with square downlights (unlit, so it reads as a lit ceiling).
img = np.zeros((N, N, 3)) + [58, 60, 64]
img[(yy % 16) < 3] = [34, 35, 38]
sq = ((xx % 256) > 112) & ((xx % 256) < 144) & ((yy % 256) > 112) & ((yy % 256) < 144)
img[sq] = [255, 250, 236]
save(img, "ceil_amtrak", UL, surf="metal")

# Amtrak departures board, 40 x 10 ft: blue header, white and amber train rows on black.
im = Image.new("RGB", (1024, 256), (6, 6, 8))
dr = ImageDraw.Draw(im)
dr.rectangle((0, 0, 1023, 34), fill=(16, 50, 110))
dr.text((512, 17), "DEPARTURES", font=font(26), fill=(255, 255, 255), anchor="mm")
for x, h in ((20, "Time"), (110, "Train"), (290, "Destination"), (700, "Status"), (900, "Track")):
    dr.text((x, 46), h, font=font(14), fill=(170, 170, 175), anchor="lm")
rows = (("5:05", "Acela 2165", "Boston South Station", "On Time", "14"), ("5:12", "NE Regional 173", "Washington DC", "Boarding", "9"),
        ("5:20", "Empire 241", "Albany-Rensselaer", "On Time", ""), ("5:30", "Keystone 655", "Harrisburg", "On Time", ""),
        ("5:45", "Acela 2259", "Boston South Station", "5 Late", ""), ("6:00", "NE Regional 135", "Newport News", "On Time", ""),
        ("6:05", "Adirondack 69", "Montreal", "On Time", ""), ("6:20", "Carolinian 79", "Charlotte", "On Time", ""))
for i, r in enumerate(rows):
    y = 72 + i * 23
    cols = ((255, 255, 255), (255, 190, 40), (255, 255, 255),
            (120, 220, 120) if r[3] == "Boarding" else (255, 190, 40), (255, 255, 255))
    for x, txt, col in zip((20, 110, 290, 700, 900), r, cols):
        dr.text((x, y), txt, font=font(17), fill=col, anchor="lm")
save(np.asarray(im, float), "amboard", UL, surf="metal")

# Column halo: the ring of lights round each blue column under the ceiling (model material).
save(np.zeros((64, 64, 3)) + [255, 250, 232], "halo", UNLIT, surf="metal", model=True)

# --- Area 4, the NJ Transit concourse (refs: NJ_Transit_concourse_New_York_Penn_Station_November_27_2023.jpg,
# NJ_Transit_Ticket_Counter_Penn_Station_NY.jpg) ---
# Floor: diamonds of pink and grey granite with small black squares where the corners meet.
d1, d2 = ((xx + yy) // 256) % 2, ((xx - yy + N) // 256) % 2
img = np.where((d1 ^ d2)[..., None] == 1, [176, 140, 126], [190, 192, 194]).astype(float)
img *= (1 + (rng.random((N, N)) - .5) * 0.22)[..., None]
img *= (1 + fbm(N, 5) * 0.06)[..., None]
cx, cy = (xx + yy) % 256, (xx - yy + N) % 256
img[(np.minimum(cx, 256 - cx) < 18) & (np.minimum(cy, 256 - cy) < 18)] = [30, 30, 32]
save(img, "floor_njt", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$envmap" "env_cubemap"\n\t"$envmaptint" "[0.1 0.1 0.1]"\n}\n')

# Wall: cream marble panels with tan stripes and fine veins.
img = np.zeros((N, N, 3)) + [222, 204, 176]
img *= (1 + fbm(N, 6) * 0.08)[..., None]
img[(yy % 128) < 14] = img[(yy % 128) < 14] * [0.86, 0.76, 0.66]
img[((yy % 256) < 2) | ((xx % 256) < 2)] *= 0.8
save(img, "wall_njt")

# Track gates band, 200 x 12.5 ft on the north wall: 10 bays of marble, each with a brown dado,
# a gold-framed glass door under a black TRACK sign and a departure screen.
im = Image.new("RGB", (2048, 128), (222, 204, 176))
dr = ImageDraw.Draw(im)
dr.rectangle((0, 100, 2047, 127), fill=(150, 80, 40))
for i in range(10):
    x = int(i * 204.8)
    dr.line((x, 0, x, 127), fill=(190, 170, 140), width=2)
    dr.rectangle((x + 70, 34, x + 134, 127), fill=(160, 130, 60))
    dr.rectangle((x + 76, 40, x + 128, 127), fill=(70, 80, 84))
    dr.rectangle((x + 70, 10, x + 134, 30), fill=(14, 14, 16))
    dr.text((x + 102, 20), "TRACK %d" % (i + 1), font=font(12), fill=(255, 255, 255), anchor="mm")
    dr.rectangle((x + 150, 14, x + 196, 44), fill=(10, 10, 40))
    for r in range(4):
        dr.line((x + 153, 20 + r * 6, x + 193, 20 + r * 6), fill=((200, 40, 40), (40, 160, 80), (255, 190, 40), (230, 230, 230))[r], width=2)
save(np.asarray(im, float), "trackgates", UL)

# NJ Transit ticket windows, 80 x 10 ft: black fascia with the name, lit windows with numbers.
im = Image.new("RGB", (1024, 128), (238, 232, 214))
dr = ImageDraw.Draw(im)
dr.rectangle((0, 0, 1023, 30), fill=(16, 16, 18))
dr.text((512, 15), "NJ TRANSIT Tickets", font=font(22), fill=(240, 240, 240), anchor="mm")
for i in range(8):
    x = i * 128
    dr.rectangle((x + 6, 36, x + 122, 92), fill=(250, 248, 236))
    dr.line((x, 30, x, 127), fill=(200, 190, 170), width=3)
    dr.rectangle((x + 46, 36, x + 82, 48), fill=(240, 240, 240))
    dr.text((x + 64, 42), "WINDOW %d" % (i + 1), font=font(8), fill=(20, 20, 20), anchor="mm")
dr.rectangle((0, 92, 1023, 127), fill=(226, 214, 190))
save(np.asarray(im, float), "njt_tickets", UL)

# Clean glass for rails, screens and glazed walls: faint blue-green tint, mostly clear (replaces the
# stock glasswindow007a, which read as dirty up close; an env_cubemap sheen rendered white unbuilt).
save(np.zeros((64, 64, 3)) + [150, 175, 180], "glass_clean",
     '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n\t"$translucent" "1"\n}\n',
     surf="glass", alpha=np.full((64, 64), 28))

# --- Area 5, the platforms (refs: Track_21_New_York_Penn_Station.jpg, Track_16_Penn_Station_New_York_during_COVID_pandemic.jpg,
# Amtrak_and_LIRR_trains_at_Penn_Station_tracks_January_6_2024.jpg, NJ_Transit_MultiLevel_Coach_7051_SB_at_Secaucus_Junction.jpg) ---
# Platform deck: worn red-grey painted concrete with scuffs and slab joints.
img = np.zeros((N, N, 3)) + [128, 104, 100]
img *= (1 + fbm(N, 6) * 0.14)[..., None]
img[((yy % 256) < 2) | ((xx % 256) < 2)] *= 0.7
save(img, "plat_floor")

# Platform edge: yellow tactile strip, rows of raised domes.
img = np.zeros((N, N, 3)) + [214, 172, 30]
img *= (1 + fbm(N, 4) * 0.08)[..., None]
img[((xx % 32) - 16) ** 2 + ((yy % 32) - 16) ** 2 < 49] *= 1.12
img[((xx % 32) - 14) ** 2 + ((yy % 32) - 18) ** 2 < 9] *= 0.8
save(img, "plat_edge")

# Trackbed: dark ballast stones with grime and the odd rusty tie between them.
img = np.zeros((N, N, 3)) + [70, 66, 62]
img *= (1 + (rng.random((N, N)) - .5) * 0.5)[..., None]
img *= (1 + fbm(N, 5) * 0.3)[..., None]
img[(xx % 64) < 20] = img[(xx % 64) < 20] * [0.7, 0.55, 0.45]
save(img, "ballast", surf="gravel")

# Track walls: grimy grey concrete in tall pours with drip stains.
img = np.zeros((N, N, 3)) + [96, 94, 88]
img *= (1 + fbm(N, 6) * 0.2)[..., None]
img *= (1 - np.clip(fbm(N, 3), 0, 1) * (yy / N) * 0.6)[..., None]
img[(xx % 256) < 3] *= 0.6
save(img, "tunnel_wall", surf="concrete")

# Platform ceiling: dark concrete slab with deep beams every 128 texels and a pipe run.
img = np.zeros((N, N, 3)) + [74, 70, 64]
img *= (1 + fbm(N, 5) * 0.18)[..., None]
img[(xx % 128) < 18] *= 0.55
img[((yy % 256) > 120) & ((yy % 256) < 136)] = [150, 140, 120]
save(img, "plat_ceil", surf="concrete")

# Platform columns: tan paint over a blue dado with a red band, as on tracks 16 and 21.
img = np.zeros((N, N, 3)) + [196, 166, 110]
img *= (1 + fbm(N, 5) * 0.08)[..., None]
img[yy > N - 120] = [52, 80, 140]
img[(yy > N - 132) & (yy <= N - 120)] = [150, 30, 30]
save(img, "plat_col", surf="concrete")

VLG = UNLIT.replace("UnlitGeneric", "VertexLitGeneric")
# MultiLevel coach side (model): stainless, a lower and upper window band, doors, NJ Transit stripes.
im = Image.new("RGB", (1024, 256), (178, 182, 188))
dr = ImageDraw.Draw(im)
for x in range(0, 1024, 4):
    dr.line((x, 0, x, 255), fill=(170 + (x // 4) % 3 * 6,) * 3)
dr.rectangle((0, 168, 1023, 180), fill=(230, 110, 30))
dr.rectangle((0, 181, 1023, 188), fill=(110, 40, 130))
dr.rectangle((0, 189, 1023, 196), fill=(20, 60, 150))
for x in range(150, 870, 46):
    dr.rounded_rectangle((x, 46, x + 36, 82), 5, fill=(28, 34, 40))
    dr.rounded_rectangle((x, 112, x + 36, 150), 5, fill=(28, 34, 40))
for x in (60, 904):
    dr.rectangle((x, 100, x + 60, 228), fill=(120, 124, 130))
    dr.rectangle((x + 4, 104, x + 28, 228), fill=(150, 154, 160))
    dr.rectangle((x + 32, 104, x + 56, 228), fill=(150, 154, 160))
    dr.rectangle((x + 8, 120, x + 24, 160), fill=(28, 34, 40))
    dr.rectangle((x + 36, 120, x + 52, 160), fill=(28, 34, 40))
save(np.asarray(im, float), "mlside", VLG, surf="metal", model=True)

# MultiLevel coach end (model): stainless with a diaphragm door.
im = Image.new("RGB", (128, 256), (170, 174, 180))
dr = ImageDraw.Draw(im)
dr.rectangle((30, 60, 98, 230), fill=(30, 30, 32))
dr.rectangle((40, 80, 88, 140), fill=(60, 66, 72))
save(np.asarray(im, float), "mlend", VLG, surf="metal", model=True)
