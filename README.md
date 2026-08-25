# rayleigh-coding

Public **Cursor marketplace** for coding skills and **`/vatsal-mode`**.

Built for Cursor Cloud Agents and local Cursor. Personal / fleet / writing
skills stay in a private catalogue and are never published here.

## Install (Import Marketplace)

This repo is a marketplace (`.cursor-plugin/marketplace.json` + `plugins/…`).
Do **not** use the single-plugin flow alone if you want Cloud Agent marketplace
sync — use **Import Marketplace**:

1. Cursor → **Settings → Plugins → Import Marketplace** (or Team Marketplaces → **+ Import Marketplace**).
2. Repository: `https://github.com/VatsalSy/rayleigh-coding`
3. Scope: User (or Team).
4. Enable the **rayleigh-coding** plugin when listed.
5. Reload the window if skills do not appear immediately.

Then run:

```text
/vatsal-mode
```

### Alternatives

**Chat command** (single-plugin style; may pin an old commit on some builds):

```text
/add-plugin VatsalSy/rayleigh-coding
```

**Local clone** (best for live updates while developing):

```bash
mkdir -p ~/.cursor/plugins/local
git clone https://github.com/VatsalSy/rayleigh-coding.git ~/.cursor/plugins/local/rayleigh-coding
```

Reload Cursor (**Developer: Reload Window**). Pull later with:

```bash
git -C ~/.cursor/plugins/local/rayleigh-coding pull
```

## Layout

```
.cursor-plugin/marketplace.json     - marketplace registry
plugins/rayleigh-coding/            - the coding plugin
  .cursor-plugin/plugin.json
  skills/                           - public skills (/vatsal-mode, …)
  docs/                             - CODING.md + skill inventory
scripts/check_no_private_leakage.sh - hard privacy gate
.github/workflows/privacy-check.yml - CI on every push/PR
```

## What is included

- **Mode:** `vatsal-mode`
- **Plan / decide:** `create-plan`, `grill-me`, `change-impact-analysis`, `why`
- **Parallel work:** `orchestration-gpt`, `orchestration-claude`, `swarm-planner`, `parallel-task`
- **Verify:** `verification-contract`, `playwright`, `screenshot`
- **Review / security:** `code-review`, `autofix`, `coderabbit-config`, `dev-review-ultra`, `security-*`
- **GitHub / Origin:** `git-master`, `git-repo-init`, `git-*`, `gh-*`, `origin-*`
- **UI / apps:** `dev-frontend-design`, `develop-web-game`, `figma`, `figma-implement-design`
- **Deploy (discover IDs via CLI):** `vercel`, `netlify-deploy`, `render-deploy`, `cloudflare`
- **Tooling:** `python-env`, `jupyter-notebook`, `skill-creator`, `find-skills`, …

See `plugins/rayleigh-coding/docs/CODING.md` and `plugins/rayleigh-coding/docs/SKILLS.md`.

## Privacy hard gate

This repository must not contain private host topology, vault paths, personal
deploy inventories, secrets, or private skill-catalogue content. CI runs
`scripts/check_no_private_leakage.sh` on every push and PR. Locally:

```bash
bash scripts/check_no_private_leakage.sh
```

## License

MIT
