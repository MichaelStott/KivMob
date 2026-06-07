#!/usr/bin/env bash
# Logcat smoke tests for one or more ad apps (banner, interstitial, rewarded).
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <banner|interstitial|rewarded> ..." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
# Workspace is :ro in the smoke container; scripts are executable in git and on the host.

ADB_HOST="${ADB_CONNECT:-kivmob-android-emulator:5555}"
export ANDROID_SERIAL="${ANDROID_SERIAL:-$ADB_HOST}"

echo "==> Verifying emulator is still up before smoke tests"
if ! ./scripts/ci/wait_for_android_emulator.sh; then
  exit 1
fi

export ADB="adb -s $ANDROID_SERIAL"

for app in "$@"; do
  case "$app" in
    banner | interstitial | rewarded) ;;
    *)
      echo "Unknown ad app: $app" >&2
      exit 1
      ;;
  esac
  apk="$(ls -t "tests/android_ci/$app"/bin/*debug*.apk 2>/dev/null | head -n1 || true)"
  if [ -z "$apk" ]; then
    echo "No APK for $app in tests/android_ci/$app/bin" >&2
    exit 1
  fi
  echo ""
  echo "========================================"
  echo "  Smoke test: $app"
  echo "  APK: $apk"
  echo "========================================"
  ./scripts/ci/emulator_ad_test.sh "$app" "$apk"
done

echo ""
echo "PASS: smoke test(s) completed for: $*"
