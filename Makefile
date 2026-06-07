# KivMob: Python package, Android demo (Buildozer/Docker), ad smoke tests (Docker emulator).

DEMO_DIR            := demo
ANDROID_PACKAGE     := org.kivmob.kivmob
PYTHON_ACTIVITY     := org.kivy.android.PythonActivity
ANDROID_ADS         := banner interstitial rewarded
MAVEN_REPO_USERNAME := MichaelStott

DOCKER_IMAGE ?= kivy/buildozer:latest
ANDROID_EMULATOR_SERIAL ?= localhost:5555
DEMO_ADB_HOME           := $(CURDIR)/.docker-android/adb-home
ADB_HOME ?= $(HOME)
ADB          := env HOME="$(ADB_HOME)" adb $(if $(ANDROID_SERIAL),-s $(ANDROID_SERIAL),)
PYTHON       ?= python3

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
	-e GIT_CONFIG_COUNT=1 \
	-e GIT_CONFIG_KEY_0=safe.directory \
	-e GIT_CONFIG_VALUE_0='*' \
	-e GITHUB_TOKEN \
	-e MAVEN_REPO_USERNAME \
	-e MAVEN_REPO_PASSWORD \
	$(DOCKER_IMAGE)

GRADLE_BRIDGE := ./scripts/ci/docker_gradle_bridge.sh
ANDROID_TEST  := ./scripts/ci/docker_android_test.sh

.PHONY: help test test-cov version fmt \
	build sync-demo-module sync-demo-spec \
	android-test android-test-banner android-test-interstitial android-test-rewarded \
	maven-publish-bridge-local maven-publish-bridge \
	pypi-build pypi-publish \
	check-adb ensure-android-emulator demo-view install uninstall run deploy clean

## help — Print targets.
help:
	@echo "KivMob"
	@grep -h '^##' "$(firstword $(MAKEFILE_LIST))" | sed 's/^##[[:space:]]*//' | sed 's/^/  /'

## version — Print release versions from changelog/.
version:
	@echo "kivmob: $$( $(PYTHON) scripts/version.py kivmob )"
	@echo "kivmob-android-bridge: $$( $(PYTHON) scripts/version.py kivmob-android-bridge )"

## test — Run unit tests (pytest).
test:
	cd "$(CURDIR)" && $(PYTHON) -m pytest tests/

## test-cov — Unit tests with coverage for kivmob.py and demo/main.py.
test-cov:
	cd "$(CURDIR)" && $(PYTHON) -m coverage run --branch --source=. --omit='tests/*,setup.py,docs/*' -m pytest tests/ -q
	cd "$(CURDIR)" && $(PYTHON) -m coverage report -m --include='kivmob.py,demo/main.py'

## build — Demo debug APK via Docker (buildozer).
build: sync-demo-spec maven-publish-bridge-local
	$(DOCKER_RUN) android debug

## android-test — Docker emulator: build and smoke-test all ad types (same as GHA android-ad-* workflows).
android-test:
	$(ANDROID_TEST) banner interstitial rewarded

## android-test-banner — Docker emulator: build and smoke-test banner ads.
android-test-banner:
	$(ANDROID_TEST) banner

## android-test-interstitial — Docker emulator: build and smoke-test interstitial ads.
android-test-interstitial:
	$(ANDROID_TEST) interstitial

## android-test-rewarded — Docker emulator: build and smoke-test rewarded video ads.
android-test-rewarded:
	$(ANDROID_TEST) rewarded

sync-demo-module:
	cp "$(CURDIR)/kivmob.py" "$(CURDIR)/$(DEMO_DIR)/kivmob.py"

## sync-demo-spec — Sync demo/buildozer.spec bridge version from changelog/.
sync-demo-spec: sync-demo-module
	@BRIDGE_VERSION="$$($(PYTHON) scripts/version.py kivmob-android-bridge)"; \
	sed -i 's|org.kivmob:kivmob-android-bridge:[^,]*|org.kivmob:kivmob-android-bridge:'"$$BRIDGE_VERSION"'|' \
		"$(CURDIR)/$(DEMO_DIR)/buildozer.spec"

