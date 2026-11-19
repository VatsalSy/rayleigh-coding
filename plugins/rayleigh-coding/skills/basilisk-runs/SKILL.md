---
name: basilisk-runs
description: >-
  Use to preflight, launch, restart, monitor or close out a Basilisk
  simulation or an authorised campaign of runs.
---

# Basilisk production runs

Use the project's existing runner to prepare and operate a named Basilisk
simulation or an authorised campaign. This skill owns solver-specific run
evidence. It does not supply a new launcher or a scientific acceptance
threshold.

Enter at the requested operation. A launch needs the case, build and
start-mode checks; monitoring or closeout reuses the existing run record and
starts from live status and results.

## Authority and stopping point

- Use [research-compute-dispatch](../research-compute-dispatch/SKILL.md) for
  choosing hardware, reserving CPUs, scheduler lifecycle, process control and
  output custody. Its checks apply to every launch, stop and restart.
- Use [basilisk-master](../basilisk-master/SKILL.md) for compiler and install
  provenance and for source-grounded answers about headers, events, MPI and
  `dump`/`restore`.
- A successful compile or restart is not physical validation. Choose the
  evidence the observable needs (see `verification-contract`).
- Launch authority comes from the user's request or the accepted run scope;
  a preflight grants none. Stopping or signalling a running job needs the
  user's request for that run or a stop condition already in its scope
  (endpoint reached, walltime, fatal error). Otherwise report the evidence and
  a recommendation.

## 1. Resolve the case and runner

Read the project instructions, the existing runner and the selected case's
parameters and source. Reuse the accepted case list, endpoints and purpose;
distinguish a rough estimate from a quantitative claim. Do not create a sweep,
benchmark or refinement study by implication.

Identify the runner's parameter path, case identity, output directory,
fresh-start or restart mode, and completion and failure signals. Read the
runner before invoking it. Use a dry-run or `--check` mode only if it is
genuinely non-submitting. Do not assume that a script with a familiar name has
particular flags or output paths.

## 2. Bind the actual build and inputs

Before producing results, establish:

- the simulation source commit and any local patch affecting the executable;
- the pinned Basilisk ref and the compiler actually resolved in the execution
  environment, not an unexplained ambient `qcc`;
- the build command and options, dimension and grid, physics headers, and
  serial, OpenMP or MPI layout actually used;
- the resolved parameters, geometry and initial condition, end condition,
  diagnostics and dump cadence.

Write a small manifest into each run directory before compiling, for example
`manifest.json` with:

| Field | Content |
|---|---|
| `params_sha256` | SHA-256 of the parameter file; keep a byte-identical copy as `run.params` |
| `code_commit` | Source commit, suffixed `-dirty` if `git status --porcelain` is non-empty (modified tracked files or untracked files) |
| `extra_inputs` | Path and SHA-256 of any compiler input outside the committed tree (an ignored or out-of-repository header, a local patch); empty when none |
| `basilisk_ref` | Installed Basilisk ref; must equal the recorded pin |
| `qcc_version`, `compile_command` | First line of `qcc --version` and the exact command |
| `executable_sha256` | Hash of the built executable (null if the build failed) |
| `container_image` | Digest-pinned image, when the build ran in a container |
| `restart_from`, `restart_sha256` | Checkpoint path and hash, for a restart |

A run without a valid manifest, or with a null executable hash, should not
feed a figure; a `-dirty` commit, or a non-empty `extra_inputs` that the
commit does not reproduce, should not feed a published one. The pinned
Basilisk tree is covered by `basilisk_ref`, not by `extra_inputs`. Generate
hashes from the files; never transcribe a digest by hand. Reuse provenance
that still matches source, executable and environment; rebuild only when that
binding is missing or changed.

Check that trimming output or changing diagnostics preserves the intended
physics and event timing. A smaller output set or a clean compile alone does
not establish that.

## 3. Fresh start or restart

Give every fresh run and every restart a new run directory outside the source
repository. Never continue in, reuse or clear an earlier run directory, and
make sure the runner cannot silently pick up an old checkpoint.

For a restart, identify the exact checkpoint, the run and source that wrote
it, its physical time and completeness, and the intended continuation. Check
the project's compatibility conditions for fields, grid, dimension, executable
and parallel layout. Confirm how a successful `restore` is observed. If
restoration fails, report the failure; do not accept a silent fallback to a
fresh initialisation.

## 4. Dispatch, observe and continue

Hand the resolved runner, case and resource request to the dispatcher and
reuse its reservation and run identity.

After the scheduler accepts the job, record its ID and arrange a real
continuation (scheduler dependency, completion signal or scheduled check),
then do other useful work instead of polling. At a justified first check,
confirm the process is the one you launched, its CPU binding matches the
reservation, and fresh output is appearing. For a restart, confirm the
reported start time and state against the chosen checkpoint.

Observe physical time and the requested quantities, plus whatever cell count,
timestep, solver diagnostics, resource use or fatal signatures the case
actually emits. Choose evidence for the current question; do not invent a
diagnostic suite or fabricate missing fields. A queued or healthy job does not
need continuous attention: estimate the next useful check from measured
progress.

Use `publication-plots` to plot the requested observable, show informative
spatial structure, and make a short video when time-resolved fields explain
the mechanism. During a run, read only completed snapshots and label partial
time coverage. Never stop or alter a healthy run to get a frame.

## 5. Record the result or next decision

Keep one compact run record, reusing an existing one when it already holds the
evidence. The [run-record template](assets/run-record.md) lists fields, not a
schema; it cites the manifest rather than copying its values. Keep run records
and provisional observations in private project notes, not in a public
repository.

Report submitted, running, failed, inconclusive or complete accurately. A
scheduler exit code alone is not a scientific result: check the requested
endpoint and observables. Route retries, signals, archive copies and
reservation release through the dispatcher. When evidence raises a
consequential physical question, bring the observation and a recommendation
to the person who owns the science before running another variant.

A public figure or caption cites the code commit and Basilisk ref, not run
names, host names or paths.

## Recurring traps

- A pin file or local `qcc` lookup does not prove which compiler a remote
  batch script used. Resolve the actual build environment.
- A correct parameter file proves nothing if the executable reads another
  path. Trace the runner's real input route.
- A checkpoint filename does not prove a successful continuation. Verify the
  restore outcome and starting state.
- A qcc parse warning can still produce an executable that skips solver
  initialisation. Treat it as a failed build.
- Do not add bulky dumps by default; keep the output and restart coverage the
  run needs.
