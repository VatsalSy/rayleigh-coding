# Gitignore Templates

## Python

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
.venv/
.env/

# Distribution / packaging
dist/
build/
*.egg-info/
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo

# Jupyter
.ipynb_checkpoints/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Type checking
.mypy_cache/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## C / C++

```gitignore
# Compiled objects
*.o
*.obj
*.so
*.dylib
*.a

# Executables
*.exe
*.out
a.out

# Build directories
build/
_build/
cmake-build-*/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Debug files
*.dSYM/

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## C (Basilisk CFD)

```gitignore
# OS specific files
**/.DS_Store
**/Thumbs.db
**/.Spotlight-V100
**/.Trashes

# Prerequisites
*.d

# Object files
*.o
*.ko
*.obj
*.elf

# Linker output
*.ilk
*.map
*.exp

# Precompiled Headers
*.gch
*.pch

# Libraries
*.lib
*.a
*.la
*.lo

# Shared objects (inc. Windows DLLs)
*.dll
*.so
*.so.*
*.dylib

# Executables
*.exe
*.out
*.app
*.i*86
*.x86_64
*.hex

# Debug files
*.dSYM/
*.su
*.idb
*.pdb

# Kernel Module Compile Results
*.mod*
*.cmd
.tmp_versions/
modules.order
Module.symvers
Mkfile.old
dkms.conf

# debug information files
*.dwo

# No _darcs
**/_darcs
**/.project_config

# Basilisk installation (local only)
basilisk/
**/.local-basilisk

# Case folders (4-digit case numbers: 1000-9999)
simulationCases/[0-9][0-9][0-9][0-9]/
**/docs/simulationCases/[0-9][0-9][0-9][0-9]/

# bview file
**/display.html

# SLURM output files
*.err
slurm-*.out
slurm-*.err

# Temporary sweep directories
.sweep_tmp_*

# postProcessing specific
**/getData*
**/getFacet*
**/getFootPrint
**/Video

# always add .c and .h
!*.c
!*.h
!*.sh
!*.sbatch

# Local install scripts (do not commit)
reset_install_*.sh

# Documentation generation artifacts
**/__pycache__/
**/*.pyc

# Timestamped CSS backups
**/custom_styles_backup_*.css

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```


## LaTeX / Manuscript

```gitignore
# LaTeX / manuscript build artefacts
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.lof
*.log
*.lot
*.nav
*.out
*.run.xml
*.snm
*.synctex.gz
*.toc
*.vrb
build/

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## JavaScript / TypeScript

```gitignore
# Dependencies
node_modules/
package-lock.json
yarn.lock
pnpm-lock.yaml

# Build output
dist/
build/
.next/
out/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Testing
coverage/
.nyc_output/

# Logs
*.log
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## Rust

```gitignore
# Generated files
/target/
Cargo.lock

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## Go

```gitignore
# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary
*.test

# Output
/bin/
/vendor/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## LaTeX

```gitignore
# Generated files
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
*.lof
*.lot
*.nav
*.snm
*.vrb

# Build directories
_minted-*/
auto/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## General / Minimal

```gitignore
# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Local CLAUDE.md (references AGENTS.md)
CLAUDE.md
```

## Usage

Combine templates as needed. For multi-language projects, merge relevant sections.

Example for Python + LaTeX project:
1. Start with Python template
2. Add LaTeX auxiliary file patterns
3. Remove duplicates (OS, IDE sections are common)
