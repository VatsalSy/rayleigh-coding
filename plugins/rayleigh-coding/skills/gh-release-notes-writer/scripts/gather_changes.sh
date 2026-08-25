#!/usr/bin/env bash
# Gather changes since last release for release notes generation.
# Usage:
#   gather_changes.sh [base-tag]
#   gather_changes.sh --base-tag <tag> [--tag-scheme major|minor|patch] [--prefer-patch-level]
#
# Rules:
# - --tag-scheme (or RELEASE_TAG_SCHEME) explicitly controls the scheme.
# - --prefer-patch-level is a convenience flag when no explicit scheme is set.
# - If no tags exist, determine_tag_scheme() still returns a deterministic scheme.

set -euo pipefail

print_usage() {
  cat <<'EOF'
Usage: gather_changes.sh [base-tag]
       gather_changes.sh --base-tag <tag> [--tag-scheme major|minor|patch] [--prefer-patch-level]

Options:
  --base-tag <tag>                Use a specific tag as the release base.
  --tag-scheme <major|minor|patch>
                                  Force a tag scheme for suggestions.
  --prefer-patch-level            Prefer patch scheme when no explicit scheme is set.
  -h, --help                      Show this help.

Env:
  RELEASE_TAG_SCHEME              Same values as --tag-scheme.
EOF
}

