# Process control on shared compute

Read this before stopping, restarting, cleaning up, re-pinning or otherwise
signalling a simulation process on any compute host, and before launching a
pinned run on a multi-tenant workstation. A retry does not inherit process
ownership from an earlier observation.

## Prove ownership, then signal

1. Re-read the run record, the reservation and the live process or scheduler
   state. Resolve the exact run directory and recorded job ID. Keep the
   reservation `active` while any owned process or job is running.
2. On a scheduler, use only the recorded job ID and the scheduler's own
   cancel command (for example `scancel <jobid>`). Never replace a job action
   with a host-wide process kill.
3. On a workstation, list candidates without signalling them
   (`ps -eo pid=,ppid=,user=,args=`). For every exact PID prove:
   - the effective user is you;
   - its working directory is inside this run's directory. Linux:
     `readlink -e /proc/<pid>/cwd`; macOS: `lsof -a -p <pid> -d cwd -Fn`.
     Resolve symlinks on both sides before comparing;
   - at least one stable run marker matches: a cgroup or systemd scope, a
     scheduler job ID, ancestry from the runner's own process, or a PID file
     written by the runner. If no marker exists, do not signal.
4. Never use `pkill -f`, `killall`, a `ps | grep | kill` pipeline, or a bare
   solver or interpreter name. Signal only verified PIDs. A process group is
   eligible only after every member has been enumerated and proved. If one
   PID cannot be attributed, leave it alone.
5. Guard against PID reuse. On Linux, open a pidfd for the candidate before
   checking its identity, keep it open while checking, and signal through it
   (for example Python's `os.pidfd_open` with `signal.pidfd_send_signal`).
   Otherwise use the runner's or supervisor's own process handle. Without
   either, do not send a direct PID signal.
6. Send a graceful signal first, re-list the exact PIDs, and escalate only
   those still owned, if the runner's shutdown contract allows it. Re-check the
   reservation and run record afterwards; stopping a process never implies
   releasing the capacity.

## CPU affinity on a multi-tenant workstation

- Every CPU claim names an explicit, non-overlapping cpuset in logical CPU
  numbers, covering whole physical cores (both hyper-thread siblings). Read
  the sibling layout with `lscpu -e=CPU,CORE`.
- The launcher must enforce that cpuset. `taskset -c <list>` works for
  threaded, non-MPI solvers. MPI ranks may escape a `taskset` on the launcher
  (Open MPI 5 does this), so use the MPI library's binding (rankfile, or its
  CPU-set option where supported) or a cgroup scope.
- Open MPI defaults to one slot per physical core, so the rank ceiling is the
  number of physical cores in the cpuset, not the logical CPU count. A
  hostfile only caps slot counts; it does not set affinity.
- Verify containment on every thread, not only at process level:
  `grep Cpus_allowed_list /proc/<pid>/task/*/status`.
- On a host where affinity cannot be enforced, reserve the whole host or use
  a verified alternative. Do not claim isolated CPUs that nothing enforces.
