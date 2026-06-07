#!/usr/bin/env bash
# Verify the host can run the docker-android emulator (KVM + Docker device passthrough).
set -euo pipefail

_docker_total_mem_mib() {
  local bytes
  bytes="$(docker info --format '{{.MemTotal}}' 2>/dev/null || true)"
  [ -n "$bytes" ] && [ "$bytes" -gt 0 ] 2>/dev/null || return 1
  echo $((bytes / 1024 / 1024))
}

_ci_kvm_defaults() {
  : "${ANDROID_EMU_MEMORY:=4096}"
  : "${ANDROID_EMU_SHM:=2gb}"
  : "${ANDROID_EMU_CORES:=2}"
  export ANDROID_EMU_MEMORY ANDROID_EMU_SHM ANDROID_EMU_CORES
}

_tune_android_emu_for_docker() {
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    _ci_kvm_defaults
    return 0
  fi
  local total base cap
  total="$(_docker_total_mem_mib)" || return 0
  base=4096
  if [ -z "${ANDROID_EMU_MEMORY:-}" ]; then
    cap=$((total - 1536))
    [ "$cap" -lt 1536 ] && cap=1536
    [ "$base" -gt "$cap" ] && base=$cap
    ANDROID_EMU_MEMORY=$base
    export ANDROID_EMU_MEMORY
  fi
  if [ -z "${ANDROID_EMU_SHM:-}" ] && [ "$total" -lt 6144 ]; then
    ANDROID_EMU_SHM=1gb
    export ANDROID_EMU_SHM
  fi
  if [ -n "${ANDROID_EMU_MEMORY:-}" ] && [ -n "${ANDROID_EMU_SHM:-}" ]; then
    if [ "$ANDROID_EMU_MEMORY" -lt 3072 ] || [ "${ANDROID_EMU_SHM}" = "1gb" ]; then
      echo "WARNING: Docker reports ${total} MiB RAM; using MEMORY=${ANDROID_EMU_MEMORY} MiB, shm=${ANDROID_EMU_SHM}." >&2
      echo "         Allocate more RAM to Docker if the emulator is OOM-killed." >&2
    fi
  fi
}

_reason=""
if [ ! -e /dev/kvm ]; then
  _reason="/dev/kvm is missing (load kvm module or enable virtualization in BIOS)"
else
  _kvm_probe_err="$(
    docker run --rm --device /dev/kvm:rw --entrypoint test docker:27.1.1-cli -e /dev/kvm 2>&1
  )" || {
    if echo "$_kvm_probe_err" | grep -qiE 'docker-credential-desktop|credsStore'; then
      _reason='Docker pull failed: ~/.docker/config.json still has credsStore "desktop" from Docker Desktop — remove credsStore or set "auths": {} only'
    elif docker info 2>/dev/null | grep -qi 'Docker Desktop'; then
      _reason="Docker Desktop cannot pass /dev/kvm into containers"
    elif echo "$_kvm_probe_err" | grep -qi 'permission denied'; then
      _reason="cannot access /dev/kvm (add user to kvm group: sudo usermod -aG kvm \$USER)"
    else
      _reason="Docker cannot pass /dev/kvm (see: docker run --device /dev/kvm:rw ... test -e /dev/kvm)"
    fi
  }
fi

if [ -n "$_reason" ]; then
  echo "ERROR: KVM is required but unavailable: $_reason" >&2
  echo "" >&2
  echo "Use native Docker Engine with KVM on Linux:" >&2
  echo "  sudo apt install docker.io && sudo usermod -aG docker,kvm \$USER" >&2
  echo "  (log out/in, stop Docker Desktop, docker context use default)" >&2
  echo "  ./scripts/ci/verify_android_kvm_host.sh" >&2
  exit 1
fi

: "${ANDROID_EMU_CORES:=2}"
export ANDROID_EMU_CORES

_tune_android_emu_for_docker

if [ -n "${GITHUB_ACTIONS:-}" ]; then
  echo "==> CI: KVM + Docker passthrough OK (MEMORY=${ANDROID_EMU_MEMORY:-4096} MiB, shm=${ANDROID_EMU_SHM:-2gb}, CORES=${ANDROID_EMU_CORES})" >&2
fi
