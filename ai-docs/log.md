# Log

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, verify, verify-failed, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

## [2026-11-26] init | scaffolded
- 2026-11-26 Setup: repo, ai-docs, plan, tooling from penn-gmod renamed to gm_penn_modern / pennmodern / pm_*, shared GMod lock (tools/gmod_lock.sh; penn-gmod PR #9), starter Moynihan box, 40-session continue prompt, driver launched (PID in HANDOFF Grants).
## [2026-11-26] index | rebuilt (2 entries)
## [2026-11-26] add | session 1: Moynihan refs, dimensions, first compile
- 15 Commons refs (refs/SOURCES.md), notes/moynihan-dimensions.md, box sized 200x155x92 ft, compile loads (141 verts), shots 146 fps. The GMod lock waited out penn-gmod's shots without trouble.
## [2026-11-26] add | session 2: Moynihan blockout
- Wells, lower stub, side halls, balcony, truss/purlin/clock MDL (yaw 90 for studiomdl's axis swap). 688 verts, 146 fps.
## [2026-11-26] add | session 3: Moynihan materials, skylight glass, boards
- pm_textures.py rewritten for Moynihan and run by compile.sh; skylight.mdl translucent vault; shop fronts; LED boards need per-face UVs (u=+x reads mirrored on the +y-facing face). 756 verts, 146 fps, BSP 13.2 MB.
## [2026-11-26] add | session 4: gabled Pratt trusses, upper floor glazing, DXT textures
- Truss profile now leg, knee, flat gable like the refs; DXT1/5 VTFs cut the BSP 13.2 to 4.2 MB. 742 verts, 146 fps.
- 2026-11-26 session 4: ../penn-modern-gmod-s3 and -s4 folders could not be deleted (Permission denied, a shell held them); they are pruned from git, delete the leftovers if still there. srctools 2.7 writes DXT1/DXT5 VTFs directly.
