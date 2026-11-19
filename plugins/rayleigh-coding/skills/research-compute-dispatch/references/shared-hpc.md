# Shared-HPC conduct

Use a shared cluster as a careful user at a shell would for the named task.
Permission is not purpose: being able to read something does not make it part
of the job.

## Before any command

Know the project, run, account and allocation you are acting for, and the
site's documented way of running (modules, container image, scheduler). Once a
run is queued or running, tie every scheduler, file, log and transfer action to
its recorded job ID and run directory. If those are missing, stop and resolve
them rather than guessing.

## Permitted

- Within your project, run directory, account and allocation: read source,
  design diagnostics, compile, test, analyse, and inspect your own logs and
  outputs.
- Account-scoped scheduler queries (`squeue --me`, `sacct -j <id>`).
- On a login node: short status checks, source or configuration reading,
  site-permitted compile probes, job submission and data transfer.
- Substantial compilation, test suites, analysis and anything heavy run inside
  a compute allocation.

## Run directories and storage

- Put run directories and restart files under the site's project storage, not
  scratch and not your home quota.
- Scratch is for job-local temporary I/O only. The job script copies results
  back to project storage and verifies them before exiting successfully.
- Project storage is working storage: allocations expire and it is often not
  backed up. Keep a verified copy off the cluster.
- Check quota and site policy against the estimated output before submitting.

## Forbidden

- Browsing other users' home directories, jobs or processes; host-wide process
  enumeration; reading `/etc`, broad `/proc` or scheduler configuration out of
  curiosity.
- `sudo`, system services, global package installs, or changing permissions to
  widen access.
- Heavy compute, large builds, test suites or broad file-system searches on a
  login node.

These limits hold even when the account or file permissions would technically
allow the action. Cluster administration is a separate task with its own
authority.
