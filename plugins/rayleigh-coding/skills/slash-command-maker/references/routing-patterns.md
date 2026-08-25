# Routing Patterns

Advanced patterns for skill-first routing, delegation, and conditional execution in slash commands.

## Routing Fundamentals

### Direct vs Routed Execution

**Direct Execution** - Command handles task itself:
```markdown
You execute [task] directly by:
1. [Step 1]
2. [Step 2]
3. [Deliver result]
```

**Skill/Plugin Routing** - Command routes to a skill or plugin flow:
```markdown
Route this request to the appropriate skill or plugin:
- [Pattern A] → review-ultra
- [Pattern B] → jarvis-memory-manager
```

### When to Delegate

Route when:
- Task maps cleanly to an existing skill or plugin capability
- Multiple domains involved
- Task exceeds command's focused scope
- Consistency with existing skill behavior is needed

Handle directly when:
- Task is simple and well-defined
- No matching skill or plugin flow exists
- Speed/efficiency is critical
- Task is self-contained

## Pattern 1: Keyword-Based Routing

Route based on keywords in user request:

```markdown
## Routing Logic

Analyze the user request and route based on keywords:

**Code review keywords** → review-ultra
- "implement", "code", "function", "bug", "fix", "refactor"

**Documentation keywords** → docs skill or direct handling
- "document", "readme", "explain", "comment"

**Memory keywords** → jarvis-memory-manager
- "test", "spec", "coverage", "assert"

**Default** → Handle directly or ask for clarification
```

## Pattern 2: Intent Classification

Route based on inferred intent:

```markdown
## Intent Classification

Classify user intent, then route:

1. **Creation intent** - User wants to build something new
   - Signals: "create", "make", "build", "generate", "new"
   - Route → direct execution or the most relevant skill

2. **Modification intent** - User wants to change existing work
   - Signals: "edit", "modify", "update", "change", "fix"
   - Route → direct execution or editing skill

3. **Analysis intent** - User wants to understand something
   - Signals: "explain", "analyze", "review", "what is", "why"
   - Route → analysis skill or docs lookup

4. **Execution intent** - User wants to run/deploy something
   - Signals: "run", "execute", "deploy", "start", "launch"
   - Route → execution skill or plugin flow
```

## Pattern 3: Domain-Based Routing

Route based on domain/technology:

```markdown
## Domain Router

Identify the primary domain and route accordingly:

| Domain | Indicators | Route To |
|--------|-----------|----------|
| Frontend | React, CSS, HTML, UI, component | direct handling or frontend skill |
| Backend | API, server, database, endpoint | direct handling or relevant coding skill |
| DevOps | deploy, CI/CD, Docker, k8s | deploy or infrastructure skill |
| Data | SQL, analytics, dashboard, ETL | direct handling or relevant analysis skill |

**Multi-domain requests:** Break down and route each part to the smallest appropriate layer.
```

## Pattern 4: Complexity-Based Routing

Route based on task complexity:

```markdown
## Complexity Assessment

Assess complexity before routing:

**Simple (handle directly):**
- Single-step operations
- Lookup/retrieval tasks
- Formatting/transformation
- Clear, unambiguous requests

**Medium (route to a single skill or plugin flow):**
- Multi-step workflows
- Domain-specific expertise needed
- Requires context gathering

**Complex (orchestrate multiple skills or steps):**
- Cross-domain tasks
- Multi-file operations
- Requires planning phase
- Iterative refinement expected

For complex tasks:
1. Create execution plan
2. Route subtasks to the appropriate skills or execution layers
3. Aggregate results
4. Present unified output
```

## Pattern 5: Fallback Chains

Define fallback routing when primary route fails:

```markdown
## Fallback Chain

Try routes in order until one succeeds:

1. **Primary:** matching skill or plugin flow
   - Best for exact matches
   - Fail condition: capability unavailable or returns error

2. **Secondary:** direct command handling
   - Handles broader cases
   - Fail condition: Task outside capability

3. **Tertiary:** Ask for clarification
   - Ask the user for more details or to refine the request
   - When no route can handle the request
```

