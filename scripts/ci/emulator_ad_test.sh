#!/usr/bin/env bash
# Install APK on a running emulator/device and validate AdMob smoke via logcat.
# STRICT_DISMISS=1 — fail interstitial smoke if dismiss log is not seen (default: warn only).
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
STRICT_DISMISS="${STRICT_DISMISS:-0}"

ADB_BIN="${ADB:-adb}"
if [ -n "${ANDROID_SERIAL:-}" ]; then
  ADB="$ADB_BIN -s $ANDROID_SERIAL"
else
  ADB="$ADB_BIN"
fi

_adb_device_ready() {
  $ADB get-state 2>/dev/null | grep -q '^device$'
}

echo "==> Checking for Android device (timeout ${ADB_DEVICE_TIMEOUT}s)…"
_elapsed=0
_offline_streak=0
while [ "$_elapsed" -lt "$ADB_DEVICE_TIMEOUT" ]; do
  if _adb_device_ready; then
    break
  fi
  _state="$($ADB get-state 2>/dev/null || true)"
  if [ "$_state" = "offline" ] || [ "$_state" = "unknown" ]; then
    _offline_streak=$((_offline_streak + 1))
    if [ "$_offline_streak" -ge 5 ]; then
      echo "Device went offline — emulator likely exited. Check: docker logs kivmob-android-emulator" >&2
      exit 1
    fi
  else
    _offline_streak=0
  fi
  sleep 2
  _elapsed=$((_elapsed + 2))
done
if ! _adb_device_ready; then
  echo "No Android device detected (adb empty/offline or emulator not running)." >&2
  echo "  make android-test-banner   # build APK, start emulator, smoke" >&2
  exit 1
fi
$ADB devices -l

echo "==> Waiting for boot completion (timeout ${BOOT_TIMEOUT}s)…"
_elapsed=0
while [ "$_elapsed" -lt "$BOOT_TIMEOUT" ]; do
  boot="$($ADB shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
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
$ADB install -r "$APK"

echo "==> Launching $ACTIVITY"
$ADB logcat -c
$ADB shell am start -n "$ACTIVITY"

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

$ADB logcat -v brief '*:S' 'python:I' 'python:D' 'KivMobAdsBridge:D' >"$LOG_FILE" &
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

# Google test interstitials ignore BACK on emulators; close X is top-right.
_dismiss_interstitial_ad() {
  local size w h attempt
  echo "==> Waiting for test interstitial close control"
  sleep 5
  for attempt in 1 2 3; do
    size="$($ADB shell wm size 2>/dev/null | tr -d '\r' | grep -oE '[0-9]+x[0-9]+' | tail -1 || true)"
    if [ -n "$size" ]; then
      w="${size%x*}"
      h="${size#*x}"
      echo "==> Dismiss attempt $attempt: tap top-right (${w}x${h})"
      $ADB shell input tap $((w * 95 / 100)) $((h * 5 / 100))
      sleep 1
    fi
    echo "==> Dismiss attempt $attempt: BACK key"
    $ADB shell input keyevent 4
    sleep 2
    if grep -qE 'interstitial dismissed' "$LOG_FILE" 2>/dev/null; then
      return 0
    fi
  done
  return 1
}

wait_for_log_with_dismiss() {
  local pattern="$1"
  local timeout="$2"
  local elapsed=0
  echo "==> Waiting for log: $pattern (timeout ${timeout}s, retrying dismiss)"
  while [ "$elapsed" -lt "$timeout" ]; do
    if grep -qE "$pattern" "$LOG_FILE" 2>/dev/null; then
      echo "OK log: $pattern"
      return 0
    fi
    if [ "$elapsed" -gt 0 ] && [ $((elapsed % 10)) -eq 0 ]; then
      _dismiss_interstitial_ad || true
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "Timeout waiting for log: $pattern" >&2
  echo "--- logcat tail ---" >&2
  tail -n 80 "$LOG_FILE" >&2 || true
  return 1
}

# Kivy Logger splits on the first colon (e.g. "CI_TEST:banner_init" -> "[CI_TEST     ]banner_init").
case "$AD_TYPE" in
  banner)
    wait_for_log 'banner_init' "$LOG_TIMEOUT"
    wait_for_log 'banner_shown' 60
    wait_for_log 'Mobile Ads initialized' 90 || true
    ;;
  interstitial)
    wait_for_log 'interstitial_init' "$LOG_TIMEOUT"
    wait_for_log 'interstitial loaded' 120
    wait_for_log 'interstitial_show' 30
    wait_for_log 'interstitial shown' 60
    _dismiss_interstitial_ad || true
    if ! wait_for_log_with_dismiss 'interstitial dismissed' 90; then
      if [ "$STRICT_DISMISS" = "1" ]; then
        echo "FAIL: interstitial dismiss not confirmed (STRICT_DISMISS=1)" >&2
        exit 1
      fi
      echo "WARNING: dismiss not confirmed on emulator (load+show OK; test ads often ignore BACK/tap)" >&2
    fi
    ;;
  rewarded)
    wait_for_log 'rewarded_init' "$LOG_TIMEOUT"
    wait_for_log 'rewarded ad loaded' 120
    wait_for_log 'rewarded_show' 30
    wait_for_log 'rewarded ad shown' 60
    wait_for_log 'rewarded_earned' 120
    ;;
esac

_stop_logcat
echo "PASS: $AD_TYPE ad smoke test completed"
