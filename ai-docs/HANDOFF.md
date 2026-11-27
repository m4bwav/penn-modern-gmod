# HANDOFF: gm_penn_modern

Status: in progress
Updated: 2026-11-26 (session 1)

- Prompt: plans/2026-11-26-penn-modern-40x-continue-prompt.md
- Chain: session 1 of 40
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

## Next
1. Session 2: Moynihan blockout: floor with escalator wells to a stub West End Concourse, two-storey side halls with the 20 ft balcony, wall band to ~50 ft, skylight (texture) with the 3 transverse trusses + secondary trusses as MDL in pm_models.py (replace the 1910 corinthian content; it still builds corinthian.mdl), clock MDL at the centre. Full compile, shots, vbspinfo.
2. Then detail against refs with compare.jpg, lighting, 0.1.0 to a new Workshop item (gmpublish create).

## Waiting on Mark
- Nothing.
