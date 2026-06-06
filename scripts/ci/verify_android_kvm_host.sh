#!/usr/bin/env bash
# Fail fast if the host cannot run the docker-android emulator with KVM (CI gate).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Verifying /dev/kvm"
if [ ! -e /dev/kvm ]; then
  echo "ERROR: /dev/kvm is missing on this runner." >&2
  exit 1
fi
ls -l /dev/kvm

echo "==> Verifying Docker can pass /dev/kvm into a container"
docker run --rm --device /dev/kvm:rw --entrypoint test docker:27.1.1-cli -e /dev/kvm

# shellcheck source=/dev/null
source "$(dirname "$0")/check_android_emulator_host.sh"

if docker info 2>/dev/null | grep -qi 'Docker Desktop'; then
  echo "ERROR: Docker Desktop cannot pass /dev/kvm; CI requires native Docker Engine." >&2
  exit 1
fi

echo "==> KVM host verification passed"
