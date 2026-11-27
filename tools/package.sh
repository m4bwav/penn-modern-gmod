#!/bin/sh
# Package the compiled BSP as a .gma and update Workshop item ${WORKSHOP_ID:?set WORKSHOP_ID (first upload: gmpublish create)}.
# Run tools/compile.sh first. Usage: sh tools/package.sh "change note" [preview.jpg ...]
# DRY=1 builds the .gma only.
set -e
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
ID="${WORKSHOP_ID:?set WORKSHOP_ID; first upload: gmpublish create, then record the id here}"
cd "$(dirname "$0")/.."
. tools/gmod_lock.sh; gmod_lock_take   # shared GMod lock, released on exit
NOTE="${1:-Update}"
[ $# -gt 0 ] && shift
rm -rf build/addon && mkdir -p build/addon/maps
cp src/gm_penn_modern.bsp build/addon/maps/
[ -f src/gm_penn_modern.nav ] && cp src/gm_penn_modern.nav build/addon/maps/   # from tools/nav.sh
cat > build/addon/addon.json <<'EOF'
{
	"title": "gm_penn_modern",
	"type": "map",
	"tags": ["scenic", "realism"],
	"ignore": []
}
EOF
"$G/bin/gmad.exe" create -folder build/addon -out build/gm_penn_modern.gma | tail -2
ls -la build/gm_penn_modern.gma
[ -n "$DRY" ] && exit 0
"$G/bin/gmpublish.exe" update -id "$ID" -addon build/gm_penn_modern.gma -changes "$NOTE" | tail -3
python tools/workshop_update.py "$ID" --desc workshop/description.txt ${1:+--preview "$@"}
