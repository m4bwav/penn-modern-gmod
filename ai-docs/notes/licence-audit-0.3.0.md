# Licence audit, 0.3.0 (2026-11-27)

Delta since [licence-audit-0.2.0.md](licence-audit-0.2.0.md).

- refs/: 7 Amtrak concourse photos added in session 10, Wikimedia Commons CC0, CC BY 2.0, CC BY 4.0 and CC BY-SA 3.0, each in refs/SOURCES.md with author and URL. Used for proportions and colour only; none are in the map or the .gma.
- New textures (floor_terrazzo, ceil_amtrak, amboard, halo): procedural, tools/pm_textures.py (Pillow, numpy; Arial glyphs rendered into the image).
- New models (amcol, seats): procedural, tools/pm_models.py; materials reuse stock HL2 metal/metalwall001a, shipped with Garry's Mod, not bundled.
- Train names and destinations on the departures board are real Amtrak services; times, numbers and tracks are invented.
- No AI images in the map. Result: OK to publish.
