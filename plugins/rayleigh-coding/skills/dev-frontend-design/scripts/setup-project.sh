#!/usr/bin/env bash
# setup-project.sh
# Scaffold a new frontend project using Vite+ with sensible defaults.
# Usage: bash setup-project.sh [project-name] [template]
# Templates: react-ts, vue-ts, svelte-ts, vanilla-ts

set -euo pipefail

PROJECT_NAME="${1:-my-app}"
TEMPLATE="${2:-react-ts}"

echo "🎨 Setting up frontend project: $PROJECT_NAME (template: $TEMPLATE)"

# Check vp is available
if ! command -v vp &>/dev/null; then
  echo "❌ Vite+ not installed. Run: curl -fsSL https://vite.plus | bash"
  exit 1
fi

# Scaffold
vp create "$PROJECT_NAME" --template "$TEMPLATE"
cd "$PROJECT_NAME"

# Install deps
vp install

# Initial check — make sure everything is clean
vp check

echo ""
echo "✅ Project ready: $PROJECT_NAME"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  vp dev          → start dev server"
echo "  vp check        → lint + format + type-check"
echo "  vp build        → production build"
echo "  vp test         → run tests"
