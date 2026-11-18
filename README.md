# rayleigh-coding

Portable coding skills for Cursor Cloud Agents and local Cursor.

## Install (Import Marketplace)

1. Cursor → **Settings → Plugins → Import Marketplace**
2. Repository: `https://github.com/VatsalSy/rayleigh-coding`
3. Enable the **rayleigh-coding** plugin
4. Reload the window if needed and run `/coding-workflow`, or invoke an individual skill.

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

Use `coding-workflow` to scope, verify and review a change. The bundle also
includes GitHub delivery, security review, frontend, and deployment skills.

Version 0.6 removes the installer that wrote global model rules. If you used
it, review the model rules it created in
`~/.cursor/rules/rayleigh-models.mdc` and `.cursor/rules/rayleigh-models.mdc`.
Remove either file if you no longer want its rules. If you switched to a
marketplace install, check for a redundant local plugin symlink before removal.

## Checks

Install ripgrep and the Python test dependencies (`pytest` and `PyYAML`).

```bash
bash scripts/check_no_private_leakage.sh
bash scripts/check_executable_scripts.sh
python3 scripts/validate_marketplace.py
python3 scripts/validate_skills.py
python3 -m pytest -q scripts/tests plugins/rayleigh-coding/skills
bash scripts/check_history_hygiene.sh
```

## License

MIT for original content. Third-party skill subtrees keep their upstream
licences — see `THIRD_PARTY.md`.
