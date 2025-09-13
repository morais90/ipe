---
description: Review and update CLAUDE memory files to ensure accuracy with current codebase
argument-hint: "[directory]"
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Task, TodoWrite
---

# refine-memory

Think carefully about the relationships between memory files and codebase accuracy. Systematically review and update all CLAUDE memory files to ensure they accurately reflect the current codebase, removing outdated information and reorganizing content to appropriate locations.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: Discovery, Verification, Update, Consolidation, Completion
   - Check for existing CLAUDE.md and CLAUDE.local.md files in project hierarchy

2. **Discover**
   - Find all CLAUDE memory files using `**/CLAUDE*.md` pattern
   - Map the memory file structure and identify component boundaries
   - Validate scope and plan approach

3. **Transform**
   - Verify technical claims against actual codebase implementation
   - Update incorrect details and remove outdated information
   - Consolidate duplicate entries and relocate misplaced information
   - Add missing critical knowledge where needed

4. **Validate**
   - Confirm all build commands and scripts still work
   - Verify architectural descriptions match current structure
   - Check API endpoints and patterns are accurate
   - Report results and metrics

## Behavior

### Constraints

- Preserve existing code style and conventions
- Maintain information hierarchy (root → component → local)
- Keep valuable historical context and tribal knowledge

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No targets | Create initial CLAUDE.md with discovered patterns |
| Partial failure | Report which files were updated vs skipped with reasons |
| Complete failure | Show detailed error and suggest manual review |

## Usage

/refine-memory  # Review all CLAUDE memory files in project
/refine-memory apps/frontend  # Refine specific directory
/refine-memory infrastructure  # Focus on infrastructure docs

## Output

Reports refinement results including:

- Number of memory files processed and updated
- List of outdated information removed or corrected
- Consolidation actions taken (duplicates merged, content relocated)
- Verification results for commands, patterns, and architecture
- Summary of critical knowledge added or preserved
