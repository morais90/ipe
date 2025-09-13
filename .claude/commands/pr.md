---
description: Create pull requests strictly following project PR templates
argument-hint: "[title] [base-branch]"
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git remote:*), Bash(git push:*), Bash(gh pr create:*), Bash(find:*), Glob, Read, TodoWrite
---

# pr

Think about the complete PR creation workflow, including git state validation, template discovery, change analysis, and reviewer-focused content generation. Consider all edge cases like missing templates, uncommitted changes, and branch relationships.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: State Check, Template Discovery, Change Analysis, Template Processing, PR Creation
   - Verify current branch is not main/master and all changes are committed

2. **Discover**
   - Find PR templates using exact search: `find .github -type f -maxdepth 1 -iname "pull_request_template.md" 2>/dev/null`
   - Validate scope and determine base branch (default: main or master)

3. **Transform**
   - Analyze git changes with `git log --oneline base..HEAD` and `git diff base...HEAD`
   - If template exists: parse sections, fill placeholders, check appropriate boxes
   - If no template found: stop execution and inform user
   - Generate clear title from commits if not provided

4. **Validate**
   - Ensure branch is pushed to remote (`git push -u origin <branch>` if needed)
   - Create PR using `gh pr create` with complete filled template
   - Verify PR creation success and provide URL

## Behavior

### Constraints

- Preserve existing code style and conventions
- NEVER modify template structure when template exists
- ALWAYS follow template sections exactly as provided
- Respect the language of the template (e.g., if template is in Portuguese, write PR content in Portuguese)
- Focus on reviewer-friendly content and clear context

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No targets | Check if on feature branch, suggest creating branch first |
| Partial failure | Report specific git or template parsing errors with suggested fixes |
| Complete failure | Show detailed error and provide step-by-step manual instructions |

## Usage

/pr  # Auto-generate title and description for current branch
/pr "feat: implement user authentication"  # Custom title with auto-description
/pr "fix: resolve memory leak" develop  # Custom title targeting develop branch

## Output

PR URL and number for the created pull request
