---
name: dev-readme-writer
description: >
  Use when the user says "write readme", "create readme", "document this
  project", "readme for basilisk", or "scientific readme" for a Basilisk CFD
  or scientific-Python codebase. NOT for whole-repo restructuring.
---

# Scientific README Writer

## Audience gate

Treat a component README as public-candidate regardless of repository
visibility. Use precise, evidence-led, proportionate prose and exclude private
operational detail. Simulation-time findings and troubleshooting belong in
internal project records first; do not promote them here without the tracker
receipt `promotion approved — <finding> -> <target>` for this README. Follow
`shared-compute-dispatch/references/documentation-boundary.md`. Any README
figure creation or edit must also use `publication-plots`.

## Reader contract and Diataxis mode

Before exploring the repository, identify the README's primary reader and
their first successful outcome. Choose the dominant Diataxis mode for each
major section: tutorial for a first run, how-to for a known operation,
reference for parameters/API, and explanation for physics or design context.
Keep reader load explicit with prerequisites, expected outputs, ordered
commands, and links to deeper material. Do not turn a scientific README into a
generic essay or expose private operational detail.

Acceptance check: a reader can tell what the project is, what they need, how
to run one supported path, where to look up parameters, and what evidence
supports the scientific claims.

You are an expert of Basilisk C (basilisk.fr/src) and also an expert README writer. Generate publication-quality README files for Basilisk CFD simulations and scientific codebases.

## Basilisk Source Grounding

Before documenting or changing any Basilisk source, API, or numerics behaviour,
Skip Basilisk-specific steps when that skill is unavailable. Use a local Basilisk source index if available in
the mandatory order `symbol` (known identifier) → `search --scope source`
(behaviour) → `read` (surrounding implementation). Archiver may supply the user's
notes and project context, but it is not evidence for Basilisk implementation
claims.

## Critical Output Format

**ALWAYS nest your final README output in triple backticks so the user can copy-paste directly:**

```markdown
# Project Title
...content...
```

Only reply with the README.md content and nothing else after completing analysis.

## Workflow

### 1. Explore the Codebase

Before writing, inspect the directories that can answer the reader contract.
Check these key locations when they exist:

```
testCases/          # Simulation files, understand the physics
src-local/          # Custom headers, modifications to Basilisk
postProcess/        # Post-processing tools (if present)
```

**What to look for:**
- Main simulation `.c` files - extract physics, parameters, boundary conditions
- Custom headers in `src-local/` - understand modifications
- Parameter files (`.params`) - extract default values
- Existing scripts (`runSimulation.sh`, `runParameterSweep.sh`)
- Data files for initial conditions

### 2. Analyze and Extract

From the code, extract:
- **Physics**: Governing equations, dimensionless numbers, physical setup
- **Parameters**: Command-line arguments, their meanings and ranges
- **Structure**: File organization, what each component does
- **Running methods**: Serial, OpenMP, MPI options
- **Dependencies**: Basilisk headers used, custom modifications

### 3. Generate README

Follow the template structure below. Output ONLY the README content wrapped in code blocks.

---

## Template Structure (9 Sections)

### 1. Project Title and Badges

```markdown
# Project Title

[![Basilisk](https://img.shields.io/badge/Basilisk-C-blue)](http://basilisk.fr)
[![DOI](https://zenodo.org/badge/DOI/10.XXXX/zenodo.XXXXXXX.svg)](https://doi.org/10.XXXX/zenodo.XXXXXXX)
[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
```

- Project name should be descriptive
- Include DOI badge from Zenodo (if available)
- Include arXiv badge if preprint exists
- Include journal badge when published

### 2. Overview / Project Description

```markdown
## Overview

Brief description (2-3 sentences) of what the simulation does, the physical
phenomenon being studied, and key capabilities.

The article can be found at: [link to paper]
```

- Link to related paper/article
- Core focus of the research/project

### 3. Physics (Science-First Approach)

**This section is CRITICAL for scientific codebases.**

```markdown
## Physics

### Problem Description

[Describe the physical setup, geometry, initial conditions]

### Governing Equations

The simulation solves the incompressible Navier-Stokes equations:

$$\nabla \cdot \mathbf{u} = 0$$

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \nabla \cdot (2\mu \mathbf{D}) + \mathbf{f}$$

### Dimensionless Parameters

| Parameter | Definition | Physical Meaning |
|-----------|------------|------------------|
| $Re$ | $\rho U L / \mu$ | Inertia vs. viscous forces |
| $We$ | $\rho U^2 L / \sigma$ | Inertia vs. surface tension |
| $Oh$ | $\mu / \sqrt{\rho \sigma L}$ | Viscous vs. capillary forces |
| $Bo$ | $\rho g L^2 / \sigma$ | Gravity vs. surface tension |
```

### 4. Basilisk Installation (Modern Format)

**Use the ref-locked installation method:**

```markdown
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
```

### 5. Repository Structure

```markdown
## Repository Structure

```
├── simulationCases/           Main simulation code
│   ├── simulation.c          Primary simulation file
│   └── DataFiles/            Input geometry/initial conditions
├── src-local/                 Custom Basilisk headers
│   ├── custom-header.h       Project-specific modifications
│   └── parse_params.sh       Parameter parsing utilities
├── postProcess/               Post-processing tools
│   ├── getData.c             Field extraction utilities
│   ├── getFacet.c            Interface geometry extraction
│   └── Video.py              Visualization pipeline
├── runSimulation.sh           Single case runner
├── runParameterSweep.sh       Parameter sweep runner
├── default.params             Default configuration
└── sweep.params               Sweep configuration
```
```

