---
name: origin-pr-create
description: >
  Use when the session workshop is Origin and the user says "create PR", "open
  PR", "make a pull request", or "origin-pr-create". GitHub-workshop PRs are
  gh-pr-create. In an Origin-selected detached workshop a PR is mandatory;
  never push Origin main directly.
---

# Origin PR Creator

Open a change on Cursor Origin (`origin.cursor.com`) with the `origin` CLI.
Reviewer is **Cursor Bugbot**, never CodeRabbit. Bugbot has no review CLI;
it comments on the open change. Do not run `autofix`, `coderabbit-config`,
or `code-review`.

An Origin-selected Category B change always uses this PR path, even when the
user merely said to implement or update something. “PR only when explicitly
requested” applies to GitHub workshops, not Origin workshops.

## Execution

1. Confirm workshop is Origin (`git-master` workshop contract). If GitHub,
   stop and use `gh-pr-create`.
2. `git --version` and `origin auth status`. If Origin auth fails: "`origin`
   is missing or unauthenticated. Install or run `origin auth login`, then
   retry."
3. Resolve the Origin remote by host `origin.cursor.com`, not by the git
   remote name `origin`. Push the feature branch only there.
4. Commits use this machine's global git identity. Do not switch author for Origin.
5. Create an **open** change (not draft unless asked):

```bash
origin pr create --status open --push --fill --remote <origin-cursor-remote>
```

6. Use `origin-babysit-pr`: require `origin pr checks --watch` to complete the
   Cursor Bugbot review on the exact head, inspect full comments, and address
   every actionable finding. A generated summary is not a review receipt.
7. Merge later with `origin pr merge -m` only. Never `origin pr merge -s`.
8. After merge, fast-forward GitHub `main` only. Then GitHub Actions may run.

## Gotchas

1. `origin pr create` defaults to **draft**. Pass `--status open` or Bugbot
   may not review.
2. `--remote` defaults to git remote `origin`, which is often GitHub. Pass the
   `origin.cursor.com` remote explicitly.
3. Squash merge rewrites the author. Always `-m`.

## Public runtime contract

This skill does not call private project trackers or profile services.
