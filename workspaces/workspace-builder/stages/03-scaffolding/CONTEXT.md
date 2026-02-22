# Stage 03: Scaffolding

Generate the complete workspace folder structure, CONTEXT.md files, and placeholder reference files.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-mapping/output/stage-contracts.md` | Full file | The contracts to implement as folders and files |
| Discovery output | `../01-discovery/output/workflow-map.md` | "Tool Prerequisites" section | Tools that need setup guides |
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
   - prerequisites/ if any tools were identified (with CONTEXT.md and one setup guide per tool)
3. Populate each stage CONTEXT.md using the template, filled with the contract's inputs, process, and outputs
4. Create the workspace CLAUDE.md using the template: folder map, triggers, routing table
5. Create the workspace CONTEXT.md using the template: task routing table, shared resources
6. Create placeholder reference files for each stage with `{{PLACEHOLDER}}` variables for user-specific content
7. Create the context folder (brand-vault equivalent) with placeholder files
8. If tools were identified in the workflow map, create a prerequisites/ folder:
   - Write prerequisites/CONTEXT.md with a table of all tools, which stages need them, and whether each is required or optional
   - Write one setup guide per tool ([tool-name]-setup.md): what it is, how to install it, how to verify it works, and how the workspace uses it
   - If a tool is only used by one stage, the setup guide can live in that stage's references/ folder instead, but prerequisites/CONTEXT.md should still list it
9. Add .gitkeep files in all output/ directories
10. Write everything to output/

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Generated workspace | `output/` | Complete folder structure with all files. Ready for questionnaire design. |
