---
name: grill-me
description: >-
  Use when the user says "grill me", "interrogate this", "ask me questions
  before planning", or asks to pressure-test a consequential underspecified
  decision. NOT for generic code review or manuscript interview prompts; use
  code-review or prompter-paper-interview.
user-invocable: true
---

# Grill Me

## Purpose

Turn a consequential but loose piece of work into defensible decisions before
planning or execution. Act as a sharp collaborator: inspect the real context,
separate facts from choices, expose weak premises, and ask only questions whose
answers can change the outcome.

This is a stateless adaptation of the dependency-aware grilling
idea described at <https://www.aihero.dev/skills-grill-me>. It is independently
written for this workflow and has no upstream installer or runtime
dependency.

## Entry contract

- **Explicit invocation:** `$grill-me`, "grill me", "interrogate this", or
  "ask me questions before planning" starts the session immediately. Honour
  that choice even if the topic looks routine or reversible; do not veto it.
  Normal safety and scope boundaries still apply: explicit invocation changes
  interview depth, not authority.
- **Implicit fit:** for a consequential, materially underspecified decision,
  recommend a grilling session in one sentence and wait for the user to accept.
  Do not ask grilling questions before consent.
- Do not suggest this for routine, reversible work, a factual question, or a
  request already precise enough to execute.
- Grilling is read-only. Starting it does not authorise edits, locks, launches,
  publishing, external contact, purchases, deletion, or execution.

## Routing fence

Grill-me owns consequential user elicitation: it resolves choices that the user
must make before planning or execution. It does not perform generic code
review, security review, PR feedback triage, or architecture critique. Route
those to `code-review`, `dev-review-ultra`, `security-threat-model`, or the
relevant review skill. Code may be the subject of a grilling session only
when a material user decision remains open.

## Workflow

### 1. Ground in evidence first

Inspect the smallest relevant set of available sources before asking anything:
the current repository, nearest `AGENTS.md`, existing plans or designs, tests,
and task-relevant context. Use tools explicitly when the answer is
discoverable. Delegate a bounded read-only investigation only when independent
exploration will materially improve speed or coverage.

Classify every unknown:

- **Fact:** discover it; never make the user act as a file index or repeat known
  system state.
- **Decision:** ask the user when the choice materially changes the result.
- **Empirical uncertainty:** identify the research, diagnostic, prototype, or
  experiment that could settle it.
- **Unimportant detail:** choose a reasonable reversible default and record it.

Do not open tracker work or mutate project state merely to grill. Read-only
inspection stays on the zero-ceremony path.

### 2. Build the decision frontier

Start with the load-bearing spine: intended outcome and completion test,
audience or owner, current state, boundaries, constraints, and the most
important trade-off. Treat settled evidence and the user's earlier answers as
prerequisites in a decision tree.

The frontier contains only decisions that can be answered now. A question
whose answer depends on another unsettled choice waits for a later round.
Recompute the frontier after every response; never march through a fixed
questionnaire or re-ask a settled point.

### 3. Ask in small rounds

Ask two to four independent, high-impact questions per round. Use one question
only when it is genuinely the sole load-bearing frontier item. For each
question:

1. State the decision plainly.
2. Offer two or three meaningful options when useful.
3. Give one recommended answer and the concrete reason or trade-off.

Keep each question compact. If one numbered item hides several dependent
decisions, split it across rounds. Challenge contradictions and hand-waving
directly; do not silently reconcile incompatible constraints. Preserve
the user's strong technical language, use British English, and skip praise,
filler, recaps they did not ask for, and performative harshness.

Maintain a compact internal decision ledger containing settled choices,
defaults, constraints, rejected alternatives, open evidence needs, and the
acceptance test. Use it to shape later rounds, not as a running transcript.

### 4. Adapt the pressure test

Use only the lenses relevant to the work:

- **Research:** mechanism, scaling, dimensionless control parameters, limiting
  cases, competing explanations, discriminating evidence, numerical or
  experimental validation, and whether a claimed conclusion is actually
  supported. Keep theory/scaling work distinct from collaborator-owned
  experiments; do not reassign ownership silently.
