# Shared Garry's Mod lock, sourced by compile.sh, shots.sh, nav.sh and package.sh.
# Several chains share one GMod install (penn-gmod, penn-modern-gmod, ...). Holding the lock is required
# before writing into garrysmod/ (maps, materials, models, lua/autorun), launching gmod.exe or packaging.
# The lock file holds the holder's Windows PID; a lock whose PID is dead, or older than 6 h, is stale and taken over.
# Usage: . tools/gmod_lock.sh; gmod_lock_take; ... (released on exit by the trap)
#        gmod_snapshot; "$G/gmod.exe" ... & ; ...; gmod_kill_own   (kills only gmod.exe started after the snapshot)
GMOD_LOCK="${GMOD_LOCK:-C:/Users/m4bwa/.chainwright/gmod.lock}"
_gl_me() { cat /proc/$$/winpid 2>/dev/null || echo $$; }
_gl_alive() { tasklist //FI "PID eq $1" //FO CSV //NH 2>/dev/null | grep -q "\"$1\""; }
_gl_gmods() { tasklist //FI "IMAGENAME eq gmod.exe" //FO CSV //NH 2>/dev/null | grep -i gmod.exe | cut -d'"' -f4; }
gmod_lock_take() {
	me=$(_gl_me); [ "$GMOD_LOCK_HELD" = "$me" ] && return 0   # re-entry from a script that already holds it
	mkdir -p "$(dirname "$GMOD_LOCK")"
	deadline=$(( $(date +%s) + ${GMOD_LOCK_WAIT:-14400} )); said=""
	while :; do
		if ( set -C; printf '%s %s %s %s\n' "$me" "$(basename "$PWD")" "$(basename "$0")" "$(date -u +%FT%TZ)" > "$GMOD_LOCK" ) 2>/dev/null; then break; fi
		holder=$(cut -d' ' -f1 "$GMOD_LOCK" 2>/dev/null)
		age=$(( $(date +%s) - $(date -r "$GMOD_LOCK" +%s 2>/dev/null || date +%s) ))
		if [ -n "$holder" ] && { ! _gl_alive "$holder" || [ "$age" -gt 21600 ]; }; then
			echo "gmod.lock: stale lock from PID $holder (age ${age}s), taking it over"; rm -f "$GMOD_LOCK"; continue
		fi
		[ -z "$said" ] && { echo "gmod.lock: waiting for $(cat "$GMOD_LOCK" 2>/dev/null)"; said=1; }
		[ "$(date +%s)" -gt "$deadline" ] && { echo "gmod.lock: gave up waiting"; exit 3; }
		sleep 15
	done
	export GMOD_LOCK_HELD="$me"
	trap 'gmod_lock_release' EXIT
	trap 'exit 130' INT TERM
	# A chain whose scripts predate the lock may still run GMod: give its gmod.exe up to 20 min to finish.
	for n in $(seq 1 80); do [ -z "$(_gl_gmods)" ] && break; [ "$n" = 1 ] && echo "gmod.lock: a gmod.exe is already running, waiting"; sleep 15; done
}
gmod_lock_release() {
	[ "$(cut -d' ' -f1 "$GMOD_LOCK" 2>/dev/null)" = "$(_gl_me)" ] && rm -f "$GMOD_LOCK"
	return 0
}
gmod_snapshot() { GMOD_BEFORE=" $(_gl_gmods | tr '\n' ' ') "; }
gmod_kill_own() {
	for PID in $(_gl_gmods); do case "$GMOD_BEFORE" in *" $PID "*) ;; *) taskkill //PID "$PID" //F >/dev/null 2>&1 ;; esac; done
}
