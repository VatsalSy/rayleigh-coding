---
name: modernize
disable-model-invocation: true
description: >-
  Use only when the user explicitly invokes `$modernize` or says "modernize":
  bring an old PR or branch up to date and judge whether it should still
  exist. Taking over unfinished work: takeover.
---

# Modernize

Modernize the idea, not just the branch. A clean rebase does not prove that
the PR still belongs in the product.

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`). Prefer Cursor and Grok first-party models via `/vatsal-mode`.

## Guardrails

- Fetch the latest remote state of the branch, its base, and any related
  branch before starting.
- Treat existing worktree changes as user-owned. Use a disposable worktree
  (`git-worktree-playbook`) when the active one is dirty or in use.
- A modernize request authorizes updating that PR's own branch, including
  `--force-with-lease` bound to the head SHA observed before a rebase, and
  opening a superseding PR. It does not authorize merging, closing the old
  PR, deleting branches, changing the base branch, expanding scope, or
  force-pushing any other branch. Never use an unqualified force push.
- Never send email or chat on anyone's behalf, and never move secrets or
  money as part of modernizing.
- Post no PR comment unless the user asked for one; replies follow
  `gh-address-comment`.

## Establish the intent

Record the PR or branch URL, state, base, head repository and branch, head
SHA, author, checks, and review state. Read the title, body, linked issues,
commits, review threads, and the complete diff. State the smallest coherent
goal the change was trying to achieve before judging its implementation. Use
the actual base branch and record the merge base.

## Check what changed around it

Inspect commits added to the base since the branch diverged. Search merged
and open PRs when titles, paths, or behaviour suggest a replacement.

- Has the same problem already been solved?
- Did APIs, types, schemas, dependencies, or architectural boundaries change?
- Do both sides now claim the same behaviour or invariant?
- Was the code being changed deleted, moved, or intentionally simplified?
- Would landing it restore old behaviour or create two ways to do one thing?
- Is the original benefit still worth its maintenance cost?

Git reporting no conflicts does not make a change current.

## Choose a disposition before pushing

- **UPDATE:** the goal and implementation still fit. Merge the base into the
  branch; rebase only a short branch that nobody else has pushed to and with
  no open threads anchored to it.
- **RECUT:** the goal still fits but the branch is long-conflicted or carries
  stale commits. Re-apply the minimal change on a fresh branch from the
  current base and open a new PR whose body says `Supersedes #N`. The user
  decides whether the old PR is closed.
- **REWORK:** the goal still fits but a mechanical update would preserve the
  wrong implementation. Explain the smallest credible rewrite and stop before
  pushing unless the user also asked for that rework. Use `create-plan` when
  the rewrite is consequential.
- **CLOSE:** superseded, obsolete, directionally wrong, or no longer worth
  its cost. Cite concrete evidence and stop. Do not update an obsolete
  branch, and do not close it without explicit permission.

Be willing to recommend CLOSE. Age alone is not evidence, and sunk effort is
not a reason to keep a PR alive.

## Update without losing intent

For UPDATE or RECUT:

1. Create a safe local branch or disposable worktree at the recorded head
   (UPDATE) or at the fresh base (RECUT).
2. Merge or rebase the base, or re-apply the minimal change.
3. Resolve each conflict by the change's intent and the base's newer
   invariants. A conflict that reveals a design disagreement reopens the
   disposition; do not guess.
4. Inspect the final diff against the base; after a rebase, also compare the
   series with `git range-diff`.
5. Run the focused checks for the touched area. Use `verification-contract`
   when claiming a workflow works. Run `code-review` before pushing
   behavioural changes when the CLI is available and the diff is safe to
   send.
6. Push normally after a merge. After a rebase, push with
   `--force-with-lease=<branch>:<observed-sha>`; if the lease fails, fetch
   and reassess. File a RECUT PR with `gh-pr-create`.

Do not merge.

## Report

Lead with UPDATE, RECUT, REWORK, or CLOSE and the reason. Then: meaningful
base changes; conceptual conflicts or confirmation that none were found; the
update and push result; checks run and their results; and the remaining
decision with the PR links. Separate observed facts from judgement and say
what could not be verified.
