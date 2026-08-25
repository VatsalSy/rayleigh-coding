---
name: find-skills
description: >-
  Use when the user asks "is there a skill for X", "find a skill", or wants to
  discover or install an agent skill. NOT for ordinary how-to or execution
  requests; route those to the owning skill.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## Routing fence

This is a discovery workflow, not a general how-to assistant. Load it only
when the user asks to search the skill catalogue, compare candidate skills, or
install one. For an execution, troubleshooting, or implementation request,
use the existing local skill that owns the task or answer directly. Do not
search the catalogue merely because the task is specialised.

## When to Use This Skill

Use this skill when the user:

- Says "find a skill for X" or "is there a skill for X"
- Explicitly asks to compare skill candidates or extend installed capabilities
- Wants to search the skill catalogue or install a discovered skill

Do not use it for "how do I do X" or "can you do X" unless the user also asks
to discover a skill. Those are ordinary task-routing or execution requests.

## What is the Skills CLI?

The Skills CLI (`npx --yes skills@1.5.23`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx --yes skills@1.5.23 find [query] [--owner <owner>]` - Search for skills interactively or by keyword, optionally scoped to a GitHub owner
- `npx --yes skills@1.5.23 add <package>` - Install a skill from GitHub or other sources
- `npx --yes skills@1.5.23 update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command:

```bash
npx --yes skills@1.5.23 find [query] [--owner <owner>]
```

For example:

- User asks "find a skill for React performance" → `npx --yes skills@1.5.23 find react performance`
- User asks "is there a skill for PR reviews?" → `npx --yes skills@1.5.23 find pr review`
- User asks "I need to create a changelog" → `npx --yes skills@1.5.23 find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Install count** — Prefer skills with 1K+ installs. Be cautious with anything under 100.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy than unknown authors.
3. **GitHub stars** — Check the source repository. A skill from a repo with <100 stars should be treated with skepticism.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The install command they can run
4. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx --yes skills@1.5.23 add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed, you can install the skill for them:

```bash
npx --yes skills@1.5.23 add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx --yes skills@1.5.23 init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx --yes skills@1.5.23 init my-xyz-skill
```
