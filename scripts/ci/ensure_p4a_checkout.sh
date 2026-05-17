#!/usr/bin/env bash
# Local python-for-android checkout for CI (matches demo's proven p4a commit).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
P4A_COMMIT="${P4A_COMMIT:-957a3e5f}"
P4A_DIR="${P4A_DIR:-$ROOT/.ci-cache/p4a-$P4A_COMMIT}"

if [ ! -d "$P4A_DIR/.git" ]; then
  mkdir -p "$(dirname "$P4A_DIR")"
  git clone --filter=blob:none https://github.com/kivy/python-for-android.git "$P4A_DIR"
fi

git -C "$P4A_DIR" fetch --depth 1 origin "$P4A_COMMIT" 2>/dev/null || git -C "$P4A_DIR" fetch --unshallow 2>/dev/null || true
git -C "$P4A_DIR" checkout -f "$P4A_COMMIT"

echo "$P4A_DIR"
