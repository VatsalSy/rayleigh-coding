---
name: skill-creator
description: >
  Use when the user says "create/update/migrate a skill", "promote this to a
  skill", "sharpen this description", or asks whether something is skill or
  memory. NOT for one-off scripts or edits that need no reusable workflow.
---

# Skill Creator

## The three-tier skill system

| Tier | Location | Use when |
|------|----------|----------|
| **Shared** | `<skills-dir>/<name>/` | Cross-agent, cross-project workflows (e.g. notes, weather, slack) |
| **Agent-specific** | `<agent-workspace>/skills/<name>/` | One agent owns this; other agents shouldn't see it (e.g. email agent's `literature-paper-triage`) |
| **Repo-specific** | `<repo-root>/.agents/skills/<name>/` | Scoped to a single codebase; activated via overlay script |

**Precedence (highest to lowest):**
1. `<workspace>/skills/<name>/` — agent workspace override
2. `<skills-dir>/<name>/` — shared custom skills
3. Bundled Claude Code skills
4. `skills.load.extraDirs` config

Repo overlay: `scripts/repo-skill-overlay.py activate <repo-root>`
Deactivate: `scripts/repo-skill-overlay.py deactivate`

---

## Skill vs. Memory — the critical distinction

| It's a **skill** when... | It's **memory** when... |
|--------------------------|-------------------------|
| It describes a workflow or set of steps to follow | It stores state, feedback, or configuration data |
| It instructs an agent HOW to do something | It records WHAT happened or what preferences are |
| It needs to trigger on specific task types | It needs to be read and written across runs |
| Example: `literature-pipeline/SKILL.md` | Example: `literature-triage-feedback.json` |

**Rule of thumb:** if you find yourself putting step-by-step instructions in a `.md` file inside `memory/`, it should be a skill instead.

---

## Skill taxonomy — nine types

Before building, classify what you're making. The best skills fit cleanly into one category:

| # | Type | What it does | Our examples |
|---|------|-------------|-------------|
| 1 | **Library & API Reference** | How to use a CLI, library, or SDK correctly; edge cases + gotchas | `domain-solver-docs`, `http-cli-example`, `python-env` |
| 2 | **Product Verification** | Test / verify that code or a workflow is working; paired with playwright, tmux, etc. | (gaps here — worth building) |
| 3 | **Data Fetching & Analysis** | Connect to data stacks; dashboard IDs, query patterns, credentials | `personal-notes-search`, `memory-query` |
| 4 | **Business Process & Automation** | Automate a repetitive workflow into one command | `daily-focus-planner`, `archiver-reminders-sync`, `github-reminders-sync` |
| 5 | **Code Scaffolding & Templates** | Generate boilerplate for a specific pattern; natural-language requirements | `solver-project-scaffold`, `git-repo-init` |
| 6 | **Code Quality & Review** | Enforce standards; spawn adversarial reviewers; run lint/style | `dev-review-ultra`, `dev-docstring`, `dev-commit-message` |
| 7 | **CI/CD & Deployment** | Fetch, push, deploy code; babysit PRs; handle CI failures | `gh-fix-ci`, `gh-pr-create`, `gh-pr-triage` (GitHub); `origin-pr-create`, `origin-babysit-pr` (Origin/Bugbot) |
| 8 | **Runbooks** | Take a symptom → multi-tool investigation → structured report | `domain-solver-docs` (partial) |
| 9 | **Infrastructure & Operations** | Routine maintenance; destructive actions with guardrails | (gaps — e.g. NAS/sim storage operations) |

Skills that straddle multiple categories are usually too broad — split them.


---

## Skill structure

```text
skill-name/
├── SKILL.md          (required — frontmatter + workflow body)
├── scripts/          (optional — deterministic helper scripts)
├── references/       (optional — long docs loaded on demand, not at trigger)
└── assets/           (optional — templates, output formats, binaries)
```

Keep `SKILL.md` concise. Heavy reference material goes in `references/` so it doesn't bloat context.

**Progressive disclosure:** Tell Claude what files are in the skill folder — it will read them at the right time. Split detailed API signatures into `references/api.md`, put output templates in `assets/`, store helper scripts in `scripts/`. This lets the model load only what it needs. Skills that try to inline everything become too heavy and degrade performance.

