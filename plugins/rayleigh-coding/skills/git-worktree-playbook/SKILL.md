---
name: git-worktree-playbook
description: Use when creating, inspecting, troubleshooting, or removing isolated Git worktrees for branches or parallel tasks.
---

# Git worktrees

Run `git worktree list --porcelain` and inspect status in the relevant checkout.
Confirm the intended base, the destination path, and whether work needs its own
branch. Use the harness's native worktree option when the harness must bind a
session to that checkout. Creating a shell worktree alone leaves the session
bound to its current workspace.

```sh
git worktree add -b <branch> <path> <base>
git worktree add <path> <existing-branch>
git worktree add --detach <path> <commit>
git -C <path> status --short --branch
```

A branch normally has one checkout. If occupied, use the existing checkout
with its owner's agreement, or select a fresh branch or detached commit.
Check the new worktree's root, branch and exact base before writing. Workers
report their commits or patches. The integration owner brings each result
into the target branch and verifies it before starting dependent work.

Before cleanup, verify that tracked and untracked work is safely integrated
or saved, and that the worktree is no longer used by another session. Use
`git worktree remove <path>` and verify with `git worktree list`. Remove the
branch separately only when authorised. For stale registrations, inspect
`git worktree prune --dry-run`; use `git worktree repair` for a moved worktree.
Avoid forced removal as a recovery shortcut.
