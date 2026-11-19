---
name: research-compute-dispatch
description: >-
  Use to choose hardware for, reserve, launch, resume, stop, monitor or
  reconcile a research computation (simulation, sweep or analysis job), or to
  place its outputs, without disturbing other people's runs.
---

# Research compute dispatch

Coordinate research computation without double-booking a computer, disturbing
someone else's run, or losing results. Three things own the truth:

| Surface | Owns |
|---|---|
| Your run record (project notes, tracker or issue) | Scientific purpose, status, job ID, run directory, host |
| A shared reservation file or ledger | Who has claimed which CPUs, GPUs, memory and disk on a shared workstation |
| The live host or scheduler | What is actually running |

A promise in chat that a computer is free is not a reservation. Idle telemetry
is not availability: a reserved-but-idle host is still reserved.

For Basilisk runs, combine this skill with
[basilisk-runs](../basilisk-runs/SKILL.md). Use `publication-plots` for every
figure.

## 1. Resolve one run

1. Name the run with a stable identifier, for example
   `<project>/<simulation-id>`, and reuse it for retries.
2. Record the physics and code, resource shape (cores, GPUs, memory), expected
   duration, input data, output size estimate, and completion criterion.
3. If a reservation already exists for this run, inspect it before proposing
   another. One run gets one reservation.
4. For a campaign or anything likely to outlive the session, write down the
   next scientific decision and the evidence sufficient for it, so that
   monitoring and retries serve that decision rather than habit.

## 2. Audit before choosing

Compare three views and report conflicts before placing anything:

- declared reservations;
- your own run records;
- live processes and scheduler jobs.

On a **shared workstation** (no scheduler), look at current load and at other
users' processes. The commands below are for Linux; on macOS use `uptime`,
`sysctl hw.physicalcpu hw.logicalcpu hw.memsize` and `ps aux -r`, and note
that macOS offers no user-level CPU pinning, so reserve the whole computer
there rather than a cpuset.

```bash
uptime; nproc; free -g        # load, logical CPUs, memory
ps -eo user,pid,psr,pcpu,etime,args --sort=-pcpu | head -30
lscpu -e=CPU,CORE,SOCKET,NODE # which logical CPUs share a physical core
df -h <candidate-volume>
```

Busy-but-unreserved is someone's unattributed work, not room to squeeze in. An
empty reservation file does not mean the computer is free.

On a **shared cluster**, audit only through your own account's scheduler and
allocation views (`squeue --me`, `sacct`, the site's budget tool). Read
[shared-HPC conduct](references/shared-hpc.md) before the first command.

## 3. Select the target

Choose the smallest suitable target, in this order:

1. hard constraints: architecture, scheduler, software, GPU and memory, site
   policy;
2. existing reservations and the host's system headroom (leave cores and
   memory for the operating system and interactive users);
3. data locality and output storage;
4. live load and expected queue delay;
5. reproducibility, transfer cost and allocation budget.

Prefer a workstation for bounded work that fits without disturbing anyone.
Prefer a scheduler-managed cluster for production or resources not available
locally. Never compute on a cluster login node. An explicit user choice of host
is a constraint, not permission to oversubscribe it.

## 4. Reserve

On a shared workstation without a scheduler, agree a simple shared ledger with
the other users, for example one file per claim in a shared directory or a
small Git repository:

```yaml
# reservations/<project>--<simulation-id>.yaml
id: <project>/<simulation-id>
owner: <your-name>
host: <host>
cpuset: "8-15,40-47"      # logical CPUs covering whole physical cores
memory_gib: 64
storage: { volume: /data, estimated_peak_gib: 200 }
state: planned            # planned -> active -> released
review_at: 2026-12-01T09:00Z
reason: <one line of purpose>
```

- Claim the real shape. Do not pad the request because the host is large.
- Claim whole physical cores (both hyper-threads). Read the sibling layout
  from `lscpu -e`; it differs between hosts.
- Never overlap the `cpuset` of any claim that is not `released`; a
  `planned` claim occupies its CPUs just as an `active` one does.
- Make the check-and-claim step atomic, or two people can each see free CPUs
  (or free memory or disk) and both launch. Disjoint CPU sets are not enough:
  two claims can still overcommit memory or storage together. Hold one lock for the whole sequence: re-read the ledger,
  repeat the live audit, write the claim, then release.

  ```bash
  (
    flock -x 9 || exit 1             # one claimant at a time (Linux)
    # re-read reservations/ and repeat the live audit, then check every
    # claimed resource against that fresh state: no CPU overlap; and, per
    # host and per volume, this request plus each non-released claim's
    # remaining commitment (its claim minus its current use, never below
    # zero) within the live free memory or space less a system headroom.
    # Measure every claim's use first and the free figure last: anything
    # written in between then counts twice, which errs safe. A run already
    # above its estimate is charged at its real use; then write
    # reservations/<project>--<simulation-id>.yaml
  ) 9> reservations/.lock
  ```

  Where `flock` is unavailable, `mkdir reservations/.lock` (atomic; remove
  the directory afterwards) serves the same purpose. With a Git ledger, a
  rejected non-fast-forward push means the claim did not land: fetch, re-check
  and retry. Never resolve a conflicting claim blindly, and launch only after
  the claim is written.

