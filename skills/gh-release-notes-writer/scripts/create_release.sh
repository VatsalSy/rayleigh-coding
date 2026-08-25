#!/usr/bin/env bash
# Create git tag and GitHub release
# Usage: create_release.sh <version> <notes-file>
# Example: create_release.sh v2.0 /tmp/release-notes.md

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: create_release.sh <version> <notes-file>"
  echo "Example: create_release.sh v2.0 /tmp/release-notes.md"
  exit 1
fi

VERSION="$1"
NOTES_FILE="$2"

# Validate version format
if [[ ! "$VERSION" =~ ^v[0-9]+\.[05]$ && ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ Invalid version format: $VERSION"
  echo "  Expected one of:"
  echo "  - vMAJOR.MINOR where MINOR is 0 or 5 (examples: v1.0, v1.5)"
  echo "  - vMAJOR.MINOR.PATCH (examples: v1.0.0, v1.2.3)"
  exit 1
fi

# Check notes file exists
if [[ ! -f "$NOTES_FILE" ]]; then
  echo "❌ Notes file not found: $NOTES_FILE"
  exit 1
fi

# Check if tag already exists
if git tag --list | grep -q "^${VERSION}$"; then
  echo "❌ Tag $VERSION already exists"
  echo "  Existing tags:"
  git tag --list 'v*' --sort=-version:refname | head -5
  exit 1
fi

echo "=== Creating Release $VERSION ==="
echo

# Create annotated tag (use git commit wrapper for bot-authored identity)
echo "📌 Creating annotated tag..."
git tag -a "$VERSION" -m "Release $VERSION"
echo "  ✅ Tag created: $VERSION"

# Push tag to remote via git push
echo "🚀 Pushing tag to origin..."
if ! git push "$VERSION"; then
  echo "❌ Failed to push tag"
  echo "  Removing local tag..."
  git tag -d "$VERSION"
  exit 1
fi
echo "  ✅ Tag pushed"

# Create GitHub release via gh
echo "📦 Creating GitHub release..."
if ! gh release create "$VERSION" \
  --title "$VERSION" \
  --notes-file "$NOTES_FILE"; then
  echo "❌ Failed to create GitHub release"
  echo "  Tag was pushed - you may need to create the release manually"
  exit 1
fi

echo
echo "✅ Release $VERSION published successfully!"
echo
gh release view "$VERSION" --web 2>/dev/null \
  || echo "View at: $(gh repo view --json url -q .url)/releases/tag/$VERSION"
