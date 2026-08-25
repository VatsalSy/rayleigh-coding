---
name: raycast-pr-checkout
description: Use when the user shares a github.com/raycast/extensions/pull/* URL or Raycast PR number — sparse-checkouts only that extension for local review, stopping before install/run (`npm install && npm run dev` stays manual).
---

# Raycast PR Checkout

GitHub-only (`github.com/raycast/extensions`). Origin changes use
`origin-pr-checkout`. This skill never talks to `origin.cursor.com`.

## Overview

Accept a Raycast extensions PR URL (or number), perform an automated sparse checkout for the target extension, and leave the environment ready for manual local run in Raycast.
Default clone target is the user's fork via SSH: `git@github.com:OWNER/raycast-extensions.git`.

## Workflow

1. Validate the PR input and extract PR number.
2. Query PR metadata using `gh pr view ... --repo raycast/extensions`.
3. Detect the extension name from changed files under `extensions/<extension-name>/`.
4. Clone from fork, add `upstream`, fetch `pull/<PR>/head`, and sparse-checkout `extensions/<extension-name>`.
5. Stop before dependency install and tell the user:
   - `cd <checked-out-extension-dir>`
   - `npm install && npm run dev`

## Commands

```bash
python3 skills/raycast-pr-checkout/scripts/checkout_raycast_pr.py \
  "https://github.com/raycast/extensions/pull/25509"
```

### Useful options

- Override fork URL:
  - `--fork-url "https://github.com/OWNER/raycast-extensions.git"`
  - `--fork-url "git@github.com:OWNER/raycast-extensions.git"`
- Force extension name when PR touches multiple extension folders:
  - `--extension-name "<extension-name>"`
- Choose destination directory:
  - `--dest-dir "/path/to/folder"`
- Dry run:
  - `--dry-run`

## Requirements

- `git`
- `gh` authenticated for GitHub access (`gh auth status`)
- Network access to GitHub

## Failure Handling

If extension detection is ambiguous or unavailable, retry with `--extension-name`.
If clone destination exists, use `--dest-dir` with a clean directory.
