---
name: orchestration-gpt
description: >
  Use when the user asks for parallel GPT/Codex subagents or a task needs
  deliberate decomposition and model/effort routing. NOT for Claude Code
  (orchestration-claude).
---

# Orchestration — GPT/Codex harness

You are the frontier model (GPT-5.6 Sol) in Codex. Your context is the most
expensive resource in the room. Spend it on judgement, synthesis, and the
critical path; rent cheaper contexts for everything else.

## When to orchestrate

Delegate when the task has **two or more independent parts** that each need
more than a handful of tool calls, or when raw material (logs, transcripts,
many files) would flood your context but the conclusion is small.

Do it yourself when:
- the task fits in a handful of tool calls;
- the parts are tightly coupled;
- it is tracker/lock state, external actions, or final synthesis — those never
  leave the main session;
- you would spawn an agent merely to verify your own work.

## Model and effort routing

| Role | Model / effort | Why |
|---|---|---|
| Orchestrator (you) | Sol, high | Decomposition, judgement, synthesis, anything the user reads |
| Thinking / planning subagents | **Sol medium/light** or **Terra high/medium** | Design alternatives, adversarial review, plan critique |
| Execution / exploration subagents | **Luna xhigh** | Bulk edits, repo sweeps, log aggregation, mechanical transforms |

Set model and reasoning effort explicitly on every spawn. Do not burn Sol-high
subagents on mechanical sweeps; do not hand Luna a design decision — route
design to Terra or a lighter Sol.

## Contract for every subagent prompt

1. **Self-contained**: absolute paths, exact scope list, needed doctrine
   inline. The subagent has none of your conversation.
2. **File ownership up front**: disjoint file/directory sets per agent. Two
   agents never edit the same file.
3. **Stop-point**: say exactly where to stop ("edit files only, NO git
   commands", "report, do not fix"). Commits, pushes, locks, and anything
   external stay with the orchestrator. Sol subagents especially need the
   stop-point stated or they keep going.
4. **Deliverable shape**: demand a compact structured report (one line per
   item, counts, deviations flagged) — not a narrative.
5. **Read-only vs mutating**: audits and exploration are read-only by
   instruction; say so in the prompt.

**Bad:** "Explore the repo and fix what looks off."
**Good:** "In <abs-path>, read-only: list every SKILL.md whose description
exceeds 60 words. Output: `name: word-count`, one per line. Do not edit."

## Brief contract and decision discipline

Every delegated brief must state these fields explicitly, in this order:

`Objective`; `Scope and ownership`; `Inputs/authority`; `Method or question`;
`Constraints and stop-point`; `Acceptance predicate`; `Evidence to return`;
`Output format`.

The acceptance predicate says what would make the work usable, not merely
finished. Evidence must be compact and inspectable: changed paths or examined
sources, command/test receipt where applicable, the decisive observation, and
an explicit `inconclusive` when the predicate was not met. Do not ask for a
long narrative or a duplicate of raw logs.

Use the right parallel shape:

- **Coverage split:** partition disjoint surfaces (directories, tests, data
  sources, or hypotheses). Each agent returns observations only for its owned
  surface; the main session synthesises cross-surface conclusions.
- **Arena:** give competing designs or interpretations the same bounded facts
  and evaluation criteria. Assign an independent judge who did not author a
  contender to compare trade-offs and evidence. Do not resolve an arena by
  majority vote or by the loudest model.

Agents may investigate or prepare isolated edits in parallel, but they never
concurrently mutate shared state: trackers, locks, Git state, reservations,
external systems, or a shared document. Collect independent outputs first;
then the main session serialises the authoritative decision and mutation after
checking the evidence.

## Pattern

1. Scout inline until you can write disjoint work-lists.
2. Launch independent agents together: Terra/Sol-light for thinking, Luna for
   doing.
3. Keep working the critical path while they run; never idle-poll.
4. Verify the decisive claim from each agent before building on it; sample
   only where the claim is mechanical and low-risk.
5. Synthesise, serialise shared state, and commit from the main session only.

## Gotchas

- A subagent's final report is invisible to the user — relay what matters.
- Delegation never widens external-action or lock boundaries (`AGENTS.md`
  gates still apply).
- Parallel agents racing on git state: forbid git in their prompts.
- Draft-PR habit: any subagent that files a PR must file a real PR, never a
  draft, and follow `gh-pr-create` conventions.
- the user has given standing permission for delegation; do not ask again, but
  say in one line what you delegated and why.
