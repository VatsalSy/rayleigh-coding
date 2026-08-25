# Git and GitHub CLI Commands Reference

## Plain git/gh commands


## Pre-PR Checks

```bash
# Check current state
git status

# Ensure all changes committed
git status --porcelain  # Empty output = clean

# Resolve base branch
BASE_BRANCH_SCRIPT="<skills-dir>/gh-pr-create/scripts/get-base-branch.sh"
BASE_BRANCH="$("$BASE_BRANCH_SCRIPT")"

# View commits since base branch
git log "${BASE_BRANCH}"..HEAD --oneline

# View file changes since base branch
git diff "${BASE_BRANCH}"...HEAD --stat

# Check if branch tracks remote
git branch -vv
```

## Pushing Changes

```bash
# Push and set upstream (first push)
git push -u origin HEAD

# Force push (use carefully)
git push --force-with-lease origin HEAD

# Push specific branch
git push origin feature-branch
```

## Creating PRs with gh CLI

### Basic PR Creation

```bash
gh pr create --title "Title" --body "Body text"
```

### Multi-line Body (HEREDOC)

```bash
gh pr create --title "Add rate limiting" --body "$(cat <<'EOF'
## Summary
- Implement request rate limiting

## Changes
- Add RateLimiter middleware
- Create configuration file

## Testing
- Verified limits trigger correctly
EOF
)"
```

### Specify Base Branch

```bash
gh pr create --base "${BASE_BRANCH}" --title "Title" --body "Body"
```

### Draft PR

```bash
gh pr create --draft --title "WIP: Feature" --body "Work in progress"
```

### Assign Reviewers

```bash
gh pr create --reviewer username1,username2 --title "Title" --body "Body"
```

> Do not use the PR author as a reviewer on their own PR. Use
> `--assignee "${GH_ASSIGNEE}"` (default: authenticated user) for visibility.

## After PR Creation

```bash
# Get PR URL
gh pr view --json url -q .url

# View PR status
gh pr status

# List open PRs
gh pr list

# Check PR details
gh pr view
```

## Troubleshooting

### Branch Already Has PR

```bash
# Check for existing PR
gh pr list --head $(git branch --show-current)

# View existing PR
gh pr view
```

### Not Authenticated

```bash
# Login to GitHub
gh auth status

# Check auth status
gh auth status
```

### No Commits Ahead

```bash
# Verify base
BASE_BRANCH_SCRIPT="<skills-dir>/gh-pr-create/scripts/get-base-branch.sh"
BASE_BRANCH="$("$BASE_BRANCH_SCRIPT")"

# Verify commits exist
git log "${BASE_BRANCH}"..HEAD --oneline

# If empty, nothing to PR
```

### Remote Conflicts

```bash
# Fetch latest remote
git fetch origin

# Rebase on base if needed
BASE_BRANCH_SCRIPT="<skills-dir>/gh-pr-create/scripts/get-base-branch.sh"
BASE_BRANCH="$("$BASE_BRANCH_SCRIPT")"
if [ -z "$BASE_BRANCH" ]; then
  echo "Unable to resolve base branch" >&2
  exit 1
fi
git rebase "origin/${BASE_BRANCH}"

# Push with force-with-lease
git push --force-with-lease
```

## Complete Workflow Example

```bash
# 1. Verify clean state
git status

# 2. Push branch
git push -u origin HEAD

# 3. Detect base and inspect PR scope
BASE_BRANCH_SCRIPT="<skills-dir>/gh-pr-create/scripts/get-base-branch.sh"
BASE_BRANCH="$("$BASE_BRANCH_SCRIPT")"
git log "${BASE_BRANCH}"..HEAD --oneline
git diff "${BASE_BRANCH}"...HEAD --stat

# 4. Create PR
gh pr create --title "Add user authentication" --base "${BASE_BRANCH}" --body "$(cat <<'EOF'
## Summary
- Add JWT-based authentication system

## Changes
- Create AuthService module
- Add login/logout endpoints
- Implement token refresh

## Testing
- Unit tests for AuthService
- Integration tests for endpoints
EOF
)"

# 5. Get URL
gh pr view --json url -q .url
```
