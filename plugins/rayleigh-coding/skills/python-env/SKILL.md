---
name: python-env
description: >
  Use when asked which Python to use, how to run scripts locally, whether to
  use python3, pip, uv, or conda, where packages install, or when fixing
  Python environment confusion.
---

# python-env

Choose the right interpreter and package manager before running scripts.

## Defaults

| Situation | Prefer |
|---|---|
| Existing project with `.venv` / `uv.lock` / `poetry.lock` | That project's environment |
| New or greenfield project | `uv` |
| One-off script with declared deps | `uv run --with <pkg>` or a throwaway venv |
| System/Homebrew `python3` | Only when explicitly required |

Do not install scientific packages into a Homebrew-managed interpreter. PEP 668 (`externally-managed-environment`) will fight you.

## uv (preferred for new work)

```bash
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run python script.py
```

`uv run` may create a project-local `.venv`. That is correct for repo work and wrong if you intended a shared global env.

## pip + venv

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python script.py
```

## Decision rule

Use `uv` when creating a new project-local environment, managing per-repo deps, or the user asks for it.

Stay on the existing venv/`uv.lock` when the repo already has one. Do not invent a second environment beside it.

## Conda

Conda is not the baseline. Do not require it unless the repository already uses it.

## Gotchas

1. Raw `python3 -m pip install` into system Python often fails under PEP 668. Use a venv or `uv`.
2. Packages installed into one interpreter are invisible to another. Confirm `which python` before debugging imports.
3. Prefer project-local envs in Cloud Agent VMs. Shared home envs may not exist.
