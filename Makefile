# KivMob Android demo: Buildozer in Docker, adb install/run, optional Gradle bridge under android/kivmob-bridge.

DEMO_DIR            := demo
ANDROID_CI_APPS     := banner interstitial rewarded
ANDROID_PACKAGE     := org.kivmob.kivmob
PYTHON_ACTIVITY     := org.kivy.android.PythonActivity
ANDROID_BRIDGE      := $(CURDIR)/android/kivmob-bridge
MAVEN_REPO_USERNAME := MichaelStott

DOCKER_IMAGE    ?= kivy/buildozer:latest
AVD_NAME        ?= Pixel_7_API_34

ADB := adb $(if $(ANDROID_SERIAL),-s $(ANDROID_SERIAL),)

PYTHON ?= python3

DOCKER_VOLUMES := \
	-v "$(CURDIR)/$(DEMO_DIR):/home/user/hostcwd" \
	-v "$(HOME)/.buildozer:/home/user/.buildozer" \
	-v "$(HOME)/.m2:/root/.m2"

DOCKER_RUN := docker run --rm \
	--entrypoint buildozer \
	$(DOCKER_VOLUMES) \
	-w /home/user/hostcwd \
	-e HOME=/home/user \
	-e TAR_OPTIONS=--no-same-owner \
	-e GITHUB_TOKEN \
	-e MAVEN_REPO_USERNAME \
	-e MAVEN_REPO_PASSWORD \
	$(DOCKER_IMAGE)

define _resolve_emulator
EMU_BIN="$$(command -v emulator 2>/dev/null || true)"; \
if [ -z "$$EMU_BIN" ] && [ -n "$$ANDROID_SDK_ROOT" ] && [ -x "$$ANDROID_SDK_ROOT/emulator/emulator" ]; then \
	EMU_BIN="$$ANDROID_SDK_ROOT/emulator/emulator"; \
fi; \
if [ -z "$$EMU_BIN" ] && [ -n "$$ANDROID_HOME" ] && [ -x "$$ANDROID_HOME/emulator/emulator" ]; then \
	EMU_BIN="$$ANDROID_HOME/emulator/emulator"; \
fi
endef

define _need_android_sdk
@test -n "$$ANDROID_HOME" || test -n "$$ANDROID_SDK_ROOT" || \
	(echo "Set ANDROID_HOME or ANDROID_SDK_ROOT for Gradle."; exit 1)
endef

GRADLE_BRIDGE := cd "$(ANDROID_BRIDGE)" && ./gradlew :kivmob-bridge:

.PHONY: help test test-cov build android-debug android-debug-docker android-debug-local android-debug-emulator \
	ci-android-build ci-android-smoke sync-demo-module sync-bridge-java android-bridge-assemble \
	maven-publish-bridge-local maven-publish-bridge \
	pypi-build pypi-check pypi-publish pypi-publish-test version fmt \
	check-adb check-emulator emulator-start emulator-wait install uninstall run deploy \
	logcat devices fix-perms clean clean-distclean

## help — Print targets (lines starting with ## in this Makefile).
help:
	@echo "KivMob Android"
	@grep -h '^##' "$(firstword $(MAKEFILE_LIST))" | sed 's/^##[[:space:]]*//' | sed 's/^/  /'

## version — Print release versions from changelog/ (kivmob + kivmob-bridge).
version:
	@echo "kivmob: $$( $(PYTHON) scripts/version.py kivmob )"
	@echo "kivmob-bridge: $$( $(PYTHON) scripts/version.py kivmob-bridge )"

## test — Run unit tests (pytest classic output; use test-cov for code coverage).
test:
	cd "$(CURDIR)" && $(PYTHON) -m pytest tests/

## ci-android-build / ci-android-smoke — CI ad apps under tests/android_ci/ (APP=banner|interstitial|rewarded).
## test-cov — Same tests with branch coverage report for kivmob.py and demo/main.py (needs: pip install -r requirements-test.txt).
test-cov:
	cd "$(CURDIR)" && $(PYTHON) -m coverage run --branch --source=. --omit='tests/*,setup.py,docs/*' -m pytest tests/ -q
	cd "$(CURDIR)" && $(PYTHON) -m coverage report -m --include='kivmob.py,demo/main.py'

