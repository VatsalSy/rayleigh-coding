#!/usr/bin/env bash
# Create and verify a draft on an existing, approved GitHub tag.
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: create_release.sh <owner/repo> <version> <notes-file> <commit-sha>" >&2
  exit 2
fi

repo=$1
version=$2
notes=$3
commit=$(printf '%s' "$4" | tr 'ABCDEF' 'abcdef')
if [[ ! "$repo" =~ ^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+$ ||
      ! "$version" =~ ^v?[0-9]+\.[0-9]+(\.[0-9]+)?([-+][A-Za-z0-9.+-]+)?$ ||
      ! "$commit" =~ ^[0-9a-f]{40}$ || ! -f "$notes" ]]; then
  echo "Expected a GitHub repository, version tag, notes file, and full commit SHA." >&2
  exit 2
fi

verify_tag() {
  local target
  target=$(gh api graphql --hostname github.com \
    -f owner="${repo%/*}" -f name="${repo#*/}" -f ref="refs/tags/$version" \
    -f query='query($owner:String!,$name:String!,$ref:String!){
      repository(owner:$owner,name:$name) {
        ref(qualifiedName:$ref) { target {
          ... on Commit { oid }
          ... on Tag { target { ... on Commit { oid } } }
        } }
      }
    }' --jq '.data.repository.ref.target | .oid // .target.oid // empty')
  if [[ "$target" != "$commit" ]]; then
    echo "The tag is missing or does not point to the requested commit." >&2
    return 1
  fi
}

verify_tag
gh release create "$version" --repo "github.com/$repo" --draft --verify-tag \
  --title "$version" --notes-file="$notes"
readback=$(gh release view "$version" --repo "github.com/$repo" --json isDraft,tagName,url \
  --jq 'if .isDraft then [.tagName, .url] | @tsv else empty end')
if [[ "$readback" != "$version"$'\t'https://* ]]; then
  echo "GitHub did not return the expected draft. Check the remote before retrying." >&2
  exit 1
fi
verify_tag
printf 'Verified draft %s\n' "$readback"
