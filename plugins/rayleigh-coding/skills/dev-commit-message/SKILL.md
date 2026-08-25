---
name: dev-commit-message
description: >-
  Use when the user asks to draft a commit message, or explicitly to commit /
  stage / push. Drafting text alone must not mutate the repository.
---

# Commit Message Writer

## Modes

**Draft-only (default for phrasing like "write a commit message", "suggest a
commit message", "what should the commit say"):**

1. Inspect `git status` / `git diff` (and `git log --oneline -5` for style).
2. Propose subject (+ optional body) in the reply.
3. Do not mutate the repository.

**Mutating — execute only the operations the user explicitly named:**

| User said | Allowed actions |
|---|---|
| `stage` only | `git add` / pathspec staging only |
| `commit` (and optionally stage) | stage in-scope files if needed, then `git commit` — do **not** push |
| `push` | push only after an existing clean commit; do not stage/commit unless also asked |

Never chain an unrequested mutation. "Commit" does not imply push. "Stage"
does not imply commit.

When committing:

1. Assess state: `git status --porcelain`, `git diff --cached --stat`
2. Match style: `git log --oneline -5`
3. Stage only files in scope; honour exclusions; split unrelated changes
4. Optional CodeRabbit pass via `code-review` when shipping behavioural code on
   a GitHub workshop and the CLI is available — inspect the outgoing diff first
   and skip the review if it would send secrets or clearly unpublished material
5. `git commit -m "…"`; never AI trailers / `--trailer`
6. Re-check `git status --porcelain`

## Exclusions

Never stage `.comphy/`. Prefer pathspecs such as
`git add --all -- ':!.comphy'`.

## Message standards

- Subject: imperative, <72 chars
- Body (optional): what/why, not how
- No AI signatures or `Co-authored-by` trailers from tools

## Scope

This skill drafts and (when asked) stages/commits/pushes only as authorised.
It does not run project profile updates or other workshop bookkeeping.

## Gotchas

1. "Write a commit message" ≠ permission to commit.
2. Author is the machine global `user.name` / `user.email`.
3. Dirty tree after commit: always re-status.
