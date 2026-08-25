---
name: setup-rayleigh
description: >
  Install and initialize the rayleigh-coding plugin (skills + /vatsal-mode)
  for this Cursor environment and the user-global Cursor home. Writes the
  always-applied model rule with every role set to auto. Use for
  /setup-rayleigh, first-time install, "enable rayleigh-coding", or resetting
  rayleigh model defaults to auto.
---

# Setup rayleigh-coding

Install the **rayleigh-coding** plugin so its skills and `/vatsal-mode` are
available, then initialize model policy.

Unlike pstack setup: **do not ask which models to use.** Always write `auto`
for every role unless the human (or an agent already running under this
plugin) explicitly overrides a role in the same session.

## Goals

1. Plugin loadable in this environment (Cloud Agent env and/or local Cursor).
2. Same install available user-globally under `~/.cursor/plugins/local/`.
3. Always-applied model rule: every role is `auto`.
4. Confirm `/vatsal-mode` is the next step.

## Steps

### 1. Detect current state

Check, in order:

| Probe | Meaning |
|---|---|
| This skill is already executing from the plugin | Marketplace or local plugin is loaded for this session |
| `~/.cursor/plugins/local/rayleigh-coding/.cursor-plugin/plugin.json` exists | User-global local install present |
| Workspace `.cursor/rules/rayleigh-models.mdc` or `~/.cursor/rules/rayleigh-models.mdc` | Model rule already written |

Record what is missing. Do not invent host paths beyond `$HOME` / `~/.cursor`.

### 2. Install user-global (local plugin path)

Ensure Cursor can load the plugin from the documented local path. The loaded
directory itself must contain `.cursor-plugin/plugin.json` (nested marketplace
layout → symlink the nested plugin folder).

Prefer the bundled installer (handles absolute paths, git worktrees, dest
guards, and manifest validation):

```bash
bash <path-to-setup-rayleigh>/scripts/install_local.sh
```

`<path-to-setup-rayleigh>` is the directory that contains this `SKILL.md`
(plugin skills tree, local install, or marketplace cache). If you cannot
resolve that path, run the equivalent:

```bash
set -euo pipefail
mkdir -p ~/.cursor/plugins/local
SRC_RAW="${RAYLEIGH_CODING_SRC:-$HOME/.cursor/plugins/local/rayleigh-coding-src}"
SRC="$(python3 -c 'import os,sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' "$SRC_RAW")"
if git -C "$SRC" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  TOPLEVEL="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$(git -C "$SRC" rev-parse --show-toplevel)")"
  if [ "$TOPLEVEL" != "$SRC" ]; then
    echo "error: $SRC is inside git work tree $TOPLEVEL; set RAYLEIGH_CODING_SRC to the clone root" >&2; exit 1
  fi
  git -C "$SRC" pull --ff-only || echo "warning: pull failed; using existing tree"
elif [ -e "$SRC" ]; then
  echo "error: $SRC is not a git work tree" >&2; exit 1
else
  git clone https://github.com/VatsalSy/rayleigh-coding.git "$SRC"
fi
if [ ! -f "$SRC/scripts/validate_marketplace.py" ] || [ ! -f "$SRC/scripts/validate_skills.py" ]; then
  echo "error: missing validators under $SRC/scripts" >&2; exit 1
fi
python3 "$SRC/scripts/validate_marketplace.py"
python3 "$SRC/scripts/validate_skills.py"
DEST="$HOME/.cursor/plugins/local/rayleigh-coding"
if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then
  echo "error: $DEST exists and is not a symlink; remove or rename it" >&2; exit 1
fi
ln -sfn "$SRC/plugins/rayleigh-coding" "$DEST"
test -f "$DEST/.cursor-plugin/plugin.json"
echo "installed: $DEST -> $SRC/plugins/rayleigh-coding"
```

Optional override: set `RAYLEIGH_CODING_SRC` to an existing clone or worktree
(absolute or relative to the current working directory).

### 3. Marketplace / Cloud Agent environment

If this session is a Cursor Cloud Agent or the user prefers Import Marketplace:

1. Tell them (once): **Settings → Plugins → Import Marketplace** →
   `https://github.com/VatsalSy/rayleigh-coding` → enable **rayleigh-coding**.
2. For a Cloud Agents environment, enable the same marketplace plugin on that
   environment so new agent runs inherit it.
3. Ask them to **Developer: Reload Window** (or start a new agent) after install
   if skills are not yet visible.

Do not pretend the UI click succeeded without a receipt (plugin path present,
or this skill / `/vatsal-mode` resolving after reload).

### 4. Write model rules (always `auto`)

Default policy for rayleigh-coding: **every Task / subagent role uses `auto`**
(omit the Task `model` field so the child inherits the parent chat / Auto).

Touch **only** these two files when writable (never other `.cursor/rules`
files):

1. User-global: `~/.cursor/rules/rayleigh-models.mdc`
2. This workspace / env: `.cursor/rules/rayleigh-models.mdc`

Create parent directories as needed.

Managed role labels (one line each):

```text
default
code
judgment
review
swarm workers
parallel-task
```

**Normal install / re-run (not an explicit reset):**

- If the file is missing, create it with the shape below (all managed roles
  `auto`).
- If it exists, upsert only missing managed-role lines as `auto`. Keep any
  existing non-`auto` values and any extra lines or comments. Do not wipe the
  file.

**Explicit reset** ("reset to auto", "fresh model defaults"): overwrite the
whole file with the shape below.

Shape (new file or explicit reset):

```markdown
---
description: rayleigh-coding model choices (default auto; overrides skill defaults)
alwaysApply: true
---
# rayleigh-coding model configuration. One line per role.
# Policy: always `auto` unless a human or rayleigh-coding agent overwrites a line.
# `auto` / `inherit-parent`: omit Task `model` so the subagent follows the parent chat.
default: auto
code: auto
judgment: auto
review: auto
swarm workers: auto
parallel-task: auto
```

**Do not** prompt for model picks. Do not substitute named frontier slugs.

**Override rule:** only change a line away from `auto` when the human clearly
asks, or when an agent already operating under rayleigh-coding /
`/vatsal-mode` is told to pin a model for a role. Prefer editing the same rule
file over scattering one-off Task `model` arguments. After an override, say
which roles changed.

### 5. Confirm

Tell the user:

- Local plugin path (if installed) and whether marketplace enablement is still needed
- That both model rule paths were written or updated (or which one was skipped and why)
- Whether intentional non-`auto` overrides were preserved
- New chats / reloaded windows pick up the rule
- Next command: `/vatsal-mode`

Re-running `/setup-rayleigh` is safe: pull + relink + upsert `auto` defaults
(respecting the merge/reset rules in step 4).
