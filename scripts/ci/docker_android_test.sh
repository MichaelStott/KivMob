#!/usr/bin/env bash
# Build APK(s) then run logcat smoke on a Docker emulator (banner / interstitial / rewarded).
set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "ERROR: $0 requires bash (arrays and pipefail)." >&2
  exec /usr/bin/env bash "$0" "$@"
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <banner|interstitial|rewarded> ..." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export COMPOSE_FILE="${COMPOSE_FILE:-$ROOT/docker-compose.android.yml}"
SKIP_AUTH="${SKIP_AUTH:-true}"
CLEAN="${CLEAN:-0}"

for app in "$@"; do
  case "$app" in
    banner | interstitial | rewarded) ;;
    *)
      echo "Unknown ad app: $app (expected banner, interstitial, or rewarded)" >&2
      exit 1
      ;;
  esac
done

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running or not accessible." >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$(dirname "$0")/check_android_emulator_host.sh"

COMPOSE=(./scripts/ci/docker_compose.sh -f "$COMPOSE_FILE")

# Play Store emulator images always need matching adb keys on emulator + smoke (SKIP_AUTH is not enough).
./scripts/ci/ensure_docker_adb_keys.sh
if [ -f "$ROOT/.docker-android/keys/.generated" ]; then
  echo "==> New adb keys: resetting emulator volume so the AVD trusts them"
  "${COMPOSE[@]}" down -v 2>/dev/null || true
  rm -f "$ROOT/.docker-android/keys/.generated"
fi

chmod +x scripts/ci/*.sh
export SKIP_AUTH

./scripts/ci/free_github_runner_disk.sh

# Compose pulls show plain interleaved "layerid Downloading X MB" lines. Use docker pull
# first so interactive terminals get the usual per-layer progress bars (DOCKER_PROGRESS=tty).
_pull_image_if_missing() {
  local img="$1"
  if docker image inspect "$img" >/dev/null 2>&1; then
    echo "==> Image already present: $img"
    return 0
  fi
  echo "==> Pulling $img (first run only; may take several minutes)..."
  if [ -t 1 ] && [ -z "${GITHUB_ACTIONS:-}" ]; then
    export DOCKER_PROGRESS="${DOCKER_PROGRESS:-tty}"
  fi
  docker pull "$img"
}

GRADLE_IMAGE="${ANDROID_GRADLE_IMAGE:-cimg/android:2025.12.1}"
EMU_IMAGE="${ANDROID_EMU_IMAGE:-halimqarroum/docker-android:api-33-playstore}"
BOZER_IMAGE="${DOCKER_IMAGE:-kivy/buildozer:latest}"

echo "==> Ensuring Docker images for android CI (build phase)"
_pull_image_if_missing "$GRADLE_IMAGE"
_pull_image_if_missing "$BOZER_IMAGE"

echo "==> Publishing kivmob-android-bridge to Maven local"
./scripts/ci/docker_gradle_bridge.sh :kivmob-android-bridge:publishToMavenLocal

for app in "$@"; do
  echo "==> Building APK: $app (emulator not started yet - avoids idle/OOM during build)"
  CI_ANDROID_CLEAN="$CLEAN" ./scripts/ci/build_android_apk.sh "$app"
done

echo "==> Ensuring emulator image for smoke tests"
_pull_image_if_missing "$EMU_IMAGE"

_root_free_mb="$(df -BM "$ROOT" 2>/dev/null | awk 'NR==2 {gsub(/M$/,"",$4); print $4}' || echo 0)"
if [ "${_root_free_mb:-0}" -lt 8000 ] 2>/dev/null; then
  echo "WARNING: low free disk on $(df -h "$ROOT" | awk 'NR==2 {print $1" ("$4" free)"}') - API 33 AVD needs ~7.4GB in the emulator volume." >&2
  echo "         Try: docker system prune -af && docker compose -f docker-compose.android.yml down -v" >&2
fi

echo "==> Starting emulator for smoke tests (apps: $*)"
if ! ./scripts/ci/ensure_docker_emulator.sh; then
  echo "" >&2
  echo "If logs show 'Killed', the emulator was OOM-killed. Try:" >&2
  echo "  docker compose -f docker-compose.android.yml down -v" >&2
  echo "  ANDROID_EMU_MEMORY=2048 ANDROID_EMU_SHM=1gb make android-test-banner" >&2
  exit 1
fi

echo "==> Running smoke tests"
"${COMPOSE[@]}" run --rm smoke \
  ./scripts/ci/docker_android_smoke.sh "$@"
