---
name: sol-loop
disable-model-invocation: true
description: >-
  Use only when the user explicitly invokes `$sol-loop` or says "sol loop":
  review a change in a bounded CodeRabbit + wise-owl loop until findings are
  settled. One-off review without the loop: code-review.
---

# Sol Loop

Make a change more correct before (or sometimes after) filing a pull request
by reviewing it in a short loop. Make the smallest changes that satisfy real
findings. Resist scope creep and push back with evidence.

The name keeps parity with upstream tstack. In this plugin the reviewers are
**CodeRabbit** (via `code-review`) and at most one read-only **wise-owl**
consult (Cursor Grok, high effort). Do not call third-party model families
for this loop. Prefer Cursor and Grok first-party models via `/vatsal-mode`.

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`).

## Reviewers

1. **CodeRabbit** through `code-review` / the CodeRabbit CLI wrapper. Inspect
   the outgoing diff first and skip the CLI if it would transmit secrets or
   unpublished sensitive material.
2. **wise-owl** (optional, once): only when an independent view could change a
   consequential decision after CodeRabbit returns. Read-only. The parent
   keeps tools, edits, and verification.

If CodeRabbit is unavailable, say so, run repository tests plus independent
inspection, and continue with a single wise-owl consult only when the claim
is consequential. Do not invent another review backend.

## Budget

- Default: 3 rounds. Round 1 is full. Later rounds check only changed code
  and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency while a blocker remains with evidence, or when the user
  asks.
- Stop early if a round returns only nits. Declined nits and comment, doc, or
  format-only fixes need no new round.
- Keep a ledger: id, severity, outcome. Never guess it from memory.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths when they separate cleanly;
otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Confirm `HEAD` matches
  the PR head (or is ahead only by this change). Base:
  `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`.

State intent and out-of-scope in one or two sentences. Run covering checks.
Do not send code this change breaks.

## 2. Round 1

Run `code-review` against the scoped base. Treat findings as:

- **blocker / Critical:** the intended case is wrong.
- **should / Warning:** a real bug callers will hit within the intent.
- **nit / Info:** other paths, rare cases, small costs, extra compatibility,
  or guards the intent does not need.

Do not edit scoped files while the review runs. A timeout, error, or empty
reply is not approval.

## 3. Answer findings

Check each finding against the source yourself.

- **Agree:** smallest fix. Prefer delete or narrow over new helpers. Add one
  focused test that fails without the fix when the intent needs it.
- **Disagree:** say why with evidence (file:line, test, output).
- **Out of scope or nit:** decline in one line; list as follow-up.

Optional: one wise-owl consult on a contested consequential finding. Do not
start a second consult without materially new evidence.

Re-run checks. If review grew the diff, cut it back first.

## 4. Next round

Start another CodeRabbit pass only while budget remains and a blocker or
should is open, behaviour code changed, or the last approval does not cover
the current behaviour diff. Send the ledger (`fixed` / `disagree` /
`declined` + evidence) with the same base.

## 5. Stop

**Agreed:** no open blocker or should, and no concern of your own on the
current behaviour diff. **Stuck:** an item stays disputed after two replies,
or the budget ends. Show both sides briefly; the user decides. Budget end is
not approval.

Do not push during the loop. Push afterwards only when the user asked to
push, ship, update the PR, or the loop runs inside `full-send` / `full-stop`.

Report: rounds, what changed, diff size before/after, fixed and declined
findings with reasons, and whether anything was pushed.
