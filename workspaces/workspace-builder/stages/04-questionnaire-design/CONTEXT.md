# Stage 04: Questionnaire Design

Build the onboarding questionnaire that hydrates the new workspace's placeholder variables.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Discovery output | `../01-discovery/output/workflow-map.md` | "User-Specific Variables" section | Variables that need onboarding questions |
| Scaffolding output | `../03-scaffolding/output/` | All files containing `{{PLACEHOLDER}}` patterns | Know where every placeholder lives |
| Template | `/_core/templates/questionnaire-template.md` | Full file | Format and design rules to follow |
| Syntax | `/_core/placeholder-syntax.md` | Full file | Placeholder and conditional section rules |

## Process

1. Read the workflow map's user-specific variables section
2. Scan all markdown files in the scaffolded workspace for `{{PLACEHOLDER}}` patterns. Build a complete list.
3. Split variables into two buckets:
   - **System-level:** Things that stay the same across runs (identity, brand, design, tools, workflow preferences). These become setup questions.
   - **Per-run:** Things that change each time the pipeline runs (project name, topic, audience, scope). These do NOT become setup questions. Instead, the entry stage's CONTEXT.md should collect them conversationally at the start of each run.
4. For each system-level placeholder, write a question:
   - Question text that a non-technical person can understand
   - The placeholder(s) it populates
   - The files where those placeholders appear
   - Input type (free text, multiple choice, yes/no)
   - A sensible default or example so the user can skip if they do not care
5. For voice/style questions, ask for concrete examples rather than descriptions. "Give me 2-3 sentences that sound like your brand" extracts pattern-matchable rules. "Describe your voice" extracts an abstraction the agent must interpret. See Rule 7 in the questionnaire template.
6. If a field can be derived from another answer, list it as a derived field under the source question. The agent fills derived fields without asking.
7. Write ALL questions as a flat numbered list -- no category groupings. The user should be able to answer everything in a single message.
8. Add conditional logic for optional stages: yes/no questions that remove folders or `{{?SECTION}}` blocks.
9. If the workspace has voice/style rules with derived fields, add a two-pass process: after the agent populates rules from answers, it presents them to the user for review before finalizing. This catches misinterpretations.
10. Verify every system-level placeholder has a corresponding question
11. Verify per-run placeholders are handled by stage CONTEXT.md files, not the questionnaire
12. Write the questionnaire.md

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Questionnaire | `output/questionnaire.md` | Flat, all-at-once questionnaire for the new workspace's setup/ folder |
