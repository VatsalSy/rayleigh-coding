#!/usr/bin/env bash
set -euo pipefail

# ensure required commands exist
if ! command -v gh >/dev/null 2>&1; then
  echo "Missing gh on PATH" >&2
  exit 2
fi
if ! command -v git >/dev/null 2>&1; then
  echo "Missing git on PATH" >&2
  exit 2
fi


if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository" >&2
  exit 1
fi

if [ -n "${PR_BASE_BRANCH:-}" ]; then
  # Require the remote-tracking ref so callers can safely use
  # origin/${BASE_BRANCH} for git log / git diff.
  if git show-ref --verify --quiet "refs/remotes/origin/${PR_BASE_BRANCH}"; then
    printf '%s\n' "${PR_BASE_BRANCH}"
    exit 0
  fi

  echo "PR_BASE_BRANCH is set to '${PR_BASE_BRANCH}' but refs/remotes/origin/${PR_BASE_BRANCH} was not found (fetch origin first)" >&2
  exit 1
fi

default_branch=""

if git remote get-url origin >/dev/null 2>&1; then
  if origin_head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"; then
    default_branch="${origin_head#origin/}"
  fi

  if [ -z "${default_branch}" ]; then
    default_branch="$(git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p' | head -n 1)"
  fi
fi

if [ -z "${default_branch}" ] && command -v gh >/dev/null 2>&1; then
  default_branch="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)"
fi

for candidate in "${default_branch}" main master develop trunk; do
  [ -n "${candidate}" ] || continue

  if git show-ref --verify --quiet "refs/remotes/origin/${candidate}"; then
    printf '%s\n' "${candidate}"
    exit 0
  fi
done

echo "Unable to resolve base branch via refs/remotes/origin/*. Fetch origin, or set PR_BASE_BRANCH / pass --base explicitly." >&2
exit 1