## build, android-debug, android-debug-docker — Debug APK via Docker (buildozer). Override DOCKER_IMAGE=…
build android-debug: android-debug-docker

sync-demo-module:
	cp "$(CURDIR)/kivmob.py" "$(CURDIR)/$(DEMO_DIR)/kivmob.py"

## sync-bridge-java — Copy bridge Java into p4a_recipes (before commit or Docker build).
sync-bridge-java:
	./scripts/ci/sync_bridge_for_p4a.sh

## ci-android-clean — Remove tests/android_ci build tree + Docker volume for APP.
ci-android-clean:
	@test -n "$(APP)" || (echo "Set APP=banner, interstitial, or rewarded."; exit 1)
	@docker volume rm "kivmob-ci-$(APP)-buildozer" 2>/dev/null || true
	@rm -rf "tests/android_ci/$(APP)/.buildozer" "tests/android_ci/$(APP)/bin" 2>/dev/null || true
	@if [ -d "tests/android_ci/$(APP)/.buildozer" ] || [ -d "tests/android_ci/$(APP)/bin" ]; then \
		echo "Removing root-owned Docker artifacts (sudo)…"; \
		sudo rm -rf "tests/android_ci/$(APP)/.buildozer" "tests/android_ci/$(APP)/bin"; \
	fi

## ci-android-build — Build tests/android_ci APK (APP=banner|interstitial|rewarded). Add CLEAN=1 to drop .buildozer first.
ci-android-build:
	@test -n "$(APP)" || (echo "Set APP=banner, interstitial, or rewarded."; exit 1)
	$(_need_android_sdk)
	$(MAKE) sync-bridge-java maven-publish-bridge-local
	CI_ANDROID_CLEAN="$(CLEAN)" ./scripts/ci/build_android_apk.sh "$(APP)"

## ci-android-rebuild — ci-android-clean then ci-android-build (use after CI spec / kivmob changes).
ci-android-rebuild:
	@test -n "$(APP)" || (echo "Set APP=banner, interstitial, or rewarded."; exit 1)
	$(MAKE) ci-android-clean APP="$(APP)"
	$(MAKE) ci-android-build APP="$(APP)" CLEAN=1

