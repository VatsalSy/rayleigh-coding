---
name: dev-commit-message
description: Use when committing or staging code changes, or when the user says "commit", "save changes", "push", or "write a commit message".
---

# Commit Message Writer

## Workflow

Use plain `git` for commit/push operations. If the repo's global identity is
wrong, set `user.name` and `user.email` on the commit command instead of
relying on wrappers:

1. **Assess state**: Run `git status --porcelain` and `git diff --cached --stat`
2. **Check style**: Run `git log --oneline -5` to match repository conventions
3. **Group changes**: Stage related files together; split unrelated changes into separate commits (see Exclusions below)
   - Scope guard: stage and commit only files relevant to the current run scope; avoid unrelated dirty files unless user explicitly requests it.
   - If the user says “commit all” but also requests exclusions (for example, “do not commit PLAN.md”), honor the exclusions and confirm what will be left out.
   - If the user says “commit all” and “do it granularly,” create multiple logical commits and summarize the planned grouping before committing if the grouping is ambiguous.
   - For the default direct-to-main route, fetch `origin/main`, verify
     `git branch --show-current` is `main`, and require local `HEAD` to equal
     the fetched `origin/main` before the review and commit. Stop on mismatch
     until it is safely reconciled.
4. **CodeRabbit pass (GitHub-workshop code and behavioural-skill pushes only)**:
   skip this step on Origin workshop. Bugbot has no review CLI; after each
   push to an open Origin change, wait for its comments rather than running
   a local review.
   When the workshop is GitHub, the commit will be pushed and the staged
   diff is code or behavioural skill
   instructions (source/scripts/CI/infrastructure tooling or `SKILL.md` runtime
   contracts — not ordinary prose, vault notes, generated artefacts, or context-git
   context repos), run the
   repository-aware `code-review` guard once on the coherent outgoing diff
   with `--uncommitted`; add `--light` for small mechanical diffs. Run it only
   from an isolated worktree or after
   proving every tracked staged and unstaged edit belongs to the intended
   commit; otherwise it can expose unrelated user changes. The guard reuses
   only a receipt matching repository, required organisation and visibility,
   scope/base, exact diff, effective config/instruction digests, and CLI
   version. This permits the verified public OSS route without inventing paid
   attribution. Fix or note
   Critical/Warning findings before committing. Machine-written
   operational state (e.g. `comphy-fleet-reservation` reserve/release
   commits) is direct-to-main by design: run its repository validator, never a
   CodeRabbit ritual, and never route it through a PR. Skip entirely for
   commit-only sessions. If the CLI is absent, record the unavailable review
   and run repository tests plus independent inspection; do not silently claim
   the CodeRabbit gate passed
   (`CONVENTIONS.md` "Code review before push and merge").
5. **Write message**: Follow standards below
6. **Commit**: Use `git commit -m "message"`; for a multi-line body, repeat `-m` (e.g. `git commit -m "subject" -m "body"`). Never pass `--trailer`. Never add `Co-authored-by: Cursor <cursoragent@cursor.com>` or any AI/Cursor attribution. After commit, `git log -1 --format=%B` must be clean of those trailers. If Cursor still injected one and the commit is unpushed and created in this turn, amend it out. Do not rewrite published history.
7. **Push (if requested)**: Confirm target remote/branch, then push after a clean commit
   - For the user-owned repositories, default to a clean, synchronised local
     `main`, the bounded repository-aware CodeRabbit CLI review above, and a
     direct push to `origin main`.
   - Do not create a branch or pull request unless the user explicitly requests
     one, or local and remote `main` genuinely cannot be reconciled safely.
   - If `origin/main` moved, fetch and reconcile before pushing; re-run affected
     validation after every merge, rebase, fast-forward, conflict resolution,
     or other reconciliation. If reconciliation materially changes the
     reviewed diff, run the one permitted CodeRabbit follow-up on the new exact
     outgoing diff before pushing.
   - For an explicitly requested branch, verify it with
     `git branch --show-current`, then name that confirmed remote and branch in
     its first `git push -u`; use `git push` for subsequent pushes.
