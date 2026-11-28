# Moving walkway: one pair, in the passage under Eighth Avenue

Date: 2026-11-28 (session 13, movers)

## Decision
Add one pair of moving walkways (two lanes, opposite directions) and only in the passage under Eighth Avenue between the West End Concourse stub and the LIRR concourse (build_vmf.py `movers()`, x 1000..1880, 73 ft). Eastbound belt on the south side (keep right), westbound on the north, each 4 ft wide, 4 u proud of the floor, with dark side rails. Open floor stays down the middle and along both walls.

## Why
- It is the longest plain corridor in the map with nothing else in it (95 ft, 30 ft wide), it links two areas, and a walkway there reads as plausible.
- The other long spaces are rooms people stand and look around in (Moynihan hall, the LIRR corridor with its columns and boards, the Amtrak and NJ Transit halls, the platform): a belt would block circulation and has no real counterpart.
- Real Penn Station has no moving walkways; this is a gameplay addition the owner asked for, so it stays a single, contained one.
- Keeping the middle clear means the existing to_lirr walk route and anyone ignoring the belts are unaffected.

## How
func_conveyor (flat is its native case), speed 100 u/s, scrolling belt textures walkbelt_e / walkbelt_w (TextureScroll proxy, one per direction). See solutions/moving-escalators-in-source.md.
