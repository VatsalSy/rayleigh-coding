# Dependabot Batch Workflow Cheatsheet

## Input Sources

Prefer this order:
1. Query live PRs via `gh` (`--from-gh`) for accuracy.
2. Parse pasted PR titles from text (`--input-file` or stdin).
3. Parse manually extracted lines from screenshots when API access is unavailable.

Expected title shape:

`build(deps-dev): bump eslint from 9.39.2 to 10.0.0`

## Core Commands

Collect and inspect updates:

```bash
python skills/gh-dependabot-batch-pr/scripts/collect_dependabot_updates.py --from-gh
```

Write normalized JSON:

```bash
python skills/gh-dependabot-batch-pr/scripts/collect_dependabot_updates.py --from-gh --write-json tmp/dependabot-updates.json --json
```

Generate grouped npm commands:

```bash
python skills/gh-dependabot-batch-pr/scripts/collect_dependabot_updates.py --from-gh --npm-install
```

Run repo quality gate:

```bash
python skills/gh-dependabot-batch-pr/scripts/run_repo_checks.py --require-scripts
```

Close superseded Dependabot PRs after opening the combined PR:

```bash
BATCH_PR_URL="$(gh pr view --json url -q .url)"
python skills/gh-dependabot-batch-pr/scripts/close_superseded_dependabot_prs.py --updates-json tmp/dependabot-updates.json --batch-pr-url "$BATCH_PR_URL" --dry-run
python skills/gh-dependabot-batch-pr/scripts/close_superseded_dependabot_prs.py --updates-json tmp/dependabot-updates.json --batch-pr-url "$BATCH_PR_URL"
```

## Failure Strategy

If checks fail:
1. Fix deterministic breakages first (lint/types/typescript configs).
2. Re-run quality gate.
3. If still failing, bisect updates by splitting the bump list into smaller sets.
4. Keep one aggregate PR only when checks and review are clean.

## PR Creation Handoff

After checks pass and diff review is complete, invoke:

`$gh-pr-create`

Use a PR title like:

`Batch Dependabot dependency updates`

After PR creation, close the superseded Dependabot PRs with the closure script.
