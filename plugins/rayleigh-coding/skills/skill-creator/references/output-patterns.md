# Output Patterns

## Template Pattern

Provide templates for output format. Match strictness to needs.

**Strict (API responses, data formats):**

```markdown
## Report structure

ALWAYS use this exact template:

# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Actionable recommendation
2. Actionable recommendation
```

**Flexible (when adaptation useful):**

```markdown
## Report structure

Default format (adapt as needed):

# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt based on discoveries]

## Recommendations
[Tailor to context]
```

## Examples Pattern

For quality-dependent output, provide input/output pairs:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Examples clarify desired style better than descriptions.
