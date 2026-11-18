---
name: parallel-task
description: >-
  Use when the user authorises agents to execute an implementation plan with independent tasks. Resolve dependencies, isolate writes, and verify integration.
---


# Parallel task execution

1. Read the approved plan and scope. Check that task IDs are unique, prerequisites
   exist, and the graph is acyclic. If the user selects a subset, verify the required
   work already exists or include its prerequisites within the accepted scope.
2. Start only unblocked tasks with disjoint writes or verified isolation. Use the
   session's advertised tool and honour explicit model or effort constraints. If
   delegation is unavailable or unsafe, keep eligible work with the lead and do it
   in dependency order.
3. Brief each worker with its exact task, base, scope, writable paths, acceptance
   criteria, validation, and stop point. Have workers report the resulting diff or
   revision, tests, and blockers. Keep the plan and shared integration state under
   one owner. Workers do not publish or trigger deployments.
4. Check the actual result and terminal state before transferring overlapping
   ownership. Integrate in dependency order and verify that downstream tasks start
   from a base containing the required changes. Keep a blocked task and its
   dependants visible while independent work continues.
5. Run the integration checks and report the combined revision, verified outcomes,
   and remaining blockers. A worker summary alone does not complete its task.

Use `swarm-planner` to build or repair the dependency graph.
