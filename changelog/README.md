# Changelogs

Each publishable artifact has its own changelog and SemVer.

| File | Artifact | Registry |
|------|----------|----------|
| [kivmob.md](kivmob.md) | Python `kivmob` | PyPI |
| [kivmob-bridge.md](kivmob-bridge.md) | `org.kivmob:kivmob-bridge` | GitHub Packages Maven |

The first numbered section below `## [Unreleased]` in a file is that artifact’s published version.

## Releasing

1. Edit the changelog for the artifact you are releasing (move **Unreleased** into `## [X.Y.Z] - YYYY-MM-DD`, add a new **Unreleased**).
2. Create a GitHub release with a matching tag:
   - Python: `kivmob-vX.Y.Z` (example: `kivmob-v2.1.0`)
   - Bridge: `kivmob-bridge-vX.Y.Z` (example: `kivmob-bridge-v1.0.0`)
3. CI validates the tag against the changelog and publishes only that artifact.

You can also run the **Release** workflow manually and choose the package and version.

## Compatibility

When a release needs a minimum bridge version, document it in [kivmob.md](kivmob.md) under that release (for example: “Requires kivmob-bridge ≥ 1.0.0”). Android CI pins the bridge version from [kivmob-bridge.md](kivmob-bridge.md) when generating `buildozer.spec`.
