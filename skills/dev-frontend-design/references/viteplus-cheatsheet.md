# Vite+ (`vp`) Cheatsheet

## Install (one-time, global)
```bash
curl -fsSL https://vite.plus | bash
source ~/.zshrc   # or restart terminal
vp help
```

> **Note:** `vp env` manages Node.js versions — skip it if you manage Node yourself (Homebrew, nvm, volta, asdf). The rest of `vp` is unaffected.

---

## Project lifecycle

```bash
vp create          # scaffold new project (choose React/Vue/Svelte/Vanilla/etc.)
vp migrate         # migrate existing Vite/webpack project to Vite+
```

---

## Daily workflow

```bash
vp install         # install deps (auto-detects pnpm/npm/yarn from lockfile)
vp dev             # dev server — instant HMR, native ESM
vp check           # format + lint + type-check in ONE pass
vp check --fix     # same, auto-fix where possible
vp test            # Vitest (Jest-compat API)
vp test --browser  # run tests in real browser (Browser Mode)
vp build           # production build (Vite + Rolldown) — 40× faster than webpack
vp preview         # preview production build locally
```

---

## Package management (wraps your package manager)

```bash
vp add <pkg>           # add dependency
vp add -D <pkg>        # add dev dependency
vp remove <pkg>        # remove package
vp update              # update all packages
vp outdated            # check outdated packages
vp list                # list installed packages
vp why <pkg>           # explain why a package is installed
```

---

## Library publishing

```bash
vp pack                # build library for npm, generates DTS + exports
```

---

## Pre-commit hook setup

Add to `.husky/pre-commit` (or equivalent):

```bash
vp staged
```

Configure in `vite.config.ts`:
```ts
export default defineConfig({
  staged: {
    '*': 'vp check --fix',
  }
})
```

---

## Monorepo tasks

```bash
vp run <task>          # run task with dep-aware caching
vp run build --filter  # run only for affected packages
vp cache clean         # clear task cache
```

---

## Performance notes

| Tool replaced | Speed gain |
|---|---|
| webpack → Rolldown | ~40× faster builds |
| ESLint → Oxlint | ~50–600× faster linting |
| Prettier → Oxfmt | ~30× faster formatting |
| tsc → tsgo | significantly faster type-checks |

---

## Single config file

All of the above is configured in one `vite.config.ts`:

```ts
import { defineConfig } from 'vite-plus'

export default defineConfig({
  // Dev server / build (standard Vite config)
  plugins: [],

  // Vitest
  test: {
    include: ['src/**/*.test.ts'],
    browser: { enabled: false },
  },

  // Oxlint
  lint: {
    ignorePatterns: ['dist/**', 'node_modules/**'],
  },

  // Oxfmt (Prettier-compat)
  fmt: {
    semi: false,
    singleQuote: true,
    tabWidth: 2,
  },

  // Staged files
  staged: {
    '*.{ts,tsx,js,jsx,css}': 'vp check --fix',
  },

  // Vite Task (monorepo)
  run: {
    tasks: {
      'generate:icons': {
        command: 'node scripts/generate-icons.js',
      },
    },
  },
})
```
