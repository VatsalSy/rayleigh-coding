---
name: basilisk-master
description: >-
  Use for Basilisk (basilisk.fr) solver know-how: reading the source, API and
  header behaviour, qcc and MPI build errors, installation, adapt_wavelet,
  two-phase, axisymmetric and viscoelastic set-ups.
---

# Basilisk master

Basilisk is an open-source solver for partial differential equations on
adaptive Cartesian grids, written in Basilisk C and compiled with `qcc`
([basilisk.fr](http://basilisk.fr)). This skill has two rules:

1. Prefer existing Basilisk patterns (core headers, examples, tests and the
   target repository's own cases) over invention.
2. Read the source before asserting API behaviour. Basilisk's documentation is
   its literate source; memory of an API is not evidence.

For preparing, launching, restarting or monitoring a production run, use
[basilisk-runs](../basilisk-runs/SKILL.md). For choosing hardware and avoiding
other people's runs, use
[research-compute-dispatch](../research-compute-dispatch/SKILL.md). For
docstrings in `.c`, `.h` or `.py` files that feed a documentation site, use
`dev-docstring`.

## Gotchas

- **In `axi.h` the axis of symmetry is the bottom boundary, not the left.**
  `y` is the radial coordinate; a wall or substrate is usually `left`.
  Swapping them compiles cleanly and gives wrong physics.
- **Known identifiers need a definition lookup before a conceptual search.**
  `adapt_wavelet` appears in thousands of examples; find its definition in
  `src/` first, then read examples for usage.
- **`which qcc` can be stale after a reinstall.** The shell hash or `PATH`
  order may point at an old compiler. Run `hash -r` (bash) or `rehash` (zsh)
  and compare `qcc --version` with the install you intended.
- **qcc can report a Basilisk C parse error as a warning and still link.** The
  executable may skip solver initialisation. Treat such a warning as a failed
  build.
- **Include order matters.** `axi.h` comes before the solver; a `FILTERED`
  density/viscosity switch must be defined before `two-phase.h`.

## Source lookup protocol

Work from a local Basilisk tree (`$BASILISK` points at its `src/`
directory) or the online source at
[basilisk.fr/src](http://basilisk.fr/src/README). Each header is a literate
page with explanation and code together.

1. **Known symbol** (function, macro, field, event): locate the definition.

   ```bash
   rg -n --type-add 'bc:*.{h,c}' -t bc '\badapt_wavelet\s*\(' "$BASILISK" | head
   ```

   Prefer a hit in a core header (`src/*.h`, `src/grid/`,
   `src/navier-stokes/`) over examples and tests.
2. **Concept** ("how does refinement decide to coarsen?"): search core
   headers for the relevant names, then read enough surrounding code to
   verify signatures and control flow.
3. **Usage:** read `src/examples/` and `src/test/` for supported patterns.
   Sandbox pages on basilisk.fr are contributed patterns; label them as such
   and cross-check against core source.
4. **Report** what to do, why (physics or numerics), and which files and lines
   you checked. If no source is available, say that the claim is unverified
   rather than guessing.

Read the source first for: header semantics (`centered.h`, `two-phase.h`,
`tension.h`, `log-conform.h`, `reduced.h`, `contact.h`), boundary-condition
semantics, adaptation and curvature behaviour, `dump`/`restore`, and MPI
behaviour.

## Typical two-phase axisymmetric skeleton

```c
#include "axi.h"
#include "navier-stokes/centered.h"
#define FILTERED 1
#include "two-phase.h"
#include "tension.h"
```

- Non-dimensionalise and set the dimensionless groups the problem needs (for
  example $Oh = \mu/\sqrt{\rho\sigma R}$, $We$, $Bo$, $De$), often with
  `f.sigma = 1`. Define every group where the case is documented.
- Structure the case with events: `init`, `adapt`, output and logging, and an
  end condition.
- Make long runs restartable with `dump()` and `restore()`.

This is an orientation, not a boundary-condition recipe. Before editing a case
or adding a case family, find the nearest existing driver in the target
repository and compare include order, events, parameter parsing, domain
geometry and every boundary declaration. Derive each edge condition from the
geometry and the wetting or interface physics; do not copy a generic
`f[left]` line because two cases look alike.

## Adding physics

1. Look for an existing implementation in core source, then examples and
   tests, then the repository's own local headers.
2. Only then write a new header. Keep one parameter-parsing path rather than
   duplicating parsing logic across scripts.
3. For viscoelastic or viscoplastic additions, check parameter naming against
   the repository, header order compatibility, and that the case compiles in
   every supported build mode.

## Build and runtime triage

Resolve the environment first: a container route if the repository provides
one, otherwise the project's pinned local compiler. On a shared cluster use the
site's approved modules or container image and build inside a compute
allocation, not on the login node.

Common failure classes:

- missing include or wrong include order;
- a field or component used that does not exist for the dimension or grid;
- boundary conditions applied to the wrong edge in `axi`;
- adaptation thresholds too loose for the interface resolution;
- restart inconsistency (`restore` path versus fresh initialisation).

Typical builds:

```bash
qcc -O2 -Wall -disable-dimensions case.c -o case -lm          # serial
qcc -O2 -Wall -disable-dimensions -fopenmp case.c -o case -lm # OpenMP
CC99='mpicc -std=c99' qcc -D_MPI=1 -O2 -Wall case.c -o case -lm  # MPI
```

Check the flags against the project's runner and Makefile; they are examples,
not a universal recipe.

## Installation and pinning

The upstream source is distributed with darcs from basilisk.fr (see its
`INSTALL` page). The public mirror
[comphy-lab/basilisk-C](https://github.com/comphy-lab/basilisk-C) also
publishes dated release tags and a ref-locked installer.

Use one pinned Basilisk per project, not an ambient install on `PATH`:

- Choose a release tag and record it in the repository (for example a
  committed `basilisk.ref` file). Install exactly that tag into the project
  (for example `<repo>/basilisk`, gitignored). Download and read the installer
  from the same tag before running it; do not pipe a mutable branch into a
  shell while calling the install reproducible.
- Before a campaign, confirm that `command -v qcc` resolves inside the pinned
  install and that the installed ref matches the recorded one. A compiler found
  elsewhere on `PATH` means the run is not using the pin.
- Results that cannot be attributed to a recorded Basilisk ref and code commit
  are not reproducible.

## Repository rules

- No host-specific compiler paths in committed scripts; resolve `qcc` from
  the environment.
- Keep generated Basilisk artefacts (executables, dumps, `_*.c`, build
  directories, the local install) out of Git.
- Keep one parser path for runtime parameters.
