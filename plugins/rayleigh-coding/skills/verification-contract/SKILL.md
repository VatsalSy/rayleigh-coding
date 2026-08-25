---
name: verification-contract
description: Use when the user asks to create, repair, or audit an executable repo-local verification procedure/skill for a solver, CLI, service, runner, or UI, or says "prove this workflow works". NOT for one-off test execution; use the repository's existing test workflow.
---

# Verification Contract

Create or maintain a repository-local, executable verification contract that a
future agent can run cold. It must state what is being established, drive a
real relevant path, retain direct evidence, and clean up only what its run
created. It is not a generic test checklist and it must not relabel evidence
to make a result look stronger.

## Classify the Claim First

Write the claimed evidence class before designing commands or editing a skill.

| Class | Establishes | Requires |
|---|---|---|
| Software test | A bounded implementation contract behaves as specified | deterministic input, expected observable output/failure, and a direct assertion |
| Numerical/code verification | The implemented equations/algorithm are solved correctly to the stated tolerance | exact, manufactured, independently derived, or separately integrated reference plus convergence/error evidence where applicable |
| Scientific/model validation | The model represents an external system in a stated regime | genuinely independent experimental, observational, or benchmark data; uncertainty and comparison fields |
| Operational verification | A CLI, service, runner, or UI performs a real user/operator path | launch/health precondition, real drive, observable state/side-effect, and controlled cleanup |

Do not call a higher-resolution run “validation”, a snapshot comparison
“verification”, or a green test suite a proof of scientific correctness. When
a contract spans classes, give each claim its own procedure and receipt.

## Discover the Real Surface

1. Read the repository instructions, existing tests, build/run entry points,
   CI, fixtures, and user/operator documentation. Reuse a working harness or
   runner where it exists; do not create a competing launcher.
2. Define the smallest representative surface: solver case, CLI command,
   API route, background job, simulation-runner path, or UI task. Name the
   preconditions, fixtures, environment variables, isolation boundary, and
   expected observable result.
3. Decide where the repo keeps local skills/procedures. Honour existing layout;
   otherwise use a narrowly named `.agents/skills/verify-<surface>/SKILL.md`
   or an existing test/verification directory, not the shared skills tree.
4. Keep default runs local, deterministic, bounded, and non-destructive. Do
   not use production credentials, live data, or shared/production compute
   simply to make a procedure impressive. If a claim truly requires a remote
   or shared runner, state that as an explicit prerequisite and obtain scope
   confirmation before scheduling anything.

## Author the Contract

Give the repo-local procedure these sections, with concrete commands and no
placeholders:

1. **Claim and evidence class:** exact behaviour/model statement, tolerance or
   acceptance rule, and what the procedure does not establish.
2. **Prerequisites and doctor:** required tools, pinned/reported version,
   fixtures, isolation, and one fast check that the instance/environment is
   safe to drive.
3. **Launch or preparation:** exact build/start command, readiness signal, and
   ownership of every process, port, temporary directory, case directory, or
   generated output.
4. **Drive and assert:** commands/selectors/input files that exercise the real
   path, expected direct artefact, and explicit pass/fail assertion. For UIs,
   capture action plus resulting visible state and side effect; for services,
   capture request plus response and persisted effect; for solvers, retain the
   input manifest, reference, error/convergence data, and comparison command.
5. **Receipt:** named, stable repository-approved evidence location outside
   the run-owned temporary directory; command, relevant version/commit,
   parameters, exit status, generated artefact paths, measured vs expected
   values, and timestamp. A screenshot or success log alone is insufficient
   when the claim concerns a side effect.
6. **Cleanup:** remove only resources this run created, using recorded PIDs and
   explicit temporary paths. Never kill by process name, delete shared outputs,
   or delete the receipt. State how cleanup itself is checked.
7. **Failure triage:** known failure signatures, diagnostic commands, and the
   boundary at which the procedure stops rather than modifying product code or
   infrastructure.

Helper scripts are justified only when they make the contract deterministic.
Keep them small, executable, documented at their call site, and covered by the
same procedure. Do not hide key assertions in an opaque wrapper.

## Prove and Maintain It

1. Run the new or changed procedure once in its intended isolated mode. Record
   a direct-artifact receipt and verify after cleanup that the receipt remains
   while run-owned resources are gone. If it cannot be run safely, label the
   contract a draft and state the exact blocker; do not claim verification.
2. On maintenance, audit drift before editing: compare the procedure’s
   commands, dependencies, feature/case map, fixtures, readiness signal, and
   receipt schema against current source, build tooling, CI, and user-facing
   entry points. Test one representative path for every changed surface and
   all paths whose evidence class or external interface changed.
3. Correct contract or harness drift only inside its owned verification
   surface. A product defect is reported with its receipt, not silently
   documented as expected behaviour. Re-run each corrected path and retain its
   new receipt.

## Output Contract

Report the contract path; claimed evidence class; surfaces covered and
excluded; executable receipt location and pass/fail result; cleanup result;
drift found/fixed; and any remaining gap. A missing receipt, failed cleanup,
or unrun draft is a non-pass.

## Gotchas

1. Tests that call private helpers can be useful but do not prove the
   user/operator or solver path named by the contract.
2. “No error” is not an assertion. Compare a direct observable artefact,
   state transition, or reference value to an explicit expectation.
3. Shared state makes repeatable evidence dishonest. Isolate ports, database
   names, profiles, output directories, and case IDs, or state why the
   procedure cannot safely run concurrently.
4. Cleanup that erases the evidence has proven nothing anyone else can audit.

## Dependencies

- Use the owning domain skill for scientific-test/verification/validation
  design and interpretation.
- Use `playwright` or the relevant browser skill for UI driving, not coordinate
  guessing.
- Use `change-impact-analysis` before changing a verification contract that
  affects CI, production release gates, data migration, or shared runners.
