---
name: slash-command-maker
description: |
  Use when the user says "write/create/make a slash command", "new jarvis
  command", "edit my slash command", "command to [action]", works on files in
  ~/jarvis/commands/, or targets OpenCode/comphy-code plugin commands or
  jarvis routing. Jarvis is skills-first — prefer skills for new automation.
---

# Slash Command Maker

Create high-quality slash commands for the jarvis system when slash commands are explicitly in scope. Prefer skills for new workflow automation unless the user is targeting a command-based or OpenCode plugin flow.

## Workflow Overview

1. **Clarify requirements** - Understand functionality, triggers, and routing needs
2. **Check documentation** - Run `/docs slash-commands` for latest syntax (or read `references/command-format.md` if unavailable)
3. **Design command structure** - Plan direct execution, skill invocation, or plugin routing as needed
4. **Create command file** - Write to `~/jarvis/commands/`
5. **Validate** - Run `scripts/validate_command.py` on the file
6. **Remind user** - Jarvis reload required for activation

## Command File Location

All commands MUST be saved to: `~/jarvis/commands/`
- Use `.md` extension for markdown-based commands
- Filename should match command name (e.g., `git-sync.md` for `/git-sync`)

## Command Structure

Every slash command file has two parts:

### 1. YAML Frontmatter (Required)

```yaml
---
name: command-name
description: |
  Concise description of what this command does.
  Include trigger patterns and example invocations.
  
  <example>
  Context: [When to use]
  user: "[example invocation]"
  assistant: "[expected behavior]"
  <commentary>
  [Why this triggers the command]
  </commentary>
  </example>
model: [opus|sonnet|haiku]  # Optional: default model
color: [green|blue|purple|orange|red]  # Optional: UI color
---
```

### 2. Markdown Body (Required)

The body contains:
- **Role/identity statement** - What the command specializes in
- **Core responsibilities** - Key functions
- **Workflow/process** - Step-by-step instructions
- **Guidelines** - Best practices and constraints
- **Output format** - Expected response structure

## Reference Files

Load as needed from `references/`:

| File | When to Load |
|------|--------------|
| `command-format.md` | Full syntax specification and field details |
| `routing-patterns.md` | Skill-first routing, delegation, and plugin patterns |
| `examples.md` | Complete command file examples |

## Naming Conventions

- **Command names**: lowercase, hyphenated (e.g., `git-sync`, `note-create`, `pr-review`)
- **Action-oriented**: Start with verb when possible (`create-`, `sync-`, `review-`, `generate-`)
- **Specific over generic**: `pdf-merge` not `file-combine`
- **Consistent prefixes**: Group related commands (`git-*`, `note-*`, `doc-*`)

## Routing Logic

Commands can handle tasks directly, invoke skills, or route into plugin-specific layers when needed:

### Direct Execution
Command handles the task itself:
```markdown
You are an expert at [task]. Execute [steps] directly.
```

### Skill Invocation
Command invokes an existing skill:
```markdown
Based on the request, use the appropriate skill:
- **Code review** → Use `review-ultra`
- **Memory operations** → Use `jarvis-memory-manager`
```

### Conditional Routing
Use pattern matching for intelligent routing:
```markdown
<routing>
If request mentions "review" → use `review-ultra`
If request mentions "memory" or a memory path → use `jarvis-memory-manager`
If request targets OpenCode plugin commands → route to the relevant plugin flow
Default → handle directly
</routing>
```

See `references/routing-patterns.md` for advanced patterns.

## Pattern Matching in Descriptions

The `description` field determines when commands trigger. Include:

1. **Explicit trigger phrases** - Exact phrases that should invoke the command
2. **Context patterns** - Situations where the command applies
3. **Example blocks** - Concrete user/assistant exchanges

Example pattern structure:
```yaml
description: |
  Brief functional description.
  
  **Triggers:** "phrase 1", "phrase 2", "phrase 3"
  
  **Context:** When user is working with [domain] and needs [functionality].
  
  <example>
  Context: User needs to [task]
  user: "[natural language request]"
  assistant: "[I'll use command-name to...]"
  <commentary>
  [Explanation of why this matches]
  </commentary>
  </example>
```

**Bad:** `description: Helps with git stuff.`
**Good:** `description: Sync the current repo — pull --rebase then push, stopping on conflicts. Triggers: "/git-sync", "sync this repo".`

## Quality Checklist

Before finalizing any command, verify:

- [ ] **Name** is lowercase, hyphenated, action-oriented
- [ ] **Description** includes triggers, context, and examples
- [ ] **Examples** show realistic user invocations
- [ ] **Body** has clear role statement and responsibilities
- [ ] **Routing** logic covers all expected cases
- [ ] **Fallback** behavior handles edge cases
- [ ] **File saved** to `~/jarvis/commands/`
- [ ] **Validation** passes (`scripts/validate_command.py`)

## Validation

Run validation before delivery:

```bash
python scripts/validate_command.py ~/jarvis/commands/command-name.md
```

The validator checks:
- YAML frontmatter syntax
- Required fields (`name`, `description`)
- Naming conventions
- Example block structure
- File location

## Common Patterns

### Single-Purpose Command
For focused, specific tasks:
```markdown
You are an expert at [specific task]. Your job is to:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Always [constraint]. Never [anti-pattern].
```

### Multi-Mode Command
For commands with different operational modes:
```markdown
This command operates in [N] modes:
1. **Mode A**: [description] - Triggered by [pattern]
2. **Mode B**: [description] - Triggered by [pattern]

Determine the mode from user input, then execute accordingly.
```

### Wrapper Command
For commands that primarily route work:
```markdown
You coordinate [domain] tasks by choosing the correct execution layer:

- Request type A → relevant skill
- Request type B → direct execution
- OpenCode-specific request → plugin command or comphy-code flow

Prefer the simplest layer that matches the request.
```

## Output Format

When creating a command, present:

1. **Command overview** - What it does and when it triggers
2. **Full file content** - Complete .md file ready to save
3. **File path** - `~/jarvis/commands/[name].md`
4. **Activation reminder** - "Reload jarvis to activate"

## Iteration Guidance

If the user wants to modify an existing command:

1. Read the current command file
2. Identify what needs changing
3. Present the updated version with changes highlighted
4. Save to the same location (overwrites previous)
5. Remind about jarvis reload
