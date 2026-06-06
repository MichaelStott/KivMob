#!/usr/bin/env bash
# Host-side: shared adb keys, Docker emulator, and adb connect for make deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KEY_DIR="$ROOT/.docker-android/keys"
ADB_HOME="$ROOT/.docker-android/adb-home"
ANDROID_SERIAL="${ANDROID_SERIAL:-localhost:5555}"

command -v adb >/dev/null 2>&1 || {
  echo "ERROR: adb not in PATH (install android-tools-adb)." >&2
  exit 1
}

"$ROOT/scripts/ci/ensure_docker_adb_keys.sh"

mkdir -p "$ADB_HOME/.android"
if ! cmp -s "$KEY_DIR/adbkey" "$ADB_HOME/.android/adbkey" 2>/dev/null ||
  ! cmp -s "$KEY_DIR/adbkey.pub" "$ADB_HOME/.android/adbkey.pub" 2>/dev/null; then
  cp "$KEY_DIR/adbkey" "$KEY_DIR/adbkey.pub" "$ADB_HOME/.android/"
  chmod 600 "$ADB_HOME/.android/adbkey"
fi

if [ -f "$KEY_DIR/.generated" ]; then
  echo "==> New adb keys: resetting emulator volume so the AVD trusts them"
  "$ROOT/scripts/ci/docker_compose.sh" -f "$ROOT/docker-compose.android.yml" down -v 2>/dev/null || true
  rm -f "$KEY_DIR/.generated"
fi

"$ROOT/scripts/ci/ensure_docker_emulator.sh"

export HOME="$ADB_HOME"
export ADB_CONNECT="$ANDROID_SERIAL"
export ANDROID_SERIAL
"$ROOT/scripts/ci/wait_for_android_emulator.sh"

echo "==> Host adb ready ($ANDROID_SERIAL)"
