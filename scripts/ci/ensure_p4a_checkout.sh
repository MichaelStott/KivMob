#!/usr/bin/env bash
# Pinned python-for-android for CI: Python 3.11.5 + AGP 8.11 (Kotlin 2.x / play-services-ads 25.x).
# Do not use p4a HEAD — it targets Python 3.14 and breaks the pinned buildozer image toolchain.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
P4A_COMMIT="${P4A_COMMIT:-a8f2ca1c5b1bb6696b47fdf2c052285e116e0ebe}"
P4A_DIR="${P4A_DIR:-$ROOT/.ci-cache/p4a-$P4A_COMMIT}"

if [ ! -d "$P4A_DIR/.git" ]; then
  mkdir -p "$(dirname "$P4A_DIR")"
  git clone --filter=blob:none https://github.com/kivy/python-for-android.git "$P4A_DIR"
fi

git -C "$P4A_DIR" fetch --depth 1 origin "$P4A_COMMIT" 2>/dev/null || git -C "$P4A_DIR" fetch --unshallow 2>/dev/null || true
git -C "$P4A_DIR" checkout -f "$P4A_COMMIT"

echo "$P4A_DIR"
