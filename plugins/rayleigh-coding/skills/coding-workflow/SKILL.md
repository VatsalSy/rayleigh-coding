---
name: coding-workflow
disable-model-invocation: true
description: >-
  Use for a complete coding workflow in Cursor, from scoping and implementation through evidence-based verification, review, and GitHub handoff.
---


# Coding workflow

1. Read the repository rules, inspect the checkout, and identify the intended outcome
   and allowed external actions. Preserve unrelated changes. Resolve routine choices
   locally and ask when the decision materially changes scope, cost, or authority.
2. Make the smallest coherent change through the normal entry point. Reuse established
   code and preserve supported inputs and callers. Use `change-impact-analysis` for a
   consequential change or `swarm-planner` for independent work that needs coordination.
3. Drive the relevant path, then record the command or interaction, revision, expected
   behaviour, and observed result. Use `verification-contract` when maintaining a
   repeatable verification procedure. State separately what still needs live validation.
4. Review the exact diff with `code-review`. Resolve reproducible findings and verify
   the final diff. Use `sol-loop` for a bounded sequence of material revisions.
5. Use `git-master` for delivery choices and the matching GitHub skill for the
   requested operation. Confirm the remote state after a push, PR change, or merge.
   `full-send` and `full-stop` have distinct, explicit invocation and landing rules.

When parallel work is authorised, prefer the current session's advertised delegation
tool. Preserve explicit model and effort selections when supported. Otherwise omit the
model override and inherit the session default. Keep the lead responsible for
integration and verification. The workflow needs no global configuration.
