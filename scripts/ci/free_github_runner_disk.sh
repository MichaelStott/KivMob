#!/usr/bin/env bash
# Reclaim disk on GitHub-hosted runners before Android Docker builds (NDK/SDK extract needs ~3GB+).
set -euo pipefail

if [ -z "${GITHUB_ACTIONS:-}" ]; then
  exit 0
fi

echo "==> Disk before cleanup:"
df -h /

# Pre-installed toolchains on ubuntu-latest; our build uses Docker + buildozer caches instead.
sudo rm -rf /usr/local/lib/android /usr/local/share/android-sdk || true
sudo rm -rf /usr/share/dotnet /usr/share/swift || true
sudo rm -rf /opt/ghc /opt/hostedtoolcache/CodeQL || true
sudo rm -rf /usr/local/.ghcup || true

# Swap competes with large zip extracts on the same volume.
sudo swapoff -a 2>/dev/null || true
sudo rm -f /swapfile /mnt/swapfile 2>/dev/null || true

sudo apt-get clean 2>/dev/null || true

# Runner may retain images/volumes from prior jobs on the same host.
docker system prune -af --volumes 2>/dev/null || true

echo "==> Disk after cleanup:"
df -h /

_avail_mb="$(df -BM / 2>/dev/null | awk 'NR==2 {gsub(/M$/,"",$4); print $4}' || echo 0)"
if [ "${_avail_mb:-0}" -lt 12000 ] 2>/dev/null; then
  echo "WARNING: less than 12GB free on / after cleanup (${_avail_mb}MB) — NDK extract may still fail." >&2
fi
