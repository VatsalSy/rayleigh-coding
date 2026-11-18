---
name: gh-pr-triage
description: Use when the user says "triage the PR", "analyze the PR feedback", "what did the reviews say", or right after opening/updating a PR to sort review bundles into must-fix vs decline. NOT for applying fixes — that is gh-address-comment.
---

# PR Triage

GitHub-workshop skill. Origin is out of scope for this plugin; use this
`gh-pr-triage` skill on GitHub only.

## Execution Backend

1. Verify `git` with `git --version` and `gh` with `gh auth status`.
2. Run `extract_pr_comments.py`, which calls plain `gh`, as documented below.
3. If either verification fails, STOP and report the failed check. For a `gh`
   failure, report verbatim: "`gh` is missing or unauthenticated. Install it if
   needed, run `gh auth login`, then retry."

Extract and analyze all PR comments to produce a prioritized action plan.

## Workflow

1. **Trigger timing** → Run right after PR open/update (or on demand) so feedback is triaged before ad-hoc fixes.
2. **Check CodeRabbit status.** Inspect available reviews and configured
   requirements. When the App is running, use the bounded window in
   `autofix`. At the cap, report missing review evidence and route through
   its fallback while preserving required gates. App installation cannot
   be inferred from silence.
3. **Freshness:** Reassess unresolved findings against current source, including those from before the latest push. A new head by itself gives no evidence the defect was fixed. Check material drift against the PR's actual base. Ask before closing an overlapping PR unless that closure was already authorised.
4. **Extract comments** → Run `<skills-dir>/gh-pr-triage/scripts/extract_pr_comments.py <PR_URL_or_NUMBER>`
5. **Verify before classifying** → For each bot finding you would mark P0/P1, read the flagged source lines first. CodeRabbit and other AI reviewers are helpful but not always right — a finding that doesn't survive inspection goes to "Decline with reason", not the fix queue.
6. **Analyze** → Categorize and prioritize each actionable comment
7. **Classify** → Split into:
   - `Must-fix before merge` (true blockers)
   - `Optional/defer` (nice-to-have, stylistic, or low impact)
   - `Decline with reason` (invalid after inspection, or out of scope — see below)
   **Anti-scope-creep is the governing rule:** review feedback must not expand the PR beyond the user's original goal. Suggestions to refactor adjacent code, add features, or generalise "while you're here" are classified `Decline with reason` no matter how sensible they sound. A PR that triples in size while being babysat is a failure even if every comment was "addressed".
8. **Output** → Generate action plan in the format below. Every declined item needs a one-line reason; the downstream skill (`autofix` for CodeRabbit threads, `gh-address-comment` for the rest) posts that reason on the thread and resolves it — declined threads are never silently ignored.

## Comment Categories

| Category | Description | Priority Hint |
|----------|-------------|---------------|
| Security | Auth, validation, encryption issues | P0 |
| Breaking | API changes, behavioral changes | P0 |
| Bug | Logic errors, edge cases | P1 |
| Performance | Efficiency, scaling concerns | P1 |
| Architecture | Design patterns, structure | P2 |
| Code Quality | Style, maintainability, DRY | P2 |
| Testing | Missing tests, coverage gaps | P2 |
| Documentation | Comments, naming, clarity | P3 |
| Nitpick | Style preferences, minor suggestions | P3 |

## Priority Levels

- **P0 (Critical)**: Must fix before merge. Security, breaking changes, major bugs.
- **P1 (High)**: Should fix. Performance issues, significant functionality problems.
- **P2 (Medium)**: Improve if time permits. Quality, maintainability.
- **P3 (Low)**: Nice to have. Style, minor optimizations.

## Output Format

```markdown
# PR Triage: [PR Title]

## Summary
- **Total comments**: X actionable (Y resolved)
- **Blockers**: N items require attention before merge
- **Must-fix now**: N
- **Optional/defer**: N

## Action Items

### P0 — Critical
#### [Short description]
- **File**: `path/to/file.py:L42`
- **Reviewer**: @username
- **Issue**: [What's wrong]
- **Action**: [Specific fix]
- **Validation**: [How to verify]

### P1 — High
[...]

### P2 — Medium
[...]

### P3 — Low / Deferred
[...]

## Dependencies
[If any items depend on others]

## Quick Wins
[Items that can be addressed in <5 min]

## Optional / Deferred
[Lower-priority items intentionally deferred]

## Declined (with reasons)
[Items judged invalid after source inspection, or out of the PR's original
scope — one-line reason each, to be posted on the thread at resolution time]
```

## Notes

- Skip resolved threads unless user requests them
- Group related comments into single action items
- Quote specific reviewer concerns when unclear
- Link to comment URLs for context

## Handoff to gh-address-comment

After producing the action plan, pass it directly to the `gh-address-comment` skill
to resolve must-fix items. Do **not** re-implement comment-addressing inline.
CodeRabbit-authored threads go to `autofix` instead — it fetches unresolved
CodeRabbit threads and applies fixes with per-change approval.

```
Skill: <skills-dir>/gh-address-comment/SKILL.md
Trigger: "address the open PR comments" or "fix the must-fix items"
```

Load `gh-address-comment` explicitly before starting code changes.
Do NOT inline-implement git checkout + edit + commit logic — the skill handles it.


## Gotchas

1. **Do not inline-implement fixes after triage** -- triage produces an action plan only. Applying fixes is the job of `gh-address-comment`. Re-implementing checkout+edit+commit logic here creates duplicate, divergent workflows (this exact issue was logged 2026-02-23).
2. **Resolved threads are hidden by default** -- `extract_pr_comments.py` skips resolved threads unless called with `--include-resolved`. If a user asks 'why was X not addressed', re-run with resolved threads included before concluding the item was missed.
3. **Automated review bots inflate comment counts** -- tools like Copilot, Reviewdog, or custom bots can post dozens of nitpick comments. Triage these as P3 by default and group them into a single action item rather than one per comment. **Exception — CodeRabbit:** triage its findings by their stated severity, not as blanket P3 — its "Potential issue"/security findings are genuine P0/P1 candidates; only its nitpick/style class defaults to P3. Route CodeRabbit-authored threads to `autofix` (not `gh-address-comment`) in the handoff.
4. **Silent empty triage is wrong** -- if the script returns zero actionable comments, confirm that the PR number/URL was resolved correctly before reporting 'nothing to do'. A failed or partial read exits with an error.

## Invocation

`extract_pr_comments.py` calls plain `gh`. Run from the repo root:

```bash
<skills-dir>/gh-pr-triage/scripts/extract_pr_comments.py <PR_URL>
```
