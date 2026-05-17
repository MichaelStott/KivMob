#!/usr/bin/env bash
# Generate tests/android_ci/<app>/buildozer.spec from buildozer.spec.in
set -euo pipefail

APP="${1:?Usage: $0 <banner|interstitial|rewarded>}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TEMPLATE="$ROOT/tests/android_ci/buildozer.spec.in"
OUT_DIR="$ROOT/tests/android_ci/$APP"
OUT_SPEC="$OUT_DIR/buildozer.spec"

case "$APP" in
  banner)
    APP_TITLE="KivMob CI Banner"
    PACKAGE_NAME="kivmobci_banner"
    ;;
  interstitial)
    APP_TITLE="KivMob CI Interstitial"
    PACKAGE_NAME="kivmobci_interstitial"
    ;;
  rewarded)
    APP_TITLE="KivMob CI Rewarded"
    PACKAGE_NAME="kivmobci_rewarded"
    ;;
  *)
    echo "Unknown app: $APP (expected banner, interstitial, or rewarded)" >&2
    exit 1
    ;;
esac

test -f "$TEMPLATE"

BRIDGE_VERSION="$(python3 "$ROOT/scripts/version.py" kivmob-bridge)"

mkdir -p "$OUT_DIR"
sed \
  -e "s|@APP_TITLE@|$APP_TITLE|g" \
  -e "s|@PACKAGE_NAME@|$PACKAGE_NAME|g" \
  -e "s|@BRIDGE_VERSION@|$BRIDGE_VERSION|g" \
  "$TEMPLATE" >"$OUT_SPEC"

echo "Wrote $OUT_SPEC (package org.kivmob.ci.$PACKAGE_NAME)"
