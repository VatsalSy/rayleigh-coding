#!/usr/bin/env bash
# Fail if private / personal leakage patterns appear in published marketplace content.
# Hard gate: private skill catalogues (e.g. jarvis-skills) and fleet topology must
# never land in this public repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Denied path fragments (case-sensitive path/name hits).
DENIED_PATH_FRAGMENTS=(
  'jarvis-skills'
  'second-brain'
  'Projects-cowork'
  'comphy-state'
  'openclaw'
  'medical-record'
  'durham-expenses'
)

# Content patterns that must never appear in published trees.
PATTERN='Rayleigh|Worthington|Kelvin/Stokes|/Users/vatsal|/Users/comphy|openclaw|second-brain|comphy-state|\bsgit\b|stokes-ts|Projects-cowork|dual-sync-main|medical-record|durham-expenses|vatsalsanjay\.com|vatsal\.sanjay@|5b283a1192f0a78f|2e852c08b4428ffafda676c354c13c98|264b1512bed863f81da699991dafb514|0dd798a4d4f2ba386457f3cdbe54fba9|8e47b17c0904dc8eb4a934c4038b7fa7|prj_bHRfpwCUfu05|prj_stHuYYHE9RJG|prj_SHsyjr2vTYTe|prj_rT3QjtWigNGR|prj_HmDrwzVsRwfe|prj_Yyc9nVMvlNc5|prj_8NGwHM9hYo3q|Synosync|ireminder|calcli|zoteroctl|jarvis-skills|comphy-bot'

SCAN_PATHS=(plugins .cursor-plugin README.md LICENSE)
# Optional roots (present after layout migrations).
for optional in docs; do
  if [[ -e "$optional" ]]; then
    SCAN_PATHS+=("$optional")
  fi
done

fail=0

echo "== path-fragment gate =="
while IFS= read -r -d '' path; do
  rel="${path#./}"
  for frag in "${DENIED_PATH_FRAGMENTS[@]}"; do
    if [[ "$rel" == *"$frag"* ]]; then
      echo "Denied path fragment '$frag' in: $rel" >&2
      fail=1
    fi
  done
done < <(find plugins .cursor-plugin -type f -print0 2>/dev/null)

echo "== content pattern gate =="
hits=""
if command -v rg >/dev/null 2>&1; then
  hits="$(rg -n --pcre2 "$PATTERN" "${SCAN_PATHS[@]}" 2>/dev/null || true)"
else
  hits="$(grep -RInE "$PATTERN" "${SCAN_PATHS[@]}" 2>/dev/null || true)"
fi

if [[ -n "${hits}" ]]; then
  echo "Private leakage patterns found:" >&2
  echo "${hits}" >&2
  fail=1
fi

# Refuse accidental promotion markers that copy private catalogues by name.
echo "== promotion-marker gate =="
if command -v rg >/dev/null 2>&1; then
  promo="$(rg -n -i 'promoted from.*(jarvis|private skill)|copied from.*jarvis-skills|source:\s*jarvis-skills' plugins 2>/dev/null || true)"
else
  promo="$(grep -RInE 'promoted from.*(jarvis|private skill)|copied from.*jarvis-skills|source:[[:space:]]*jarvis-skills' plugins 2>/dev/null || true)"
fi
if [[ -n "${promo}" ]]; then
  echo "Private promotion markers found:" >&2
  echo "${promo}" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "Privacy check FAILED." >&2
  exit 1
fi

echo "Privacy check passed."
