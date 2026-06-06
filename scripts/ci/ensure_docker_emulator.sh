#!/usr/bin/env bash
# Host-side: ensure the docker-android emulator container is up and booted.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-$ROOT/docker-compose.android.yml}"
COMPOSE=(./scripts/ci/docker_compose.sh -f "$COMPOSE_FILE")

EMU_CONTAINER="${ANDROID_EMU_CONTAINER:-kivmob-android-emulator}"
_boot_timeout="${ANDROID_BOOT_TIMEOUT:-600}"

_emulator_running() {
  [ "$(docker inspect -f '{{.State.Running}}' "$EMU_CONTAINER" 2>/dev/null || echo false)" = "true" ]
}

_emulator_logs_tail() {
  "${COMPOSE[@]}" logs --tail 40 emulator 2>&1 || true
}

_stale_avd_lock_in_logs() {
  _emulator_logs_tail | grep -qE 'multiple emulators with the same AVD|read-only flag to enable'
}

_reset_emulator_volume() {
  echo "==> Resetting emulator data volume (stale AVD lock)"
  "${COMPOSE[@]}" down -v
}

_log_emulator_failure() {
  local logs
  logs="$(_emulator_logs_tail)"
  if echo "$logs" | grep -qE 'multiple emulators with the same AVD|read-only flag to enable'; then
    echo "" >&2
    echo "The persisted AVD volume still has a lock from a previous emulator run." >&2
    echo "  docker compose -f docker-compose.android.yml down -v" >&2
    echo "  ANDROID_EMU_REQUIRE_KVM=1 make android-test-banner" >&2
  fi
  if echo "$logs" | grep -q 'Not enough space to create userdata partition'; then
    echo "" >&2
    echo "The emulator needs several GB free on the Docker data disk (API 33 userdata is large)." >&2
    echo "  df -h /var/lib/docker    # or your Docker data root" >&2
    echo "  docker system prune -af   # reclaim unused images/layers" >&2
    echo "  docker compose -f docker-compose.android.yml down -v" >&2
    echo "  ANDROID_EMU_PARTITION_MB=3072 make android-test-banner   # smaller AVD if still tight" >&2
  fi
  echo "$logs" >&2
}

_emu_status="$(docker inspect -f '{{.State.Status}}' "$EMU_CONTAINER" 2>/dev/null || echo missing)"

if ! _emulator_running; then
  if [ "$_emu_status" = "exited" ] && _stale_avd_lock_in_logs; then
    _reset_emulator_volume
  fi
  echo "==> Starting emulator container"
  "${COMPOSE[@]}" up -d emulator
elif [ "$_emu_status" = "exited" ]; then
  if _stale_avd_lock_in_logs; then
    _reset_emulator_volume
    echo "==> Starting emulator container (fresh volume)"
    "${COMPOSE[@]}" up -d emulator
  else
    echo "==> Emulator container had exited; recreating"
    "${COMPOSE[@]}" up -d --force-recreate emulator
  fi
fi

_wait_compose_health() {
  local elapsed=0 interval=10
  while [ "$elapsed" -lt "$_boot_timeout" ]; do
    if [ "$(docker inspect -f '{{.State.Running}}' "$EMU_CONTAINER" 2>/dev/null || echo false)" != "true" ]; then
      echo "ERROR: emulator container is not running" >&2
      _log_emulator_failure
      return 1
    fi
    local hs
    hs="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}starting{{end}}' "$EMU_CONTAINER" 2>/dev/null || echo missing)"
    case "$hs" in
      healthy)
        echo "==> Emulator healthcheck passed (${elapsed}s)"
        return 0
        ;;
      unhealthy)
        echo "ERROR: emulator healthcheck reported unhealthy" >&2
        return 1
        ;;
    esac
    if [ "$elapsed" -ge 30 ] && [ $((elapsed % 30)) -eq 0 ]; then
      echo "    … waiting for emulator health (${elapsed}s / ${_boot_timeout}s, status: ${hs})"
    fi
    sleep "$interval"
    elapsed=$((elapsed + interval))
  done
  echo "ERROR: timed out waiting for emulator healthcheck (${_boot_timeout}s)" >&2
  return 1
}

echo "==> Waiting for emulator container healthcheck (timeout ${_boot_timeout}s)"
if ! _wait_compose_health; then
  if [ "${ANDROID_EMU_RESET_RETRY:-1}" = "1" ] && _stale_avd_lock_in_logs; then
    ANDROID_EMU_RESET_RETRY=0
    _reset_emulator_volume
    echo "==> Retrying emulator start after volume reset"
    "${COMPOSE[@]}" up -d emulator
    _wait_compose_health || { _log_emulator_failure; exit 1; }
  else
    _log_emulator_failure
    exit 1
  fi
fi

echo "==> Verifying adb from smoke container"
if ! "${COMPOSE[@]}" run --rm --no-deps \
  -e ANDROID_BOOT_TIMEOUT="${ANDROID_EMU_ADB_TIMEOUT:-300}" \
  smoke ./scripts/ci/wait_for_android_emulator.sh; then
  echo "ERROR: Emulator healthcheck passed but adb smoke check failed." >&2
  "${COMPOSE[@]}" logs --tail 80 emulator >&2 || true
  exit 1
fi
