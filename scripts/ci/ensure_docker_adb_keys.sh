#!/usr/bin/env bash
# Shared adb keys for docker-android Play Store images (emulator + smoke must match).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KEY_DIR="$ROOT/.docker-android/keys"

mkdir -p "$KEY_DIR"
chmod 700 "$KEY_DIR" 2>/dev/null || true

if [ -f "$KEY_DIR/adbkey" ] && [ -f "$KEY_DIR/adbkey.pub" ]; then
  exit 0
fi

_keygen() {
  local dir="$1"
  rm -f "$dir/adbkey" "$dir/adbkey.pub"
  adb keygen "$dir/adbkey"
}

echo "==> Generating shared adb keys in $KEY_DIR (required for Play Store emulator images)"
if command -v adb >/dev/null 2>&1; then
  _keygen "$KEY_DIR"
else
  docker run --rm -v "$KEY_DIR:/keys" debian:bookworm-slim bash -ec '
    apt-get update -qq && apt-get install -y -qq adb >/dev/null
    adb keygen /keys/adbkey
  '
fi

if [ ! -f "$KEY_DIR/adbkey" ] || [ ! -f "$KEY_DIR/adbkey.pub" ]; then
  echo "ERROR: failed to create adb keys in $KEY_DIR" >&2
  exit 1
fi

chmod 600 "$KEY_DIR/adbkey" 2>/dev/null || true
# New keys are not yet trusted by an existing AVD userdata volume.
date -Iseconds >"$KEY_DIR/.generated"
echo "==> Created adb keys. If the emulator was used before, reset its volume:"
echo "    docker compose -f docker-compose.android.yml down -v"
