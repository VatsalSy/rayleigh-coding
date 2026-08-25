# Command Format Specification

Complete syntax reference for jarvis slash command files.

## File Structure

```
command-file.md
├── YAML Frontmatter (between --- markers)
│   ├── name (required)
│   ├── description (required)
│   ├── model (optional)
│   └── color (optional)
└── Markdown Body (instructions for the command)
```

## YAML Frontmatter Fields

### `name` (Required)

The command identifier. Users invoke with `/name`.

**Rules:**
- Lowercase letters only
- Hyphens for word separation
- No spaces, underscores, or special characters
- 2-30 characters recommended

**Valid:** `git-sync`, `note-create`, `pr-review`, `docs`
**Invalid:** `Git_Sync`, `note create`, `PR-Review!`, `a`

### `description` (Required)

Determines when the command triggers. This is the primary matching mechanism.

**Structure:**
```yaml
description: |
  [Functional summary - 1-2 sentences]
  
  [Trigger patterns and context]
  
  <example>
  Context: [Situation]
  user: "[User message]"
  assistant: "[Expected response]"
  <commentary>
  [Why this triggers the command]
  </commentary>
  </example>
```

**Guidelines:**
- First line: Clear functional summary
- Include explicit trigger phrases
- Add 2-3 example blocks for pattern coverage
- Use `<commentary>` to explain matching logic

### `model` (Optional)

Default model for command execution.

**Values:** `opus`, `sonnet`, `haiku`
- `opus` - Most capable, complex reasoning
- `sonnet` - Balanced performance
- `haiku` - Fast, simple tasks

**Default:** System default if not specified

### `color` (Optional)

UI accent color for the command.

**Values:** `green`, `blue`, `purple`, `orange`, `red`

**Usage suggestions:**
- `green` - Creation, success-oriented commands
- `blue` - Information, documentation commands
- `purple` - Creative, generative commands
- `orange` - Warning, careful-operation commands
- `red` - Destructive, irreversible commands

## Markdown Body Structure

### Recommended Sections

```markdown
# [Command Name] - Brief descriptor

[Optional: Opening context/identity statement]

## Core Responsibilities / Purpose

[What the command does - bulleted or numbered list]

## Workflow / Process

[Step-by-step instructions]

## Guidelines / Rules

[Constraints, best practices, warnings]

## Output Format

[Expected response structure]
```

### Minimal Structure

At minimum, include:
1. Identity/role statement
2. Key responsibilities
3. Basic process or behavior description

### Identity Statements

Strong identity statements:
```markdown
You are an expert [role] specializing in [domain].
```

```markdown
You are a [type] architect with deep understanding of [area].
```

Weak (avoid):
```markdown
You help with [task].
```

```markdown
This command does [thing].
```

## Example Blocks

### Standard Format

```yaml
<example>
Context: [Brief situation description]
user: "[Exact user message that triggers this]"
assistant: "[Expected assistant response or action]"
<commentary>
[Explanation of the match - why this input triggers this command]
</commentary>
</example>
```

### Multiple Examples

Include examples covering:
1. **Primary use case** - Most common invocation
2. **Alternative phrasing** - Different ways to request the same thing
3. **Edge case** - Boundary conditions or less obvious triggers

### Example Quality Checklist

- [ ] User message sounds natural
- [ ] Context provides necessary setup
- [ ] Assistant response shows expected behavior
- [ ] Commentary explains the matching logic

## Complete File Example

```markdown
---
name: git-status
description: |
  Check git repository status, staged changes, and branch information.
  Provides quick overview of working directory state.

  **Triggers:** "git status", "what's changed", "check my repo", "show staged files"

  <example>
  Context: User wants to see uncommitted changes
  user: "What files have I changed?"
  assistant: "I'll check your git status to show modified and staged files."
  <commentary>
  Question about changed files maps to git status functionality.
  </commentary>
  </example>

  <example>
  Context: User preparing to commit
  user: "Am I ready to commit?"
  assistant: "Let me check your staged changes and working directory status."
  <commentary>
  Pre-commit check implies need to review git status.
  </commentary>
  </example>
model: haiku
color: blue
---

# Git Status - Repository State Inspector

You are a git expert that provides clear, actionable repository status information.

## Core Responsibilities

1. Report current branch and tracking status
2. List staged changes ready for commit
3. Show modified but unstaged files
4. Identify untracked files
5. Highlight potential issues (conflicts, diverged branches)

## Process

1. Run `git status` in the repository
2. Parse output into structured categories
3. Summarize state in plain language
4. Suggest logical next actions

## Output Format

```
Branch: [name] (tracking: [remote/branch])
Status: [clean | X files changed]

Staged (ready to commit):
  - [file1]
  - [file2]

Modified (not staged):
  - [file3]

Untracked:
  - [file4]

Suggested action: [next logical step]
```

## Guidelines

- Always show branch information first
- Group files by status category
- Use relative paths for readability
- Suggest concrete next actions
- Warn about uncommitted changes before destructive operations
```

## Escaping Special Characters

### In YAML

```yaml
description: |
  Use pipes to escape "quotes" and special: characters
  Literal block style (|) preserves newlines
```

### In Markdown

- Backticks for inline code: `` `code` ``
- Triple backticks for code blocks
- Backslash for literal special chars: `\*not italic\*`

## Validation Rules

Commands must pass these checks:

1. **Frontmatter present** - File starts with `---`
2. **Name field exists** - Non-empty `name:` value
3. **Name format valid** - Lowercase, hyphenated, no spaces
4. **Description exists** - Non-empty `description:` value
5. **Description has example** - At least one `<example>` block
6. **Body not empty** - Content after closing `---`
7. **File location correct** - In `~/jarvis/commands/`
