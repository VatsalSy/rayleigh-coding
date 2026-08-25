#!/usr/bin/env bash
# Fail if skill scripts that agents invoke directly are non-executable.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
while IFS= read -r -d '' f; do
  case "$f" in
    */__pycache__/*) continue ;;
    *.pyc) continue ;;
    *.py|*.sh|*.js|*.mjs|*.swift|*.ps1)
      if [[ ! -x "$f" ]]; then
        echo "non-executable: $f" >&2
        fail=1
      fi
      ;;
  esac
done < <(find plugins/rayleigh-coding/skills -path '*/scripts/*' -type f -print0)

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "executable-bit check passed."
