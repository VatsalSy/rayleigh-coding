# Slash Command Quick Reference

## File Location
```
~/jarvis/commands/<command-name>.md
```

## Minimal Template

```markdown
---
name: command-name
description: |
  What it does.
  
  **Triggers:** "phrase 1", "phrase 2"
  
  <example>
  Context: When to use
  user: "example input"
  assistant: "expected action"
  <commentary>Why this matches</commentary>
  </example>
---

# Command Name

You are an expert at [task].

## Process
1. Step one
2. Step two

## Guidelines
- Rule one
- Rule two
```

## Required Fields

| Field | Purpose |
|-------|---------|
| `name` | Command identifier (lowercase, hyphenated) |
| `description` | Trigger patterns + examples |

## Optional Fields

| Field | Values |
|-------|--------|
| `model` | opus, sonnet, haiku |
| `color` | green, blue, purple, orange, red |

## Naming Rules

✓ `git-sync`, `note-create`, `pr-review`  
✗ `Git_Sync`, `note create`, `PR-Review!`

## Example Block Format

```yaml
<example>
Context: [situation]
user: "[message]"
assistant: "[response]"
<commentary>
[why it matches]
</commentary>
</example>
```

## Commands

```bash
# Initialize new command
python scripts/init_command.py <name> [--model X] [--color Y]

# Validate command
python scripts/validate_command.py <path/to/command.md>

# Validate all commands
python scripts/validate_command.py ~/jarvis/commands/
```

## After Creating

1. Save to `~/jarvis/commands/`
2. Validate with `validate_command.py`
3. Reload jarvis