8. **Verify cleanliness**: Re-run `git status --porcelain` to confirm no staged/unstaged changes remain unless the user asked to leave some files out
9. **Tracker checkpoint** (see [Tracker checkpoint after commit](#tracker-checkpoint-after-commit)): resolve the project by walking to `project.yaml` and matching the repository's normalised remote, then fire `project-tracker update <slug>` with a commit-linked note. Skip only unprofiled workspace hygiene.

## Exclusions

Always exclude these paths when staging files, even if not in `.gitignore`:
- `.comphy/` - Never stage or commit files from this directory

When running `git add`, explicitly exclude these paths:
- Use `git add --all -- ':!.comphy'` instead of `git add -A`
- Or stage specific files individually, skipping excluded paths

User-specified exclusions:
- If the user names additional paths to exclude (for example, `PLAN.md`), use pathspec exclusions like `git add --all -- ':!.comphy' ':!PLAN.md'` or stage only the allowed files explicitly.
- If multiple exclusions are given, list them back to the user before committing to avoid accidental inclusion.

## Commit Message Standards

**Format**:
- Subject: imperative mood, <72 chars (e.g., "Add authentication middleware")
- Body (optional): explain *what* and *why*, not *how*

**Required**:
- Descriptive subjects that help future developers understand intent
- Match existing repository style

**Prohibited**:
- AI tool signatures, advertisements, or co-authored-by tags from AI tools
- Generic messages: "Update files", "Fix bug", "Changes"

## Examples

Good:
```
Add rate limiting to API endpoints

Prevents abuse from high-frequency requests.
Configurable via RATE_LIMIT_PER_MINUTE env var.
```

```
Fix null pointer in user lookup

UserService.find() returned null for deleted users,
causing crash in profile rendering.
```

Bad:
```
Fix stuff

🤖 Generated with Claude
Co-Authored-By: claude <noreply@anthropic.com>
```


## Gotchas

1. **Author is this machine's global `user.name` / `user.email`.** Use plain `git commit`. Do not override identity with `git -c user.name` / `user.email` for GitHub vs Origin. No AI-tool signatures, no `Co-authored-by` trailers (including `Co-authored-by: Cursor <cursoragent@cursor.com>`), no `--trailer`, no bot accounts. Cursor's Agent Attribution setting is off; still never pass a trailer, and the global `commit-msg` hook must strip any that leak through.
2. **`.comphy/` will sneak into `git add -A`** — never stage this directory; always use `':!.comphy'` pathspec exclusion or stage files explicitly.
3. **"Commit all + granularly" is ambiguous** — if the user says both, propose the commit grouping plan first and confirm before staging anything. Silent groupings cause audit pain.
4. **Dirty tree after push** — always re-run `git status --porcelain` after committing to verify no staged/unstaged leftovers; a partially staged commit silently breaks the next PR diff.

## Tracker checkpoint after commit

A commit is a natural checkpoint, so step 9 fires the `project-tracker` skill's `update` verb on the profile that owns the work. Rules:

**Resolve the slug from the workspace and remote.** Walk upward from the
committed checkout to `project.yaml`, then require the checkout's normalised
remote to match either `workspace.repository` or one `workspace.components`
record in the owning profile. For
an intentionally untracked path, use changed-file evidence only to decide
whether this is workspace hygiene; never guess a project from a warehouse
folder name.

**Skip the checkpoint entirely when:**
- The commit is pure component-repository hygiene with no profile-scoped
  content. Root context `.gitignore`, `AGENTS.md`, `project.yaml`, `README.md`,
  and `CLAUDE.md` are profile-scoped and must update the guarded mirror.
- The commit touches an Area component while the enclosing child manifest owns
  the work; checkpoint the child profile instead of the Area.
- No profiled project is a plausible owner.

**Note format** — preferred form:
- Single commit: `commit <short-sha> — <subject>` (truncate subject to ~160 chars).
- Multi-commit batch from one invocation: `checkpoint — N commits: <subject-1>; <subject-2>[; …]` capped at ~180 chars.
- Push-only (no new commit): `checkpoint — pushed HEAD (<short-sha>)`.

**How to invoke.** After the verify-cleanliness step, resolve the slug, then call `project-tracker update <slug> "<note>"`. The `update` verb persists the D1 profile (Focus pull, session log, revision bump). A checkpoint is still a profile write even though it does not change lifecycle status. Do not write `_TRACKER.md`.

**Independent repository boundaries are expected.** The enclosing
`project.yaml` assigns components to the owning tracker profile. The root is a
separate private context repository and component repositories remain ignored.
Context commits direct-push with `context-git sync`; they do not open GitHub PRs.

**Don't double-fire.** If the user explicitly wraps the session right after the commit ("that's it", "wrap up"), the `done` that fires next already covers the tracker write. Skip the commit-time `update` in that case.

## Multi-Commit Strategy

For large changesets:
1. Identify logical groupings (feature, refactor, tests, docs)
2. Stage and commit each group separately
3. Each commit should be atomic—buildable and testable on its own

## Additional Resources

- [examples-gallery.md](references/examples-gallery.md) - Expanded examples by commit type
