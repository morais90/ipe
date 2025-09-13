---
description: Generate a comprehensive CLAUDE.md file following best practices for any project
argument-hint: "[directory]"
allowed-tools: Read, Write, Glob, Grep, Bash, TodoWrite, Task
---

# generate-claude-md

Think deeply about the project structure and conventions to generate a concise, machine-optimized CLAUDE.md that establishes strict rules and patterns for this codebase.

## Implementation

1. **Initialize**
   - Use TodoWrite to track progress: Analyze Project, Detect Stack, Extract Patterns, Generate Sections, Create CLAUDE.md
   - Check if CLAUDE.md already exists and offer to update or replace

2. **Discover**
   - Analyze package.json, requirements.txt, go.mod, Gemfile, or other dependency files
   - Detect project structure and architecture patterns
   - Identify test frameworks, build tools, and development workflows
   - Extract coding conventions from existing code

3. **Transform**
   - Load template from ./claude/claude_md_template.md
   - Generate concise CLAUDE.md by filling template sections:
     - Sacred Vow (binding commitment to follow rules)
     - Project Context (one-line purpose)
     - Concurrent Execution Rules (performance critical)
     - Tech Stack (versions only)
     - Commands (must-run before commits)
     - Conventions (detected patterns)
     - DO NOT TOUCH (critical files)
     - Canary (verification)

4. **Validate**
   - Ensure all detected tools and frameworks are documented
   - Verify commands are executable and correct
   - Include rationale and examples for important rules
   - Report generation summary and recommendations

## Behavior

### Constraints

- Machine-optimized: terse bullet points, no fluff
- Use CRITICAL/MUST sparingly for true priorities
- Commands without explanation
- Pattern > explanation
- No junior dev onboarding content

### Error Scenarios

| Situation | Response |
|-----------|----------|
| No project files | Guide user to run in project root with recognizable structure |
| Existing CLAUDE.md | Offer options: update, merge, or replace |
| Unknown stack | Generate template with placeholders and guidance |

## Usage

/generate-claude-md  # Generate for current directory
/generate-claude-md ~/projects/my-app  # Generate for specific project
/generate-claude-md --update  # Update existing CLAUDE.md

## Output

Creates machine-optimized CLAUDE.md with:

- Sacred vow for rule compliance
- Concurrent execution rules
- Terse tech stack & commands
- Detected patterns (no explanations)
- Critical DO NOT TOUCH list
- Canary verification

## Template

The CLAUDE.md template is maintained in ./claude/claude_md_template.md and follows the Bushido Code pattern with sections for project context, concurrent execution rules, tech stack, commands, conventions, and critical files.
