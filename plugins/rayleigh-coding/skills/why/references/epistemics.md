# Evidence and confidence

Historical evidence is fragmentary. Code, commits, issues, documents, chat,
and telemetry were created for different purposes and can contradict one
another. Classify every claim before writing it.

## Tiers

### Direct

An author, decision-maker, or authoritative record explicitly states the
motivation or choice. Examples include a PR explaining the constraint, an ADR
rejecting an alternative, a code comment giving the reason for a threshold,
or a decision note linking a failure to the accepted fix.

Direct claims may use `because` when the citation sits beside the claim.

### Supported

Independent indirect records converge, although none alone states the whole
answer. A failing test timeline, issue discussion, and introducing commit may
jointly support an incident-driven explanation. Name every contributing item.

### Inferred

The evidence permits a reasonable interpretation but does not establish it.
Show the chain and use calibrated phrasing such as `appears to`, `likely`,
`suggests`, or `is consistent with`.

### Speculative

The explanation is plausible, evidence is thin, and alternatives fit. Say
that explicitly and state what evidence would distinguish the hypotheses.

### Unknown

The bounded search did not answer the question. Record the queries, windows,
sources, retention/access limits, and likely human authority. Unknown is a
useful result.

## Rules

- Every Direct or Supported claim needs a stable citation.
- Code is evidence for mechanics, not its own motivation.
- A user's suggested reason is a hypothesis to test independently.
- A null result is meaningful only with the searched scope and query.
- An unavailable source is a coverage gap, not a null result.
- Surface contradictions; do not select the tidier account silently.
- Do not retrofit intent because today's design looks coherent.
- Temporal correlation and before/after telemetry support causation only when
  another record links the change to the observed effect.
- Model consensus never raises an evidence tier.

## Final calibration

Before returning, ask of every claim:

1. Is the citation real, reachable, and accurately represented?
2. Does the wording match the tier?
3. Is this motivation, or merely an observation about the implementation?
4. What evidence would exist if the leading interpretation were wrong?
5. Did the report name the important gaps and contradictions?
