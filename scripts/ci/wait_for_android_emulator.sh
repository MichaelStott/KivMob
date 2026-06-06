#!/usr/bin/env bash
# Wait until the docker-android emulator accepts adb and reports boot complete.
set -euo pipefail

ADB_HOST="${ADB_CONNECT:-kivmob-android-emulator:5555}"
export ANDROID_SERIAL="${ANDROID_SERIAL:-$ADB_HOST}"
BOOT_TIMEOUT="${ANDROID_BOOT_TIMEOUT:-600}"
ADB_BIN="${ADB:-adb}"
ADB_PORT="${ADB_PORT:-5555}"
# Host part of ADB_HOST (for /dev/tcp probe); may be a Docker service name.
ADB_PORT_HOST="${ADB_PORT_HOST:-${ADB_HOST%%:*}}"

_adb_port_open() {
  # bash /dev/tcp works in the smoke image (debian).
  timeout 2 bash -c "echo >/dev/tcp/${ADB_PORT_HOST}/${ADB_PORT}" 2>/dev/null
}

_fail_emulator_gone() {
  echo "ERROR: Nothing is listening on ${ADB_PORT_HOST}:${ADB_PORT}." >&2
  echo "       The docker-android emulator process probably exited (OOM, crash)." >&2
  echo "       On the host: docker logs kivmob-android-emulator" >&2
  echo "       Then: docker compose -f docker-compose.android.yml down -v" >&2
  echo "       Retry: ANDROID_EMU_MEMORY=2048 ANDROID_EMU_SHM=1gb make android-test-banner" >&2
  echo "       Or raise Docker Desktop memory to 8 GiB+ (Settings → Resources)." >&2
  exit 1
}

echo "==> Waiting for emulator at $ADB_HOST (timeout ${BOOT_TIMEOUT}s)"

_elapsed=0
_connected=0
while [ "$_elapsed" -lt 120 ]; do
  if _adb_port_open; then
    break
  fi
  if [ "$_elapsed" -ge 30 ] && [ $((_elapsed % 30)) -eq 0 ]; then
    echo "    … waiting for adb port (${_elapsed}s)"
  fi
  sleep 5
  _elapsed=$((_elapsed + 5))
done
if ! _adb_port_open; then
  _fail_emulator_gone
fi

$ADB_BIN disconnect "$ADB_HOST" 2>/dev/null || true
_elapsed=0
while [ "$_elapsed" -lt 120 ]; do
  if $ADB_BIN connect "$ADB_HOST" 2>/dev/null | grep -qiE 'connected|already'; then
    _connected=1
    break
  fi
  if ! _adb_port_open; then
    _fail_emulator_gone
  fi
  sleep 2
  _elapsed=$((_elapsed + 2))
done
if [ "$_connected" -ne 1 ]; then
  echo "ERROR: Could not connect adb to $ADB_HOST (port open but adb failed)" >&2
  exit 1
fi

ADB="$ADB_BIN -s $ANDROID_SERIAL"

_elapsed=0
_last_log=0
_offline_streak=0
while [ "$_elapsed" -lt "$BOOT_TIMEOUT" ]; do
  if ! _adb_port_open; then
    _fail_emulator_gone
  fi

  _state="$($ADB get-state 2>/dev/null || true)"
  if [ "$_state" = "unauthorized" ]; then
    echo "ERROR: adb device unauthorized — emulator and client must share the same adbkey." >&2
    echo "       Run: ./scripts/ci/ensure_docker_adb_keys.sh" >&2
    echo "       Then: docker compose -f docker-compose.android.yml down -v" >&2
    echo "       Retry: make android-test-banner" >&2
    exit 1
  fi
  case "$_state" in
    device)
      _offline_streak=0
      boot="$($ADB shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
      if [ "$boot" = "1" ]; then
        echo "==> Emulator boot complete (${_elapsed}s)"
        exit 0
      fi
      ;;
    offline | unknown)
      _offline_streak=$((_offline_streak + 1))
      if [ "$_offline_streak" -ge 6 ]; then
        echo "ERROR: adb reports device offline — emulator likely crashed." >&2
        _fail_emulator_gone
      fi
      ;;
  esac

  if [ "$_elapsed" -ge "$_last_log" ]; then
    echo "    … still booting (${_elapsed}s / ${BOOT_TIMEOUT}s, adb state: ${_state:-none})"
    _last_log=$((_elapsed + 30))
  fi
  sleep 5
  _elapsed=$((_elapsed + 5))
done

echo "ERROR: Timed out waiting for sys.boot_completed=1" >&2
$ADB shell getprop sys.boot_completed 2>/dev/null || true
exit 1
