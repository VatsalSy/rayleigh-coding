# Coding conventions (public)

Exportable rules for agents using rayleigh-coding. No private fleet, vault, or
lab topology belongs here.

## Autonomy

- Discover repository facts with tools.
- Ask only for load-bearing product or preference decisions.
- Hard-stop before irreversible external actions (force-push to shared
  branches, production deploys, deletion, customer messages, purchases).

## Git workshops

Choose GitHub vs Cursor Origin from the **remote URL host**
(`github.com` vs `origin.cursor.com`), never from a machine name.

Prefer merge commits. Do not squash unless the user asks.

## Review

- GitHub: CodeRabbit via the guarded `code-review` entrypoint when the CLI is
  available.
- Origin: Bugbot / Origin review skills. Do not invent a Bugbot CLI.
- Stop on rate limits for an unchanged diff. Do not burn quota with no-op
  retries.

## Verification

Name the evidence class before claiming success. Drive a real path. Keep a
receipt. Do not call a green unit suite "scientific validation."

## Commits and PRs

- Imperative subject, roughly ≤50 characters when practical.
- No AI co-author trailers or "Made-with" noise.
- Optional `GH_ASSIGNEE` / `MERGE_BOT_LOGIN` via environment, never hard-coded
  personal logins in skills.

## Deploy skills

Discover Cloudflare account/zone IDs and Vercel project IDs through the CLI or
API at runtime. Never commit personal inventories into skills.
