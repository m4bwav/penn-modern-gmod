# HANDOFF: gm_penn_modern

Status: in progress
Updated: 2026-11-26 (session 3)

- Prompt: plans/2026-11-26-penn-modern-40x-continue-prompt.md
- Chain: session 3 of 40
- Plan: plans/penn-modern-plan.md.
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod, SHARED with the penn-gmod chain; see the GMod lock rule in AGENTS.md.
- Workshop ID: none yet. First upload creates a new item (gmpublish create); record the ID here and in tools/package.sh.

## Grants
- Driver: chain_loop.py, PID 381748 (started 2026-11-26 21:35, chainwright 0.16.0 chain_loop.py, stdout/stderr C:/Users/m4bwa/.chainwright/penn-modern-driver.out/.err), prompt copy C:/Users/m4bwa/.chainwright/penn-modern-prompt.md, stop check C:/Users/m4bwa/.chainwright/penn_modern_stop.py, log C:/Users/m4bwa/.chainwright/penn-modern-chain.log, ledger C:/Users/m4bwa/.chainwright/penn-modern-ledger.json. Bounds: 40 sessions, 24 h, 180 min per session, limit wait 1800 s x 12, retry failed 1. Sessions it starts never start another driver.
- Pre-approved: first Workshop upload to a new item and later updates; tags and GitHub releases; making the repo public after a licence audit.
- GMod lock: C:/Users/m4bwa/.chainwright/gmod.lock, shared with penn-gmod (driver PID 393900, never touched by this chain).

## Done
- Setup (session 0): private repo m4bwav/penn-modern-gmod, ai-docs, plan, tooling copied from penn-gmod with names moved off penn-gmod's (gm_penn_modern, pennmodern, pm_*), shared GMod lock (tools/gmod_lock.sh, also merged into penn-gmod as PR #9), starter build_vmf.py (sealed placeholder Moynihan box, PLACEHOLDER sizes, stock dev textures), three starter cameras. Not compiled yet. pm_models.py and pm_textures.py still hold the 1910 column and travertine content as patterns; replace them.
- Session 1: 15 Commons refs of Moynihan (8 CC0, rest CC BY / BY-SA) in refs/photos, logged in refs/SOURCES.md; fetch_refs.py now writes the 6-column table and refuses NC/ND. Dimensions in ai-docs/notes/moynihan-dimensions.md (cited: 31,000 sq ft concourse, 92 ft skylight, 12 ft clock, 20 ft balcony; derived: 200 x 155 ft plan, 3 transverse trusses / 4 bays, springing ~50 ft). build_vmf.py box sized to that. First full compile (FAST) loads: vbspinfo verts 141, faces 112, brushes 6, BSP 1.0 MB; shots/20261126-2139 hall_west/up/east all 146 fps. compile.sh tolerates an empty materials folder.
- Session 2 (PR from branch s2-moynihan-blockout): Moynihan blockout. Floor slab with two escalator wells (glass balustrades) down to a sealed West End Concourse stub 30 ft below (140 x 80 ft), escalators as ~27 degree ramp wedges; side halls 25 ft deep under the 20 ft balcony (piers every 25 ft, glass rail), wall band to the 50 ft springing; skylight still a sky ceiling. pm_models.py now builds truss.mdl (elliptical arched truss, 2 chords + web + legs), purlins.mdl (11 longitudinal ribs), clock.mdl (4 dials, 12 ft, on a 30 ft rod); 1910 corinthian removed. Props need yaw 90 (studiomdl turns SMD +x to prop +y). Full compile: verts 688, faces 552, brushes 45, BSP 2.3 MB; shots/20261126-2146 (6 cams) and -2148, all ~146 fps. Shots cameras: hall_west/up/east, wells, side_south, lower.
- Session 3: Moynihan materials (tools/pm_textures.py rewritten, now run by compile.sh: floor_marble, wall_stone, trim_dark, storefront, board_name/board_info LED boards, model skylight + clockface), translucent skylight vault MDL over the trusses (6 ft glass grid), lit shop fronts under both balconies, two 30 x 15 ft LED boards per side wall (per-face UVs in board_uv so both walls read left to right), compare.py pairs for Moynihan. Full compile: 756 verts, 584 faces, 51 brushes, BSP 13.2 MB (uncompressed RGB textures). shots/20261126-2154 (+ compare.jpg) and -2157: all cams 146-147 fps.

## Next
1. Session 4: rest of the detail pass: truss shape is a flatter Pratt truss with a gabled glass roof in the refs (ours is a round arch: reshape in pm_models.py arch()), glazed upper floor over the balcony, stairs or escalator to the balcony, real escalator models in the wells, the clock is a stepped square art-deco case hanging lower, storefront texture less blotchy, DXT1-compress the VTFs (srctools) to cut the BSP size.
2. Then lighting (tonemap, warm downlights, less blown-out sun), 0.1.0 to a new Workshop item (gmpublish create), licence audit and public repo.

## Waiting on Mark
- Nothing.
