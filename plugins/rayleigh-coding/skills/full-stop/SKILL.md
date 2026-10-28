---
name: full-stop
disable-model-invocation: true
description: >-
  Use only when the user explicitly invokes `/full-stop` or `$full-stop`, or
  clearly asks to run the full-stop skill: do the full-send work, then stop
  with the PR ready for the owner to merge. Never merge it. Do not treat an
  ordinary closing "Full stop." as activation. Unattended landing: full-send.
---

# Full Stop

Do the same work as [full-send](../full-send/SKILL.md), but stop at the last
reversible point with the pull request ready for the owner to merge. Never
merge it.

Read full-send and follow its scope, steps, proof, review, babysitting, and
question rules. An explicit `/full-stop`, `$full-stop`, or "run full-stop"
request authorizes that work, including full-send's testing permission,
without a separate "full send". Its merge permission does not apply; the
overrides below take precedence. A bare closing "Full stop." is not enough.

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`). Prefer Cursor and Grok first-party models via `/vatsal-mode`.

## No merging

You may commit, push, rebase, fix conflicts, and use `--force-with-lease` on
this task's own PR branch. Never merge, enable auto-merge, enter a merge
queue, push to the default branch, bypass branch protection, or delegate
those actions.

Disable existing auto-merge and remove the PR from any merge queue before
work begins; check again before each push. Report those changes. If you
cannot prevent automatic merging, report the blocker before proceeding.

Full-send's safety stops still apply: never bypass review or merge gates,
never send email or chat on anyone's behalf, and never move secrets or money.

## Stop at the gate

Use full-send's merge gate as the readiness check. Replace its merge and
final-report landing steps with a handoff. Proof and review must cover the
final diff; recheck behaviour changes and meaningful conflict fixes before
handoff.

Fetch the target branch and check the live PR's head, base, checks, reviews,
and mergeability. Confirm it is open, not a draft, and not set to merge
without the owner. If someone else merged it, report that instead.

- **Ready to merge:** the merge gate passes. Leave the PR open and unmerged.
- **Waiting for required approval:** only human (or optional
  `MERGE_BOT_LOGIN`) approval remains. Confirm that this is the actual
  blocker.
- **Blocked:** explain what prevents readiness, what you tried, and what is
  needed. Ask under full-send's rules.

Report the PR link, final head SHA, verdict, proof, reviewer outcome, and
remaining risks. State plainly that the PR is still open and unmerged.
