#!/usr/bin/env bash
# Invoke Docker Compose v2 (docker compose plugin). Legacy docker-compose v1 is a last resort.
set -euo pipefail

_compose_v2_plugin_paths=(
  /usr/libexec/docker/cli-plugins/docker-compose
  /usr/lib/docker/cli-plugins/docker-compose
  /usr/local/lib/docker/cli-plugins/docker-compose
)

_broken_compose_plugin_symlink() {
  local link="${HOME}/.docker/cli-plugins/docker-compose"
  [ -L "$link" ] && [ ! -e "$link" ]
}

if docker compose version >/dev/null 2>&1; then
  exec docker compose "$@"
fi

for plugin in "${_compose_v2_plugin_paths[@]}"; do
  if [ -x "$plugin" ] && "$plugin" version >/dev/null 2>&1; then
    exec "$plugin" "$@"
  fi
done

if command -v docker-compose >/dev/null 2>&1 && docker-compose version >/dev/null 2>&1; then
  exec docker-compose "$@"
fi

cat >&2 <<'EOF'
ERROR: Docker Compose v2 is required (docker compose).

Install the Compose plugin, then verify:

  sudo apt install docker-compose-plugin
  docker compose version

Then retry, e.g.: make deploy
EOF

if _broken_compose_plugin_symlink; then
  cat >&2 <<EOF

Broken plugin symlink: ${HOME}/.docker/cli-plugins/docker-compose
After installing the plugin, remove the stale link if "docker compose" still fails:

  rm ${HOME}/.docker/cli-plugins/docker-compose
EOF
fi

exit 1
