---
name: gh-release-notes-writer
description: Use when the user says "cut a release", "release notes", "tag a new version", "publish a release", "prepare a release". NOT for opening pull requests — that is gh-pr-create.
---

# Release Notes Writer

GitHub Releases (`gh release`). Origin is out of scope for this plugin; use
this `gh-release-notes-writer` skill on GitHub only.

## Execution Backend

1. Verify `git` with `git --version` and `gh` with `gh auth status`.
2. Run the bundled scripts and plain `git`/`gh` workflow below.
3. If either verification fails, STOP and report the failed check. For a `gh`
   failure, report verbatim: "`gh` is missing or unauthenticated. Install it if
   needed, run `gh auth login`, then retry."

Generate professional release notes by scanning git history, then create and publish GitHub releases.

## Versioning Scheme

Supported formats:
- `vMAJOR.MINOR`
- `vMAJOR.MINOR.PATCH`

Default selection:
- Start with `vMAJOR.MINOR`.
- If existing repo tags already use patch-level versions, continue with `vMAJOR.MINOR.PATCH`.
- Only move to patch-level tagging when the repo already follows it or the user explicitly requests it.
- Deterministic override: pass `--tag-scheme major|minor|patch` (or set `RELEASE_TAG_SCHEME`) to force the scheme.
- Convenience override: pass `--prefer-patch-level` to prefer `patch` when no explicit scheme is set.

Decision function used by `scripts/gather_changes.sh`:
- `determine_tag_scheme(base_tag, explicit_scheme, prefer_patch_level)` returns `explicit_scheme` first.
- If no explicit scheme is set, it infers from existing tags (`vX.Y.Z` -> `patch`, otherwise `minor`).
- If no prior tags exist, it still returns deterministically: `patch` when explicitly requested (or when `--prefer-patch-level` is set), otherwise `minor`.

If the repo already uses `vMAJOR.MINOR` with MINOR in `{0,5}`, preserve that pattern unless the user asks to move to patch-level tags.

| Version | Meaning |
|---------|---------|
| vX.0 | Major milestone or breaking changes |
| vX.5 | Mid-cycle feature release (when using the 0/5 scheme) |
| vX.Y.Z | Patch-level releases (bug fixes, small improvements) |

Progression (0/5 scheme): v1.0 → v1.5 → v2.0 → v2.5 → ...
Progression (patch scheme): v1.0.0 → v1.0.1 → v1.1.0 → v2.0.0 → ...

## Workflow

### 1. Prerequisites Check

```bash
scripts/check_prerequisites.sh
```

Verifies: gh authenticated, git repo clean, on a branch.

### 2. Gather Release Context

```bash
scripts/gather_changes.sh [last-tag] [--tag-scheme major|minor|patch] [--prefer-patch-level]
```

Returns: commits since last tag, changed files, suggested next version.
> Note: `gather_changes.sh` uses read-only `git` commands — no bot identity needed.

If no previous tags exist, gathers all commits and uses the flag/option to control first suggested version: `v1.0` for `major|minor`, `v1.0.0` for `patch`.

### 3. Generate Release Notes

Analyze the gathered changes and write notes following this structure:

```markdown
## What's New

[2-3 sentence thematic summary]

### ✨ Features
- Feature descriptions (user-facing impact)

### 🔧 Improvements  
- Enhancement descriptions

### 🐛 Bug Fixes
- Fix descriptions (if applicable)

### ⚠️ Breaking Changes
- Breaking change descriptions (major releases only)

---
**Full Changelog**: <previous-tag>...<new-tag>
```

Guidelines:
- Lead with user impact, not implementation details
- Group related changes
- Omit empty sections
- Use present tense ("Adds..." not "Added...")

### 4. Confirm the release

Prepare the version, notes, destination repository and exact commit locally.
Confirm authority before creating a remote tag, draft, or published release.
Use the repository's tag workflow for a new tag and verify the remote tag
before proceeding. Keep any existing tag on its current commit.

### 5. Create and read back the draft

```bash
scripts/create_release.sh <owner/repo> <version> <notes-file> <commit-sha>
```

The helper requires an existing tag at the approved commit, creates a draft,
and verifies the draft and tag. It supports lightweight tags and annotated
tags pointing directly to a commit. If an API read or verification fails,
inspect the remote draft and tag before retrying.

Publishing is a separate operation. Read back the approved draft, tag and
commit, and publish only with authority for that release. Verify the live
release and tag afterward. For an authorised publication, use
`gh release edit <tag> --repo github.com/<owner/repo> --draft=false`, then confirm
`isDraft` is false and the tag still resolves to the approved commit.

## Error recovery

| Error | Resolution |
|---|---|
| Tag missing | Use the repository's tag workflow after approval. |
| Tag points somewhere else | Confirm the intended version and commit. Preserve the existing tag. |
| GitHub CLI unauthenticated | Check `gh auth status` for the target host. |
| Uncertain remote state | Read back before retrying. |
