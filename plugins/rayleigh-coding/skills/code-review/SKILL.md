---
name: code-review
description: >-
  Use when the user says "review my code", "run coderabbit", "check code
  quality", or before pushing behavioural code/skill changes. Thin CodeRabbit
  CLI wrapper for this plugin.
metadata:
  version: "0.4.0"
---

# CodeRabbit Code Review

Run the local CodeRabbit CLI through the wrapper in
`scripts/coderabbit_repo_review.py`.

This skill is a thin CLI helper: organisation hinting from env/remote, then
`coderabbit review`. It does not maintain review-receipt ledgers or cadence
locks.

## Prerequisites

1. `coderabbit` CLI installed and authenticated
   (<https://www.coderabbit.ai/cli>).
2. A GitHub remote when you want organisation hints from the repo owner.
3. Never pass secrets into the review diff. Inspect the outgoing change first
   and skip the review if it would transmit unpublished or sensitive material.

If the CLI is missing, say so and stop. Do not invent another review backend.

## Invocation

```bash
python3 /absolute/path/to/code-review/scripts/coderabbit_repo_review.py \
  -- --base main
```

Useful flags on the wrapper (before `--`):

| Flag | Meaning |
|---|---|
| `--uncommitted` | Prefer reviewing against `--base` for local work |
| `--base <ref>` | Comparison base (default `main`) |
| `--switch-org` | Accepted for compatibility; org still comes from env/remote |

Organisation hint order:

1. `CODERABBIT_ORG` if set
2. else GitHub `origin` owner
3. optional `CODERABBIT_REQUIRE_ORG=1` refuses when unset

## After review

- Fix or explicitly note Critical/Warning findings before push when the user
  asked for a guarded ship.
- If CodeRabbit is unavailable, say the gate was skipped and run repository
  tests plus independent inspection instead.

## Related

- `autofix` — address review-thread comments on an open PR
- `coderabbit-config` — `.coderabbit.yaml` authoring
- `dev-review-ultra` — adversarial human-style review without CodeRabbit
