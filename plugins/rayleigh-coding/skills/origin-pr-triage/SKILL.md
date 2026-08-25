---
name: origin-pr-triage
description: >
  Use when the session workshop is Origin and the user says "triage the PR",
  "what did the reviews say", or right after opening/updating an Origin
  change. GitHub triage is gh-pr-triage. Applying fixes is
  origin-address-comment.
---

# Origin PR Triage

Sort Origin review comments into must-fix vs decline. Reviewer is **Cursor
Bugbot**, never CodeRabbit. Bugbot has no review CLI; require its check with
`origin pr checks --watch`, then read full comments with
`origin pr view --checks --comments` and `origin pr thread list --comments`.

## Execution

1. Confirm Origin workshop.
2. `origin pr checks --watch`, then require the Cursor Bugbot JSON row to have
   `status: completed` and `conclusion: neutral|success` for the latest head.
   Inspect `origin pr view --checks --comments` and
   `origin pr thread list --comments`. A successful check with no finding
   threads is a clean pass; a missing or running check is not approval.
3. Freshness: ignore comments on superseded commits.
4. Classify:
   - Must-fix before merge
   - Optional/defer
   - Decline with reason (invalid or out of scope)
5. Anti-scope-creep governs: adjacent refactors and "while you're here"
   features are Decline, however sensible.
6. Hand must-fix to `origin-address-comment`. Do not apply fixes in this
   skill. Do not route anything to `autofix`.

## Gotchas

1. A wrong change number yields an empty thread list, not an error. Confirm
   the target before reporting "nothing to do".
2. Bugbot severity is real until inspection fails; do not blanket-P3 it.
