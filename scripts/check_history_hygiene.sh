#!/usr/bin/env bash
# Refuse noisy export/canary subjects on commits introduced since base.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASE="${HISTORY_HYGIENE_BASE:-origin/main}"
if git rev-parse --verify "$BASE" >/dev/null 2>&1; then
  range="${BASE}..HEAD"
  count="$(git rev-list --count "$range" 2>/dev/null || echo 0)"
  echo "commit_count_since_base=$count base=$BASE"
  subjects="$(git log --pretty=%s "$range")"
else
  count="$(git rev-list --count HEAD)"
  echo "commit_count=$count"
  subjects="$(git log --pretty=%s)"
fi

bad="$(printf '%s\n' "$subjects" | rg -n -i 'batch [0-9]+|canary|probe-|stub commit|restore [0-9]+|jquery|golang [0-9]+' || true)"
if [[ -n "$bad" ]]; then
  echo "History hygiene failed — export/canary subjects still present:" >&2
  echo "$bad" >&2
  exit 1
fi

echo "history hygiene passed."
