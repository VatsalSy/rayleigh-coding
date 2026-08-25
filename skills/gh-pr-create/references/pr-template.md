# PR Description Template

## Standard Template

```markdown
## Summary
- [Primary change and its purpose]
- [Secondary changes if applicable]
- [Business value or user impact]

## Changes Made
- [Specific file/component modifications]
- [Architectural decisions explained]
- [Breaking changes highlighted]

## Testing
- [Validation steps performed]
- [Test results or coverage]
- [Manual testing notes if applicable]
```

## Template Variations

### Feature PR
```markdown
## Summary
- Add [feature name] to enable [user capability]
- Implements [ticket/issue reference if applicable]

## Changes Made
- Create [new components/modules]
- Update [existing files] to support new feature
- Add [configuration/environment variables]

## Testing
- Unit tests added for [components]
- Manual testing: [scenarios verified]
- Edge cases: [specific cases tested]
```

### Bug Fix PR
```markdown
## Summary
- Fix [bug description] that caused [impact]
- Root cause: [brief explanation]

## Changes Made
- [Specific fix applied]
- [Related preventive changes]

## Testing
- Verified fix resolves original issue
- Regression testing: [areas tested]
- Added test to prevent recurrence
```

### Refactoring PR
```markdown
## Summary
- Refactor [component/module] for [goal: readability/performance/maintainability]
- No behavioral changes

## Changes Made
- [Structural changes]
- [Code organization improvements]
- [Technical debt addressed]

## Testing
- Existing tests pass
- No functional changes verified
```

### Documentation PR
```markdown
## Summary
- Update documentation for [topic]
- Improves clarity on [specific areas]

## Changes Made
- [New sections added]
- [Existing content updated]
- [Examples added/updated]

## Testing
- Links verified
- Formatting checked
- Examples tested where applicable
```

## Anti-Patterns

Avoid these patterns:

```markdown
# Too vague
## Summary
Updated some files

# AI signatures (never include)
## Summary
Changes to authentication

Generated with Claude 🤖

# Generic template unfilled
## Summary
- TODO: Add summary

## Changes Made
- TODO: List changes
```

## Tips for Good PRs

1. **Write for reviewers** - They haven't seen the code yet
2. **Be specific** - "Add rate limiting" not "Update API"
3. **Explain why** - The code shows what, PR describes why
4. **Keep it scannable** - Bullet points, not paragraphs
5. **No AI metadata** - Focus on the changes, not the tools
