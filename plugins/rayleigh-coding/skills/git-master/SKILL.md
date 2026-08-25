---
name: git-master
description: >-
  Trigger on git/branch/PR workshop questions for coding agents — branch
  hygiene, commits, remotes, GitHub (`gh`) or Cursor Origin (`origin`) PRs,
  merges, and CI. Not for architecture review or security threat modeling.
---

# Git Master

Local git plus the active workshop CLI. Choose the workshop from the
**remote URL host**, never from the machine hostname or a remote's git name.

## Choose the workshop

```bash
git remote -v
```

| Host in URL | Workshop | CLI |
| --- | --- | --- |
| `github.com` | GitHub | `gh` + `git` |
| `origin.cursor.com` | Cursor Origin | `origin` + `git` |

- A remote named `origin` is only a label. Resolve by host.
- If both hosts exist, pick one workshop for the task and push the feature
  branch to that side only. Ask the user when unclear.
- Never infer workshop from machine name, profile, or local path.

## Execution checks

1. `git --version`
2. GitHub: `gh auth status`. On failure: "`gh` is missing or unauthenticated.
   Install it if needed, run `gh auth login`, then retry."
3. Origin: `origin auth status`. On failure: "`origin` is missing or
   unauthenticated. Install or run `origin auth login`, then retry."
4. Read-only inspection needs no auth check.

An `origin` install helper does not choose the workshop.

## Merge policy

- Prefer **merge commits**. Never squash unless the user asks.
- GitHub: `gh pr merge --merge` (not `--squash`).
- Origin: `origin pr merge -m` only. Never `origin pr merge -s`.
- Never force-push or amend pushed history unless the user asks. Prefer
  `--force-with-lease` when a force is required.
- Never rebase `main` / `master`.

## Core git rules

- Prefer several focused commits over one large commit.
- Match recent commit message style in the repo.
- Use this machine's configured `user.name` / `user.email`. Do not override
  with `git -c` by workshop.
- No `Co-authored-by` trailers, bot authors, or AI-tool signatures. After
  commit, `git log -1 --format=%B` must not contain
  `Co-authored-by: Cursor <cursoragent@cursor.com>`. Amend it out of an
  unpushed commit from this turn if Cursor injected it.
- Default base branch is `main`. Override only when the user names another.

## Preflight

```bash
git status --short
git branch --show-current
git log -20 --oneline
```

## Commits

1. Inspect: `git diff --stat`, `git status --short`
2. Group by concern; commit each group separately
3. Verify: `git status --short`, `git log -1 --oneline`

```bash
git add -p   # or path-scoped adds
git commit -m "message"
```

## Branches and PRs

### Feature branch

```bash
git fetch <remote>
git checkout -b <branch> <remote>/main
# ... commits ...
git push -u <remote> HEAD
```

`<remote>` is the remote whose URL host matches the chosen workshop.

### GitHub workshop (`gh`)

```bash
gh pr create --base main --title "..." --body "$(cat <<'EOF'
## Summary
- ...

## Changes
- ...

## Testing
- ...
EOF
)"
gh pr view --json url,state,statusCheckRollup
gh pr checks <pr>
gh pr merge <pr> --merge
```

Open a GitHub PR when the user asks, or when direct delivery to `main` is
not appropriate. Fork-first for public repos without collaborator access;
work in-repo when the user has access (`OWNER/repo`).

```bash
gh pr list
gh pr view <n>
gh run list --limit 10
gh api repos/OWNER/REPO/pulls/<n> --jq '.title,.state'
```

Deeper GitHub flows: `gh-pr-create`, `gh-pr-triage`, `gh-address-comment`,
`gh-babysit-pr`, `gh-fix-ci`.

### Origin workshop (`origin`)

Work only against the `origin.cursor.com` remote. Prefer an open change for
review rather than pushing Origin `main` directly.

```bash
origin pr create --status open --push --fill --remote <origin-cursor-remote>
origin pr checks --watch
origin pr view --checks --comments
origin pr thread list --comments
origin pr merge -m
```

Pass `--remote` when the git remote named `origin` points at GitHub.
`origin pr create` may default to draft; use `--status open` unless the user
asked for draft.

Deeper Origin flows: `origin-pr-create`, `origin-pr-triage`,
`origin-address-comment`, `origin-babysit-pr`, `origin-code-review`.

### After opening a PR

Return the primary checkout to `main` unless the user wants to keep working
on the branch: `git checkout main`.

## Review and CI (light)

- Verify each bot finding against source before editing. Decline invalid or
  out-of-scope comments with a short reason.
- Act on checks and comments for the **latest head** only. Refresh from
  `main` when base drift is material.
- Prefer smallest safe fixes. Do not expand the PR beyond the user's goal.
- CI flakes (runner loss, timeouts, registry errors): re-run failed jobs
  before a "fix" commit (`gh run rerun <run_id> --failed`).
- Before calling done, re-fetch live unresolved-thread and check counts.

Helper scripts (GitHub-oriented):

```bash
python3 <skills-dir>/git-master/scripts/extract_pr_comments.py <PR>
python3 <skills-dir>/git-master/scripts/fetch_comments.py
python3 <skills-dir>/git-master/scripts/inspect_pr_checks.py --repo . --pr <n>
```

## Worktrees

For parallel checkouts, linked trees, cleanup, or `.worktrees`, use
`git-worktree-playbook`. Do not duplicate that playbook here.

## Safe history cleanup

- Interactive rebase / autosquash on **feature branches only**.
- If already pushed, warn before `--force-with-lease`.
- Never rewrite shared `main` / `master`.

## Gotchas

1. Remote name `origin` ≠ Cursor Origin. Always read the URL host.
2. Squash merges rewrite history and authorship; use merge commits unless
   the user asks otherwise.
3. After `pr create`, check out `main` so later work starts clean.
4. Permission failures: stop and report the exact error to the user.

## Output expectations

1. Workshop chosen (GitHub vs Origin) and how (remote host)
2. Commands run
3. What changed (branches / commits / PR links)
4. Remaining blockers and next action
