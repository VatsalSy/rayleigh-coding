# AGENTS.md Template

AGENTS.md provides context for AI assistants working with the codebase. Keep it concise and focused on what an AI needs to know.

## Standard Template

```markdown
# Project Name

Brief description of what this project does.

## Structure

\`\`\`
project/
├── src/          # Source code
├── tests/        # Test files
├── docs/         # Documentation
└── config/       # Configuration
\`\`\`

## Development

\`\`\`bash
# Build command
make build

# Run tests
make test

# Run locally
make run
\`\`\`

## Guidelines

- [Key coding conventions for this project]
- [Important patterns to follow]
- [Things to avoid]
```

## Variations by Project Type

### Research / Scientific Code

```markdown
# Project Name

[One line: what scientific problem this addresses]

## Structure

\`\`\`
project/
├── simulations/  # Simulation code
├── analysis/     # Data analysis scripts
├── data/         # Input/output data
└── figures/      # Generated plots
\`\`\`

## Running Simulations

\`\`\`bash
# Compile
make

# Run simulation
./simulation params.txt
\`\`\`

## Guidelines

- Units: [SI/CGS/dimensionless]
- Data format: [description]
- Naming: [conventions]
```


### Paper / LaTeX

```markdown
# Project Name

[One line about the manuscript and target venue]

## Structure

```text
project/
├── main.tex
├── references.bib
├── figures/
├── build/
├── compile_tex.sh
├── check_citations.sh
├── paperctl.sh
└── Makefile
```

## Development

```bash
# Preferred front door
./paperctl.sh build

# Citation check only
./paperctl.sh check

# Clean
./paperctl.sh clean

# Or native make
make
```

## Guidelines

- Journal class: [PRF / PRL / etc.]
- Author block: use `references/latex-paper-template.md`
- Keep generated aux files out of version control
- Prefer the hybrid wrapper when the repo has both Makefile and shell scripts
```

### Python Project

```markdown
# Project Name

Brief description.

## Structure

\`\`\`
project/
├── src/          # Main source
├── tests/        # pytest tests
├── pyproject.toml
└── requirements.txt
\`\`\`

## Development

\`\`\`bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -e .

# Test
pytest

# Lint
ruff check .
\`\`\`

## Guidelines

- Style: Follow PEP 8
- Types: Use type hints
- Tests: pytest with coverage
```

### JavaScript/TypeScript Project

```markdown
# Project Name

Brief description.

## Structure

\`\`\`
project/
├── src/          # Source code
├── tests/        # Test files
├── package.json
└── tsconfig.json
\`\`\`

## Development

\`\`\`bash
# Install
npm install

# Dev server
npm run dev

# Build
npm run build

# Test
npm test
\`\`\`

## Guidelines

- Style: ESLint + Prettier
- Types: Strict TypeScript
- Components: [patterns used]
```

### C / Basilisk CFD Project

```markdown
# Project Name

Brief description of simulation/study.

## Structure

\`\`\`
project/
├── *.c           # Basilisk source files
├── Makefile      # Build configuration
├── params/       # Parameter files
└── postproc/     # Post-processing scripts
\`\`\`

## Building

\`\`\`bash
# Compile with qcc
qcc -O2 -Wall simulation.c -o simulation -lm

# Or use Makefile
make
\`\`\`

## Running

\`\`\`bash
./simulation [options]
```

## Guidelines

- Use Basilisk conventions for field names
- Grid: [adaptive/fixed, typical resolution]
- Output: [formats used]
```

## Key Principles

1. **Concise**: Only include what AI needs to know
2. **Actionable**: Include actual commands that work
3. **Structured**: Use consistent sections
4. **Current**: Keep updated with project evolution
5. **Specific**: Tailor to the project, not generic advice
