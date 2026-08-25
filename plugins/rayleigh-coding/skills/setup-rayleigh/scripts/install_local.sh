#!/usr/bin/env bash
# Install rayleigh-coding as a user-global local Cursor plugin.
# The loaded path must itself contain .cursor-plugin/plugin.json.
set -euo pipefail

PLUGIN_LOCAL="${HOME}/.cursor/plugins/local"
REPO_URL="${RAYLEIGH_CODING_REPO:-https://github.com/VatsalSy/rayleigh-coding.git}"
SRC_RAW="${RAYLEIGH_CODING_SRC:-${PLUGIN_LOCAL}/rayleigh-coding-src}"

# Physical absolute path so symlink/case forms of the same clone root match
# git rev-parse --show-toplevel.
SRC="$(python3 -c 'import os,sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' "${SRC_RAW}")"

mkdir -p "${PLUGIN_LOCAL}"

if git -C "${SRC}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  TOPLEVEL="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$(git -C "${SRC}" rev-parse --show-toplevel)")"
  if [[ "${TOPLEVEL}" != "${SRC}" ]]; then
    echo "error: ${SRC} is inside git work tree ${TOPLEVEL}; set RAYLEIGH_CODING_SRC to the rayleigh-coding clone root" >&2
    exit 1
  fi
  if ! git -C "${SRC}" pull --ff-only; then
    echo "warning: git pull --ff-only failed in ${SRC}; continuing with existing tree" >&2
  fi
elif [[ -e "${SRC}" ]]; then
  echo "error: ${SRC} exists but is not a git work tree; set RAYLEIGH_CODING_SRC" >&2
  exit 1
else
  git clone "${REPO_URL}" "${SRC}"
fi

PLUGIN_SRC="${SRC}/plugins/rayleigh-coding"
if [[ ! -f "${PLUGIN_SRC}/.cursor-plugin/plugin.json" ]]; then
  echo "error: missing ${PLUGIN_SRC}/.cursor-plugin/plugin.json" >&2
  exit 1
fi

if [[ -f "${SRC}/scripts/validate_marketplace.py" && -f "${SRC}/scripts/validate_skills.py" ]]; then
  python3 "${SRC}/scripts/validate_marketplace.py"
  python3 "${SRC}/scripts/validate_skills.py"
else
  echo "error: missing validators under ${SRC}/scripts" >&2
  exit 1
fi

DEST="${PLUGIN_LOCAL}/rayleigh-coding"
if [[ -e "${DEST}" || -L "${DEST}" ]]; then
  if [[ ! -L "${DEST}" ]]; then
    echo "error: ${DEST} exists and is not a symlink. Remove or rename it, then re-run." >&2
    exit 1
  fi
fi

ln -sfn "${PLUGIN_SRC}" "${DEST}"

test -f "${DEST}/.cursor-plugin/plugin.json"
echo "installed: ${DEST} -> ${PLUGIN_SRC}"
