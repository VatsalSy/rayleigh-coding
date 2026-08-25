---
name: origin-code-review
description: >
  Use when the session workshop is Origin and the user says "review this PR",
  "check the Bugbot review", or "review my Origin change". GitHub CodeRabbit
  CLI review is code-review. Bugbot has no review CLI — do not invent one.
---

# Origin code review

On Origin, review means **wait for Cursor Bugbot comments on the open
Origin change**, then read them. Bugbot has **no review CLI**. Do not run
`coderabbit`, do not invent `bugbot review`, and do not treat `origin-code-review`
as a local scanner.

1. Confirm Origin workshop. If GitHub, use `code-review` (CodeRabbit CLI).
2. Ensure the branch is pushed to `origin.cursor.com` and the change is
   **open** (`origin pr ready` if it is still draft). Drafts often get no
   Bugbot comments.
3. Run `origin pr checks <change> --watch`, then require its JSON row to have
   `status: completed` and `conclusion: neutral|success` for the exact latest
   head. Then read full comments with
   `origin pr view --checks --comments` and
   `origin pr thread list --comments` — those are Origin PR commands, not a
   Bugbot review tool. A generated PR summary is not a completed review.
4. Triage with `origin-pr-triage`, fix with `origin-address-comment`.
5. Do not run `coderabbit`, `autofix`, or `coderabbit-config`.

## Gotchas

1. There is no Bugbot equivalent of the CodeRabbit CLI. Local CodeRabbit on
   an Origin branch still phones CodeRabbit's GitHub org routing — skip it.
2. A successful current-head Bugbot check with no finding threads is a clean
   pass; it does not need a synthetic comment. A missing or still-running
   check is not approval.
