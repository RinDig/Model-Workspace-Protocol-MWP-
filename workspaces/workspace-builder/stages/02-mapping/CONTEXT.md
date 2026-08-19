# Stage 02: Mapping

Turn the workflow map into formal stage contracts and verify the dependency graph.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-discovery/output/workflow-map.md` | Full file | The workflow to formalize |
| Core conventions | `../../../../_core/CONVENTIONS.md` | "Pattern 1: Stage Contracts" and "Pattern 3: One-Way Cross-References" | The rules for writing contracts |

## Process

1. Read the workflow map from discovery output
2. For each stage, write the formal Inputs/Process/Outputs contract following the stage contract pattern
3. Map cross-references: which stages read from which other stages?
4. Identify canonical sources: where does each piece of information live? (one home per fact)
5. Check for circular references: draw the dependency graph and verify it flows one way only
6. Verify every stage's output is consumed by at least one downstream stage (or is the final output)
7. **[Checkpoint]** -- Present the dependency diagram and contracts to the user. Ask: Does the flow make sense? Any missing connections?
8. Run the audit checks below. If any fail, revise before saving.
9. Produce the contracts document with a dependency diagram

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 6 | Dependency diagram and draft contracts for all stages | Whether the dependency flow and contract definitions are correct |

## Audit

| Check | Pass Condition |
|-------|---------------|
| No circular references | Dependency graph flows in one direction only |
| Output consumption | Every stage's output is read by at least one downstream stage or is the final deliverable |
| Contract completeness | Every stage has Inputs, Process, and Outputs sections with no empty fields |
| Canonical sources | No piece of information is defined as authoritative in more than one stage |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Stage contracts | `output/stage-contracts.md` | Formal Inputs/Process/Outputs blocks for every stage, plus ASCII dependency diagram |
