# kivmob (PyPI)

Python AdMob bindings for Kivy.

## [Unreleased]

### Added

- Per-package changelog and versioning under `changelog/`.
- `destroy_interstitial()` / `destroy_rewarded_video_ad()` clear loaded ads in the Java bridge.

### Changed

- Interstitial/rewarded callbacks ignore stale in-flight loads after `destroy_*` or a superseding load.
- `set_rewarded_ad_listener()` updates the Java bridge listener and preserves earned-reward state mid-session.
- Test devices use `RequestConfiguration.setTestDeviceIds()` instead of deprecated `AdRequest.Builder.addTestDevice()`.
- Rewarded dismiss invokes `on_rewarded_video_ad_completed()` when the user earned a reward in that session.
- Routine `KivMob` API calls log at debug level instead of info.

### Removed

- `on_rewarded_video_ad_left_application` is not invoked on Android (no equivalent in Play Services Ads 25.x).

## [2.1.0] - 2026-05-17

### Changed

- Normalize the prior PyPI version `2.1` to SemVer `2.1.0`.

### Compatibility

- Android builds using the Gradle bridge should use **kivmob-android-bridge ≥ 1.0.0**.
