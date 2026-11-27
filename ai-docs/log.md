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
- 2026-11-26 driver pass 4 (meant as session 5) saw the driver PID alive and skipped as 'already handled'; a driver-started session must do the item. Pass 5 is doing session 5.
## [2026-11-26] add | session 5: lighting, balcony stairs, pylons
- Tonemap controller, softer sun, warm balcony downlights, west-end stairs, departure pylons. 1227 verts, 146 fps.
## [2026-11-26] add | session 6: escalator models, pylon screens
- escalator.mdl pairs in both wells over playerclip ramps, TRACKS 11 12 pylon screens, calmer storefront. 1224 verts, 146 fps. Stair walk test not done yet (no in-game walk tool used).
## [2026-11-26] add | session 7: walk test, 0.1.0 release
- tools/walk.sh walks stairs and escalators in game; it caught the well-end balustrade blocking the escalator tops. Walk start points must clear every step under the 32 u hull or the player is stuck and never moves.
- 0.1.0: gmpublish create -> Workshop 3846578407, workshop_update.py set title/desc/previews/public (EResult 1). Banner: Z-Image Turbo on the Mac, comfy_gen.py with the building-sprite workflow patched to 1536x640 and a bare {SUBJECT} prompt.
- 2026-11-26 session 7: release v0.1.0 was first created before PR #7 merged (merge returned 'Base branch was modified', a transient). Deleted and re-cut on the merge commit. Create releases only after confirming the merge commit is on origin/main.
## [2026-11-26] add | session 8: LIRR concourse blockout
- 9 Commons refs (CC BY / BY-SA), lirr-dimensions.md, lirr() in build_vmf.py: passage under Eighth Avenue through a real opening in the stub's east wall, 57 ft x 18 ft corridor (wood/white ceilings, blue columns), 40 ft lit-coffer 33rd St pavilion with an escalator to a sealed street mezzanine. 6 new textures. 1694 verts, 6.5 MB, 146 fps; walk 7/7 PASS (walk routes take an optional x target for level walks).
- ceil_white with $selfillum still renders dark grey in game; not solved yet.
## [2026-11-27] add | session 9: LIRR detail, 0.2.0
- $selfillum on LightmappedGeneric brushes did not brighten ceil_white in game (tint or not); UnlitGeneric does. _box() UVs were v-flipped (text upside down). colboard + tvm MDLs, compare.py lirr set. 1681 verts, 6.6 MB, 146 fps, walk 7/7. Workshop 3846578407 updated, v0.2.0.
