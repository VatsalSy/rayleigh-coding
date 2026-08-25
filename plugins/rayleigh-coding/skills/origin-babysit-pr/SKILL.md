---
name: origin-babysit-pr
description: >
  Use when the session workshop is Origin and the user says "babysit this PR",
  "watch the PR", "loop until green", or "shepherd this to merge" on an
  Origin change. GitHub-workshop watches are gh-babysit-pr. One-pass review
  without the standing watch is git-master.
---

# Babysit an Origin PR

Own an Origin change until it is merge-ready. Reviewer is **Cursor Bugbot**,
never CodeRabbit. Bugbot has **no local review CLI**; poll its check and full
comments with `origin pr checks`, `origin pr view --checks --comments`, and
`origin pr thread list --comments`. GitHub Actions are not the merge gate here;
they run after GitHub `main` is fast-forwarded.

Follow `git-master` review babysitting rules 1–7 by number. Rule 8 (merge-bot
GitHub approval comment) does not apply on Origin. Ignore GitHub-only
subclauses of rule 3: do not route silent or rate-limited CodeRabbit heads
to `autofix`.

## Loop

1. Baseline: `origin pr view --checks --comments`, `origin pr checks`, and
   `origin pr thread list --comments` on the change. Record head SHA, base
   branch, Bugbot check state, unresolved Bugbot threads, and the user's goal.
   `origin pr checkout` before any write.
2. Wait with bounded polls. Allow at most two fix pushes. Never busy-loop.
3. On each wake, act only on comments newer than the last push:
   - New Bugbot threads → `origin-address-comment` (must-fix) after
     `origin-pr-triage`.
   - Human threads → same.
   - Run `origin pr checks <change> --watch` for the Cursor Bugbot check.
     Missing GitHub Actions are irrelevant, but a pending, absent, cancelled,
     or failed Bugbot check is not approval.
     Re-read with `origin pr checks --json name,status,conclusion` and require
     the Cursor Bugbot row to have `status: completed` and `conclusion` equal
     to `neutral` or `success`; any other conclusion is a hard stop.
   - Material base drift → update from Origin `main` and re-push to the
     Origin remote only.
4. Decline out-of-scope Bugbot nits with a signed dismissal on the thread
   (`origin pr thread reply`), then `origin pr thread resolve`.
5. Exit merge-ready only when the Cursor Bugbot check has the accepted
   completed conclusion above for the exact latest head and every actionable
   Bugbot thread is fixed or
   declined-with-reason. Generated summary threads do not count as findings
   and need not be resolved. Record a fresh receipt from `origin pr checks`,
   `origin pr view --checks --comments`, and
   `origin pr thread list --comments`. Merge only if pre-authorised, and only
   `origin pr merge -m`.
6. After merge, fast-forward GitHub `main`. If CI then fails, `gh-fix-ci`
   on GitHub — not this skill.

## Gotchas

1. Do not invoke CodeRabbit, `autofix`, or `code-review` here.
2. Never squash-merge.
3. Do not push the feature branch to GitHub.
4. A generated `## PR Summary` is not proof the Bugbot review check completed.
