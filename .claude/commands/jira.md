---
description: Implement Jira issues with critical analysis and clarification using MCP
argument-hint: "<issue-url-or-key>" - Jira issue URL or issue key (e.g., PROJ-123)
allowed-tools: mcp__jira__get_issue, mcp__jira__search_issues, mcp__jira__update_issue, mcp__jira__add_comment, mcp__jira__get_comments, mcp__jira__transition_issue, Glob, Grep, Read, Edit, MultiEdit, Write, TodoWrite, Task, Bash(git:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*)
---

# jira

Think carefully about the requirements and acceptance criteria before implementing Jira issues. Analyze the issue details, dependencies, and potential conflicts with existing architecture to ensure proper understanding and implementation. Maintain language consistency - respond in the same language as the issue.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: Fetch Issue, Analyze Requirements, Implement Solution, Validate Changes, Update Jira
   - Verify MCP Jira tools are available
   - Check for existing project structure and conventions

2. **Discover**
   - Fetch Jira issue using mcp__jira__get_issue with issue key
   - Get issue comments using mcp__jira__get_comments for context
   - Search for related issues using mcp__jira__search_issues if needed
   - Extract requirements, acceptance criteria, and dependencies
   - Note the language used in the issue for consistent communication
   - Validate scope and plan approach

3. **Transform**
   - Implement changes according to acceptance criteria
   - Follow existing code patterns and conventions
   - Add tests matching acceptance criteria
   - Handle edge cases and error scenarios
   - Add progress comments to Jira using mcp__jira__add_comment (in issue's language)

4. **Validate**
   - Run existing tests to ensure no regressions
   - Verify implementation meets all acceptance criteria
   - Update issue status using mcp__jira__transition_issue if appropriate
   - Add completion comment with mcp__jira__add_comment (in issue's language)
   - Report results and metrics

## Behavior

### Constraints

- Preserve existing code style and conventions
- Align with Jira workflow and team standards
- Use MCP tools for all Jira interactions
- Keep all Jira communications in the same language as the issue

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No targets | Issue not found via MCP - verify issue key and permissions |
| Partial failure | Update Jira with partial completion status and blockers |
| Complete failure | Add comment to Jira explaining failure and request guidance |

### Clarification Triggers

Ask for clarification when:

- Acceptance criteria are ambiguous or missing
- Requirements conflict with existing architecture
- Multiple implementation approaches exist
- Dependencies or integration points are unclear
- Jira issue lacks sufficient detail

## Usage

/jira PROJ-123  # Fetch and implement issue by key
/jira BUG-456  # Fix bug and update status in Jira
/jira STORY-789  # Implement story with progress updates

## Output

Returns implementation summary including:

- Issue details fetched via MCP (type, priority, status)
- Files modified to meet acceptance criteria
- Test results showing criteria validation
- Jira updates made (comments, status transitions) - in issue's language
- Any clarifications needed or assumptions made
- Suggested commit message with Jira reference
