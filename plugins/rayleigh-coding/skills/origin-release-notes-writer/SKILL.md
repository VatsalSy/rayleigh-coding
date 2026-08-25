---
name: origin-release-notes-writer
description: >
  Use when the session workshop is Origin and the user says "cut a release",
  "release notes", or "tag a new version" for a repo whose merge happened on
  Origin. GitHub Releases (`gh release`) stay gh-release-notes-writer after
  GitHub main has the tag.
---

# Origin release notes

Draft notes from git history on the Origin-merged `main`, tag annotated
tag with the global git identity, and push the tag to `origin.cursor.com`.

GitHub Releases and changelog CI run only after GitHub `main` (and tags)
are fast-forwarded. Then hand off to `gh-release-notes-writer` if a GitHub
Release object is required.

Do not run CodeRabbit as part of cutting the Origin tag.

## Gotchas

1. Origin has no GitHub Release API. `gh release create` is GitHub-workshop
   work after the fast-forward.
2. Never squash-merge to manufacture a single release commit.
