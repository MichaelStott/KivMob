#!/usr/bin/env bash
# Build a debug APK for tests/android_ci/<app> via Docker buildozer (emulator profile).
set -euo pipefail

APP="${1:?Usage: $0 <banner|interstitial|rewarded> [--clean]}"
CLEAN="${CI_ANDROID_CLEAN:-0}"
if [ "${2:-}" = "--clean" ] || [ "${2:-}" = "clean" ]; then
  CLEAN=1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$ROOT/tests/android_ci/$APP"
DOCKER_IMAGE="${DOCKER_IMAGE:-kivy/buildozer:latest}"
BOZER_VOLUME="kivmob-ci-${APP}-buildozer"

"$ROOT/scripts/ci/generate_buildozer_spec.sh" "$APP"
cp "$ROOT/kivmob.py" "$APP_DIR/kivmob.py"
"$ROOT/scripts/ci/sync_bridge_for_p4a.sh"
P4A_DIR="$("$ROOT/scripts/ci/ensure_p4a_checkout.sh")"

if [ "$CLEAN" = "1" ]; then
  echo "Removing Docker volume $BOZER_VOLUME and local build dirs"
  docker volume rm "$BOZER_VOLUME" 2>/dev/null || true
  sudo rm -rf "$APP_DIR/.buildozer" "$APP_DIR/bin" 2>/dev/null || rm -rf "$APP_DIR/.buildozer" "$APP_DIR/bin" 2>/dev/null || true
fi

if [ -d "$APP_DIR/.buildozer/android/platform/build-x86_64/build/other_builds/kivmob" ]; then
  echo "Removing stale kivmob recipe tree from old CI spec"
  docker volume rm "$BOZER_VOLUME" 2>/dev/null || true
  sudo rm -rf "$APP_DIR/.buildozer" 2>/dev/null || rm -rf "$APP_DIR/.buildozer" 2>/dev/null || true
fi

docker volume create "$BOZER_VOLUME" >/dev/null

# .buildozer on a named volume avoids parallel-make races on bind mounts (openssl .d.tmp).
DOCKER_VOLUMES=(
  -v "$ROOT:/home/user/project"
  -v "$P4A_DIR:/home/user/p4a:ro"
  -v "${BOZER_VOLUME}:/home/user/project/tests/android_ci/$APP/.buildozer"
  -v "${HOME}/.buildozer:/home/user/.buildozer"
  -v "${HOME}/.m2:/root/.m2"
)
WORK_DIR="/home/user/project/tests/android_ci/$APP"

mkdir -p "$APP_DIR/bin"
DIST="$(grep '^package\.name' "$APP_DIR/buildozer.spec" | sed 's/.*= *//')"
APK_GLOB="/vol/android/platform/build-x86_64/dists/${DIST}/build/outputs/apk/debug/*debug*.apk"

set +e
docker run --rm \
  --entrypoint buildozer \
  "${DOCKER_VOLUMES[@]}" \
  -w "$WORK_DIR" \
  -e HOME=/home/user \
  -e TAR_OPTIONS=--no-same-owner \
  -e CCACHE_DISABLE=1 \
  -e NDK_CCACHE=0 \
  -e MAKEFLAGS=-j2 \
  "$DOCKER_IMAGE" \
  --profile emulator android debug
_bozer_status=$?
set -e

# Buildozer often builds the APK in the .buildozer volume but fails copying to bin/ on bind mounts.
docker run --rm \
  -v "${BOZER_VOLUME}:/vol" \
  -v "$APP_DIR/bin:/out" \
  --entrypoint sh \
  "$DOCKER_IMAGE" \
  -c "cp -f ${APK_GLOB} /out/ 2>/dev/null || true; chown -R $(id -u):$(id -g) /out 2>/dev/null || true"

apk="$(ls -t "$APP_DIR"/bin/*debug*.apk 2>/dev/null | head -n1)"
if [ -z "$apk" ] && [ "$_bozer_status" -ne 0 ]; then
  echo "buildozer exited $_bozer_status and no APK was found in bin/ or the Docker volume" >&2
  exit "$_bozer_status"
fi
if [ -z "$apk" ]; then
  echo "No debug APK produced under $APP_DIR/bin" >&2
  exit 1
fi
if [ "$_bozer_status" -ne 0 ]; then
  echo "Note: buildozer exited $_bozer_status after APK copy; recovered APK from Docker volume."
fi
echo "Built $apk"
