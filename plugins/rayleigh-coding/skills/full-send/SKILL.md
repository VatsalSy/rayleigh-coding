---
name: full-send
disable-model-invocation: true
description: >-
  Use only when the user explicitly invokes `/full-send` or `$full-send`:
  finish, prove, review, and babysit the task unattended to a merge-ready PR,
  then merge only after gates pass and the owner has authorized landing.
  Stop ready for the owner to merge: full-stop.
---

# Full Send

The user said "full send" because they are not watching this thread. Own the
named task from its current state through a merge-ready pull request, then
land it only under the merge rules below. Progress updates and the final
message may go unread, so a question in ordinary prose stalls the work
silently. Without a clear "full send" request, none of the extra authority
below applies.

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`). Use only Cursor and Grok first-party models via
`/vatsal-mode`. Do not use third-party model families or private agent home
directories.

## Safety stops (never bypass)

A "full send" request never overrides these:

- Never bypass a required review, status check, branch-protection rule, or
  merge gate. Never use `--admin` or other privilege bypasses.
- Never merge into a protected or production branch, and never merge a PR on a
  **public** repository, unless the owner explicitly authorized landing for
  this task (a clear "full send" on the named task counts) **and** every gate
  below still passes on the exact head.
- Never send email or chat messages on anyone's behalf.
- Never handle secrets beyond what the repo already uses for ordinary CI, and
  never move money, change billing, or make purchases.
- Never force-push any branch other than this task's own PR branch, and then
  only with `--force-with-lease` bound to the head observed before the rebase.
- Never touch production deploys, DNS, data deletion, or closing unrelated PRs
  unless the same request names that action.

## What the request grants

For the named task only:

- Finish the change on a feature branch (create one if you are on the default
  branch).
- Run the proof methods the change needs: builds, tests, running an app or
  dev server, browser automation, screenshots, and other visual checks.
  Repository rules on *how* to test still apply; this only removes ask-first
  barriers for those methods.
- Open or update a non-draft PR with `gh-pr-create`.
- Babysit with `gh-babysit-pr` (and `gh-address-comment` / `gh-fix-ci` as
  needed). Honour optional `MERGE_BOT_LOGIN` when set.
- Merge the task's own PR only after the merge gate passes.

GitHub is the workshop for these skills. Origin is out of scope here.

## Steps

1. **Finish the change.** Smallest change that meets the goal. Fix the case
   that happened, not every case that could.
2. **Prove it.** See "Proof".
3. **Review it.** Run `sol-loop` (CodeRabbit via `code-review`, plus at most
   one read-only `wise-owl` consult when a finding is consequential).
4. **File the PR** with `gh-pr-create`. Rebase onto the latest default branch
   first. Add one short line in the body describing how you proved the change.
5. **Babysit** with `gh-babysit-pr`. Fix real findings and CI failures. Prove
   each fix before pushing it. Keep scope at the original goal.
6. **Merge** only when the merge gate passes and the safety stops above allow
   it. Prefer merge commits unless the user asked to squash. Stay until GitHub
   reports the PR merged when a merge queue or auto-merge is in use.
7. **Report** the PR URL, merge commit (or why it stayed open), proof, review
   outcome, and every decision made for the user.

Stay active from step 1 to step 7. Ending a turn while checks or bots are
pending stops the work unless a watcher will wake you. Use the babysit loop
from `gh-babysit-pr`. Do not invent a custom poller.

## Proof

Proof is evidence observed in this session: command output, a reproduction, a
screenshot, or a live UI check. Prefer the most direct proof:

- Reproduce the failure, apply the fix, watch the same reproduction pass.
- Run the checks the repository's CI runs.
- Add one focused test that fails without the fix when behaviour has none and
  the repo has a test setup.
- For UI and runtime behaviour, run the app and look at the change. Green
  mocked tests do not prove the user experience.

Without proof there is no full confidence: ask through the harness question
tool so the thread visibly waits.

## Merge gate

All of these must hold on the latest head:

- Proof covers every change in the diff.
- Required checks are green.
- Review bots finished within their budgets; each finding is fixed or
  dismissed with a written reason.
- No human review still requests changes.
- When `MERGE_BOT_LOGIN` is set, that login has **APPROVED** the exact head.
- The branch is not `BEHIND` or `DIRTY`, and no base commits since the last
  green run touch this PR's files.
- Safety stops above still permit landing.

A wake from babysit is news, not a merge decision. Recheck the gate yourself.

## Asking the user

Ask only when you cannot continue alone: unprovable change, gate you cannot
fix, step outside the grant, ambiguous goal that changes the result, or
another PR making this one obsolete. Put the PR link, blocker, and options
(recommendation first) in one structured question. If no question tool exists
or no answer comes, leave the PR open and unmerged and lead the final message
with the question.

## Report

Lead with endpoint state and live receipts (PR URL, head SHA, merge commit or
"left open"). Then proof, review outcome, decisions made for the user, and
remaining risks.