- **Code:** users, public interfaces, data flow, ownership boundaries,
  compatibility, migration, failure and recovery, observability, and tests at
  the real seam.
- **Infrastructure:** authority, controller and host identity, live state,
  recovery path, blast radius, rollback, rollout order, monitoring, and exact
  verification receipts.
- **Writing:** audience, central claim, evidence, scope, voice, likely reviewer
  objection, and the boundary between internal findings and public-candidate
  prose.
- **Administration and strategy:** decision owner, deadline, dependencies,
  cost of delay, external versus the user-owned next action, failure path, and
  proof of completion.

Do not flatten technical work into beginner questions. Mechanism and evidence
come before generic storytelling.

### 5. Handle "I don't know"

Do not keep rephrasing the same question.

- For a low-cost reversible choice, recommend and record a default, then move
  on.
- For an empirical unknown, stop that branch and propose the smallest useful
  research step, diagnostic, prototype, calculation, or experiment.
- For a consequential irreversible, destructive, external, expensive, or
  public choice, leave it explicitly open and name the evidence or authority
  needed. Never manufacture certainty to empty the frontier.

Some questions are ungrillable: interaction feel may need a prototype;
scientific causality may need a matched control; infrastructure safety may
need a fresh-path test. Say so and route to evidence instead of making the
conversation balloon.

### 6. Stop and brief

Stop when the decision frontier is empty, the user says "enough", "stop", or an
equivalent, or every remaining branch needs evidence rather than preference.
Do not continue asking questions for the appearance of rigour.

Return a concise chat-only decision brief:

```markdown
## Decision brief

**Outcome:** <what is being decided or built>

**Settled choices**
- <choice and rationale>

**Assumptions and defaults**
- <assumption, including whether it is reversible>

**Open evidence and risks**
- <unknown, risk, and how to resolve it>

**Acceptance test:** <observable definition of success>

**Recommended next action:** <one concrete action and owning skill/workflow>
```

Route onward only when requested. For example, use `create-plan` for an
implementation plan, `skill-creator` for a reusable skill, or the relevant
execution skill for implementation. Answers given during grilling are not
execution approval.

## Boundaries and sibling routing

- Use `prompter-paper-interview` when the deliverable is a reusable manuscript
  interview prompt. An explicit live request to pressure-test a paper's core
  mechanism may still use this skill, but it must not create the interview
  artefact.
- Use `create-plan` when requirements are already decision-complete and the user
  simply wants an implementation plan.
- Do not write a `CONTEXT.md`, ADR, plan file, tracker entry, memory entry, or
  any other persistent state. The decision brief lives in chat.
- Context searches must be relevant and bounded. Do not dredge unrelated
  private material merely because it is accessible.
- No file type triggers this skill by itself. A plan, design, manuscript, or
  configuration file is relevant only when the user explicitly requests
  pressure-testing or accepts an implicit suggestion.

## Gotchas

1. **Implicit fit is suggestion-only.** Loading this skill without an explicit
   trigger is not consent to interrogate. Offer it once and wait; conversely,
   never refuse an explicit invocation because the topic seems too small.
   Refuse or narrow only when ordinary safety or scope rules require it.
2. **Inspection precedes questions.** Asking where code, tests, branches,
   project state, or documented constraints live is a failure when tools can
   answer it.
3. **Small rounds are not question dumps.** Two to four means independent
   frontier decisions, not eight questions hidden behind three headings.
4. **Recommendations are part of the work.** Do not make the user invent all the
   options while the agent pretends neutrality.
5. **Do not treat every unknown alike.** Reversible defaults, empirical probes,
   and irreversible open decisions require different handling.
6. **Discussion is not delivery authority.** Never drift from grilling into
   planning, editing, deployment, communication, or destructive action without
   the separate owning request and workflow.
7. **A brief without an acceptance test is incomplete.** "We agree" is not an
   observable definition of success.
