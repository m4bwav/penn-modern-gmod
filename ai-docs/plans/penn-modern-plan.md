# gm_penn_modern plan

## Goal
A Workshop-published GMod map of today's Penn Station and Moynihan Train Hall, built by a 40-session chain.

## Status
Setup done 2026-11-26; state in HANDOFF.md.

## Next single action
Session 1: Moynihan refs, dimensions, first compile.

Map: `gm_penn_modern`, today's Penn Station (New York) at 1 ft = 12 units, one map unless the budget forces a split (askwright page first).

## Scope and area order
1. Moynihan Train Hall: the Farley Building's former mail-sorting room under the glass-and-steel skylight (steel trusses, clock, ticketing and waiting rooms along the sides, escalators down to the platforms). Ships as 0.1.0, first upload to a NEW Workshop item (pre-approved).
2. LIRR concourse: the 2021 rebuilt 33rd Street concourse, high ceiling, LED panels, wide corridor.
3. Amtrak concourse.
4. NJ Transit concourse.
5. Platforms with a train (MDL train).
6. Eighth Avenue entrances and street: Farley facade and colonnade, Moynihan's street entrances, the Eighth Avenue stairs, a slice of street with MSG above.

Joining: the West End Concourse links Moynihan to the platforms; real openings, not teleports.

## Scale and budgets (lessons from gm_grand_central and penn-gmod)
- vbsp cap 65,536 unique verts; vbspinfo after every compile, log verts, faces, BSP size in HANDOFF.
- Skylight trusses, escalators, benches, boards, kiosks, the train: MDL models (pm_models.py). Grids, ceiling panels, signage, LED boards: textures. One func_brush per area for decor.
- 150 MB file budget, 60 fps on a mid-range PC.

## References
Wikimedia Commons only, licences that allow redistribution (CC0, PD, CC BY, CC BY-SA); logged in refs/SOURCES.md. Dimensions with citations in ai-docs/notes/ (historywright).

## Release
Each area: README, level map, wiki, Workshop (new item ID in HANDOFF and package.sh), version bump, tag and GitHub release (pre-approved). Repo goes public after a licence audit of refs and assets (README with ComfyUI banner, no Krea 2; LICENSE; SECURITY.md).
