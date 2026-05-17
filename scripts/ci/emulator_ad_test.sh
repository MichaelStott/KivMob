#!/usr/bin/env bash
# Install APK on a running emulator/device and validate AdMob smoke via logcat.
set -euo pipefail

AD_TYPE="${1:?Usage: $0 <banner|interstitial|rewarded> <apk-path>}"
APK="${2:?Usage: $0 <banner|interstitial|rewarded> <apk-path>}"

if [ ! -f "$APK" ]; then
  echo "APK not found: $APK" >&2
  exit 1
fi

case "$AD_TYPE" in
  banner) ACTIVITY_PKG="org.kivmob.ci.kivmobci_banner" ;;
  interstitial) ACTIVITY_PKG="org.kivmob.ci.kivmobci_interstitial" ;;
  rewarded) ACTIVITY_PKG="org.kivmob.ci.kivmobci_rewarded" ;;
  *)
    echo "Unknown ad type: $AD_TYPE" >&2
    exit 1
    ;;
esac

ACTIVITY="${ACTIVITY_PKG}/org.kivy.android.PythonActivity"
LOG_TIMEOUT="${LOG_TIMEOUT:-180}"
ADB_DEVICE_TIMEOUT="${ADB_DEVICE_TIMEOUT:-120}"
BOOT_TIMEOUT="${BOOT_TIMEOUT:-300}"

_adb_device_ready() {
  adb get-state 2>/dev/null | grep -q '^device$'
}

echo "==> Checking for Android device (timeout ${ADB_DEVICE_TIMEOUT}s)…"
_elapsed=0
while [ "$_elapsed" -lt "$ADB_DEVICE_TIMEOUT" ]; do
  if _adb_device_ready; then
    break
  fi
  sleep 2
  _elapsed=$((_elapsed + 2))
done
if ! _adb_device_ready; then
  echo "No Android device detected (adb devices is empty or offline)." >&2
  echo "Start an emulator, then retry:" >&2
  echo "  make emulator-start    # separate terminal" >&2
  echo "  make emulator-wait" >&2
  echo "  make ci-android-smoke APP=$AD_TYPE" >&2
  exit 1
fi
adb devices -l

echo "==> Waiting for boot completion (timeout ${BOOT_TIMEOUT}s)…"
_elapsed=0
while [ "$_elapsed" -lt "$BOOT_TIMEOUT" ]; do
  boot="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  if [ "$boot" = "1" ]; then
    echo "Emulator boot completed."
    break
  fi
  sleep 2
  _elapsed=$((_elapsed + 2))
done
if [ "$_elapsed" -ge "$BOOT_TIMEOUT" ]; then
  echo "Timed out waiting for sys.boot_completed=1" >&2
  exit 1
fi

echo "==> Installing $APK"
adb install -r "$APK"

echo "==> Launching $ACTIVITY"
adb logcat -c
adb shell am start -n "$ACTIVITY"

LOG_FILE="$(mktemp)"
LOG_PID=""
_stop_logcat() {
  if [ -n "$LOG_PID" ]; then
    kill "$LOG_PID" 2>/dev/null || true
    wait "$LOG_PID" 2>/dev/null || true
    LOG_PID=""
  fi
}
trap '_stop_logcat; rm -f "$LOG_FILE"' EXIT

adb logcat -v brief '*:S' 'python:I' 'python:D' 'KivMobAdsBridge:D' >"$LOG_FILE" &
LOG_PID=$!

wait_for_log() {
  local pattern="$1"
  local timeout="$2"
  local elapsed=0
  echo "==> Waiting for log: $pattern (timeout ${timeout}s)"
  while [ "$elapsed" -lt "$timeout" ]; do
    if grep -qE "$pattern" "$LOG_FILE" 2>/dev/null; then
      echo "OK log: $pattern"
      return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "Timeout waiting for log: $pattern" >&2
  echo "--- logcat tail ---" >&2
  tail -n 80 "$LOG_FILE" >&2 || true
  return 1
}

case "$AD_TYPE" in
  banner)
    wait_for_log 'CI_TEST:banner_init' "$LOG_TIMEOUT"
    wait_for_log 'CI_TEST:banner_shown' 60
    wait_for_log 'KivMob: Mobile Ads initialized' 90 || true
    ;;
  interstitial)
    wait_for_log 'CI_TEST:interstitial_init' "$LOG_TIMEOUT"
    wait_for_log 'KivMob: interstitial loaded\.' 120
    wait_for_log 'CI_TEST:interstitial_show' 30
    wait_for_log 'KivMob: interstitial shown' 60
    sleep 2
    adb shell input keyevent 4
    wait_for_log 'KivMob: interstitial dismissed' 45
    ;;
  rewarded)
    wait_for_log 'CI_TEST:rewarded_init' "$LOG_TIMEOUT"
    wait_for_log 'KivMob: rewarded ad loaded\.' 120
    wait_for_log 'CI_TEST:rewarded_show' 30
    wait_for_log 'KivMob: rewarded ad shown' 60
    wait_for_log 'CI_TEST:rewarded_earned' 120
    ;;
esac

_stop_logcat
echo "PASS: $AD_TYPE ad smoke test completed"
