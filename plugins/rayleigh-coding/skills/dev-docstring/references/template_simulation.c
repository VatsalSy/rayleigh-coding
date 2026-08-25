/**
# Two-Phase Flow Simulation

Axisymmetric simulation of interfacial dynamics using the Basilisk framework.

## Physics Overview

This simulation models two-phase flow with surface tension using the
Volume-of-Fluid (VOF) method. The governing equations are:

$$\nabla \cdot \mathbf{u} = 0$$

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \nabla \cdot (2\mu \mathbf{D}) + \sigma \kappa \delta_s \mathbf{n}$$

where $\mathbf{D}$ is the strain-rate tensor, $\sigma$ is surface tension,
$\kappa$ is interface curvature, and $\delta_s$ is the interface delta function.

## Usage

```
./simulation maxLevel Oh Bond tmax
```

@file template_simulation.c
@author Your Name
@version 1.0
@date Jan 2025
*/

#include "axi.h"
#include "navier-stokes/centered.h"
#include "two-phase.h"
#include "tension.h"

/**
## Simulation Parameters

- `Oh`: Ohnesorge number, $Oh = \mu / \sqrt{\rho \sigma L}$
- `Bond`: Bond number, $Bo = \rho g L^2 / \sigma$
- `MAXlevel`: Maximum adaptive refinement level
*/

int MAXlevel;
double Oh, Bond, tmax;

/**
## Error Tolerances
*/
#define fErr   (1e-3)   // VOF volume fraction
#define VelErr (1e-3)   // Velocity field

/**
## Boundary Conditions

Outflow on right, no-slip on bottom (axis):
*/
u.n[right] = neumann(0.);
p[right] = dirichlet(0.);
u.t[left] = dirichlet(0.);

/**
## Main Function

Initialize parameters and configure the simulation domain.
*/
int main(int argc, char const *argv[])
{
  MAXlevel = atoi(argv[1]);
  Oh = atof(argv[2]);
  Bond = atof(argv[3]);
  tmax = atof(argv[4]);

  /**
  Domain size based on physical length scales: */
  L0 = 8.0;
  init_grid(1 << 6);

  /**
  Set fluid properties (density ratio = 1000, viscosity via Oh): */
  rho1 = 1.0;
  rho2 = 1e-3;
  mu1 = Oh;
  mu2 = Oh * 0.02;
  f.sigma = 1.0;

  run();
}

/**
## Initialization Event

Set initial interface shape and velocity field.
*/
event init(t = 0)
{
  /**
  Initialize with circular interface at origin: */
  fraction(f, sq(x) + sq(y) - sq(0.5));

  /**
  Start from rest: */
  foreach() {
    u.x[] = 0.;
    u.y[] = 0.;
  }
}

/**
## Adaptive Refinement

Refine based on interface position and velocity gradients.
*/
event adapt(i++)
{
  adapt_wavelet({f, u.x, u.y}, (double[]){fErr, VelErr, VelErr}, MAXlevel);
}

/**
## Logging Event

Output simulation progress and diagnostics.

### Outputs
- Time, timestep, grid cell count
- Maximum velocity magnitude
*/
event logfile(i += 10)
{
  fprintf(stderr, "t = %.4f, dt = %.2e, cells = %ld\n", t, dt, grid->tn);
}

/**
## Snapshot Output

Save simulation state at regular intervals for post-processing.
*/
event snapshot(t += 0.1; t <= tmax)
{
  char filename[80];
  sprintf(filename, "snapshot-%.4f", t);
  dump(file = filename);
}
