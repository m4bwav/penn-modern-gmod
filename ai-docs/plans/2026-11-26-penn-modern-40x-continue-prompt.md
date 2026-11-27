# Penn Station today for Garry's Mod, 40-session chain

Goal: `gm_penn_modern`, a Garry's Mod map of today's New York Penn Station (https://en.wikipedia.org/wiki/New_York_Penn_Station): the underground concourses under Madison Square Garden (LIRR, NJ Transit and Amtrak levels, the 2021 LIRR concourse with its high ceiling) and Moynihan Train Hall across Eighth Avenue (the old Farley post office with its glass-and-steel skylight hall). Built the way gm_grand_central (m4bwav/gcs-gmod) and gm_penn_station (m4bwav/penn-gmod, the 1910 station, a separate chain running at the same time) were, and published on the Steam Workshop. Repo: m4bwav/penn-modern-gmod at `D:/m4bwa/Claude/Projects/Ai/penn-modern-gmod`.

## Area order (refine in plans/penn-modern-plan.md)
1. Moynihan Train Hall (skylight hall, trusses, clock, side halls, escalators). Ships as the first release.
2. The LIRR concourse (the 2021 rebuild, high ceiling).
3. The Amtrak concourse.
4. The NJ Transit concourse.
5. Platforms with a train.
6. The Eighth Avenue entrances and street.

## Keep going (read first)
A "session" is one unit of work, not the end of the conversation. When an item finishes, bump the session number and start the next item in the same conversation. Hand over only at a stop point or when context runs low. In an interactive session, then start chainwright's driver (`chain_loop.py --go`, bounds in HANDOFF.md under Grants) unless one is already running for this prompt. A session started by the driver (headless `claude -p`, or a `chain_loop.py` process is running) never starts another driver: it finishes its item, updates HANDOFF.md and ends.

## Unattended runs
A headless session ends when its turn ends, and background jobs die with it. Run compiles, nav, shots and packaging in the foreground (under the 10-minute tool timeout; split long chains), never in the background, and don't end the turn while one runs. Before finishing, commit and push your branch even if the work is unfinished, and name it in HANDOFF.md. A leftover worktree from an earlier session means resume it, unless a vbsp/vrad process or a gmod.exe started by this repo's scripts is actually running. Never run two compile or shots jobs at once.

## Shared Garry's Mod (read before any compile, shots, nav or package)
The penn-gmod chain (driver PID 393900) uses the same GMod install. Never stop, restart or edit that driver, its files in C:/Users/m4bwa/.chainwright/ (penn_stop.py, penn-prompt.md, penn-chain.log, penn-ledger.json) or its repo. tools/compile.sh, shots.sh, nav.sh and package.sh take `C:/Users/m4bwa/.chainwright/gmod.lock` (holder's Windows PID, via tools/gmod_lock.sh) and release it on exit. A waiting script prints `gmod.lock: waiting for ...`: let it wait; if the wait would pass the tool timeout, do other work (refs, textures, models, docs) and try again. Anything new that writes into garrysmod/ or launches gmod.exe sources tools/gmod_lock.sh and calls gmod_lock_take first. Kill only the gmod.exe your own script started (gmod_snapshot, gmod_kill_own). Never delete a lock whose PID is alive. Keep to this map's names in garrysmod/ (gm_penn_modern, pennmodern, pm_*).

## Budget rules from GCT (vbsp's hard caps)
65,536 unique vertices is the limit you hit first. Use textures for grids, ceiling panels, signage and LED boards, MDL models for props and repeated structure (skylight trusses, escalators, benches, kiosks, the train), one func_brush per area for decor, and vbspinfo after every compile. Plan for Moynihan's skylight trusses to be models from day one. 150 MB file budget, 60 fps on a mid-range PC. Read `D:/m4bwa/Claude/Projects/Ai/gcs-gmod-pennprompt/notes/lessons-for-penn.md` once.

## References and licences
References and any asset must allow redistribution: Wikimedia Commons CC0, public domain, CC BY or CC BY-SA (no NC, no ND, no all-rights-reserved photos, no ripped game assets), each logged in refs/SOURCES.md (file, subject, author, licence, URL, date). Dimensions from cited sources in ai-docs/notes/. Images made with comfyui-gen: never Krea 2.

## Each session
1. `git fetch`, then read HANDOFF.md, the log tail and the plan from origin/main. Work in your own worktree (`git worktree add ../penn-modern-gmod-sN -b sN-topic origin/main`). Skills: modwright, polywright, comfyui-gen (never Krea 2), artwright/-judge, photowright, historywright (facts, sources), askwright, quirkwright, labwright, releasewright, grindwright.
2. Read and consume answered askwright sets.
3. Bump `Chain: session N of 40`. Take the next item: refs (logged in refs/SOURCES.md), blockout, playable compile joined through a real opening, detail matched against photos with compare.jpg, then lighting. Every map change ends in a full compile that loads, shots, and vbspinfo numbers.
4. After each area: update the README, level map, wiki and Workshop, bump the version, tag and release (pre-approved). The first upload creates a NEW Workshop item (pre-approved, `gmpublish create`), never an update of penn-gmod's 3846546331; record the new ID in HANDOFF.md and tools/package.sh.
5. Make the repo public after a licence audit of refs/ and every asset (README with a ComfyUI banner, no Krea 2; LICENSE; SECURITY.md; wiki), as penn-gmod did.
6. Stop before paid or non-redistributable assets, a scope change, or a level split (askwright page). Decide small rulings and flag them.
7. Stop early if `Status: finished` or nothing can move without Mark; say what waits on Mark (listed under "Waiting on Mark" in HANDOFF.md).

## Hand-over
Run evergreen-wrapup (if it's installed), update the log and HANDOFF.md, and only then print the start command:
`Execute D:/m4bwa/Claude/Projects/Ai/penn-modern-gmod/ai-docs/plans/2026-11-26-penn-modern-40x-continue-prompt.md`
Start it in `D:/m4bwa/Claude/Projects/Ai`. State lives in HANDOFF.md, never in this file.
