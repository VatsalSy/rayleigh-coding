# Mixed Codebase README Template

This template is for projects combining Basilisk simulations with Python post-processing. Follows the modern CoMPhy Lab format.

---

```markdown
# Project Title

Brief tagline describing the simulation and analysis.

[![Basilisk](https://img.shields.io/badge/Basilisk-C-blue)](http://basilisk.fr)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![DOI](https://zenodo.org/badge/DOI/10.XXXX/zenodo.XXXXXXX.svg)](https://doi.org/10.XXXX/zenodo.XXXXXXX)
[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

## Overview

[2-3 sentences describing what this project does, the physical phenomenon being studied, and how simulation and post-processing work together.]

The article can be found at: [link to paper/preprint]

## Basilisk (Required)

First-time install (or reinstall):
```bash
curl -sL https://raw.githubusercontent.com/EXAMPLE_ORG/basilisk-C/v2026-05-21/reset_install_basilisk-ref-locked.sh | bash -s -- --ref=v2026-05-21 --hard
```

Subsequent runs (reuses existing `basilisk/` if same ref):
```bash
curl -sL https://raw.githubusercontent.com/EXAMPLE_ORG/basilisk-C/v2026-05-21/reset_install_basilisk-ref-locked.sh | bash -s -- --ref=v2026-05-21
```

> **Note**: When a newer stable release is available, replace `v2026-05-21` in both the script URL and `--ref` with the same [release tag](https://github.com/EXAMPLE_ORG/basilisk-C/releases).

## Repository Structure

```
├── simulationCases/                 Main simulation code
│   ├── [simulation].c              Primary simulation (production runs)
│   ├── [simulation]-extended.c     Extended version with additional features
│   └── DataFiles/                  Input geometry/initial conditions
├── src-local/                       Custom Basilisk headers
│   ├── [custom-header].h           Project-specific modifications
│   └── parse_params.sh             Parameter file parsing library
├── postProcess/                     Post-processing tools
│   ├── getData.c                   Field extraction on structured grids
│   ├── getFacet.c                  Interface geometry extraction
│   ├── getCOM.c                    Center of mass extraction
│   └── Video.py                    Frame-by-frame visualization pipeline
├── runSimulation.sh                 Single case runner (OpenMP/MPI)
├── runParameterSweep.sh             Parameter sweep runner
├── runPostProcess-Ncases.sh         Batch post-processing runner
├── default.params                   Single-case configuration
├── sweep.params                     Sweep configuration template
├── runSweep[Cluster].sbatch         SLURM script for HPC
└── README.md
```

## Physics

### Problem Description

[Describe the physical setup, geometry, initial conditions, and what phenomenon is being studied.]

### Governing Equations

The simulation solves the incompressible Navier-Stokes equations:

$$\nabla \cdot \mathbf{u} = 0$$

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \nabla \cdot (2\mu \mathbf{D}) + \mathbf{f}$$

[Add additional equations as needed: VOF, surface tension, etc.]

### Dimensionless Parameters

| Parameter | Definition | Physical Meaning |
|-----------|------------|------------------|
| $Oh$ | $\mu / \sqrt{\rho \sigma R}$ | Viscous vs. capillary forces |
| $Re$ | $\rho U R / \mu$ | Inertia vs. viscous forces |
| $We$ | $\rho U^2 R / \sigma$ | Inertia vs. surface tension |
| $Bo$ | $\rho g R^2 / \sigma$ | Gravity vs. surface tension |

## Simulation Files

This project contains multiple simulation files:

### [simulation].c (Primary)
The main simulation file used for all production runs. Outputs:
- `i dt t ke [additional columns]`

### [simulation]-extended.c (Optional)
An extended version with additional tracking features. Outputs additional measurements for detailed analysis.

**Note:** Production runs use `[simulation].c`. The extended variant is provided for cases requiring additional tracking.

## Running the Code

### Using Scripts (Recommended)

```bash
# Single simulation (serial)
./runSimulation.sh default.params

# With MPI (8 cores)
./runSimulation.sh --mpi --cores 8 default.params

# Parameter sweep
./runParameterSweep.sh sweep.params

