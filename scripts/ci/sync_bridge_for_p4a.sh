#!/usr/bin/env bash
# Copy Java bridge sources into p4a_recipes (used before Gradle / Docker builds).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/p4a_recipes/kivmob/src"
SRC="$ROOT/android/kivmob-bridge/kivmob-bridge/src/main/java/org"

mkdir -p "$DEST"
rm -rf "$DEST/org"
cp -a "$SRC" "$DEST/"
