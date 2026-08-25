# .coderabbit.yaml templates

Repo-type-aware CodeRabbit configuration for new repositories. Pick the
template matching the detected project type, adapt the path filters to what
the repo *actually* contains, and write it to `.coderabbit.yaml` at the repo
root **before** `git add .` so it lands in the initial commit.

Core principle: **review the generators, not the generated.** If a repo
commits auto-generated output (HTML docs, rendered PDFs, search databases,
lockfiles), exclude that output via `path_filters` and point review effort at
the scripts that produce it (`.github/scripts/**`, `scripts/**`, figure
scripts). A filter list that hides source is worse than no config — when in
doubt, leave a path reviewable.

Shared conventions (all templates):

- Schema header line: `# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json`
- `language: "en-GB"` (lab standard; do not use en-US in new repos)
- `reviews.profile: "chill"`
- Point CodeRabbit at repo conventions: every repo has `AGENTS.md` as
  canonical (`CLAUDE.md` just defers to it, and is often gitignored) — the
  `path_instructions` below assume that
- `.coderabbit.yaml` must be **committed**, never listed in `.gitignore`
- Validate after writing: `coderabbit config validate`. If the CLI is absent,
  report that schema validation was unavailable and use an installed YAML
  parser for syntax validation; never silently claim the CodeRabbit check ran.

The CodeRabbit **CLI** honours this file too, so these filters improve guarded
local reviews in GitHub repositories even when the App is not installed.

## Basilisk / CFD simulation repo

For repos with `simulationCases/` + `src-local/` (common CFD layout).
Two docs conventions exist: legacy `docs/**` and current `.github/docs/**` —
keep both filters; the unused one is harmless.

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    # Auto-generated documentation site — review the generators in
    # .github/scripts/ instead, never the emitted HTML/assets.
    - "!docs/**"
    - "!.github/docs/**"
    # Vendored upstream Basilisk (gitignored in most repos, excluded for safety)
    - "!basilisk/**"
    # Simulation output and reference data, not source
    - "!**/reference-data/**"
    - "!**/*.tsv"
    - "!**/*.csv"
    - "!**/*.dat"
    - "!**/*.npz"
    - "!**/*.mp4"
    - "!**/*.png"
    - "!**/*.pdf"
  path_instructions:
    - path: "src-local/**"
      instructions: |
        Basilisk literate C: Markdown documentation lives inside /** */ comment
        blocks and is part of the source contract. Basilisk extends C with
        event/foreach constructs and @-macros; do not flag these as syntax
        errors. Headers like two-phase.h or navier-stokes/centered.h resolve
        from the upstream $BASILISK source tree, not this repository — do not
        report them as missing includes. Focus on: dimensional consistency,
        boundary-condition correctness, adaptivity criteria, and memory/field
        lifecycle.
    - path: "simulationCases/**"
      instructions: |
        Simulation entry points. Check parameter parsing against the .params
        conventions, CFL/timestep logic, event ordering, and output paths.
        Same Basilisk literate-C caveats as src-local.
    - path: "postProcess/**"
      instructions: |
        Python/C analysis tooling. Review as ordinary code: correctness of the
        physics extraction, file-handling robustness, and reproducibility.
    - path: ".github/scripts/**"
      instructions: |
        These scripts GENERATE the excluded docs site. Review them carefully —
        they are the reviewable surface for everything under docs/.
    - path: "AGENTS.md"
      instructions: |
        Canonical repo operating manual. Check for stale state, broken
        references, and contradictions with the actual repo layout.
  tools:
    # Standard C linters false-positive heavily on Basilisk literate C
    cppcheck:
      enabled: false
    shellcheck:
      enabled: true
    ruff:
      enabled: true
    markdownlint:
      enabled: true
    actionlint:
      enabled: true
```

## Python project

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    - "!**/*.lock"
    - "!dist/**"
    - "!build/**"
    - "!**/__pycache__/**"
    - "!**/*.ipynb_checkpoints/**"
  path_instructions:
    - path: "**/*.py"
      instructions: |
        Follow the repo's AGENTS.md conventions. Prefer stdlib-only unless the
        project declares dependencies (PEP 723 inline metadata or
        pyproject.toml). Check error handling on file and subprocess
        operations.
  tools:
    ruff:
      enabled: true
    markdownlint:
      enabled: true
    actionlint:
      enabled: true
```

## LaTeX manuscript repo

