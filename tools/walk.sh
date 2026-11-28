#!/bin/sh
# Walk test: launch GMod on gm_penn_modern, tools/lua/pm_walk_sv.lua walks every stair and
# escalator and writes PASS/FAIL lines. Run after compile.sh.
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
cd "$(dirname "$0")/.."
. tools/gmod_lock.sh; gmod_lock_take   # shared GMod lock, released on exit
D="$G/garrysmod/data"
echo 4000 > "$G/steam_appid.txt"
mkdir -p "$G/garrysmod/lua/autorun/server" "$D"
cp tools/lua/pm_walk_sv.lua "$G/garrysmod/lua/autorun/server/pm_walk_sv.lua"
cp tools/lua/a_pm_nofnaf.lua "$G/garrysmod/lua/autorun/a_pm_nofnaf.lua"
rm -rf "$D/pm_walk"; echo go > "$D/pm_walk_go.txt"
gmod_snapshot
"$G/gmod.exe" -windowed -w 1280 -h 720 -novid -nojoy -condebug +sv_cheats 1 +vj_fnaf_cache 0 +map gm_penn_modern &
for n in $(seq 1 ${WAIT:-100}); do [ -f "$D/pm_walk/done.txt" ] && break; sleep 5; done
sleep 2
gmod_kill_own
rm -f "$G/garrysmod/lua/autorun/server/pm_walk_sv.lua" "$G/garrysmod/lua/autorun/a_pm_nofnaf.lua" "$D/pm_walk_go.txt"
cat "$D/pm_walk/result.txt" 2>/dev/null || { echo "no walk result: see $G/garrysmod/console.log"; exit 1; }
! grep -q FAIL "$D/pm_walk/result.txt"
