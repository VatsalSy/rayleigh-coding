---
name: orchestration-claude
description: >-
  Use when Fable/Opus in Claude Code faces independent work needing subagents:
  multi-file audits, repo-wide edits, or parallel exploration. Decide
  whether/how to delegate. NOT for Codex/GPT harnesses (orchestration-gpt).
---

# Orchestration — Claude harness

You are the frontier model (Fable 5 or Opus 5) in Claude Code. Your context is
the most expensive resource in the room. Spend it on judgement, synthesis, and
the critical path; rent cheaper contexts for everything else.

## When to orchestrate

Delegate when the task has **two or more independent parts** that each need
more than a handful of tool calls, or when raw material (logs, transcripts,
many files) would flood your context but the conclusion is small.

Do it yourself when:
- the task fits in a handful of tool calls;
- the parts are tightly coupled (each step's output shapes the next);
- it is tracker/lock state, external actions, or final synthesis — those never
  leave the main session;
- you would spawn an agent merely to verify your own work.

## Model routing

| Role | Model | Why |
|---|---|---|
| Orchestrator (you) | Fable / Opus | Decomposition, judgement, synthesis, anything the user reads |
| Thinking / planning subagents | **Opus** | Design alternatives, adversarial review, plan critique |
| Execution / exploration subagents | **Sonnet** | Bulk edits, repo sweeps, log aggregation, mechanical transforms |

Pass `model: "opus"` or `model: "sonnet"` explicitly on every Agent call.
Never spawn a Fable subagent for work Sonnet can do; never give Sonnet a
design decision Opus should make.

## Contract for every subagent prompt

1. **Self-contained**: absolute paths, exact scope list, the doctrine it needs
   inline. The subagent has none of your conversation.
2. **File ownership up front**: disjoint file/directory sets per agent. Two
   agents never edit the same file.
3. **Stop-point**: say exactly where to stop ("edit files only, NO git
   commands", "report, do not fix"). Commits, pushes, locks, and anything
   external stay with the orchestrator.
4. **Deliverable shape**: demand a compact structured report (one line per
   item, counts, deviations flagged) — not a narrative.
5. **Read-only vs mutating**: audits and exploration are read-only by
   instruction; say so in the prompt.

**Bad:** "Look through the skills repo and improve the descriptions."
**Good:** "In <abs-path>, branch already checked out, edit ONLY these 22
skill dirs: <list>. Rewrite each SKILL.md frontmatter description to trigger
phrases, ≤40 words. No git commands. Final message: one line per skill,
old→new word count."

## Pattern

1. Scout inline until you can write disjoint work-lists.
2. Launch all independent agents in one message (background), Opus for
   thinking, Sonnet for doing.
3. Keep working the critical path yourself while they run; never idle-poll.
4. On completion, verify a sample of each agent's claims yourself before
   building on them.
5. Synthesise and commit from the main session only.

## Gotchas

- A subagent's final report is invisible to the user — relay what matters.
- Subagents inherit permissions but not authority: delegation never widens
  external-action or lock boundaries (`AGENTS.md` gates still apply).
- Parallel agents that each "quickly check git status" will race; forbid git
  in their prompts.
- If an agent dies or is skipped its result is null — check before flattening.
- the user has given standing permission for delegation; do not ask again, but
  do say in one line what you delegated and why.
