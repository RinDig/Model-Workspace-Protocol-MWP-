# Stage 03: Scaffolding

Generate the complete workspace folder structure, CONTEXT.md files, and placeholder reference files. Earned Checkpoints and Audit entries from Stage 01 carry through here unchanged; this stage does not invent them.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-mapping/output/stage-contracts.md` | Full file | The contracts to implement as folders and files |
| Discovery output | `../01-discovery/output/workflow-map.md` | "Mechanical / Judgment Split", "Named Checkpoints", "Named Failure Modes", "Tool Prerequisites", "Selected Skills" | Earned content the scaffold must carry forward without invention |
| Principles | `/_core/principles.md` | Full file | Bind scaffolding decisions to the three principles |
| Template | `/_core/templates/stage-context-template.md` | Full file | Template for stage CONTEXT.md files |
| Template | `/_core/templates/workspace-claude-template.md` | Full file | Template for the workspace CLAUDE.md |
| Template | `/_core/templates/workspace-context-template.md` | Full file | Template for the workspace CONTEXT.md |
| Syntax | `/_core/placeholder-syntax.md` | Full file | How to write placeholder variables |

## Process

1. Read the stage contracts from mapping output.
2. Create the workspace folder structure:
   - Root: CLAUDE.md, CONTEXT.md, setup/
   - Context folder (brand-vault or domain equivalent) with its own CONTEXT.md
   - stages/ with one numbered subfolder per stage, each containing CONTEXT.md, output/, and references/
   - shared/ for cross-stage reference files
   - skills/ if any skills were selected during discovery
3. Populate each stage CONTEXT.md using the template:
   - **Process steps:** For mechanical work (per the discovery split), write the step as a script call (`run scripts/X.py`) and add the script under `skills/[name]/scripts/`. For judgment work, write the step as a sentence describing what the agent attempts.
   - **Checkpoints:** Use only the moments the user named in Stage 01. Do not add any the user did not name. If a stage has no named checkpoints, delete the section entirely.
   - **Audit:** Use only the failure modes the user named in Stage 01. Do not add generic checks ("clarity", "completeness", etc.) the user did not mention. If the user has Q5 = "Never" (no real-run history), keep the section minimal with three to four obvious checks (e.g., output exists, file format is correct) and mark it "Initial audits, expand after first runs." If a stage's audits would otherwise be empty and invented, delete the section instead.
4. Create the workspace CLAUDE.md using the template: folder map, triggers, routing table, and What to Load section mapping each task to its minimal file set.
5. Create the workspace CONTEXT.md using the template: task routing table, shared resources.
6. Create placeholder reference files for each stage with `{{PLACEHOLDER}}` variables for user-specific content.
7. For content-producing workspaces, create a value framework reference file (see Pattern 13).
8. For code-producing workspaces, create a shared constants file or pattern (see Pattern 15).
9. Create the context folder (brand-vault equivalent) with placeholder files. If the workspace produces voice/style content, structure voice rules with Hard Constraints, Sentence Rules, and Pacing sections.
10. If skills were selected during discovery, create a skills/ folder:
    - For local skills: copy the entire skill folder into `skills/[skill-name]/`
    - For GitHub skills: clone the repo and copy the skill folder in
    - Move every script identified as mechanical in Stage 01 into the appropriate `skills/[name]/scripts/` folder; do not leave deterministic work as English prose in Process steps
    - Remove any custom reference files that the skill replaces
    - Update stage CONTEXT.md Inputs tables to reference `../../skills/[name]/SKILL.md`
11. If tools were identified that require system-level installation, write a setup guide in the relevant stage's `references/` folder.
12. Add `.gitkeep` files in all `output/` directories.
13. Run the audit checks below. If any fail, fix before saving.
14. Write everything to `output/`.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Folder structure | Every stage has CONTEXT.md, output/, and references/ |
| Contract fidelity | Every stage CONTEXT.md matches the contracts from Stage 02 |
| Placeholder syntax | All placeholders use `{{SCREAMING_SNAKE_CASE}}` format |
| `.gitkeep` coverage | Every output/ directory contains a .gitkeep file |
| CONTEXT.md size | No CONTEXT.md file exceeds 80 lines |
| Naming conventions | All folders and files use lowercase-with-hyphens |
| Mechanical work in scripts | Every step classified as mechanical in Stage 01 is realized as a script call, not English prose |
| Checkpoints traceable | Every Checkpoint row in every generated stage traces to a moment named in Stage 01. None were added by the scaffolder. |
| Audits traceable | Every Audit row in every generated stage traces to a failure named in Stage 01 (or the section is marked "Initial audits" when Q5 = Never). None were added by the scaffolder. |
| No em dashes | grep for U+2013 and U+2014 across the generated tree returns no results |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Generated workspace | `output/` | Complete folder structure with all files. Ready for questionnaire design. |
