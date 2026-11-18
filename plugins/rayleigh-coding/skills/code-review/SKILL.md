---
name: code-review
description: >-
  Use for an evidence-led code review of a local diff or pull request. Review the exact change, validate reachable findings, and check fixes against the final revision.
---


# Code review

## Scope and evidence

- Read the user's intent, repository instructions, base, head, and working-tree status.
  For an open pull request, use its live base and head. Include uncommitted changes only
  when they are in scope and freeze the paths while a reviewer reads them.
- Read the complete scoped diff and the affected callers. Inspect the normal entry
  points, error and retry paths, concurrent state, and pre-existing data as applicable.
  Check tests for what they actually prove. Distinguish source inspection, local execution,
  and observed service behaviour.
- Prioritise issues that are introduced or made reachable by the change. For each
  finding, give severity, a file and line, the triggering condition, the consequence,
  and the smallest correction. Group equivalent findings and omit speculation.

## Independent pass

When requested or required by repository policy, use an independent reviewer on the
same evidence. Confirm the backend and what data it receives. Limit the brief to
authorised source and omit credentials, private configuration, and personal data.
Give read-only instructions and confirm that the reviewed state stayed unchanged.
When a required reviewer is unavailable, report the missing result and retain the
repository's review requirement.

Use `autofix` for CodeRabbit App findings on GitHub and `coderabbit-config` for
configuring that integration.

## Close out

Verify the strongest finding against the source and a directed check when practical.
Record the disposition and evidence for any disputed findings. If the user requests
a fix, rerun the relevant checks and re-review materially changed behaviour. Report
the exact reviewed revision and any verification gaps. A timeout or partial review
has no approval status.
