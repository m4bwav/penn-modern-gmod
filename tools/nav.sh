#!/bin/sh
# Generate the nav mesh for nextbots and NPCs: launch GMod on gm_penn_modern with sv_cheats,
# tools/lua/pm_nav.lua runs nav_generate (nav_quicksave 1), the map reloads, the Lua writes the
# area count and quits. Copies maps/gm_penn_modern.nav to src/ (package.sh ships it). Run after compile.sh.
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
QW="C:/Users/m4bwa/.claude/plugins/cache/mark-local/quirkwright/0.2.1/skills/quirkwright/scripts/qw.py"
cd "$(dirname "$0")/.."
. tools/gmod_lock.sh; gmod_lock_take   # shared GMod lock, released on exit
D="$G/garrysmod/data"
echo 4000 > "$G/steam_appid.txt"
mkdir -p "$G/garrysmod/lua/autorun/server" "$D"
cp tools/lua/pm_nav.lua "$G/garrysmod/lua/autorun/server/pm_nav.lua"
rm -rf "$D/pm_nav" "$G/garrysmod/maps/gm_penn_modern.nav"; echo go > "$D/pm_nav_go.txt"
gmod_snapshot
"$G/gmod.exe" -windowed -w 1280 -h 720 -novid -nojoy -condebug +sv_cheats 1 +map gm_penn_modern &
for n in $(seq 1 240); do [ -f "$D/pm_nav/done.txt" ] && break; sleep 5; done
sleep 5
# Only the gmod.exe this script started, by PID (Lua quit is blocked in this GMod build; another chain may share GMod).
gmod_kill_own
rm -f "$G/garrysmod/lua/autorun/server/pm_nav.lua" "$D/pm_nav_go.txt"
cat "$D/pm_nav/done.txt" 2>/dev/null || { echo "no nav: see $G/garrysmod/console.log"; exit 1; }
cp "$G/garrysmod/maps/gm_penn_modern.nav" src/
ls -la src/gm_penn_modern.nav
