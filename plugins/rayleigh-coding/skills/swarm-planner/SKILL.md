---
name: swarm-planner
description: >-
  Use to plan independent tasks with explicit dependencies, writable paths, acceptance checks, and integration order. Planning does not start workers.
---


# Swarm planner

Read the source and scope before choosing boundaries. Prefer one owner when work
shares interfaces, state, release controls, or files. Confirm missing requirements
only when the answer would materially affect the plan.

For each task record:

- A stable ID and prerequisite IDs, with an empty list for tasks ready now.
- The outcome, prerequisites or interfaces it consumes, and owned writable paths.
- Acceptance criteria and a command or observation that verifies them.
- The integration owner and the handoff required by dependent tasks.

Check that every dependency refers to an existing task, the graph has no cycles,
and simultaneous tasks have disjoint writes or isolated worktrees. State the order
in which changes become available to dependent workers. A commit in another
worktree is available only after the integration owner deliberately brings it into
the required base.

Return the plan in chat or in the file the user asked for. Hand an authorised
execution request to `parallel-task`.
