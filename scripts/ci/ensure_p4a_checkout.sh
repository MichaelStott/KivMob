#!/usr/bin/env bash
# Pinned python-for-android for CI (Python 3.11.5, CythonRecipe pyjnius).
# AGP/Gradle are patched after checkout for play-services-ads 25.x (Kotlin 2.x / R8 8.11).
# Do not use p4a HEAD — it targets Python 3.14 and PyProjectRecipe builds that fail in buildozer.
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

patch_p4a_android_gradle() {
  local gradle_tmpl="$P4A_DIR/pythonforandroid/bootstraps/common/build/templates/build.tmpl.gradle"
  local wrapper_props="$P4A_DIR/pythonforandroid/bootstraps/common/build/gradle/wrapper/gradle-wrapper.properties"
  local manifest_tmpl="$P4A_DIR/pythonforandroid/bootstraps/sdl2/build/templates/AndroidManifest.tmpl.xml"

  sed -i \
    -e 's/com.android.tools.build:gradle:8.1.1/com.android.tools.build:gradle:8.11.0/g' \
    -e 's/jcenter()/mavenCentral()/g' \
    -e 's/packagingOptions {/packaging {/g' \
    "$gradle_tmpl"
  sed -i 's|gradle-8.0.2-all.zip|gradle-8.14.3-all.zip|g' "$wrapper_props"
  # Remove extractNativeLibs (conflicts with jniLibs.useLegacyPackaging in Gradle on AGP 8.11).
  # Replace the attribute line with ">" — do not delete the line; it holds the <application> close.
  sed -i 's/[[:space:]]*android:extractNativeLibs="true"[[:space:]]*>/ >/' "$manifest_tmpl"
}

patch_p4a_android_gradle

echo "$P4A_DIR"
