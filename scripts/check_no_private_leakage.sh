#!/usr/bin/env bash
# Full-tree content hygiene gate for this marketplace repository.
#
# Scans the worktree (including scripts/ and .github/). Pattern sources live in
# scripts/privacy-patterns.pcre and are excluded from the content scan so the
# gate does not self-match. Optional extra patterns: PRIVACY_EXTRA_PATTERN.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
PATTERNS_FILE="scripts/privacy-patterns.pcre"

RG_GLOBS=(
  --glob '!.git/**'
  --glob '!**/node_modules/**'
  --glob '!**/.venv/**'
  --glob '!**/__pycache__/**'
  --glob '!scripts/privacy-patterns.pcre'
  --glob '!scripts/check_no_private_leakage.sh'
)

DENIED_PATH_FRAGMENTS=(
  'jarvis-skills'
  'second-brain'
  'Projects-cowork'
  'comphy-state'
  'openclaw'
  'medical-record'
  'durham-expenses'
  'scrub_private_leakage'
)

if [[ ! -f "$PATTERNS_FILE" ]]; then
  echo "Missing $PATTERNS_FILE" >&2
  exit 2
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required for the privacy gate" >&2
  exit 2
fi

mapfile -t PATTERN_LINES < <(grep -vE '^\s*(#|$)' "$PATTERNS_FILE")
if [[ ${#PATTERN_LINES[@]} -eq 0 ]]; then
  echo "No privacy patterns loaded" >&2
  exit 2
fi

PATTERN="$(printf '%s\n' "${PATTERN_LINES[@]}" | paste -sd'|' -)"
if [[ -n "${PRIVACY_EXTRA_PATTERN:-}" ]]; then
  PATTERN="${PATTERN}|${PRIVACY_EXTRA_PATTERN}"
fi

echo "== path-fragment gate (full tree) =="
while IFS= read -r -d '' path; do
  rel="${path#./}"
  case "$rel" in
    .git/*) continue ;;
  esac
  for frag in "${DENIED_PATH_FRAGMENTS[@]}"; do
    if [[ "$rel" == *"$frag"* ]]; then
      echo "Denied path fragment '$frag' in: $rel" >&2
      fail=1
    fi
  done
done < <(find . -type f -print0 2>/dev/null)

echo "== content pattern gate (full tree) =="
hits="$(rg -n --pcre2 "${RG_GLOBS[@]}" -e "$PATTERN" . 2>/dev/null || true)"
if [[ -n "${hits}" ]]; then
  echo "Disallowed content patterns found:" >&2
  echo "${hits}" >&2
  fail=1
fi

echo "== forbidden tooling filenames =="
if [[ -f scripts/scrub_private_leakage.py ]]; then
  echo "scripts/scrub_private_leakage.py must not be present" >&2
  fail=1
fi

echo "== promotion-marker gate =="
promo="$(rg -n -i --glob '!.git/**' --glob '!scripts/check_no_private_leakage.sh' --glob '!scripts/privacy-patterns.pcre' \
  'promoted from.*(private skill|private catalogue)|copied from private' . 2>/dev/null || true)"
if [[ -n "${promo}" ]]; then
  echo "Promotion markers found:" >&2
  echo "${promo}" >&2
  fail=1
fi

echo "== recent commit-message scan =="
msg_hits="$(git log -n 80 --pretty=%B | rg -n --pcre2 "$PATTERN" || true)"
if [[ -n "${msg_hits}" ]]; then
  echo "Disallowed patterns in recent commit messages:" >&2
  echo "${msg_hits}" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "Privacy check FAILED." >&2
  exit 1
fi

echo "Privacy check passed."