Minimal config. Manuscript prose review stays human/writer-skill territory;
CodeRabbit adds value only on figure/analysis scripts and build tooling.
Exclude all rendered/compiled artefacts.

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    # Compiled/rendered artefacts
    - "!build/**"
    - "!**/*.pdf"
    - "!**/*.bbl"
    - "!**/*.aux"
    - "!**/*.log"
    - "!**/*.out"
    - "!**/*.fls"
    - "!**/*.fdb_latexmk"
    - "!**/*.synctex.gz"
    # Figure binaries and data
    - "!**/*.png"
    - "!**/*.jpg"
    - "!**/*.ai"
    - "!**/*.xlsx"
    - "!**/*.dat"
  path_instructions:
    - path: "**/*.tex"
      instructions: |
        Do not review scientific prose, style, or wording — that is handled
        elsewhere. Restrict findings to: undefined references or citation
        keys, label duplication, broken \input/\includegraphics paths, and
        environment-balance errors.
    - path: "**/figures/**/*.py"
      instructions: |
        Figure-generation scripts: review as ordinary Python — data-path
        robustness, deterministic output, no hardcoded absolute paths.
  tools:
    ruff:
      enabled: true
    shellcheck:
      enabled: true
```

## Infrastructure / CLI repo (fleet tooling, YAML inventories)

For repos whose content includes intentional operational detail (hostnames,
SSH public-key fingerprints, tailnet names). Suppress secret scanners only
when the repo genuinely holds such inventory data — keep them on otherwise.

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    - "!dist/**"
    - "!**/fonts/**"
    # Append-only operational history, never reviewable
    - "!reservations/history/**"
  path_instructions:
    - path: "bin/**"
      instructions: |
        Operational CLI tooling. Prioritise fail-closed behaviour, input
        validation on anything reaching a shell, and schema consistency with
        the repo's declared JSON Schemas.
    - path: "inventory/**"
      instructions: |
        Hostnames, storage IDs, and SSH public-key fingerprints here are
        intentional repository content, not leaks. Do not raise
        secret-scanning or privacy findings on them. Do check referential
        integrity against the schemas.
    - path: "reservations/**"
      instructions: |
        Machine-written operational state committed directly to main by
        agent tooling as part of the compute-dispatch hot path. Restrict
        findings to schema-shape drift and referential integrity (unknown
        host/storage IDs, malformed slugs, impossible capacity values).
        No style, naming, or structural suggestions — these files are not
        hand-edited and a review must never delay a reservation.
    - path: "services/**"
      instructions: |
        systemd units and shell helpers that run unattended on fleet hosts.
        Review restart/failure semantics and quoting rigorously.
  tools:
    shellcheck:
      enabled: true
    ruff:
      enabled: true
    yamllint:
      enabled: true
    actionlint:
      enabled: true
    # Only disable these when the repo holds intentional infra inventory:
    gitleaks:
      enabled: false
    trufflehog:
      enabled: false
```

## Website / JavaScript repo (Jekyll, Node tooling)

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    - "!_site/**"
    - "!node_modules/**"
    - "!coverage/**"
    - "!**/*.min.js"
    - "!**/*.min.css"
    - "!assets/**/*.woff"
    - "!assets/**/*.woff2"
    - "!assets/**/*.ttf"
    - "!assets/**/*.eot"
    - "!assets/images/**"
    - "!assets/videos/**"
    - "!assets/logos/**"
    - "!assets/pdf-files/**"
    - "!Gemfile.lock"
    - "!package-lock.json"
  path_instructions:
    - path: "_data/**/*.yml"
      instructions: |
        Data-driven content files with fixed schemas consumed by templates.
        Check schema-shape consistency with existing entries (keys, date
        formats, ordering) rather than YAML style.
    - path: "scripts/**"
      instructions: |
        Build/deploy/validation scripts — the reviewable surface for the
        generated site. Review path handling and failure modes carefully.
  tools:
    eslint:
      enabled: true
    markdownlint:
      enabled: true
    yamllint:
      enabled: true
    actionlint:
      enabled: true
    shellcheck:
      enabled: true
```

## General / minimal (fallback)

For mixed or unclear repos. Safe default: no exclusions beyond obvious
artefacts, lab language settings, AGENTS.md pointer.

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-GB"
early_access: false

reviews:
  profile: "chill"
  high_level_summary: true
  path_filters:
    - "!dist/**"
    - "!build/**"
    - "!**/*.lock"
  path_instructions:
    - path: "AGENTS.md"
      instructions: |
        Canonical repo operating manual; CLAUDE.md defers to it. Check for
        stale or contradictory instructions.
```

## Usage

1. Detect repo type (language detection step in SKILL.md).
2. Ask one question only if genuinely ambiguous AND the repo commits
   generated output whose location you cannot infer — otherwise pick the
   closest template and adapt silently.
3. Interrogate the actual tree before writing: which generated paths exist
   (`docs/`, `.github/docs/`, `build/`, `_site/`)? Which languages? Drop
   filter lines that reference paths the repo will never have only if you are
   sure; keeping them is harmless.
4. Write `.coderabbit.yaml`, then run `coderabbit config validate` if the CLI
   is available.
5. Never add `.coderabbit.yaml` to `.gitignore`; it must ship in the initial
   commit.
