# Documentation Reference Templates

Minimal, copy-paste-ready templates demonstrating literate programming patterns for the CoMPhy Lab documentation system.

## Templates

| Template | Use When | Key Patterns |
|----------|----------|--------------|
| `template_utility.c` | Writing data extraction, post-processing utilities | Workflow docs, extensibility guidance, CLI usage |
| `template_simulation.c` | Writing physics simulations | Physics context, parameters, boundary conditions, events |
| `template_module.py` | Writing Python modules | Module docstring (before imports!), section blocks, dataclasses |
| `template_header.h` | Writing header files | Header guards, struct docs, function declarations |

## How to Use

1. Copy the relevant template to your project
2. Replace placeholder content with your actual code
3. Keep the documentation structure—it renders to beautiful HTML via `generate_docs.py`

## Pattern Quick Reference

### C/H Files: `/** */` Blocks

```c
/**
# File Title

Description here. This becomes HTML prose.

## Section Name

More prose. Markdown works: **bold**, `code`, $LaTeX$.
*/
code_here();  // This becomes syntax-highlighted code block
```

### Python Files: Triple-Quote Docstrings

```python
"""
# Module Title

Description. MUST come before imports!
"""

import something

"""
## Section Header

Standalone docstrings between code become prose sections.
"""

code_here()
```

## Real-World Examples

These templates are distilled from production code:

- **C utility**: Based on `postProcess/getData.c` from Bursting-Bubble
- **C simulation**: Based on `simulationCases/burstingBubble.c`
- **Python module**: Based on `postProcess/Video.py`
