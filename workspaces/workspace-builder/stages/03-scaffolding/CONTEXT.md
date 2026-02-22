# Stage 03: Scaffolding

Generate the complete workspace folder structure, CONTEXT.md files, and placeholder reference files.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-mapping/output/stage-contracts.md` | Full file | The contracts to implement as folders and files |
| Discovery output | `../01-discovery/output/workflow-map.md` | "Tool Prerequisites" and "Selected Skills" sections | Tools that need setup guides, skills to bundle |
| Template | `/_core/templates/stage-context-template.md` | Full file | Template for stage CONTEXT.md files |
| Template | `/_core/templates/workspace-claude-template.md` | Full file | Template for the workspace CLAUDE.md |
| Template | `/_core/templates/workspace-context-template.md` | Full file | Template for the workspace CONTEXT.md |
| Syntax | `/_core/placeholder-syntax.md` | Full file | How to write placeholder variables |

## Process

1. Read the stage contracts from mapping output
2. Create the workspace folder structure:
   - Root: CLAUDE.md, CONTEXT.md, setup/
   - Context folder (brand-vault or domain equivalent) with its own CONTEXT.md
   - stages/ with one numbered subfolder per stage, each containing CONTEXT.md, output/, and references/
   - shared/ for cross-stage reference files
   - skills/ if any skills were selected during discovery
3. Populate each stage CONTEXT.md using the template, filled with the contract's inputs, process, and outputs
4. Create the workspace CLAUDE.md using the template: folder map, triggers, routing table
5. Create the workspace CONTEXT.md using the template: task routing table, shared resources
6. Create placeholder reference files for each stage with `{{PLACEHOLDER}}` variables for user-specific content
7. Create the context folder (brand-vault equivalent) with placeholder files
8. If skills were selected during discovery, create a skills/ folder:
   - For local skills (found in `~/.claude/skills/` or `~/.agents/skills/`): copy the entire skill folder into `skills/[skill-name]/`
   - For GitHub skills: clone the repo and copy the skill folder in, or note the clone command in a setup guide
   - Remove any custom reference files that the skill replaces (avoid duplication)
   - Update stage CONTEXT.md Inputs tables to reference `../../skills/[name]/SKILL.md` instead of deleted reference files
9. If tools were identified that require system-level installation (Node.js, Python, LibreOffice), write a setup guide in the relevant stage's `references/` folder. Tools bundled inside skills do not need separate setup guides.
10. Add .gitkeep files in all output/ directories
11. Write everything to output/

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Generated workspace | `output/` | Complete folder structure with all files. Ready for questionnaire design. |
