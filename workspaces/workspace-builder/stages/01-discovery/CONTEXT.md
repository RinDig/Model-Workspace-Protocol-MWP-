# Stage 01: Discovery

Understand the domain workflow through conversation with the user. Folds the three principles from [`/_core/principles.md`](../../../../_core/principles.md) into the discovery itself: where the human steers, what is mechanical, and what has actually failed.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | Full workflow description plus answers to Q5-Q7 from setup | The domain to build a workspace for |
| Setup answers | `../../setup/questionnaire.md` | Answers collected during `setup` | Already-stated experience level, mechanical/judgment map, and named checkpoint moments |
| Principles | `/_core/principles.md` | Full file | The three principles drive the discovery questions |
| Reference | `../../references/conventions-reference.md` | Full file | Know the ICM patterns to discover toward |
| Reference | `../../references/examples/script-to-animation-summary.md` | Full file | Concrete example of a completed workspace |

## Process

1. Ask the user to describe their workflow end to end. What do they start with? What do they end with?
2. Identify the distinct stages. Where does one task end and another begin? Look for natural handoff points where a human might want to review or edit before continuing.
3. For each stage, ask:
   - What goes in? (files, user input, previous stage output)
   - What comes out? (the artifact this stage produces)
   - What does the agent need to know? (reference material, rules, constraints)
4. Identify shared context. What information is used across multiple stages? (brand voice, design system, audience data)
5. Identify user-specific details. What varies from one user to another? These become placeholder variables.
6. Identify optional stages. Are there stages some users might skip? These become conditional sections.
7. Identify tool prerequisites. For each stage, ask: does this stage need external tools? Note name, scope (required/optional), and what it does.
8. Discover relevant skills. Scan `~/.claude/skills/` and `~/.agents/skills/` and GitHub for skill repos. Present candidates. Let the user select.
9. **(Principle 2)** For each stage, list which steps are mechanical (a script could do it reliably) and which require judgment. Mechanical steps become `skills/[name]/scripts/` candidates. Judgment steps become Process steps with Checkpoints. Use the answer to setup Q6 as the starting point and press for specifics.
10. **(Principle 1)** For each stage, ask: where exactly does the human want to stop and look at the work? Name those moments. They become Checkpoint table entries. Use the answer to setup Q7 as the starting point. Do not invent checkpoints the user did not name.
11. **(Principle 3)** For each stage, ask: what have you actually seen fail? Examples: a phrase did not match, output exceeded a length limit, two stages disagreed on a file format, a script silently produced wrong output. Each named failure becomes one Audit table entry. If the user has Q5 = "Never", note it and mark the Audit sections "Initial audits, expand after first runs." Do not invent audit entries.
12. **[Checkpoint]** Present the workflow map draft to the user. Ask: Are all stages captured? Is the mechanical/judgment split correct? Are the named checkpoints where you actually want them? Are the audit entries traceable to real failures?
13. Run the audit checks below. If any fail, revise before saving.
14. Write the workflow map summarizing everything discovered.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 12 | Draft workflow map with: stages, inputs/outputs, shared context, variables, tools, skills, mechanical-vs-judgment split, named checkpoint moments, named failure modes | Whether the breakdown is accurate, the mechanical/judgment split is right, the checkpoints are where the human wants them, and every audit entry traces to a real incident |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Stage clarity | Every stage has a clear single responsibility and a named output artifact |
| Input/output chain | Every stage's inputs are either user-provided or produced by a prior stage |
| Shared context identified | Cross-stage resources (brand, design, audience) are listed separately from stage-specific references |
| Variable coverage | Every user-specific detail is captured as a named placeholder variable |
| Mechanical / judgment split | Every stage has been classified along the deterministic vs judgment line; no step is left ambiguous |
| Named checkpoints | Every checkpoint listed in the workflow map traces to a moment the user named in Q7 or during Process step 10. None were invented by the agent. |
| Earned audit entries | Every audit entry traces to a failure the user named in Q5/Q11. If Q5 = "Never", the audit sections are explicitly marked as initial and minimal. None were invented. |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Workflow map | `output/workflow-map.md` | Structured doc: stages with inputs/outputs, shared context, user-specific variables, optional stages, tool prerequisites, selected skills, mechanical/judgment split per stage, named checkpoint moments, named failure modes per stage |
