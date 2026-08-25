# rayleigh-coding

Public Cursor plugin with coding skills and **`/vatsal-mode`**.

Built for Cursor Cloud Agents (and local Cursor). Personal / fleet / writing
skills stay in a private repo and are not published here.

## Install

```text
/add-plugin VatsalSy/rayleigh-coding
```

Or add the GitHub repo as a Cursor plugin from the marketplace / plugin UI.

## Start here

```text
/vatsal-mode
```

That mode routes planning, grilling, verification, review, and git/PR work
through the skills in this plugin.

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

See `docs/CODING.md` for exportable conventions. See `docs/SKILLS.md` for the
full inventory.

## Privacy

This repository must not contain private host topology, vault paths, personal
deploy inventories, or secrets. CI runs `scripts/check_no_private_leakage.sh`
on every push.

## License

MIT
