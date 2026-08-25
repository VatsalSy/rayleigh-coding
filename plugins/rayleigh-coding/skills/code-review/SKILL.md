---
name: code-review
description: >-
  Use when the user says "review my code", "run coderabbit", "check code
  quality", or before pushing behavioural code/skill changes. Thin public
  CodeRabbit CLI wrapper — not a private org-routing guard.
metadata:
  version: "0.4.0"
---

# CodeRabbit Code Review (public)

Run the local CodeRabbit CLI through the thin wrapper in
`scripts/coderabbit_repo_review.py`.

This public skill does **not** claim private fleet behaviour: no cadence
receipts, no paid-org lock files, no exact-diff reuse ledger, and no secret
redaction pipeline. If you need those, use a private guard outside this
marketplace.

## Prerequisites

1. `coderabbit` CLI installed and authenticated
   (<https://www.coderabbit.ai/cli>).
2. A GitHub remote when you want organisation hints from the repo owner.
3. Never pass secrets into the review diff. Inspect the outgoing change first.

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
