# rayleigh-coding

Cursor marketplace for coding skills and **`/vatsal-mode`**.

Built for Cursor Cloud Agents and local Cursor.

## Install (Import Marketplace)

1. Cursor → **Settings → Plugins → Import Marketplace**
2. Repository: `https://github.com/VatsalSy/rayleigh-coding`
3. Enable the **rayleigh-coding** plugin
4. Reload the window if needed, then run `/setup-rayleigh`, then `/vatsal-mode`

`/setup-rayleigh` installs the plugin into your user-global local plugins path
when needed, and writes always-applied model rules with every role set to
**auto** (unlike multi-model setups that ask you to pick slugs). Override a
role only when you or an agent using this plugin pin one explicitly.

### Local install

Cursor loads a plugin from a directory that itself contains
`.cursor-plugin/plugin.json`. Clone the repo, then symlink the nested plugin:

```bash
mkdir -p ~/.cursor/plugins/local
git clone https://github.com/VatsalSy/rayleigh-coding.git ~/.cursor/plugins/local/rayleigh-coding-src
ln -sfn ~/.cursor/plugins/local/rayleigh-coding-src/plugins/rayleigh-coding \
  ~/.cursor/plugins/local/rayleigh-coding
```

Reload Cursor (**Developer: Reload Window**). Update with:

```bash
git -C ~/.cursor/plugins/local/rayleigh-coding-src pull
```

## Layout

```
.cursor-plugin/marketplace.json
plugins/rayleigh-coding/
  .cursor-plugin/plugin.json
  skills.manifest
  skills/
  docs/
scripts/
.github/workflows/privacy-check.yml
THIRD_PARTY.md
```

## What is included

See `plugins/rayleigh-coding/docs/SKILLS.md`.

Highlights: `/setup-rayleigh`, `/vatsal-mode`, planning and verification,
git/PR workflows, security review helpers, frontend craft, and common deploy
CLIs.

## Checks

```bash
bash scripts/check_no_private_leakage.sh
bash scripts/check_executable_scripts.sh
python3 scripts/validate_marketplace.py
python3 scripts/validate_skills.py
python3 -m pytest plugins/rayleigh-coding/skills/code-review/tests -q
bash scripts/check_history_hygiene.sh
```

## License

MIT for original content. Third-party skill subtrees keep their upstream
licences — see `THIRD_PARTY.md`.
