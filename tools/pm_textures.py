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
save(img, "ceil_white", '"LightmappedGeneric"\n{\n\t"$basetexture" "%s"\n\t"$surfaceprop" "%s"\n'
     '\t"$selfillum" "1"\n\t"$selfillumtint" "[0.55 0.55 0.55]"\n}\n')   # reads as a lit ceiling

# Light box: the pavilion's coffer grid, glowing sky-blue panels in dark steel frames, 2 x 2 per tile.
img = np.zeros((N, N, 3)) + [24, 26, 30]
c = N // 2
inner = ((xx % c) > 22) & ((xx % c) < c - 22) & ((yy % c) > 22) & ((yy % c) < c - 22)
glow = 1 - 0.25 * ((((xx % c) - c / 2) ** 2 + ((yy % c) - c / 2) ** 2) / (c / 2) ** 2)
img[inner] = (np.array([130, 190, 245]) * glow[..., None])[inner]
img[((xx % c) - 11) ** 2 + ((yy % c) - 11) ** 2 < 16] = [255, 220, 150]
save(img, "lightbox", SL, surf="glass")

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
