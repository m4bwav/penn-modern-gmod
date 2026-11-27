# Licence audit, 0.4.0 (2026-11-27)

Delta since [licence-audit-0.3.0.md](licence-audit-0.3.0.md).

- refs/: 2 NJ Transit concourse photos added in session 11, Wikimedia Commons CC0, each in refs/SOURCES.md with author and URL. Used for proportions and colour only; none are in the map or the .gma.
- New textures (floor_njt, wall_njt, trackgates, njt_tickets, glass_clean): procedural, tools/pm_textures.py (Pillow, numpy; Arial glyphs rendered into the image). glass_clean replaces stock glass/glasswindow007a on brushes.
- New models (njtruss, njcol): procedural, tools/pm_models.py; materials reuse stock HL2 metal/metalwall001a, shipped with Garry's Mod, not bundled.
- "NJ TRANSIT" appears as plain text on the ticket fascia (no logo artwork); track numbers are invented.
- No AI images in the map. Result: OK to publish.
