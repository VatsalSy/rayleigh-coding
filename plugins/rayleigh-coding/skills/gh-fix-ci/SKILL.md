---
name: "gh-fix-ci"
description: "Use when the user says \"fix CI\", \"the checks are failing\", \"make the PR green\", \"fix the lint failure\" on a GitHub Actions check. NOT for open review threads — that is gh-address-comment."
---


# Gh Pr Checks Plan Fix

GitHub Actions only. If the session workshop is Origin, wait until the GitHub mirror has
fast-forwarded GitHub `main` and then run this on the GitHub side. Do not treat
Origin as having Actions. Origin review is `origin-babysit-pr`.

## Execution Backend

1. Verify `git` with `git --version` and `gh` with `gh auth status` (repo +
   workflow scopes).
2. Run `inspect_pr_checks.py`, which calls plain `gh`, as documented below.
3. If either verification fails, STOP and report the failed check. For a `gh`
   failure, report verbatim: "`gh` is missing or unauthenticated. Install it if
   needed, run `gh auth login`, then retry."

## Overview

Use gh to locate failing PR checks, fetch GitHub Actions logs for actionable failures, summarize the failure snippet, then implement the smallest safe fix set and recheck.
- Fast path: for formatter/lint-only failures, skip broad planning and apply the minimum fix set needed to make checks green.
- If fixes are behavioral/risky (beyond formatter/lint churn), use a plan-oriented skill (for example `create-plan`) or draft a concise plan inline before major edits.

Prereq: authenticate with `gh auth login` once, then confirm with `gh auth status` (repo + workflow scopes are typically required).

## Inputs

- `repo`: path inside the repo (default `.`)
- `pr`: PR number or URL (optional; defaults to current branch PR)
- `gh` authentication for the repo host

## Quick start

- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
- Add `--json` if you want machine-friendly output for summarization.

## Workflow

1. Verify gh authentication.
   - Run `gh auth status` in the repo.
   - If unauthenticated, run `gh auth login` (ensuring repo + workflow scopes) before proceeding.
2. Resolve the PR.
   - Prefer the current branch PR: `gh pr view --json number,url`.
   - If the user provides a PR number or URL, use that directly.
3. Inspect failing checks (GitHub Actions only).
   - Preferred: run the bundled script (handles gh field drift and job-log fallbacks):
     - `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
     - Add `--json` for machine-friendly output.
   - Manual fallback:
     - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
       - If a field is rejected, rerun with the available fields reported by `gh`.
     - For each failing check, extract the run id from `detailsUrl` and run:
       - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
       - `gh run view <run_id> --log`
     - If the run log says it is still in progress, fetch job logs directly:
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`
   - **Freshness first:** only act on check runs for the PR's latest head SHA — a red check on a superseded commit is history, not a task. If the branch has fallen behind `main` and failures stem from base drift (checks pass locally against the branch but fail against merged `main`), rebase/merge and re-push before "fixing" anything.
   - **Flake triage — distinguish repository failures from infrastructure flakes before fixing anything.** Infrastructure signatures: runner lost/cancelled, network timeouts fetching dependencies, package-registry or apt-mirror errors, ordinary Actions rate limits, artifact upload failures, out-of-disk on the runner. For these, re-run the check (`gh run rerun <run_id> --failed`) instead of writing a "fix" — a fix commit for a flake is noise that pollutes history and retriggers the whole review cycle. CodeRabbit's `Review rate limited` check is not an Actions flake and must never be rerun with `gh run rerun`; follow the review-capacity flow below.
   - Classify genuine repository failures:
     - Formatter/lint only (for example markdownlint, Prettier, ESLint/style checks)
     - Test/build/runtime failures
4. Scope non-GitHub Actions checks.
   - If `detailsUrl` is not a GitHub Actions run, label it as external and only report the URL.
   - Do not attempt Buildkite or other providers; keep the workflow lean.
   - **Exception — CodeRabbit:** a CodeRabbit check or pending review is not
     fixable CI. A passing `Review rate limited` check means no review ran.
     Route the exact missed head SHA to `autofix`, which owns the bounded
     exact-head guarded fallback. Never query capacity, request another review,
     rerun it as CI, or use a no-op push (policy: `CONVENTIONS.md` "Code review
     before push and merge").
5. Summarize failures for the user.
   - Provide the failing check name, run URL (if any), and a concise log snippet.
   - Call out missing logs explicitly.
6. Implement with minimum-diff strategy.
   - Formatter/lint-only failures: apply only directly related formatting/lint fixes; avoid opportunistic refactors.
   - Mixed failures: handle formatter/lint fixes first, then address functional failures.
   - Batch all genuine CI fixes before the next push so one coherent range gets
     the next automatic CodeRabbit review.
   - For risky or architecture-impacting changes, align with the user before proceeding.
7. Recheck status.
   - Re-run the narrowest local checks first, then verify with `gh pr checks` on the PR.
   - Report exactly which checks moved from failing to passing.


## Gotchas

1. **GitHub Actions field names drift between API versions** -- `gh pr checks --json ...` field list changes without notice. If a field is rejected, re-run with only the fields the API reports as available. The bundled `inspect_pr_checks.py` handles this; prefer it over manual gh calls.
2. **CI check names change when workflows are renamed** -- a check that was `markdownlint` last week may now be `Lint / markdownlint`. Always resolve check names dynamically from the PR checks API; never hardcode expected check names.
3. **External CI (Buildkite, CircleCI) is out of scope** -- if `detailsUrl` points to a non-GitHub host, report only the URL and stop. Attempting to interpret external CI logs leads to wrong diagnosis.
4. **Formatter-only fix scope discipline** -- when fixing lint/formatter failures, touch only the failing files. Opportunistic refactors mixed into a 'CI fix' commit obscure the actual change and make revert painful. CI repair must never expand the PR beyond its original goal.
5. **A flake "fixed" with a code change is a false diagnosis** -- if a re-run turns a failure green with no code change, it was infrastructure. Report it as a flake; do not invent a repository cause to justify a commit.

## After CI is green — PR review comments

Green Actions alone do not clear the PR for merge. First check CodeRabbit
state (repos with the App installed):

- If its review has not posted yet, or a comment matches "Come back again in a
  few minutes" (in-progress probe — see `autofix` Step 3), wait; do not
  merge or report the PR as ready.
- If the current head has a passing `Review rate limited` check, no review ran;
  route to `autofix`'s bounded exact-head guarded fallback before declaring
  merge-ready.
- CodeRabbit-authored threads → handle via `autofix`.
- Human reviewer threads → handle via `gh-address-comment`.
- No CodeRabbit activity ~10 min after last push → status unknown, not proof
  that the App is absent. Keep the review gate blocked until explicit
  installation or review-status evidence confirms it is not enabled; report
  queue, webhook, configuration, permission, or rate-limit uncertainty.

If open review threads exist on the PR after CI passes, **do not inline-implement comment addressing**.
Load `gh-address-comment` explicitly:

```
Skill: <skills-dir>/gh-address-comment/SKILL.md
Trigger: before starting any code changes to address reviewer feedback
```

Ops workers / Savart: load `gh-address-comment` before starting code changes. Do NOT re-implement git checkout + edit + commit logic inline.

## Bundled Resources

### scripts/inspect_pr_checks.py

Fetch failing PR checks, pull GitHub Actions logs, and extract a failure snippet. Exits non-zero when failures remain so it can be used in automation.

Usage examples:
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40`