determine_tag_scheme() {
  local base_tag="$1"
  local explicit_scheme="$2"
  local prefer_patch_level="$3"

  if [[ -n "$explicit_scheme" ]]; then
    echo "$explicit_scheme"
    return
  fi

  if [[ -n "$base_tag" ]]; then
    if [[ "$base_tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "patch"
      return
    fi
    # Keep existing default behavior for vMAJOR.MINOR tags.
    echo "minor"
    return
  fi

  if [[ "$prefer_patch_level" == "true" ]]; then
    echo "patch"
    return
  fi

  echo "minor"
}

BASE_TAG=""
TAG_SCHEME="${RELEASE_TAG_SCHEME:-}"
PREFER_PATCH_LEVEL="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-tag)
      if [[ $# -lt 2 ]]; then
        echo "❌ Missing value for --base-tag" >&2
        exit 1
      fi
      BASE_TAG="$2"
      shift 2
      ;;
    --tag-scheme)
      if [[ $# -lt 2 ]]; then
        echo "❌ Missing value for --tag-scheme" >&2
        exit 1
      fi
      TAG_SCHEME="$2"
      shift 2
      ;;
    --prefer-patch-level)
      PREFER_PATCH_LEVEL="true"
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    --*)
      echo "❌ Unknown option: $1" >&2
      print_usage
      exit 1
      ;;
    *)
      if [[ -n "$BASE_TAG" ]]; then
        echo "❌ Multiple base tags provided. Use only one base tag." >&2
        exit 1
      fi
      BASE_TAG="$1"
      shift
      ;;
  esac
done

if [[ -n "$TAG_SCHEME" && ! "$TAG_SCHEME" =~ ^(major|minor|patch)$ ]]; then
  echo "❌ Invalid tag scheme: $TAG_SCHEME" >&2
  echo "   Expected one of: major, minor, patch" >&2
  exit 1
fi

if [[ -z "$BASE_TAG" ]]; then
  BASE_TAG=$(git tag --list 'v*' --sort=-version:refname | head -1 || echo "")
fi

if [[ -n "$BASE_TAG" ]] && ! git rev-parse --verify --quiet "refs/tags/${BASE_TAG}" >/dev/null; then
  echo "❌ Base tag does not exist: $BASE_TAG" >&2
  exit 1
fi

SCHEME=$(determine_tag_scheme "$BASE_TAG" "$TAG_SCHEME" "$PREFER_PATCH_LEVEL")

echo "=== Release Changes Summary ==="
echo

echo "## Version Information"
if [[ -z "$BASE_TAG" ]]; then
  echo "Previous version: (none - first release)"
  echo "Tag scheme: $SCHEME"
  if [[ "$SCHEME" == "patch" ]]; then
    echo "Suggested version: v1.0.0"
  else
    echo "Suggested version: v1.0"
  fi
  RANGE="HEAD"
else
  echo "Previous version: $BASE_TAG"
  echo "Tag scheme: $SCHEME"

  MAJOR=0
  MINOR=0
  PATCH=0
  PARSED="false"

  case "$SCHEME" in
    patch)
      if [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        PATCH="${BASH_REMATCH[3]}"
        PARSED="true"
        echo "Suggested next (patch): v${MAJOR}.${MINOR}.$((PATCH + 1))"
        echo "Suggested next (minor): v${MAJOR}.$((MINOR + 1)).0"
        echo "Suggested next (major): v$((MAJOR + 1)).0.0"
      elif [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        PARSED="true"
        echo "Suggested next (patch): v${MAJOR}.${MINOR}.1"
        echo "Suggested next (minor): v${MAJOR}.$((MINOR + 1)).0"
        echo "Suggested next (major): v$((MAJOR + 1)).0.0"
      else
        echo "⚠️  Could not parse $BASE_TAG for patch scheme suggestions"
      fi
      ;;
    major)
      if [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        PARSED="true"
      elif [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        PARSED="true"
      else
        echo "⚠️  Could not parse $BASE_TAG for major scheme suggestions"
      fi

      if [[ "$PARSED" == "true" ]]; then
        echo "Suggested next (major): v$((MAJOR + 1)).0"
      fi
      ;;
    minor)
      if [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        PARSED="true"
      elif [[ "$BASE_TAG" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        PARSED="true"
      else
        echo "⚠️  Could not parse $BASE_TAG for minor scheme suggestions"
      fi

      if [[ "$PARSED" == "true" ]]; then
        if [[ "$MINOR" == "0" ]]; then
          echo "Suggested next (minor): v${MAJOR}.5"
        fi
        echo "Suggested next (major): v$((MAJOR + 1)).0"
      fi
      ;;
  esac

  RANGE="${BASE_TAG}..HEAD"
fi
echo

COMMIT_COUNT=$(git rev-list --count "$RANGE" 2>/dev/null || echo "0")
echo "## Statistics"
echo "Commits in range: $COMMIT_COUNT"
if [[ "$COMMIT_COUNT" == "0" ]]; then
  if [[ -z "$BASE_TAG" ]]; then
    echo "⚠️  No commits found in repository history"
  else
    echo "⚠️  No commits since $BASE_TAG"
  fi
  exit 0
fi
echo

echo "## Commits"
echo '```'
git log --oneline --no-decorate "$RANGE" | head -50
if [[ $COMMIT_COUNT -gt 50 ]]; then
  echo "... and $((COMMIT_COUNT - 50)) more commits"
fi
echo '```'
echo

echo "## Changed Files"
echo '```'
if [[ -z "$BASE_TAG" ]]; then
  git diff --stat --stat-width=80 "$(git rev-list --max-parents=0 HEAD)..HEAD" 2>/dev/null | tail -20
else
  git diff --stat --stat-width=80 "$RANGE" | tail -20
fi
echo '```'
echo

echo "## Changes by Area"
if [[ -z "$BASE_TAG" ]]; then
  CHANGED_FILES=$(git diff --name-only "$(git rev-list --max-parents=0 HEAD)..HEAD" 2>/dev/null || git ls-files)
else
  CHANGED_FILES=$(git diff --name-only "$RANGE")
fi

echo "$CHANGED_FILES" | cut -d'/' -f1 | sort | uniq -c | sort -rn | head -10

echo
echo "## Notable Files Changed"
echo "$CHANGED_FILES" | grep -iE "(readme|changelog|package\.json|setup\.py|cargo\.toml|go\.mod|requirements\.txt|\.md$)" | head -10 || echo "(none detected)"
