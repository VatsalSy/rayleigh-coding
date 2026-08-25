# README Template

## Standard Structure

```markdown
# Project Name

Brief one-line description of what the project does.

## Overview

2-3 sentences explaining the purpose and key functionality. What problem does it solve? Who is it for?

## Features

- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Installation

```bash
# Installation commands
```

## Usage

```bash
# Basic usage example
```

## License

[License type] - see LICENSE for details.
```

## Variations by Project Type

### Research / Scientific Code

```markdown
# Project Name

Brief description of the research focus.

## Overview

Description of the scientific problem being addressed.

## Citation

If you use this code, please cite:

```bibtex
@article{...}
```

## Requirements

- Dependency 1
- Dependency 2

## Usage

Instructions for running simulations/analysis.

## Data

Description of input/output data formats.

## License

[License] - see LICENSE for details.
```


### Paper / LaTeX

```markdown
# Paper Title

One-line description of the manuscript and target venue.

## Overview

Short summary of the paper, target journal, and the problem it addresses.

## Build

```bash
make
# or
./paperctl.sh build
```

## Check citations

```bash
./paperctl.sh check
```

## Clean

```bash
./paperctl.sh clean
```

## Main files

- `main.tex`
- `references.bib`
- `figures/`
- `build/`

## Authors / affiliations

Use the template in `references/latex-paper-template.md`.

## License

[License] - see LICENSE for details.
```

### Library / Package

```markdown
# Library Name

Brief description of what the library provides.

## Installation

```bash
pip install library-name
# or
npm install library-name
```

## Quick Start

```python
from library import function

result = function(args)
```

## API Reference

Brief overview or link to full documentation.

## License

[License] - see LICENSE for details.
```

### Tool / CLI Application

```markdown
# Tool Name

Brief description of what the tool does.

## Installation

```bash
# Installation instructions
```

## Usage

```bash
tool-name [options] <args>
```

### Options

- `-h, --help`: Show help
- `-v, --verbose`: Verbose output

## Examples

```bash
# Example 1
tool-name input.txt -o output.txt

# Example 2
tool-name --config config.yaml
```

## License

[License] - see LICENSE for details.
```

## Guidelines

1. **Keep it concise**: Users want to understand quickly what the project does
2. **Show, don't tell**: Include code examples for usage
3. **Installation first**: Make it easy for users to get started
4. **Adapt to project**: Not all sections needed for every project
5. **Update as needed**: README should evolve with the project
