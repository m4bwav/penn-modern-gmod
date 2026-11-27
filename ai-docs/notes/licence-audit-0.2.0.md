# Licence audit, 0.2.0 (2026-11-27)

Delta since [licence-audit-0.1.0.md](licence-audit-0.1.0.md).

- refs/: 9 LIRR photos added in session 8, all Wikimedia Commons CC BY 2.0 / CC BY-SA 3.0 / 4.0, each in refs/SOURCES.md with author and URL. Used for proportions and colour only; none are in the map or the .gma.
- New textures (floor_granite, ceil_wood, ceil_white, lightbox, column_blue, wall_white, sign_band, depboard, tvm_front): procedural, drawn by tools/pm_textures.py with Pillow and numpy. Fonts render text into the image (Arial on Windows); rendered glyphs in images are not a font redistribution.
- New models (colboard, tvm): procedural, tools/pm_models.py; materials reuse stock HL2 metal/metalwall001a, which ships with Garry's Mod and is not bundled.
- Station names on the departure board are real LIRR branch terminals; times and tracks are invented.
- No AI images in the map. Result: OK to publish.
