# gm_penn_modern

Garry's Mod map of today's New York Penn Station (the concourses under Madison Square Garden: LIRR, NJ Transit, Amtrak, the 2021 LIRR concourse) and Moynihan Train Hall in the Farley Building across Eighth Avenue, generated from Python.

- Start here: ai-docs/HANDOFF.md (state), ai-docs/plans/penn-modern-plan.md (scope, scale, area order, budgets), ai-docs/log.md.
- Chain prompt: ai-docs/plans/2026-11-26-penn-modern-40x-continue-prompt.md. One worktree per session; merge through PRs.
- Tooling is adapted from m4bwav/penn-gmod (1910 Penn Station, itself from gcs-gmod). tools/penn1910_build_vmf.py and tools/make_models.py (GCT) are pattern references; this map's generator is tools/build_vmf.py, its models tools/pm_models.py.
- Shared Garry's Mod: the penn-gmod chain uses the same install. Everything that writes into garrysmod/ or launches gmod.exe goes through tools/compile.sh, shots.sh, nav.sh or package.sh, which hold C:/Users/m4bwa/.chainwright/gmod.lock (tools/gmod_lock.sh). New scripts source gmod_lock.sh and call gmod_lock_take first. Run pm_models.py only through compile.sh. Kill only the gmod.exe your script started (gmod_snapshot / gmod_kill_own), never all of them. Our names in garrysmod/: map gm_penn_modern, materials/pennmodern, models/pennmodern, lua pm_*.lua, data pm_shots / pm_nav. Never touch penn-gmod's names (gm_penn_station, materials/penn, penn_*.lua).
- Never edit the VMF by hand. Repo text is LF (write from Python with newline='').
- Assets: only redistributable references and assets (Wikimedia Commons CC0, PD, CC BY, CC BY-SA; no NC/ND, no all-rights-reserved photos, no ripped game assets), each logged in refs/SOURCES.md with author, licence and URL. No Krea 2 images.

<!-- everlast -->
## Agent docs (ai-docs/)
- Before a non-trivial task: read ai-docs/INDEX.md and ai-docs/HANDOFF.md; open only matching entries.
- After a dead end, a decision or a non-obvious command: add an entry (solutions/, decisions/) and a log line.
- End of session: rewrite HANDOFF.md (under 50 lines) and append to log.md.
- Private notes (people, credentials) go to the vault sidecar, never here.
<!-- /everlast -->
