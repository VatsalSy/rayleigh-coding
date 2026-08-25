#!/usr/bin/env bash
# Refuse noisy export/canary history on release branches.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# On orphan/clean history this is a soft advisory when few commits exist.
count="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
echo "commit_count=$count"

bad="$(git log --pretty=%s | rg -n -i 'batch [0-9]+|canary|probe-|stub commit|restore [0-9]+|jquery|golang [0-9]+' || true)"
if [[ -n "$bad" ]]; then
  echo "History hygiene failed — export/canary subjects still present:" >&2
  echo "$bad" >&2
  exit 1
fi

echo "history hygiene passed."