### 6. Running Instructions

**Must include ALL execution methods:**

```markdown
## Running the Code

### Using Scripts (Recommended)

```bash
# Single simulation (serial)
./runSimulation.sh default.params

# With MPI (8 cores)
./runSimulation.sh --mpi --cores 8 default.params

# Parameter sweep
./runParameterSweep.sh sweep.params
```

### Manual Compilation

**Serial execution:**
```bash
qcc -O2 -Wall -disable-dimensions simulation.c -o simulation -lm
./simulation [args]
```

**OpenMP (shared memory):**
```bash
qcc -O2 -Wall -disable-dimensions -fopenmp simulation.c -o simulation -lm
export OMP_NUM_THREADS=8
./simulation [args]
```

**MPI (distributed memory):**
```bash
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions simulation.c -o simulation -lm
mpirun -np 8 ./simulation [args]
```

### Command Line Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `LEVEL` | Max refinement level | 10 | 7-12 |
| `Oh` | Ohnesorge number | 1e-2 | 1e-4 - 1 |
| `tmax` | Maximum time | 10.0 | > 0 |

### HPC Cluster Execution

For cluster environments (e.g., Snellius, Hamilton):
```bash
sbatch runSweepSnellius.sbatch
```
```

### 7. Post-Processing Tools

```markdown
## Post-Processing

The `postProcess/` directory contains analysis and visualization tools:

- `getData.c` - Extract field data on structured grids
- `getFacet.c` - Extract interface geometry
- `Video.py` - Generate frame-by-frame visualizations

### Usage
```bash
cd postProcess/
python Video.py ../simulationCases/
```
```

### 8. Citation Information

**Include BOTH paper and software citations:**

```markdown
## Citation

If you use this code in your research, please cite:

### Paper
```bibtex
@article{AuthorYear,
  title = {Paper Title},
  author = {Author, First and Author, Second},
  journal = {Journal of Fluid Mechanics},
  year = {2024},
  volume = {980},
  pages = {A1},
  doi = {10.1017/jfm.2024.XXX}
}
```

### Software
```bibtex
@software{RepoName2024,
  author = {Sanjay, the user},
  title = {Repository Title},
  year = {2024},
  publisher = {Zenodo},
  version = {v1.0},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://doi.org/10.5281/zenodo.XXXXXXX}
}
```
```

### 9. Authors and License

```markdown
## Authors

- **First Author** (Institution), [email@domain.com](mailto:email@domain.com)
- **Second Author** (Institution), [email@domain.com](mailto:email@domain.com)
- **Your Name** (Affiliation), [AUTHOR_EMAIL](mailto:AUTHOR_EMAIL)

## License

This project is licensed under the GNU General Public License v3.0 -
see the [LICENSE](LICENSE) file for details.
```

---

## Formatting Requirements

### Markdown Standards
- Use proper headers (`#` for main sections, `##` for subsections)
- Include code blocks with appropriate language tags (`bash`, `c`, `python`)
- Maintain consistent spacing between sections
- Use bullet points or numbered lists for clarity
- Include relative links to additional documentation

### LaTeX for Physics
- Inline math: `$Re = \frac{\rho U L}{\mu}$`
- Display math: `$$\nabla \cdot \mathbf{u} = 0$$`
- Escape backslashes in code blocks

### Code Block Language Tags
- Shell commands: ` ```bash `
- C code: ` ```c `
- Python: ` ```python `
- Plain text/structure: ` ```plaintext ` or ` ``` `

---

## Example READMEs

For reference, see these well-structured examples in `references/examples/`:

1. **Asymmetries-in-coalescence** - Best format for Basilisk installation and repo structure
2. **Bursting-Bubble-Viscoplastic** - Comprehensive physics documentation
3. **Viscoelastic-controller-b-Jets** - Full paper + software citation format
4. **BubblesOnString** - Viscoelastic implementation with external dependencies

---


## Gotchas

1. **Basilisk install format drifts** -- the `reset_install_basilisk-ref-locked.sh` URL and `--ref` tag change with each release. Always check the latest tag from EXAMPLE_ORG/basilisk-C releases; never hardcode an old ref.
2. **README output not in code fences = useless copy-paste** -- always wrap the final README in triple backticks (` ```markdown `) so the user can copy-paste directly. Plain Markdown output without the outer fence is the #1 cause of re-runs.
3. **LaTeX backslashes in code blocks need double-escaping** -- inside a Markdown code block that itself contains LaTeX, `\\nabla` (four backslashes) renders as `\nabla`. Missing escaping produces literal backslashes in the rendered README.
4. **Missing Physics section for CFD repos** -- omitting the governing equations section makes the README useless for scientific audiences. Always include dimensionless parameter table and equation block, even if brief.

## Decision Tree

```
Start
├── Explore testCases/ and src-local/
│   ├── Read main .c simulation files
│   ├── Extract physics and parameters
│   └── Understand custom headers
├── Determine project type
│   ├── Pure Basilisk simulation
│   ├── Simulation + post-processing
│   └── Scientific Python analysis
├── Gather missing information from user
│   ├── Paper/publication links
│   ├── Author affiliations
│   └── DOI/Zenodo information
├── Generate README following template
│   ├── Science-first (Physics section early)
│   ├── Modern Basilisk install format
│   └── Complete running instructions
└── Output in ``` code blocks ```
```

## References

- `references/sections-guide.md` - Detailed guidance for each section
- `references/templates/basilisk-simulation.md` - Basilisk project template
- `references/templates/scientific-python.md` - Python project template
- `references/templates/mixed-codebase.md` - Combined project template
