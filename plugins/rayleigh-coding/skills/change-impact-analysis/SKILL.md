---
name: change-impact-analysis
description: Use when the user asks "what could this break", "map the blast radius", "impact analysis", or wants a read-only pre-change/pre-merge dependency and rollback assessment. NOT for security threat modelling; use security-threat-model.
---

# Change Impact Analysis

Map the credible blast radius of a proposed or existing change without
modifying code, configuration, infrastructure, or data. The useful outcome is
a prioritised decision record, not an exhaustive caller list. Anchor every
material conclusion in an inspected artefact and mark what was not checked.

## Scope

1. State the change boundary: target paths/symbols, intended behavioural
   change, deployment or execution context, and excluded surfaces. If the
   request names only an idea, map the likely boundary from repository evidence
   and label it provisional.
2. Read the changed code or proposed design with its immediate callers,
   configuration, tests, documentation, schemas, and build/deployment paths.
   Inspect dependency manifests and pinned versions before assuming library
   semantics.
3. Keep the investigation read-only. Do not start services, submit runs,
   inspect unrelated private records, or alter user data merely to improve
   coverage.

## Surface Map

Trace only edges that can change behaviour, ownership, compatibility, or
recovery. For each relevant surface, record the artefact, the direction of
impact, confidence, and a check that would reduce uncertainty.

| Surface | Look for | Typical impact question |
|---|---|---|
| Code and interfaces | callers, imports, CLI/API contracts, config, schema and serialised formats | Who can observe a changed input, output, default, lifecycle, or error? |
| Tests | unit/integration coverage, fixtures, golden files, contract tests | Which tests encode the old contract, and which gaps leave risk unproven? |
| CI | workflows, required checks, matrix jobs, caches, secrets usage | What gate fails, skips, or silently stops protecting the change? |
| Deploy | manifests, release scripts, environment contracts, feature flags, observability | What host, service, schedule, or rollback path changes? |
| Migrations | schema/data migrations, backfills, compatibility windows, dual-write readers | Can old and new versions coexist, and is the change reversible? |
| Data and storage | readers/writers, caches, retention, recovery copies | Can it corrupt, orphan, re-interpret, expose, or make data unrecoverable? |
| Public-candidate material | README, docs, reports, figures, UI copy, generated artefacts | Does it promote provisional/private detail or make an unsupported claim? |
| Rollback | feature flags, compatibility windows, backups, migration reversibility, release procedure | Can the prior safe state be restored without data loss or split-version failure? |

Treat empty search results as evidence only when the search scope and exact
query are recorded.

## Find the Load-Bearing Safety Claim

Identify the single factual claim on which the proposed change is most
dependent. Good claims are falsifiable and narrow: “old readers reject the new
format before writing”, not “the migration is safe”. Trace it to the real
implementation, dependency source, or runtime contract.

When practical and safe, prove that claim with executable evidence that drives
the actual production path or the same dependency version: a focused test,
deterministic command, parser fixture, dry-run whose side effects were checked,
or an existing integration test. Capture command, environment/preconditions,
exit status, and the observable result. A mocked internal setter does not
prove an external compatibility claim.

If execution would mutate state, require unavailable credentials, touch
production, or cannot be made bounded, do not run it. State the strongest
evidence reached instead (source, test inspection, or reproducible proposed
check) and mark the claim **unproven**. Never turn an unproven assumption into
a safety conclusion.

## Assess and Report

1. Separate confirmed impacts, plausible risks, cleared paths, and explicit
   unknowns. Rate likelihood and consequence qualitatively only where the
   evidence supports it.
2. Give each risk a concrete failure mechanism, affected surface, citation,
   detection method, and the smallest mitigator or rollout guard. Avoid vague
   warnings such as “might affect users”.
3. Describe rollback preconditions separately from rollback steps. A rollback
   that leaves incompatible data, queued work, or public claims behind is not
   a safe rollback.
4. Flag public-candidate boundary issues before any publication. Operational
   logs, provisional results, data paths, job identifiers, and debugging notes
   remain internal unless the user explicitly approves their named target.

## Output Contract

Return:

- **Change and boundary:** what was analysed and excluded.
- **Load-bearing claim:** citation, evidence level, executable receipt when
  run, or an explicit **unproven** label.
- **Impact map:** material code, tests, CI, deploy, migrations, data/storage,
  public-candidate, and rollback edges.
- **Risks and cleared paths:** mechanism, confidence, and cheapest next check.
- **Unknowns and decision gates:** what would change the recommendation.

## Gotchas

1. A list of callers is not an impact analysis. Formats, defaults, background
   jobs, deployment configuration, and independently versioned readers often
   carry the real breakage.
2. “Dry run” is a name, not evidence. Confirm its real writes, network calls,
   queueing, and side effects before treating it as harmless.
3. A passing unit test can establish one contract while proving nothing about
   migration reversibility, storage custody, or public-facing claims.
4. Unproven claims stay labelled. Do not promote them to safety conclusions.

## Dependencies

- Use `why` when historical rationale, rather than present impact, is the
  question.
- Use `verification-contract` to establish or repair a repeatable executable
  check.
