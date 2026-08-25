# Commit Message Examples Gallery

Expanded examples organized by commit type.

## Feature Additions

```
Add dark mode toggle to settings page

- Implement ThemeContext for app-wide state
- Add toggle switch component to Settings
- Store preference in localStorage
```

```
Add CSV export for analytics dashboard

Users can now download report data as CSV.
Supports filtering by date range.
```

```
Add webhook notifications for order events

New endpoint: POST /webhooks
Supports: order.created, order.completed, order.cancelled
```

## Bug Fixes

```
Fix race condition in session management

Multiple concurrent requests could create duplicate
sessions for the same user. Added mutex lock around
session creation.
```

```
Fix date formatting in Safari

Safari doesn't support YYYY-MM-DD format in Date constructor.
Using Date.parse() with explicit timezone instead.
```

```
Fix memory leak in image processing pipeline

Large images weren't being garbage collected due to
retained references in the cache. Added explicit cleanup
after processing completes.
```

## Refactoring

```
Refactor authentication into separate module

Extract auth logic from UserController to AuthService.
No behavioral changes; improves testability.
```

```
Simplify order state machine

Replace nested conditionals with explicit state transitions.
Easier to add new states and debug transitions.
```

```
Convert callback API to async/await

All database operations now use async/await pattern.
Improves readability and error handling.
```

## Performance

```
Optimize database queries for user listing

Add compound index on (org_id, created_at).
Reduces query time from 2.3s to 45ms for large orgs.
```

```
Lazy load chart components on dashboard

Charts now load only when scrolled into view.
Reduces initial bundle size by 340KB.
```

## Configuration / DevOps

```
Add Docker multi-stage build for smaller images

Final image reduced from 1.2GB to 180MB.
Separates build dependencies from runtime.
```

```
Configure CI to run tests in parallel

Split test suite into 4 shards.
Reduces CI time from 12min to 4min.
```

## Documentation

```
Document API authentication flow

Add sequence diagram and code examples
for OAuth2 integration in README.
```

```
Add troubleshooting section for common errors

Covers: connection timeouts, auth failures,
rate limiting, and data format issues.
```

## Anti-Patterns (What NOT to Do)

```
# Too vague
Update stuff
Fix bugs
Changes

# AI signatures (never include)
Update authentication
🤖 Generated with [AI Tool]
Co-Authored-By: AI <noreply@ai.com>
Co-authored-by: Cursor <cursoragent@cursor.com>
Co-authored-by: Cursor <cursoragent@cursor.com>

# Too technical without context
Refactor AbstractFactoryBuilderImpl

# Commit message doesn't match changes
Add new feature  (when actually fixing a bug)
```

## Subject Line Verbs

Use these imperative verbs:
- **Add** - new feature or file
- **Fix** - bug repair
- **Update** - modify existing feature
- **Remove** - delete feature/file
- **Refactor** - restructure without behavior change
- **Optimize** - performance improvement
- **Document** - add/update docs
- **Configure** - settings/config changes
- **Test** - add/update tests
