#!/usr/bin/env bash
# Check prerequisites for release workflow
# Exit codes: 0 = ready, 1 = blocking issue, 2 = warning only

set -euo pipefail

errors=()
warnings=()

# Check if in git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    errors+=("Not in a git repository")
fi

# Check gh is installed and authenticated
if ! command -v gh &>/dev/null; then
    errors+=("gh CLI not found. Install gh: brew install gh")
elif ! gh auth status &>/dev/null; then
    errors+=("gh not authenticated — run: gh auth login")
fi

# Check for uncommitted changes
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    uncommitted=$(git status --porcelain | head -5)
    warnings+=("Uncommitted changes detected:\n$uncommitted")
fi

# Check if on a branch (not detached HEAD)
if ! git symbolic-ref HEAD &>/dev/null; then
    warnings+=("Detached HEAD state - consider checking out a branch")
fi

# Check remote exists
if ! git remote get-url origin &>/dev/null; then
    errors+=("No 'origin' remote configured")
fi

# Output results
echo "=== Release Prerequisites Check ==="
echo

if [[ ${#errors[@]} -gt 0 ]]; then
    echo "❌ BLOCKING ISSUES:"
    for err in "${errors[@]}"; do
        echo "   • $err"
    done
    echo
fi

if [[ ${#warnings[@]} -gt 0 ]]; then
    echo "⚠️  WARNINGS:"
    for warn in "${warnings[@]}"; do
        echo -e "   • $warn"
    done
    echo
fi

if [[ ${#errors[@]} -eq 0 && ${#warnings[@]} -eq 0 ]]; then
    echo "✅ All prerequisites met"
    exit 0
elif [[ ${#errors[@]} -eq 0 ]]; then
    echo "⚠️  Proceed with caution"
    exit 2
else
    echo "❌ Cannot proceed - fix blocking issues first"
    exit 1
fi
