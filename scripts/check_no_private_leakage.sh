#!/usr/bin/env bash
# Fail if private / personal leakage patterns appear in published skills.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATTERN='Rayleigh|Worthington|Kelvin/Stokes|/Users/vatsal|/Users/comphy|openclaw|second-brain|comphy-state|\bsgit\b|stokes-ts|Projects-cowork|dual-sync-main|medical-record|durham-expenses|vatsalsanjay\.com|vatsal\.sanjay@|5b283a1192f0a78f|2e852c08b4428ffafda676c354c13c98|264b1512bed863f81da699991dafb514|0dd798a4d4f2ba386457f3cdbe54fba9|8e47b17c0904dc8eb4a934c4038b7fa7|prj_bHRfpwCUfu05|prj_stHuYYHE9RJG|prj_SHsyjr2vTYTe|prj_rT3QjtWigNGR|prj_HmDrwzVsRwfe|prj_Yyc9nVMvlNc5|prj_8NGwHM9hYo3q|Synosync|ireminder|calcli|zoteroctl|jarvis-skills|comphy-bot'

if command -v rg >/dev/null 2>&1; then
  hits="$(rg -n --pcre2 "$PATTERN" skills .cursor-plugin docs README.md 2>/dev/null || true)"
else
  hits="$(grep -RInE "$PATTERN" skills .cursor-plugin docs README.md 2>/dev/null || true)"
fi

if [[ -n "${hits}" ]]; then
  echo "Private leakage patterns found:" >&2
  echo "${hits}" >&2
  exit 1
fi

echo "Privacy check passed."