**Memory within a skill:** If the skill needs state across runs (e.g. a standup-post that logs every post it's made), store it in a stable path outside the skill folder (e.g. `memory/<skill-name>-state.json`). Data in the skill directory can be wiped on upgrade.

---

## Frontmatter

Required:
```yaml
---
name: hyphen-case-name
description: Trigger conditions ONLY — when to pull this skill in, not what it does. Lead with "Use when the user says…". One NOT-for clause max, naming the confused sibling.
---
```

Optional frontmatter keys (use only when genuinely needed):
- `metadata` — single-line JSON object for structured tags
- `user-invocable` — expose as a user-callable command
- `disable-model-invocation` — force tool-only execution
- `command-dispatch` / `command-tool` / `command-arg-mode` — CLI integration

**The description field is for the model, not for humans.**
When Claude Code starts a session, it builds a listing of every skill with its description. That listing is what the model scans to decide "is there a skill for this?" — so the description is a trigger condition, not a summary. Write it as: "Use when: [exact phrases the user or model will produce]."

**Hard length cap: 1024 characters.** The runtime rejects any skill whose description (after YAML folding) exceeds 1024 chars with `invalid description: exceeds maximum length of 1024 characters`. The skill never loads. Always check before committing — `quick_validate.py` enforces this, but you can also count manually:

```bash
# Count the description text (strip frontmatter delimiters, the `description:` key, and the YAML fold marker)
python3 -c "import yaml,sys; d=yaml.safe_load(open('path/to/SKILL.md').read().split('---',2)[1])['description'].strip(); print(len(d))"
```

If you're brushing up against the cap: cut redundant trigger phrases first, then NOT-for clauses, then prose. Do not split the description across YAML keys — only `description:` is read at trigger time.

**Description doctrine (house rule, 2026-08):**
Every description is paid for in every session, in every model, whether or not
the skill fires; the body is free until triggered. So the description's ONLY
job is triggering — anything the model needs *while running* the skill lives
in the body.

- Target **≤40 words** (~250 chars); hard cap 60 words. The 1024-char runtime
  cap is a ceiling, never a target.
- Lead with trigger phrases: `Use when the user says "X", "Y", asks to Z, or a
  <file-type> appears with <intent>.`
- Keep distinctive trigger nouns (CLI names, journal names, `$name` aliases,
  file extensions) — they are the keywords that make routing reliable.
- One NOT-for clause max, and only when a sibling skill genuinely collides;
  name the sibling. Family routing tables belong in `SKILLS-POLICY.md`, not in
  descriptions.
- Never describe outputs, modes, or capabilities. If the description alone
  answers the question, the skill body is dead weight — move the content or
  delete the skill.

**Bad:** "Convert PDFs to Markdown with full content preservation — text,
equations (LaTeX), tables, and figure descriptions via multimodal Read. For
Obsidian-compatible notes from academic papers, reports, books."
**Good:** "Use when the user says 'pdf to md', 'convert/transcribe this pdf',
or wants a paper PDF as Markdown."

---

## Writing skills for Opus 4.7

The default model on this machine is Opus 4.7. Its behaviour differs from 4.6 in ways that matter when authoring skills:

- **Adaptive thinking is always on; fixed thinking budgets are gone.** Do not write `ultrathink`, `think hard for N seconds`, or any numeric budget — they're inert. To nudge thinking, use the exact phrases the model was trained on:
  - More reasoning: *"Think carefully and step-by-step before responding; this problem is harder than it looks."*
  - Less reasoning: *"Prioritize responding quickly rather than thinking deeply. When in doubt, respond directly."*
- **4.7 reasons more and calls tools less by default.** If a step depends on a tool actually firing (web_search, gh CLI, MCP, Bash), say "call X" or "run X" explicitly. Hints will be skipped.
- **4.7 spawns fewer subagents by default.** If a step benefits from parallel subagents, spell it out: *"Dispatch 3 Explore agents in parallel, one each for A, B, C."* Vague "investigate broadly" prompts now stay in the main thread.
- **Response length calibrates to task complexity.** Skip arbitrary caps ("respond in under 50 words") unless the output format has a real limit (Slack post, email subject, cron expression). Otherwise the model already trims simple answers and expands complex ones.
- **Positive voice examples beat negative ones for style/tone.** In writer-* and style skills, show a short passage of the target voice rather than listing anti-patterns. Safety rules ("never commit secrets", "don't force-push") stay in the negative — this point is narrowly about *voice*, not *constraints*.
- **Treat the agent as a capable engineer you're delegating to.** State intent, constraints, acceptance criteria, and file locations up front. Skip line-by-line micromanagement of routine subtasks.

Quick sanity check before shipping a new skill:
```
rg -i "ultrathink|extended thinking|thinking budget|think hard" path/to/skill/
```
Zero hits expected.

---

## Creation workflow

### 1. Decide scope
- Will any agent or session ever need this? → **Shared** (`<skills-dir>/`)
- Is this owned by one specific agent (e.g. email agent, main)? → **Agent-specific** (`<workspace>/skills/`)
- Is this scoped to a single repo's codebase? → **Repo-specific** (`<repo>/.agents/skills/`)

### 2. Create the directory and SKILL.md
```bash
mkdir -p <location>/<skill-name>
# write SKILL.md with frontmatter + workflow steps
```

Or use the init script:
```bash
python3 <skills-dir>/skill-creator/scripts/init_skill.py <name> --location <shared|agent|repo>
```

### 3. Write the SKILL.md body
Structure that works:
- **Purpose** — one paragraph, plain English
- **Trigger signals** — what input/context causes this to run
- **Step-by-step workflow** — numbered, unambiguous
- **Gotchas** ⭐ — the highest-signal section; built from real failure modes Claude hits when using this skill. Start with at least 2–3, update as more emerge.
- **Constraints** — what NOT to do (as important as what to do)
- **Dependencies** — other skills, files, tools needed

Don't state the obvious. Focus on information that pushes Claude out of its default behaviour. If Claude already does something correctly 95% of the time, skip it.

### 4. If migrating from a memory file
- Copy the content into a proper SKILL.md with frontmatter
- Remove the old memory file
- Commit both changes together with a clear message:
  `refactor: migrate <name> from memory to skill`

### 5. Validate
```bash
python3 <skills-dir>/skill-creator/scripts/quick_validate.py <path-to-skill>
```

Checks:
- frontmatter has `name` and `description`
- folder name matches `name`
- `description` ≤ 1024 chars (runtime cap; over-limit skills fail to load)
- no broken file references

Run this **before** committing. A failed length check at runtime means the skill silently disappears from the catalogue.

### 6. Test
Start a fresh session (or wait for watcher refresh) and verify the skill triggers on the expected input. If it doesn't:
- Tighten the `description` trigger wording
- Check file path precedence (see three-tier table above)
- Confirm folder name = `name` in frontmatter

---

## Updating an existing skill

1. Read current SKILL.md first — never overwrite without reading
2. Make targeted edits (use `edit` tool for surgical changes, `write` for full rewrites)
3. If changing `description`, test triggering in a fresh session
4. Commit with `update: <skill-name> — <what changed>`

### Evidence and acceptance gate

Before editing an existing skill, record a compact internal finding with the
observed trigger or workflow failure, its evidence source, the smallest useful
change, and a testable acceptance check. Prefer an executable validator or
trigger check over repeating a policy paragraph. Do not infer a broad rewrite
from a cosmetic complaint or an unrelated transcript sweep.

When the user explicitly requests a local scoped patch or forbids Git/network
work, skip branch, commit, and PR steps. Edit only the named skills, run the
available validator, and report the local result.

---

## Gotchas

1. **Never trust a third-party skill installer or registry entry just because the repo name looks right.** Namespace confusion and resolver bugs are real. If using an external skill for inspiration, read the actual source files first and treat the installed artifact as untrusted until inspected.

2. **Do not copy opaque payloads into a new skill.** If an external skill contains base64 blobs, curl|bash patterns, raw-IP fetches, plain-HTTP downloads, eval/exec wrappers, or other obfuscated installer steps, stop. Strip the workflow back to plain-English instructions and rebuild the skill yourself from the legitimate source behaviour.

3. **Create our own skill instead of importing external execution logic wholesale.** External skills are reference material, not trusted runtime. Keep the useful workflow, rewrite it in our own style, and only preserve commands that are transparent, auditable, and obviously necessary.

4. **A skill should explain what to do, not smuggle in an installer.** If a proposed skill depends on downloading and executing remote scripts, that is usually a supply-chain footgun, not a reusable skill. Prefer pinned tools, explicit commands, and local verification steps.

5. **Git forge skills must take a workshop.** Default workshop is GitHub (`gh`, guarded `code-review` entry point, Actions). Origin workshop uses the `origin` CLI and Cursor Bugbot — never CodeRabbit. Bugbot has no review CLI; do not invent one. Do not assume the git remote named `origin` is GitHub. Put shared rules in `git-master`; do not duplicate a `gh-*` skill as Origin unless review/merge actually runs on Origin.

---

## Real examples from this repo

| Skill | Location | What it does |
|-------|----------|--------------|
| `http-cli-example` | `<skills-dir>/` | Library & API Reference — drive the installed `examplectl` CLI for the live Zotero library |
| `notes-save` | `<skills-dir>/` | Business Process — classify content, save into the vault, commit + push |
| `git-master` | `<skills-dir>/` | Library & API Reference — unified git + GitHub/`origin` workshop (commits, PRs, CI, review triage) |
| `writer-general` | `<skills-dir>/` | Voice & Style — write in the user's academic/technical voice |
| `domain-solver-docs` | `<skills-dir>/` | Runbook — Basilisk CFD workflow with source-grounded semantic lookup |

---

## Debug checklist

- [ ] Folder name matches `name` in frontmatter?
- [ ] `description` specific enough to trigger, loose enough not to over-trigger?
- [ ] Skill in correct tier location?
- [ ] If repo skill: overlay active? (`scripts/repo-skill-overlay.py status`)
- [ ] Fresh session started since last edit?
- [ ] If it's a memory file disguised as a skill: migrate it properly
