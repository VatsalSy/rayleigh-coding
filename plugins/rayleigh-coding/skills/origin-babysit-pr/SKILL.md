---
name: origin-babysit-pr
description: >
  Use when the session workshop is Origin and the user says "babysit this PR",
  "watch the PR", "loop until green", or "shepherd this to merge" on an
  Origin change. GitHub-workshop watches are gh-babysit-pr. One-pass review
  without the standing watch is git-master.
---

# Babysit an Origin PR

Own an Origin change until it is merge-ready. When Bugbot runs, it is the
reviewer — never CodeRabbit. Bugbot has **no local review CLI**; poll its
check and full comments with `origin pr checks`,
`origin pr view --checks --comments`, and `origin pr thread list --comments`.
GitHub Actions are not the merge gate here; they run after GitHub `main` is
fast-forwarded.

Follow `git-master` review babysitting rules 1–7 by number. Rule 8 (merge-bot
GitHub approval comment) does not apply on Origin. Ignore GitHub-only
subclauses of rule 3: do not route silent or rate-limited CodeRabbit heads
to `autofix`.

## Bugbot — Manual Only

After the change opens and babysit starts: **do not** auto-trigger Bugbot.
Never post `bugbot run` or `@cursor review` on your own initiative.

1. Batch asks Vatsal once whether to request Bugbot before posting any
   trigger comment.
2. Only if he says yes: post exactly `bugbot run` or `@cursor review`, then
   handle that run's check and threads with the mechanics below.
3. If he says no / Hold, or has not been asked yet: babysit proceeds without
   waiting on Bugbot. Exit merge-ready must **not** require a Bugbot check or
   Bugbot threads when review was declined or never requested.

When a Bugbot run did happen (Vatsal said yes), keep the existing
Bugbot-as-reviewer handling below. The change is the **trigger / wait gate**,
not the review workflow after a run.

## Loop

1. Baseline: `origin pr view --checks --comments`, `origin pr checks`, and
   `origin pr thread list --comments` on the change. Record head SHA, base
   branch, whether Bugbot was requested, Bugbot check state (if any),
   unresolved Bugbot threads (if any), and the user's goal.
   `origin pr checkout` before any write.
2. Wait with bounded polls. Allow at most two fix pushes. Never busy-loop.
3. On each wake, act only on comments newer than the last push:
   - New Bugbot threads (only if a requested run produced them) →
     `origin-address-comment` (must-fix) after `origin-pr-triage`.
   - Human threads → same.
   - If Bugbot was requested: run `origin pr checks <change> --watch` for the
     Cursor Bugbot check. A pending, absent, cancelled, or failed Bugbot
     check is not approval. Re-read with
     `origin pr checks --json name,status,conclusion` and require the Cursor
     Bugbot row to have `status: completed` and `conclusion` equal to
     `neutral` or `success`; any other conclusion is a hard stop.
     Missing GitHub Actions are irrelevant.
   - If Bugbot was not requested: do not watch or block on a Bugbot check.
   - Material base drift → update from Origin `main` and re-push to the
     Origin remote only.
4. Decline out-of-scope Bugbot nits with a signed dismissal on the thread
   (`origin pr thread reply`), then `origin pr thread resolve`.
5. **Exit — merge-ready:**
   - If Bugbot was requested and ran: require the Cursor Bugbot check to have
     the accepted completed conclusion above for the exact latest head, and
     every actionable Bugbot thread fixed or declined-with-reason. Generated
     summary threads do not count as findings and need not be resolved.
   - If Bugbot was declined or never requested: do **not** require Bugbot
     completed; merge-ready from other babysit conditions only (human threads
     resolved, head fresh, no material blockers).
   Record a fresh receipt from `origin pr checks`,
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
5. Do not auto-post `bugbot run` / `@cursor review`; see **Bugbot — Manual Only**.
