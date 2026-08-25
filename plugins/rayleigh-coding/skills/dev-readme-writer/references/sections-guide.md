# README Sections Guide

Detailed guidance for writing each section of a scientific README.

---

## 1. Title & Badges

**Purpose:** Immediate project identification and key metadata at a glance.

**Format:**
```markdown
# Project Title

[![Badge1](url)](link) [![Badge2](url)](link)
```

**Best practices:**
- Title should be descriptive but concise (3-7 words)
- Use sentence case or title case consistently
- Place badges on same line, separated by spaces
- Order badges: language → framework → docs → license → lab

**Common badges for scientific projects:**

| Badge | Code | When to use |
|-------|------|-------------|
| Basilisk | `[![Basilisk](https://img.shields.io/badge/Basilisk-C-blue)](http://basilisk.fr)` | Any Basilisk project |
| Python | `[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)` | Python projects, specify min version |
| License | `[![License: GPL](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)` | Always include |
| Docs | `[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](URL)` | If docs site exists |
| CoMPhy Lab | `[![CoMPhy Lab](https://img.shields.io/badge/CoMPhy-Lab-orange)](https://EXAMPLE_ORG.org)` | Lab projects |
| DOI | `[![DOI](https://zenodo.org/badge/DOI/10.XXXX.svg)](https://doi.org/10.XXXX)` | If DOI exists |

---

## 2. Overview

**Purpose:** Quick understanding of what the project does and why it exists.

**Length:** 2-4 sentences (50-100 words)

**Structure:**
1. What the code simulates/analyzes
2. The physical phenomenon or problem addressed
3. Key capability or unique feature

**Example (Basilisk):**
```markdown
## Overview

Axisymmetric simulation of droplet impact on thin liquid films using the
Volume-of-Fluid method. This code investigates crown formation and splashing
dynamics across a range of Weber and Reynolds numbers. Includes adaptive mesh
refinement for resolving thin liquid sheets and satellite droplet formation.
```

**Example (Python):**
```markdown
## Overview

Post-processing toolkit for analyzing Basilisk simulation output. Extracts
velocity fields, computes vorticity, and generates publication-quality
visualizations. Supports both 2D Cartesian and axisymmetric geometries.
```

---

## 3. Physics/Theory

**Purpose:** Document the physical model and governing equations.

**Required for:** Basilisk simulations and physics-based Python codes.

**Subsections:**

### 3.1 Physical Setup

Describe the problem geometry and configuration:
```markdown
### Physical Setup

A spherical droplet of diameter $D$ impacts a quiescent liquid film of
thickness $h$ at velocity $U$. The simulation domain is axisymmetric
about the impact axis.
```

### 3.2 Governing Equations

Present the equations being solved:
```markdown
### Governing Equations

The incompressible Navier-Stokes equations with surface tension:

$$\nabla \cdot \mathbf{u} = 0$$

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \nabla \cdot (2\mu \mathbf{D}) + \sigma \kappa \delta_s \mathbf{n}$$

where $\mathbf{D}$ is the rate-of-strain tensor, $\kappa$ is the interface
curvature, and $\delta_s$ is the surface Dirac function.
```

### 3.3 Dimensionless Parameters

Use a table format:
```markdown
### Dimensionless Parameters

| Parameter | Definition | Physical Meaning |
|-----------|------------|------------------|
| $Re$ | $\rho U D / \mu$ | Inertia vs. viscous forces |
| $We$ | $\rho U^2 D / \sigma$ | Inertia vs. surface tension |
| $Oh$ | $\mu / \sqrt{\rho \sigma D}$ | Viscous vs. capillary forces |
| $h^*$ | $h / D$ | Film thickness ratio |
```

---

## 4. Dependencies/Requirements

**Purpose:** List everything needed to run the code.

**Format:**

```markdown
## Dependencies

### System Requirements
- Linux or macOS (tested on Ubuntu 22.04, macOS 14)
- GCC or Clang compiler
- Make build system

### Basilisk
- Basilisk C (http://basilisk.fr)
- Recommended: latest stable release

### Python (for post-processing)
- Python 3.8+
- numpy >= 1.20
- matplotlib >= 3.5
- scipy >= 1.7
```

**Best practices:**
- Specify minimum versions where critical
- Group by category (system, simulation, analysis)
- Include links for less common dependencies

---

## 5. Installation

**Purpose:** Step-by-step guide to get the code running.

