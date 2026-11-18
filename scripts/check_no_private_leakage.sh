#!/usr/bin/env bash
# Scan publishable paths, contents and newly introduced commit metadata.
# Matching values and potentially sensitive filenames stay out of CI logs.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v rg >/dev/null || { echo "ripgrep is required" >&2; exit 2; }

umask 077
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
patterns="$scratch/patterns"
sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' scripts/privacy-patterns.pcre > "$patterns"
if [[ ! -s "$patterns" ]]; then
  echo "No privacy patterns loaded" >&2
  exit 2
fi
if [[ -n "${PRIVACY_EXTRA_PATTERN:-}" ]]; then
  printf '%s\n' "$PRIVACY_EXTRA_PATTERN" >> "$patterns"
fi

failed=0
scan() {
  local kind=$1 output status
  shift
  if output=$(rg --no-config --pcre2 --text --files-with-matches -f "$patterns" "$@" 2>/dev/null); then
    printf 'Privacy patterns matched %s (%s matching inputs).\n' "$kind" "$(printf '%s\n' "$output" | wc -l | tr -d ' ')" >&2
    failed=1
  else
    status=$?
    if [[ "$status" -ne 1 ]]; then
      printf 'Privacy scanner failed while checking %s (exit %s).\n' "$kind" "$status" >&2
      exit 2
    fi
  fi
}

git ls-files --cached --others --exclude-standard -z > "$scratch/paths"
scan "publishable paths" --null-data -- "$scratch/paths"
files=()
while IFS= read -r -d '' path; do
  if [[ -L "$path" || ( -e "$path" && ! -f "$path" ) ]]; then
    echo "Publishable entries must be regular files." >&2
    exit 2
  fi
  case "$path" in
    scripts/check_no_private_leakage.sh|scripts/privacy-patterns.pcre) continue ;;
  esac
  if [[ -f "$path" ]]; then
    files+=("$path")
  fi
done < "$scratch/paths"
if [[ ${#files[@]} -gt 0 ]]; then
  scan "publishable file contents" -- "${files[@]}"
fi

base=${HISTORY_HYGIENE_BASE:-origin/main}
if [[ "$base" == "0000000000000000000000000000000000000000" ]]; then
  base=origin/main
fi
if ! base_sha=$(git rev-parse --verify --end-of-options "${base}^{commit}"); then
  echo "Cannot resolve the privacy scan base commit." >&2
  exit 2
fi
git log --format='%an%n%ae%n%cn%n%ce%n%B' "$base_sha..HEAD" > "$scratch/commits"
scan "new commit metadata" -- "$scratch/commits"

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
echo "Privacy check passed."
