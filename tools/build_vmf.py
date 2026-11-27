"""Build src/gm_penn_modern.vmf: today's New York Penn Station and Moynihan Train Hall at 1 ft = 12 u.

Starter stage: a sealed placeholder box for Moynihan Train Hall so the first compile, shots and
package run end to end. Session 1 replaces the PLACEHOLDER numbers with measured ones from licensed
references (refs/SOURCES.md) and logs them in ai-docs/notes/. Patterns for vaults, bays, arches,
lights and the tonemap: tools/penn1910_build_vmf.py (the 1910 chain's generator, kept as reference).
Run: python tools/build_vmf.py
"""
from pathlib import Path

from vmf_lib import box, ent, nid, _id

FT = 12
OUT = Path(__file__).resolve().parent.parent / "src" / "gm_penn_modern.vmf"

# Moynihan Train Hall, inside the Farley Building's former mail-sorting room. Long axis = x
# (east-west, +x toward Eighth Avenue and Penn Station across it). PLACEHOLDER sizes until measured.
HX, HY = 255 * FT // 2, 92 * FT // 2      # PLACEHOLDER hall plan
H = 92 * FT                               # PLACEHOLDER skylight crown height
T = 64                                    # shell thickness
TEX_FLOOR = "dev/dev_measuregeneric01b"
TEX_WALL = "dev/dev_measurewall01a"
TEX_SKY = "tools/toolsskybox"


def build():
    world = []
    W = world.append
    W(box(-HX - T, -HY - T, -T, HX + T, HY + T, 0, TEX_FLOOR))
    W(box(-HX - T, -HY - T, H, HX + T, HY + T, H + T, TEX_SKY))
    W(box(-HX - T, -HY - T, 0, -HX, HY + T, H, TEX_WALL))
    W(box(HX, -HY - T, 0, HX + T, HY + T, H, TEX_WALL))
    W(box(-HX, -HY - T, 0, HX, -HY, H, TEX_WALL))
    W(box(-HX, HY, 0, HX, HY + T, H, TEX_WALL))
    ents = [
        ent("light_environment", (0, 0, H - 64), angles="-60 30 0", pitch="-60",
            _light="255 245 225 300", _ambient="170 190 220 60"),
        ent("light", (0, 0, H // 2), _light="240 235 225 60"),
        ent("info_player_start", (-HX + 200, 0, 8), angles="0 0 0"),
        ent("env_cubemap", (0, 0, 200)),
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
