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

Run the bundled installer when you can resolve this skill on disk:

```bash
bash <path-to-setup-rayleigh>/scripts/install_local.sh
```

`<path-to-setup-rayleigh>` is the directory that contains this `SKILL.md`
(plugin skills tree, local install, or marketplace cache). If you cannot
resolve that path, run the equivalent:

```bash
mkdir -p ~/.cursor/plugins/local
SRC="${RAYLEIGH_CODING_SRC:-$HOME/.cursor/plugins/local/rayleigh-coding-src}"
if [ ! -d "$SRC/.git" ]; then
  git clone https://github.com/VatsalSy/rayleigh-coding.git "$SRC"
else
  git -C "$SRC" pull --ff-only
fi
ln -sfn "$SRC/plugins/rayleigh-coding" ~/.cursor/plugins/local/rayleigh-coding
test -f ~/.cursor/plugins/local/rayleigh-coding/.cursor-plugin/plugin.json
```

Optional override: set `RAYLEIGH_CODING_SRC` to an existing clone (for example a
workshop checkout) instead of cloning into `~/.cursor/plugins/local/`.

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

Write **both** when writable:

1. User-global: `~/.cursor/rules/rayleigh-models.mdc`
2. This workspace / env: `.cursor/rules/rayleigh-models.mdc`

Create parent directories as needed. Overwrite the whole file so re-runs stay
idempotent. Shape:

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

If a prior rule has non-`auto` values and the user asked for a fresh setup
(or "reset to auto"), overwrite back to the shape above. If they only asked
to install and the file already has intentional overrides, keep those lines
and report them — still fill any missing roles with `auto`.

### 5. Confirm

Tell the user:

- Local plugin path (if installed) and whether marketplace enablement is still needed
- That both model rule paths were written (or which one was skipped and why)
- New chats / reloaded windows pick up the rule
- Next command: `/vatsal-mode`

Re-running `/setup-rayleigh` is safe: pull + relink + rewrite `auto` defaults
(respecting the override rule in step 4).
