# Moving escalators and walkways in Source / Garry's Mod

Session 13 (2026-11-28), 0.6.0. Code: tools/build_vmf.py `movers()`, tools/pm_models.py `escalator()` (tread_up / tread_dn), tools/pm_textures.py (esctread, walkbelt_e/w), walk routes in tools/lua/pm_walk_sv.lua.

## What worked
- **Escalators: a level trigger_push per lane over the playerclip ramp wedge.** pushdir "0 0 0" (+x) or "0 180 0", speed 90 (horizontal; about 100 u/s along the 28 degree slope), spawnflags 1 (clients), box over the wedge's x range and lane half, from the bottom floor to 80 u above the top. trigger_push sets the player's base velocity; ground movement (WalkMove) adds it each tick and follows the slope, so the player rides up or down with no input and can still walk against it (200 - 90 = 110 u/s net). All 16 escalator walk routes PASS (ride_* idle, against_* walking).
- **Do not give the push an upward component.** CTriggerPush ungrounds a grounded player whenever the push has z > 0 (sets ground entity NULL and lifts 1 u), so a push along the slope would make the player hop. The level push plus the walkable ramp does the climbing.
- **Lanes:** each escalator.mdl is two escalators. The model's SMD -y lane is the up lane, +y the down lane. At yaw 90 (climbs +x) SMD axes = world axes, so the up lane is y < centre; at yaw 270 it is y > centre. The trigger halves split at the centre line.
- **Visible motion on the model:** only the tread tops (`_box(..., faces={(0,0,1): ...})`) get tread_up / tread_dn, VertexLitGeneric with a TextureScroll proxy on $basetexturetransform. _box maps u 0..1 across each tread, so one step = one texture repeat; rate 6/s = 90 u/s / 14.9 u step. The yellow edge band slides across every tread, which reads as the steps moving. Risers keep the static steptread (a scrolling riser would just flicker).
- **TextureScroll direction:** it shifts texcoords by +rate*t, so the image moves toward -u. Motion toward +u needs texturescrollangle 180.
- **Walkway: func_conveyor works for players in GMod.** movedir "0 0 0" / "0 180 0", speed 100, spawnflags 0 (flag 1 is No Push). Idle rides 1010 -> 1907 in 12 s; walking against still gets through. Belt texture scrolls via its own TextureScroll material per direction (independent of the entity's speed, so keep them matched by hand: 100 u/s / 64 u repeat = 1.5625).

## Not tried / limits
- func_conveyor on a slope: not used for escalators (its push is along movedir, flat; a sloped belt would hit the same ungrounding question). trigger_push was simpler and proven.
- The steps are static geometry; only the texture moves, so step edges do not physically travel. Good enough at walking distance.
- Props riding: trigger_push spawnflags 1 pushes players only; physics props on the escalators do not move.
