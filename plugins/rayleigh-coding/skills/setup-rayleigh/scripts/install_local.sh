#!/usr/bin/env bash
# Install rayleigh-coding as a user-global local Cursor plugin.
# The loaded path must itself contain .cursor-plugin/plugin.json.
set -euo pipefail

PLUGIN_LOCAL="${HOME}/.cursor/plugins/local"
SRC="${RAYLEIGH_CODING_SRC:-${PLUGIN_LOCAL}/rayleigh-coding-src}"
REPO_URL="${RAYLEIGH_CODING_REPO:-https://github.com/VatsalSy/rayleigh-coding.git}"

mkdir -p "${PLUGIN_LOCAL}"

if [[ -d "${SRC}/.git" ]]; then
  git -C "${SRC}" pull --ff-only
elif [[ -d "${SRC}" ]]; then
  echo "error: ${SRC} exists but is not a git clone; set RAYLEIGH_CODING_SRC" >&2
  exit 1
else
  git clone "${REPO_URL}" "${SRC}"
fi

PLUGIN_SRC="${SRC}/plugins/rayleigh-coding"
if [[ ! -f "${PLUGIN_SRC}/.cursor-plugin/plugin.json" ]]; then
  echo "error: missing ${PLUGIN_SRC}/.cursor-plugin/plugin.json" >&2
  exit 1
fi

ln -sfn "${PLUGIN_SRC}" "${PLUGIN_LOCAL}/rayleigh-coding"

echo "installed: ${PLUGIN_LOCAL}/rayleigh-coding -> ${PLUGIN_SRC}"
test -f "${PLUGIN_LOCAL}/rayleigh-coding/.cursor-plugin/plugin.json"