On a cluster, the scheduler's allocation is the reservation; record its job ID
against the run.

## 5. Launch and prove

Use the project's existing runner or scheduler script. Do not invent a second
launcher. Before calling the run started, have:

- pinned or recorded code and configuration (commit, solver version);
- a new, empty run directory outside the source repository (or an explicitly
  resumable one);
- the scheduler job ID or exact process IDs and the run directory;
- fresh log or status output proving the intended executable started;
- CPU binding that matches the reservation.

**A cpuset that is only written in the ledger is not isolation.** The launcher
must enforce it (Linux commands below):

```bash
taskset -c 8-15,40-47 ./run.sh case.params      # threaded / OpenMP solver
```

`taskset` on an MPI launcher does not reliably confine MPI ranks (for example
with Open MPI 5). For MPI, use the MPI library's own binding (a rankfile, or
`--cpu-set`/`--bind-to core` where supported), or a cgroup (`systemd-run
--user --scope -p AllowedCPUs=8-15,40-47 ...` where available). Cap the rank
count at the number of physical cores in the cpuset. Then verify every thread
of every process you own:

```bash
grep Cpus_allowed_list /proc/<pid>/task/*/status
```

Mark the reservation `active` once the run is proven, and keep it active while
any of its processes or jobs is running. If the launch fails, record the real
state; release the claim only after proving nothing is running.

## 6. Monitor

Use bounded, batched checks: scheduler or process state, fresh log lines,
numerical progress and fatal signatures. CPU usage alone does not show health.
After the job is accepted, arrange a real continuation (scheduler dependency,
completion signal or scheduled check) and do other useful work. A healthy
multi-hour run needs checks tens of minutes apart, not minute-by-minute polling.
Keep no-change checks quiet. Return to reasoning for completion, a fatal error,
progress stalled beyond its expected range, an approaching walltime or resource
limit, or a scientific decision.

Report submitted, queued, running, failed, inconclusive and complete as
different outcomes. Scheduler acceptance is not execution.

## 7. Stop, restart or retry

Before signalling any process, read [process control](references/process-control.md).
In brief: prove each PID belongs to this run by owner, working directory and a
stable run marker; never use `pkill -f`, `killall` or a `ps | grep | kill`
pipeline; on a scheduler use only the recorded job ID.

A retry or resume is reconciliation, not a second launch. Before it, compare
scheduler or process state, the reservation, the run directory and checkpoints,
and your run record for the same run ID. If the job is alive, resume monitoring.
If it ended with a valid checkpoint and the runner supports restart, restart
into a new run directory, and treat the restart as a new launch:

- **One attempt, one launcher.** Under the ledger lock, record a restart
  attempt with a unique ID against the run, unless one is already pending.
  Only the caller that recorded it may launch or submit it. A pending attempt
  is cleared only when its launcher reports the outcome, or when you can
  prove it will never launch (its process is gone and nothing ran, or the
  scheduler has no job for that attempt). Until then, nobody retries and
  cleanup leaves the claim alone.
- **Capacity as at first launch.** On a shared workstation, under the same
  lock, confirm the claim is still yours (not `released`, no overlapping
  claim, live state idle) and repeat step 4's check for the restart's peak
  memory and its extra storage (the new directory, while the earlier output
  stays), counting the retained claim once. Enlarge the claim if it is short.
  If cleanup already released it, make a new atomic claim; the old CPUs may
  belong to someone else.
- **Scheduler restarts.** Submit a new job with explicit restart arguments
  (the verified checkpoint and the attempt's directory), and record the
  returned job ID against the attempt at once. If a submission's outcome is
  uncertain, look for that attempt in the scheduler's records before any
  retry. Requeue the old job only if its batch script itself selects the
  checkpoint and a fresh directory: a requeued job reruns its script from
  the top, with the arguments it was first given. If the views conflict
or ownership is unclear, stop and resolve that first. Re-running an unchanged
failed command without new evidence is not recovery; before another repair or
variant, name the new evidence or hypothesis that makes it informative.

## 8. Verify outputs, place data, release

- Working disk (workstation internal disk or cluster project storage) holds the
  live run and its restart files. Cluster scratch is temporary; the job must
  copy results back and verify them before it exits successfully.
- Keep at least one verified copy off the compute host before calling a run
  settled. Allocation-bound cluster storage and scratch are never the only
  copy.
- Copy before deleting. Verify destination, free space, file counts and
  checksums. Treat source deletion as a separate, deliberate action.
- Keep one archive root per project with stable subdirectories (for example
  `raw/`, `processed/`, `manifests/`), and record where each copy lives.

When the run needs no more capacity: record its truthful final state, confirm
the archive copy, then set the reservation to `released` with the outcome. Do
not auto-release someone's idle reservation; ask its owner.

## Constraints

- Never launch before the reservation exists.
- Never signal a process you have not proved is yours and this run's.
- Never claim CPUs the launcher does not enforce.
- Never compute on a cluster login node.
- Never leave irreplaceable output only on scratch or a single compute host.
- Never change SSH, firewall, system services or other users' files from this
  workflow.
