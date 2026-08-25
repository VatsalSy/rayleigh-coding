---
name: origin-address-comment
description: >
  Use when the workshop is Origin and the user says "address the PR comments",
  "fix review feedback", or "resolve the review threads" on an Origin change,
  or after origin-pr-triage hands off must-fix items. NOT for GitHub threads
  (gh-address-comment).
---

# Origin PR Comment Handler

Address open review threads on a Cursor Origin change. Reviewer is **Cursor
Bugbot** (and any human comments). Never CodeRabbit.

## Execution

1. Confirm Origin workshop. Otherwise use `gh-address-comment`.
2. `origin auth status`. Checkout the change: `origin pr checkout`.
3. Require the Cursor Bugbot check to complete for the exact head with
   `origin pr checks --watch`, then list full threads with
   `origin pr thread list --comments`. Act only on comments newer than the
   latest push; generated summary threads are not findings.
4. Inspect the flagged source before changing. Bugbot is helpful, not
   always right. Decline with a written reason rather than "fixing" a bad
   finding.
5. Anti-scope-creep: do not expand the PR beyond the user's original goal.
6. Fix must-fix items in file batches. Commit with the global git identity. Push only to
   the `origin.cursor.com` remote.
7. Reply on the thread (`origin pr comment` or `origin pr thread reply`),
   then `origin pr thread resolve` **after** the fix is pushed.
8. Dismissal replies only are signed `*<model-slug> on behalf of the user:*`.
9. Receipt: re-run `origin pr checks`, `origin pr view --checks --comments`,
   and `origin pr thread list --comments`; report remaining actionable open
   count separately from generated summary threads. Never declare resolved
   from memory.

## Gotchas

1. Resolving a thread before the fix is on Origin is a false green.
2. Do not hand off to `autofix`. That skill is CodeRabbit/GitHub-only.
