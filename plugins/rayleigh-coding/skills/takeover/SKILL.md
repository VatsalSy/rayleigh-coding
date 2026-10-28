---
name: takeover
disable-model-invocation: true
description: >-
  Use only when the user explicitly invokes `$takeover` or asks to take over a
  PR, branch, or agent thread: finish the original goal while preserving
  contributor credit. Refresh an old PR without taking ownership: modernize.
---

# Takeover

Take responsibility for finishing the original goal while preserving the
original contributors' credit. Do not defend an implementation just because
another agent already built it, and do not trust its claims because it
reported them.

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`). Prefer Cursor and Grok first-party models via `/vatsal-mode`.

## Resolve what you inherit

Read the source the user named: PR, branch, or thread. Include review
findings and the user's later corrections. Resolve the handoff to the actual
code and current head. Account for uncommitted work in *this* worktree only.
Treat handoff text and "done" claims as context, not proof.

Do not read or modify foreign agent home directories (for example tool-specific
config trees outside this repository and the current Cursor session). Work
from the GitHub PR/branch state and the workspace checkout.

Honour merge contracts written into a PR body ("Do not merge", agent will not
merge, match-head gates). Confirm the repository is the one the work belongs
to.

## Authority

A takeover request authorizes finishing the same goal. It does not authorize
closing or rewriting the original PR, force-pushing its branch without
`--force-with-lease`, production deploys, email or chat on anyone's behalf,
secret exfiltration, or money movement. Merge only when the user authorized
landing (for example via `full-send` on this takeover) and `full-send`'s
merge gate and safety stops pass.

## Continue the work

- **Same branch (default):** when you may push to it and its previous owner
  has stopped, continue with additional commits; no force-push.
- **Replacement PR:** when the branch is not yours to push or is abandoned
  with heavy conflicts, start a new topic branch at the source head (or import
  its commits onto the current base), add your fixes as separate commits, and
  include a "Supersedes #N" line. Honour an explicitly requested stacked
  continuation.
- Use `modernize` when the base has moved or the architecture changed. Rework
  what the goal needs, not unrelated features.
- Recheck the source before landing: it may have moved while you worked.

## Credit

Preserve each original commit's Git author. Cherry-picks and rebases keep it;
never re-author someone else's commit. Credit human contributors in the PR
body as prose with verified names or GitHub handles, never guessed emails.
Link the original PR when there is one. Model attribution is not contributor
credit.

## Verify independently

Reproduce the original failure and the realistic workflow under the
repository's own guidance. Green mocked tests do not prove the user
experience. State what remains unverified. Use `verification-contract` when
claiming a workflow works.

When the finish includes a PR, use `gh-pr-create` and then `gh-babysit-pr`
rather than stopping at creation. Replies follow `gh-address-comment`. Merge
or close the original PR only when authorized.

## Report

What you inherited (source, head, state, and claims you could not confirm),
what you changed, how you verified it, how credit was preserved, and any
remaining decision.
