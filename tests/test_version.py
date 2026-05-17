"""Tests for per-package changelog versioning."""

import re
from pathlib import Path

import pytest

from version import PACKAGES, get_version

_VERSION_HEADING = re.compile(r"^## \[([^\]]+)\]")
_ROOT = Path(__file__).resolve().parents[1]
_CHANGELOG_DIR = _ROOT / "changelog"


def _expected_version(package: str) -> str:
    changelog = (_CHANGELOG_DIR / f"{package}.md").read_text(encoding="utf-8")
    for line in changelog.splitlines():
        match = _VERSION_HEADING.match(line.strip())
        if match and match.group(1).strip().lower() != "unreleased":
            return match.group(1).strip()
    raise AssertionError(f"No release in changelog/{package}.md")


@pytest.mark.parametrize("package", PACKAGES)
def test_get_version_matches_changelog(package):
    assert get_version(package) == _expected_version(package)


@pytest.mark.parametrize("package", PACKAGES)
def test_version_is_semver_triplet(package):
    version = get_version(package)
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), version


def test_kivmob_and_bridge_versions_are_independent():
    assert get_version("kivmob") != get_version("kivmob-bridge")