## Pattern 6: Conditional Routing with Context

Route based on conversation context:

```markdown
## Context-Aware Routing

Consider conversation history when routing:

**If previous message involved code:**
- Assume follow-up is code-related
- Route to same code-agent for continuity

**If user uploaded files:**
- Analyze file types
- Route to appropriate file-handler agent

**If in project context:**
- Use a project-specific skill or plugin flow if available
- Fall back to direct execution or a general skill

**If error was reported:**
- Route to debug-agent
- Include error context
```

## Pattern 7: User Preference Routing

Route based on user preferences:

```markdown
## Preference-Based Routing

Respect user-specified preferences:

**Explicit skill/plugin request:**
- User says "use X skill" → Route to X
- User says "use comphy-code" → Route to the OpenCode plugin flow
- Override default routing logic

**Implicit preferences:**
- User prefers verbose responses → Route to detailed-agent
- User prefers speed → Route to fast-agent (haiku)

**History-based:**
- User consistently chooses certain approach → Remember preference
```

## Pattern 8: Parallel Delegation

Send to multiple agents simultaneously:

```markdown
## Parallel Execution

For comprehensive tasks, route multiple checks in parallel when supported:

1. **Spawn parallel tasks:**
   - Send code review to `review-ultra`
   - Send docs lookup to the relevant docs skill
   - Send security review to the security skill

2. **Aggregate results:**
   - Collect all agent responses
   - Resolve conflicts (prefer security findings)
   - Merge into unified report

3. **Present combined output**
```

## Pattern 9: Pipeline Routing

Sequential agent chain:

```markdown
## Pipeline Execution

Execute steps in sequence, passing output forward:

```
User Request
    ↓
[planning step] → Execution plan
    ↓
[implementation step] → Code/content
    ↓
[review-ultra] → Feedback
    ↓
[refinement step] → Final output
    ↓
User
```

Each stage can:
- Pass to next stage
- Loop back to previous stage
- Terminate pipeline early
```

## Pattern 10: Hybrid Routing

Combine multiple patterns:

```markdown
## Hybrid Router

Combine routing strategies:

1. **First: Check explicit skill or plugin request**
   - If user specifies a skill or plugin → Route there

2. **Second: Domain classification**
   - Identify primary domain
   - Select domain-specific skill set or direct handling path

3. **Third: Complexity assessment within domain**
   - Simple → Handle directly
   - Complex → Use the most appropriate skill or plugin flow

4. **Fourth: Context refinement**
   - Adjust based on conversation history
   - Apply user preferences

5. **Execute selected route**
```

## Routing Anti-Patterns

### Avoid These

**Over-routing:**
```markdown
# Bad: Routes everything, handles nothing
Route all requests to other agents.
```

**Under-specification:**
```markdown
# Bad: No clear routing criteria
Send to the right agent.
```

**Circular routing:**
```markdown
# Bad: Can create infinite loops
If unclear → route to clarifier
clarifier: If still unclear → route back to router
```

**Ignoring context:**
```markdown
# Bad: Treats every request as independent
Always analyze request from scratch.
```

### Better Alternatives

**Balanced routing:**
```markdown
# Good: Clear criteria, handles edge cases
Handle simple requests directly.
Route complex requests to the smallest appropriate skill or execution layer.
Ask for clarification when ambiguous.
```

**Specific criteria:**
```markdown
# Good: Explicit matching rules
Route based on:
- Keyword: "deploy" → deploy skill
- File type: memory path → jarvis-memory-manager
- Context: code review → review-ultra
```

## Error Handling in Routing

```markdown
## Routing Error Handling

When routing fails:

1. **Skill or plugin unavailable:**
   - Try fallback execution path
   - If no fallback, handle directly with disclaimer

2. **Skill or plugin returns error:**
   - Parse error type
   - Retry with modified request if transient
   - Escalate to user if persistent

3. **Ambiguous routing:**
   - Present options to user
   - "This could be handled by X or Y. Which do you prefer?"

4. **No matching route:**
   - Log the unmatched pattern
   - Handle directly or ask for clarification
   - Consider adding new route for pattern
```
