# HANDOFF: gm_penn_modern

Status: in progress
Updated: 2026-11-26 (session 0, setup)

- Prompt: plans/2026-11-26-penn-modern-40x-continue-prompt.md
- Chain: session 0 of 40 (setup done 2026-11-26; the driver's first session is session 1)
- Plan: plans/penn-modern-plan.md.
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod, SHARED with the penn-gmod chain; see the GMod lock rule in AGENTS.md.
- Workshop ID: none yet. First upload creates a new item (gmpublish create); record the ID here and in tools/package.sh.

## Grants
- Driver: chain_loop.py, PID 381748 (started 2026-11-26 21:35, chainwright 0.16.0 chain_loop.py, stdout/stderr C:/Users/m4bwa/.chainwright/penn-modern-driver.out/.err), prompt copy C:/Users/m4bwa/.chainwright/penn-modern-prompt.md, stop check C:/Users/m4bwa/.chainwright/penn_modern_stop.py, log C:/Users/m4bwa/.chainwright/penn-modern-chain.log, ledger C:/Users/m4bwa/.chainwright/penn-modern-ledger.json. Bounds: 40 sessions, 24 h, 180 min per session, limit wait 1800 s x 12, retry failed 1. Sessions it starts never start another driver.
- Pre-approved: first Workshop upload to a new item and later updates; tags and GitHub releases; making the repo public after a licence audit.
- GMod lock: C:/Users/m4bwa/.chainwright/gmod.lock, shared with penn-gmod (driver PID 393900, never touched by this chain).

## Done
- Setup (session 0): private repo m4bwav/penn-modern-gmod, ai-docs, plan, tooling copied from penn-gmod with names moved off penn-gmod's (gm_penn_modern, pennmodern, pm_*), shared GMod lock (tools/gmod_lock.sh, also merged into penn-gmod as PR #9), starter build_vmf.py (sealed placeholder Moynihan box, PLACEHOLDER sizes, stock dev textures), three starter cameras. Not compiled yet. pm_models.py and pm_textures.py still hold the 1910 column and travertine content as patterns; replace them.

## Next
1. Session 1: Commons refs for Moynihan Train Hall (CC0/PD/CC BY/BY-SA) into refs/ + SOURCES.md; sourced dimensions in notes/; first full compile under the lock, shots, vbspinfo.
2. Then Moynihan blockout with real sizes, skylight trusses as MDL, detail, lighting, 0.1.0 to a new Workshop item.

## Waiting on Mark
- Nothing.
