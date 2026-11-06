#!/usr/bin/env bash
# Smoke test for Omalight. Runs against an isolated Quickshell process built
# from copies of the plugin files. It never touches omarchy-shell, and it writes
# settings to a scratch file and never changes the real screen brightness.
set -u

DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRATCH="${SCRATCH:-$(mktemp -d)}"
ROOT="$SCRATCH/root"
HARNESS="$ROOT/shell.qml"
export EDGE_LIGHT_SETTINGS="$SCRATCH/settings.json"
export EDGE_LIGHT_BRIGHTNESS=0

# Build the harness root: plugin QML and lib/ copied next to the test shell.
rm -rf "$ROOT"; mkdir -p "$ROOT"
cp "$DIR/Service.qml" "$DIR/EdgeLight.qml" "$DIR/EdgeBand.qml" "$ROOT"/ && cp -r "$DIR/lib" "$ROOT"/ && cp "$DIR/test/harness/shell.qml" "$ROOT/shell.qml"

pass=0; fail=0
ok()   { pass=$((pass+1)); echo "  PASS  $1"; }
bad()  { fail=$((fail+1)); echo "  FAIL  $1"; }
call() { quickshell ipc -p "$HARNESS" call edge call "$1" "${2:-}" 2>/dev/null; }
glowLayers() { hyprctl layers 2>/dev/null | grep -c "omarchy-omalight\b" || true; }
field() { call status | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
isTrue()  { [ "$1" = "True" ] || [ "$1" = "true" ]; }
isFalse() { [ "$1" = "False" ] || [ "$1" = "false" ]; }

# Wait for any old harness to exit, so a stale instance can't answer IPC.
pkill -f "quickshell -p $ROOT" 2>/dev/null
for _ in $(seq 1 20); do pgrep -f "quickshell -p $ROOT" >/dev/null || break; sleep 0.25; done

(quickshell -p "$HARNESS" > "$SCRATCH/harness.log" 2>&1 &)
for _ in $(seq 1 30); do call status >/dev/null && break; sleep 0.5; done

echo "Omalight smoke test (scratch: $SCRATCH)"

# Start state
isFalse "$(field enabled)" && ok "starts with light off" || bad "starts with light off"
[ "$(glowLayers)" = "0" ] && ok "no glow surface while off" || bad "glow surface mapped while off"

# Light on/off
call lightOn >/dev/null; sleep 0.5
isTrue "$(field enabled)" && ok "lightOn enables light" || bad "lightOn enables light"
[ "$(glowLayers)" -ge 1 ] && ok "glow surface mapped when on" || bad "glow surface not mapped when on"
call lightOff >/dev/null; sleep 0.5
[ "$(glowLayers)" = "0" ] && ok "glow surface unmapped when off" || bad "glow surface still mapped after off"

# Toggle (shortcut path)
call lightToggle >/dev/null; sleep 0.3
[ "$(glowLayers)" -ge 1 ] && ok "lightToggle turns on" || bad "lightToggle did not turn on"
call lightToggle >/dev/null; sleep 0.5
[ "$(glowLayers)" = "0" ] && ok "lightToggle turns off again" || bad "lightToggle did not turn off"

# Settings persist, apply, and clamp
call setValue '{"intensity":40,"kelvin":3200,"width":30}' >/dev/null; sleep 0.5
python3 -c "import json; d=json.load(open('$EDGE_LIGHT_SETTINGS')); assert d['intensity']==40 and d['kelvin']==3200 and d['width']==30" \
  && ok "setValue persists to settings file" || bad "setValue did not persist"
[ "$(field intensity)" = "40" ] && ok "setValue applies live" || bad "setValue did not apply"
call setValue '{"intensity":999,"kelvin":10}' >/dev/null
[ "$(field intensity)" = "100" ] && [ "$(field kelvin)" = "2700" ] && ok "out-of-range values are clamped" || bad "values not clamped"
call setValue '{"intensity":70,"kelvin":4000,"width":28}' >/dev/null

# Log hygiene
if grep -E "WARN|ERROR|TypeError|ReferenceError" "$SCRATCH/harness.log" | grep -v "qs-blackhole\|portal" >/dev/null; then
  bad "harness log has warnings or errors (see $SCRATCH/harness.log)"
else
  ok "harness log has no warnings or errors"
fi

pkill -f "quickshell -p $ROOT" 2>/dev/null
echo
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
