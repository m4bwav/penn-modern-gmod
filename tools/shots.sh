#!/bin/sh
# Launch GMod on gm_penn_modern, let tools/lua/pm_shots.lua capture the cameras,
# copy the JPGs into shots/. CAMS="a b" limits the run to those cameras. UNCAP=1 lifts the frame cap (fps_max 0, vsync off) for the fps log. The Lua quits the game; fallback kill is by PID only.
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
QW="C:/Users/m4bwa/.claude/plugins/cache/mark-local/quirkwright/0.2.1/skills/quirkwright/scripts/qw.py"
cd "$(dirname "$0")/.."
. tools/gmod_lock.sh; gmod_lock_take   # shared GMod lock, released on exit
D="$G/garrysmod/data"
echo 4000 > "$G/steam_appid.txt"
cp tools/lua/pm_shots.lua "$G/garrysmod/lua/autorun/client/pm_shots.lua"
cp tools/lua/a_pm_nofnaf.lua "$G/garrysmod/lua/autorun/a_pm_nofnaf.lua"
mkdir -p "$G/garrysmod/lua/autorun/server"; cp tools/lua/pm_shots_sv.lua "$G/garrysmod/lua/autorun/server/pm_shots_sv.lua"
EXTRA=""; [ -n "$UNCAP" ] && EXTRA="+fps_max 0 +mat_vsync 0" ; EXTRA="$EXTRA $GARGS"   # GARGS: extra launch args, e.g. "+sv_cheats 1 +mat_fullbright 1"
mkdir -p "$D"; rm -rf "$D/pm_shots"; echo "${CAMS:-go}" > "$D/pm_shots_go.txt"
gmod_snapshot
"$G/gmod.exe" -windowed -w 1600 -h 900 -novid -nojoy -condebug +sv_cheats 1 +vj_fnaf_cache 0 +r_drawviewmodel 0 $EXTRA +map gm_penn_modern &
for n in $(seq 1 ${WAIT:-180}); do [ -f "$D/pm_shots/done.txt" ] && break; sleep 5; done
sleep 5
# Only the gmod.exe this script started, by PID (Lua quit is blocked in this GMod build; another chain may share GMod).
gmod_kill_own
rm -f "$G/garrysmod/lua/autorun/server/pm_shots_sv.lua" "$G/garrysmod/lua/autorun/a_pm_nofnaf.lua" "$G/garrysmod/lua/autorun/client/pm_shots.lua" "$D/pm_shots_go.txt"
stamp=$(date +%Y%m%d-%H%M); mkdir -p "shots/$stamp"
cp "$D"/pm_shots/*.jpg "$D"/pm_shots/fps.txt "shots/$stamp/" 2>/dev/null; ls "shots/$stamp"
cat "shots/$stamp/fps.txt" 2>/dev/null
