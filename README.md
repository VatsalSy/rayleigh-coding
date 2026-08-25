# rayleigh-coding

Public **Cursor marketplace** for coding skills and **`/vatsal-mode`**.

This is a curated downstream distribution for Cursor Cloud Agents and local
Cursor — not a regex-scrubbed mirror of a private skill catalogue.

## Install (Import Marketplace)

1. Cursor → **Settings → Plugins → Import Marketplace**
2. Repository: `https://github.com/VatsalSy/rayleigh-coding`
3. Enable the **rayleigh-coding** plugin
4. Reload the window if needed, then run `/vatsal-mode`

### Local install (plugin directory, not marketplace root)

Cursor loads a plugin from a directory that itself contains
`.cursor-plugin/plugin.json`. Clone the repo, then point the local plugin path
at the nested plugin:

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
  skills.allowlist          # shipped skill names only
  skills/
  docs/
scripts/                    # public gates (no confidential denylist values)
.github/workflows/privacy-check.yml
THIRD_PARTY.md
```

## Public runtime contract

Every shipped skill must be usable without private sibling skills, private
profile/tracker services, or fleet hosts. Skills that cannot meet that bar are
kept out of `skills.allowlist`.

Confidential denylists and exporters stay private. CI may optionally inject
extra patterns via the `PRIVACY_EXTRA_PATTERN` repository secret.

## What is included

See `plugins/rayleigh-coding/docs/SKILLS.md` and `skills.allowlist`.

## Privacy and release gates

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
