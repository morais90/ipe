---
description: Create well-structured Git commits by analyzing specified files/folders
argument-hint: "[files/folders]" - paths to analyze for commit message generation
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), TodoWrite, Read, Grep, Glob
---

# commit

Create well-structured conventional commits by analyzing file changes to determine appropriate commit types, scopes, and generate clear commit messages following established conventions.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: Analysis, Staging, Message Generation, Commit Creation, Validation
   - Check git repository status and identify target files

2. **Discover**
   - If arguments provided: analyze changes in specified files/folders using `git diff $ARGUMENTS`
   - If no arguments: analyze all staged changes using `git diff --cached`
   - Determine commit strategy based on scope

3. **Transform**
   - Stage specified files with `git add $ARGUMENTS` if paths provided (never use git add . or git add -A)
   - Determine appropriate commit type (feat, fix, docs, etc.) based on changes
   - Identify scope based on affected modules/components
   - Generate conventional commit message using imperative mood
   - Exclude AI attribution, coverage stats, or irrelevant information

4. **Validate**
   - Create commit with generated message (never use --no-verify)
   - If commit succeeds: verify and report commit hash and summary
   - If pre-commit hooks make automatic corrections: stage corrected files and retry commit once
   - If pre-commit hooks fail with blocking errors: abort commit and report issues to user

## Behavior

### Constraints

- Follow conventional commit format: `<type>(<scope>): <subject>`
- Subject line max 50 characters
- Body wrapped at 72 characters explaining problem and solution
- Use imperative mood: "Fix bug" not "Fixed bug" or "Fixing bug"
- Never include AI attribution in commit messages
- Focus on technical changes and business value
- Avoid generic messages like "updates" or "fixes"
- Use natural explanations instead of bullet points in commit body
- Never use `git add .`, `git add -A`, `git commit -am`, or `--no-verify` flags
- Respect pre-commit hooks: retry once if auto-corrections made, abort if blocked

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No targets | Analyze all staged changes or suggest staging files first |
| Partial failure | Report which files were successfully staged vs failed |
| Pre-commit auto-fixes | Stage corrected files and retry commit once |
| Pre-commit blocks | Abort commit and report blocking issues to user |
| Complete failure | Show git errors and suggest manual review |

### Commit Types

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI configuration changes

### Common Scopes

- `api`: API-related changes
- `ui`: User interface changes
- `config`: Configuration system changes
- `auth`: Authentication and authorization
- `db`: Database changes
- `core`: Core functionality
- `utils`: Utility functions
- `test`: Test-related changes

## Usage

```bash
# Analyze all staged changes and commit
/commit

# Analyze and commit specific files
/commit src/auth/login.js

# Analyze and commit multiple files/folders
/commit src/components/ tests/ package.json

# Analyze and commit entire directory
/commit src/auth/
```

## Output

Returns commit creation results including:

- Generated conventional commit message with type and scope
- Commit hash and summary of changes

### What NOT to Include

- Generic messages: "chore: updates" or "fix: bug fixes"
- Wrong verb forms: "Fixed bug" or "Adding feature" instead of "Fix bug" or "Add feature"
- Coverage statistics, generated tags, or other irrelevant information
- Bullet points in commit body that don't add value (prefer natural explanations)
- Commands like `git add .`, `git add -A`, `git commit -am`, or `--no-verify` flags
- AI attribution: "Generated with [Claude Code](https://claude.ai/code)"
- Co-authorship: "Co-Authored-By: Claude <noreply@anthropic.com>"