**Structure:**
```markdown
## Installation

### Clone the Repository
```bash
git clone https://github.com/username/repo.git
cd repo
```

### Compile (Basilisk projects)
```bash
qcc -O2 -Wall simulation.c -o simulation -lm
```

### Install Python Dependencies (if applicable)
```bash
pip install -r requirements.txt
```
```

**Include:**
- Clone command with full URL
- Compilation command with recommended flags
- Any environment setup needed
- Verification command to test installation

---

## 6. Usage

**Purpose:** Show how to run the code with examples.

**Structure:**

### Basic Usage
```markdown
## Usage

### Basic Run
```bash
./simulation [LEVEL] [Re] [We] [tmax]
```

### Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `LEVEL` | Maximum refinement level | 9 |
| `Re` | Reynolds number | 1000 |
| `We` | Weber number | 100 |
| `tmax` | Maximum simulation time | 10.0 |
```

### Examples
```markdown
### Examples

**Low Weber number (no splashing):**
```bash
./simulation 9 1000 50 5.0
```

**High Weber number (splashing regime):**
```bash
./simulation 10 1000 500 3.0
```
```

---

## 7. File Structure

**Purpose:** Help users navigate the codebase.

**Format:**
```markdown
## File Structure

```
repo/
├── simulation.c          # Main simulation code
├── postprocess/
│   ├── extract.py        # Data extraction utilities
│   └── visualize.py      # Plotting functions
├── testcases/
│   ├── case1/            # Low We test case
│   └── case2/            # High We test case
└── docs/
    └── theory.md         # Extended theory documentation
```
```

**Include:**
- Main simulation files
- Post-processing scripts
- Test cases or examples
- Documentation

---

## 8. Output

**Purpose:** Document what the simulation produces.

**Structure:**
```markdown
## Output

### Log Files
- `log`: Simulation progress, timestep, max velocity
- `facets-*.gnu`: Interface position in Gnuplot format

### Snapshots
- `snapshot-*.dump`: Full field dumps at specified intervals
- Can be restored using Basilisk's `restore()` function

### Extracted Data
- `interface-*.dat`: Interface coordinates (r, z)
- `velocity-*.dat`: Velocity field on uniform grid
```

---

## 9. Citation

**Purpose:** Enable proper academic attribution.

**Format (published work):**
```markdown
## Citation

If you use this code in your research, please cite:

```bibtex
@article{Sanjay2024,
  title = {Droplet Impact on Liquid Films: A Numerical Study},
  author = {Sanjay, the user and Lohse, Detlef},
  journal = {Journal of Fluid Mechanics},
  year = {2024},
  volume = {980},
  pages = {A1},
  doi = {10.1017/jfm.2024.1}
}
```
```

**Format (unpublished):**
```markdown
## Citation

If you use this code, please cite this repository:

```bibtex
@software{RepoName2024,
  author = {Sanjay, the user},
  title = {Droplet Impact Simulation},
  year = {2024},
  url = {https://github.com/OWNER/repo-name}
}
```

And acknowledge Basilisk:

> Popinet, S. (2015). A quadtree-adaptive multigrid solver for the
> Serre–Green–Naghdi equations. Journal of Computational Physics, 302, 336-358.
```

---

## 10. License

**Purpose:** Clarify usage rights.

**Common choices for scientific code:**
- **GPL-3.0**: Copyleft, derivatives must be open source
- **MIT**: Permissive, minimal restrictions
- **BSD-3-Clause**: Permissive with attribution requirement

**Format:**
```markdown
## License

This project is licensed under the GNU General Public License v3.0 -
see the [LICENSE](LICENSE) file for details.
```

---

## 11. Author

**Purpose:** Attribution and contact information.

**Format:**
```markdown
## Author

**Your Name**
Email: AUTHOR_EMAIL
[CoMPhy Lab](https://EXAMPLE_ORG.org) · [Physics of Fluids](https://pof.tnw.utwente.nl)
University of Twente
```

---

## Section Order Recommendations

**Basilisk simulations:**
1. Title & Badges
2. Overview
3. Physics (Governing Equations, Parameters)
4. Dependencies
5. Installation
6. Usage
7. Output
8. File Structure
9. Citation
10. License
11. Author

**Python post-processing:**
1. Title & Badges
2. Overview
3. Dependencies
4. Installation
5. Usage
6. Data Formats
7. File Structure
8. Citation
9. License
10. Author

**Mixed codebase:**
1. Title & Badges
2. Overview
3. Physics (brief)
4. Dependencies
5. Installation
6. Usage (Simulation)
7. Usage (Post-processing)
8. Output
9. File Structure
10. Citation
11. License
12. Author
