#!/usr/bin/env bash
# Run Gradle in the Android bridge module via Docker (no host ANDROID_HOME).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="${ANDROID_GRADLE_IMAGE:-cimg/android:2025.12.1}"
TASKS="${*:-:kivmob-android-bridge:publishToMavenLocal}"

docker run --rm -u 0:0 \
  -v "$ROOT:/workspace" \
  -v "${HOME}/.m2:/root/.m2" \
  -e MAVEN_REPO_URL \
  -e MAVEN_REPO_USERNAME \
  -e MAVEN_REPO_PASSWORD \
  -w /workspace/bridges/android \
  "$IMAGE" \
  bash -ec "chmod +x gradlew && ./gradlew $TASKS --no-daemon"