# Batch post-processing
./runPostProcess-Ncases.sh
```

### Manual Compilation

**Serial execution:**
```bash
qcc -O2 -Wall -disable-dimensions [simulation].c -o [simulation] -lm
./[simulation] [args]
```

**OpenMP (shared memory):**
```bash
qcc -O2 -Wall -disable-dimensions -fopenmp [simulation].c -o [simulation] -lm
export OMP_NUM_THREADS=8
./[simulation] [args]
```

**MPI (distributed memory):**
```bash
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions [simulation].c -o [simulation] -lm
mpirun -np 8 ./[simulation] [args]
```

### Why `[simulation].c` (not `[simulation]-extended.c`)

The running scripts use `[simulation].c` because:

1. **`distance.h` is incompatible with MPI** - The `distance.h` header cannot be compiled with `-D_MPI=1`
2. **OpenMP is compatible** - `distance.h` works fine with OpenMP (`-fopenmp`)
3. **Two-stage execution** - First run briefly with OpenMP to generate restart file, then run full simulation with MPI

### Command Line Parameters

The simulation takes N arguments: `[param1] [param2] ... [paramN]`

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `LEVEL` | Maximum refinement level | 10 | 7-12 |
| `Oh` | Ohnesorge number | 1e-2 | 1e-4 - 1 |
| `tmax` | Maximum simulation time | 10.0 | > 0 |

### HPC Cluster Execution

For cluster environments:
```bash
# Snellius
sbatch runSweepSnellius.sbatch

# Hamilton
sbatch runSweepHamilton.sbatch
```

## Post-Processing

The `postProcess/` directory contains analysis and visualization tools:

| Tool | Purpose |
|------|---------|
| `getData.c` | Extract field data on structured grids |
| `getFacet.c` | Extract interface geometry |
| `getCOM.c` | Extract center of mass trajectory |
| `Video.py` | Generate frame-by-frame visualizations |

### Usage

```bash
cd postProcess/

# Compile extraction tools
qcc -O2 getData.c -o getData -lm
qcc -O2 getFacet.c -o getFacet -lm

# Run visualization
python Video.py ../simulationCases/
```

### Python Dependencies

```bash
pip install numpy matplotlib scipy
```

## Key Features

- [Feature 1: e.g., Volume of Fluid (VOF) method for interface tracking]
- [Feature 2: e.g., Adaptive Mesh Refinement (AMR) with octree grids]
- [Feature 3: e.g., Custom two-phase solver with property interpolation]
- [Feature 4: e.g., Parallel execution with OpenMP and MPI support]
- [Feature 5: e.g., Comprehensive post-processing and visualization suite]

## Citation

If you use this code in your research, please cite:

### Paper
```bibtex
@article{[AuthorYear],
  title = {[Paper Title]},
  author = {[Authors]},
  journal = {[Journal]},
  year = {[Year]},
  volume = {[Vol]},
  pages = {[Pages]},
  doi = {[DOI]}
}
```

### Software
```bibtex
@software{[RepoName][Year],
  author = {[Author Name]},
  title = {[Repository Title]},
  year = {[Year]},
  publisher = {Zenodo},
  version = {[version]},
  doi = {10.5281/zenodo.[XXXXXXX]},
  url = {https://doi.org/10.5281/zenodo.[XXXXXXX]}
}
```

## Authors

- **[First Author]** ([Institution]), [[email]](mailto:[email])
- **[Second Author]** ([Institution]), [[email]](mailto:[email])
- **Your Name** (University of Twente), [AUTHOR_EMAIL](mailto:AUTHOR_EMAIL)

## License

This project is licensed under the GNU General Public License v3.0 -
see the [LICENSE](LICENSE) file for details.

## Contact

For questions or collaboration inquiries, please contact the [CoMPhy Lab](https://EXAMPLE_ORG.org).
```

---

## Template Usage Notes

1. **Replace all `[bracketed]` content** with project-specific information
2. **Document simulation file variants** - explain why primary vs extended
3. **Include two-stage execution notes** if using `distance.h`
4. **Document post-processing tools** comprehensively
5. **Dual citations** - both paper and software when available