## ci-android-smoke — Run emulator smoke test (needs booted emulator + APK). Example: make ci-android-smoke APP=banner
ci-android-smoke: check-adb
	@test -n "$(APP)" || (echo "Set APP=banner, interstitial, or rewarded."; exit 1)
	@apk=$$(ls -t tests/android_ci/$(APP)/bin/*debug*.apk 2>/dev/null | head -n1); \
	test -n "$$apk" || (echo "No APK in tests/android_ci/$(APP)/bin. Run: make ci-android-build APP=$(APP)"; exit 1); \
	./scripts/ci/emulator_ad_test.sh "$(APP)" "$$apk"

## ci-android-smoke-wait — emulator-wait then ci-android-smoke (convenience).
ci-android-smoke-wait: emulator-wait
	$(MAKE) ci-android-smoke APP="$(APP)"

## android-bridge-assemble — Assemble bridge release AAR (Gradle).
android-bridge-assemble: sync-bridge-java
	$(_need_android_sdk)
	$(GRADLE_BRIDGE)assembleRelease

## maven-publish-bridge-local — Publish bridge to ~/.m2.
maven-publish-bridge-local: sync-bridge-java
	$(_need_android_sdk)
	$(GRADLE_BRIDGE)publishToMavenLocal

## maven-publish-bridge — Publish bridge to MAVEN_REPO_URL (optional MAVEN_REPO_USERNAME / PASSWORD).
maven-publish-bridge: sync-bridge-java
	$(_need_android_sdk)
	@test -n "$$MAVEN_REPO_URL" || (echo "Set MAVEN_REPO_URL."; exit 1)
	$(GRADLE_BRIDGE)publishReleasePublicationToRemoteRepository

## pypi-build — Build wheel + sdist from setup.py (needs: pip install build).
pypi-build:
	rm -rf dist build *.egg-info
	cd "$(CURDIR)" && $(PYTHON) -m build

## pypi-check — Validate dist/ with twine (needs: pip install twine).
pypi-check: pypi-build
	cd "$(CURDIR)" && $(PYTHON) -m twine check dist/*

## pypi-publish — Upload dist/* to PyPI (configure ~/.pypirc or TWINE_USERNAME / TWINE_PASSWORD).
pypi-publish: pypi-check
	cd "$(CURDIR)" && $(PYTHON) -m twine upload dist/*

## pypi-publish-test — Upload dist/* to TestPyPI (--repository testpypi; token in ~/.pypirc or env).
pypi-publish-test: pypi-check
	cd "$(CURDIR)" && $(PYTHON) -m twine upload --repository testpypi dist/*

## fmt — Format Python with black (needs: pip install black).
fmt:
	cd "$(CURDIR)" && $(PYTHON) -m black .

## android-debug-emulator — Debug APK with emulator profile (x86_64; often faster).
android-debug-emulator: sync-demo-module
	$(DOCKER_RUN) --profile emulator android debug

## android-debug-docker — Debug APK in Docker (buildozer). Gradle runs as root in the image;
## ~/.m2 is mounted at /root/.m2 so mavenLocal() can see `make maven-publish-bridge-local` output.
android-debug-docker: sync-demo-module
	$(DOCKER_RUN) android debug

## android-debug-local — Debug APK with host buildozer (must be installed).
android-debug-local: sync-demo-module
	cd $(DEMO_DIR) && buildozer android debug

check-adb:
	@command -v adb >/dev/null 2>&1 || { echo "adb not in PATH (e.g. apt install android-sdk-platform-tools)."; exit 1; }

check-emulator:
	@$(_resolve_emulator); \
	if [ -z "$$EMU_BIN" ]; then \
		echo "emulator not found; use PATH, ANDROID_SDK_ROOT, or ANDROID_HOME."; \
		exit 1; \
	fi

## emulator-start — Start emulator (AVD_NAME, default Pixel_7_API_34).
emulator-start: check-emulator
	@$(_resolve_emulator); \
	"$$EMU_BIN" -avd "$(AVD_NAME)" -netdelay none -netspeed full

## emulator-wait — Wait for adb device and boot completion.
emulator-wait: check-adb
	$(ADB) wait-for-device
	@until [ "$$($(ADB) shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do sleep 2; done
	@echo "Boot completed."

## install — Install newest demo/bin/*debug*.apk (ANDROID_SERIAL selects device).
install: check-adb
	@apk=$$(ls -t $(DEMO_DIR)/bin/*debug*.apk 2>/dev/null | head -n1); \
	test -n "$$apk" || (echo "No debug APK in $(DEMO_DIR)/bin. Run: make build"; exit 1); \
	$(ADB) install -r "$$apk"

## uninstall — Remove demo app (use if install fails with INSTALL_FAILED_UPDATE_INCOMPATIBLE).
uninstall: check-adb
	$(ADB) uninstall $(ANDROID_PACKAGE)

## run — Start installed app on device.
run: check-adb
	$(ADB) shell am start -n $(ANDROID_PACKAGE)/$(PYTHON_ACTIVITY)

## deploy — install then run.
deploy: install run

## logcat — Logcat filtered to Python tag.
logcat: check-adb
	$(ADB) logcat '*:S' 'python:D'

## devices — adb devices -l.
devices: check-adb
	$(ADB) devices -l

## fix-perms — chown demo/.buildozer and demo/bin after Docker as root.
fix-perms:
	sudo chown -R "$$(id -u)":"$$(id -g)" "$(DEMO_DIR)/.buildozer" "$(DEMO_DIR)/bin" || true

## clean — Remove demo/.buildozer, demo/bin, and Python packaging artifacts (dist/, build/, *.egg-info).
clean:
	rm -rf $(DEMO_DIR)/.buildozer $(DEMO_DIR)/bin dist build *.egg-info

## clean-distclean — clean plus remove ~/.buildozer.
clean-distclean: clean
	rm -rf "$(HOME)/.buildozer"
