#!/usr/bin/env bash
# Mirror the Docker emulator screen on the host (halimqarroum/docker-android is headless).
set -euo pipefail

ADB_HOME="${ADB_HOME:?Set ADB_HOME (e.g. repo/.docker-android/adb-home)}"
ANDROID_SERIAL="${ANDROID_SERIAL:-localhost:5555}"
SCRCPY_BACKGROUND="${SCRCPY_BACKGROUND:-0}"

if ! command -v scrcpy >/dev/null 2>&1; then
  cat >&2 <<'EOF'
The Docker emulator has no built-in display. Install scrcpy to mirror it on your desktop:

  sudo apt install scrcpy

Then run:

  make demo-view

The demo APK can still be installed and launched via adb without scrcpy.
EOF
  exit 1
fi

export HOME="$ADB_HOME"

_scrcpy_args=(-s "$ANDROID_SERIAL" --window-title "KivMob Demo")

if [ "$SCRCPY_BACKGROUND" = "1" ]; then
  scrcpy "${_scrcpy_args[@]}" &
  echo "==> scrcpy opened (pid $!) — interact with the emulator in that window"
else
  exec scrcpy "${_scrcpy_args[@]}"
fi
