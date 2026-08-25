---
name: origin-pr-checkout
description: >
  Use when the session workshop is Origin and the user shares an
  origin.cursor.com pull URL, an Origin change number, or says "check out
  this Origin PR". GitHub Raycast extension PRs remain raycast-pr-checkout.
---

# Origin PR checkout

```bash
origin auth status
origin pr checkout <n-or-url>
```

Use the `origin.cursor.com` remote. Do not fetch GitHub `pull/*/head` for
Origin changes.

Leave the worktree on the change branch. Do not push that branch to GitHub.

## Gotchas

1. `raycast-pr-checkout` is a GitHub sparse-checkout for
   `raycast/extensions`. It is not an Origin twin.
2. If `git remote -v` has no `origin.cursor.com` URL, add it from D1
   `origin_remote` before checkout.
