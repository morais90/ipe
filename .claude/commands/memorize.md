---
description: Persist valuable session knowledge to CLAUDE memory files, adapting to existing structure
argument-hint: "[scope]" - optional: 'local' for CLAUDE.local.md, or subdirectory path (default: project root CLAUDE.md)
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, TodoWrite
---

# memorize

Intelligently persists important session learnings to CLAUDE memory files, automatically adapting to and extending existing structure.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: Review session insights, Analyze existing structure, Adapt format, Integrate content, Validate no conflicts
   - Determine target memory file based on scope parameter

2. **Discover**
   - Find existing CLAUDE.md files using glob patterns
   - Read current structure and formatting conventions
   - Validate scope and plan approach

3. **Transform**
   - Extract high-value knowledge from current session
   - Match existing formatting (headers, lists, indentation)
   - Add content to relevant sections or create new subsections
   - Preserve all existing content - never overwrite

4. **Validate**
   - Check for duplicate information
   - Ensure no sensitive data is included
   - Verify proper structure and formatting consistency
   - Report results and what was added

## Behavior

### Memory Files

- **CLAUDE.md**: Shared project knowledge (version controlled)
  - Root: Project-wide patterns, architecture, conventions
  - Subdirectories: Component-specific details
- **CLAUDE.local.md**: Personal notes (git ignored)
  - Local environment setup, developer preferences
- **~/.claude/CLAUDE.md**: Cross-project patterns

### What to Memorize

High-value knowledge includes:

- Corrected misconceptions about implementation
- Non-obvious patterns or architecture decisions
- Critical build/test commands and their purposes
- Hidden dependencies or integration points
- Solutions to common issues

### Content Placement Rules

- Add to existing sections when relevant
- Create subsections under appropriate headers
- New top-level sections only when necessary
- Match existing style (bullet format, header case, indentation)

### Constraints

- Preserve existing structure
- Include concrete examples
- Add dates for time-sensitive info
- Group related insights

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No targets | Create new CLAUDE.md file with basic structure |
| Partial failure | Report which sections were updated successfully vs failed |
| Complete failure | Show detailed error and suggest manual review of content |

## Usage

```bash
/memorize                    # Update root CLAUDE.md
/memorize apps/frontend      # Update apps/frontend/CLAUDE.md
/memorize local             # Update CLAUDE.local.md
```

## Output

Reports memorization results including:

- File updated (CLAUDE.md path)
- Sections modified or created
- Number of insights added
- Confirmation of preserved existing content

## Best Practices

### DO

- Preserve existing structure
- Include concrete examples
- Add dates for time-sensitive info
- Group related insights

### DON'T

- Duplicate existing information
- Include sensitive data
- Create deep nesting
- Add verbose explanations

## When to Update

Update memory when you:

- Learn something new about the project
- Get corrected on implementation details
- Struggle to find information
- Discover important patterns
- Fix issues after exploration