## maven-publish-bridge-local — Publish bridge to ~/.m2 (Gradle in Docker).
maven-publish-bridge-local:
	$(GRADLE_BRIDGE) :kivmob-android-bridge:publishToMavenLocal

## maven-publish-bridge — Publish bridge to MAVEN_REPO_URL (Gradle in Docker).
maven-publish-bridge:
	@test -n "$$MAVEN_REPO_URL" || (echo "Set MAVEN_REPO_URL."; exit 1)
	$(GRADLE_BRIDGE) :kivmob-android-bridge:publishReleasePublicationToRemoteRepository

## pypi-build — Build wheel + sdist and validate with twine.
pypi-build:
	rm -rf dist build *.egg-info
	cd "$(CURDIR)" && $(PYTHON) -m build
	cd "$(CURDIR)" && $(PYTHON) -m twine check dist/*

## pypi-publish — Run tests, pypi-build, upload (PYPI_REPOSITORY=testpypi for TestPyPI).
pypi-publish: test pypi-build
	cd "$(CURDIR)" && $(PYTHON) -m twine upload \
		$(if $(filter testpypi,$(PYPI_REPOSITORY)),--repository testpypi,) dist/*

## fmt — Format Python with black.
fmt:
	cd "$(CURDIR)" && $(PYTHON) -m black .

check-adb:
	@command -v adb >/dev/null 2>&1 || { echo "adb not in PATH."; exit 1; }

## ensure-android-emulator — Start Docker emulator and connect host adb (localhost:5555).
ensure-android-emulator: check-adb
	ANDROID_SERIAL="$(ANDROID_EMULATOR_SERIAL)" ./scripts/ci/ensure_host_emulator_adb.sh

## install — Install demo debug APK (set ANDROID_SERIAL to skip auto emulator on deploy).
install: check-adb sync-demo-module
	@apk=$$(ls -t $(DEMO_DIR)/bin/*debug*.apk 2>/dev/null | head -n1); \
	test -n "$$apk" || (echo "No APK in $(DEMO_DIR)/bin. Run: make build"; exit 1); \
	$(ADB) install -r "$$apk"

## uninstall — Remove demo app from device.
uninstall: check-adb
	$(ADB) uninstall $(ANDROID_PACKAGE)

## run — Start installed demo app.
run: check-adb
	$(ADB) shell am start -n $(ANDROID_PACKAGE)/$(PYTHON_ACTIVITY)

## demo-view — Mirror Docker emulator on desktop (requires scrcpy; sudo apt install scrcpy).
demo-view: check-adb
	@ADB_HOME="$(DEMO_ADB_HOME)" ANDROID_SERIAL="$(ANDROID_EMULATOR_SERIAL)" \
		./scripts/ci/open_emulator_display.sh

## deploy — Start Docker emulator, install APK, launch app, open scrcpy window.
deploy:
	@if [ -n "$$ANDROID_SERIAL" ]; then \
		$(MAKE) install run; \
	else \
		$(MAKE) ensure-android-emulator && \
		$(MAKE) install run \
			ANDROID_SERIAL="$(ANDROID_EMULATOR_SERIAL)" \
			ADB_HOME="$(DEMO_ADB_HOME)" && \
		( ADB_HOME="$(DEMO_ADB_HOME)" ANDROID_SERIAL="$(ANDROID_EMULATOR_SERIAL)" \
			SCRCPY_BACKGROUND=1 ./scripts/ci/open_emulator_display.sh || true ); \
	fi

## clean — Remove demo/build artifacts and ~/.buildozer.
clean:
	rm -rf $(DEMO_DIR)/.buildozer $(DEMO_DIR)/bin dist build *.egg-info "$(HOME)/.buildozer"
