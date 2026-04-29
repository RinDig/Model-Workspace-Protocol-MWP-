# Stage 03: Analysis

Process collected sources and extract insights.

## Inputs

| Source | File/Location | Why |
|--------|---------------|-----|
| Previous stage | `../02-discovery/output/sources-collected.md` | Sources to analyze |
| Previous stage | `../01-scoping/output/research-goal.md` | Key questions |
| Skill | `../../skills/prompt-injection-defense/SKILL.md` | Security |
| Reference | `references/analysis-frameworks.md` | Categorization patterns |

## Process

1. Read all collected sources and annotations
2. **[Security]** Re-sanitize any quotes/excerpts before extraction
3. Apply categorization framework (theme, type, finding)
4. Extract key findings from each source
5. Link findings to specific research questions
6. Identify patterns across multiple sources
7. Note contradictions between sources
8. Identify gaps in evidence
9. Organize findings by question and theme
10. Run audit checks, revise if needed
11. Write analyzed findings document to output/

## Verifiability

**Classification:** MACHINE-VERIFIABLE

**Verification Method:** All sources processed, all required fields populated

**Human Review Trigger:** If contradictions found >30% of findings OR gaps >30% of questions

## Audit

| Check | Pass Condition |
|-------|---------------|
| All sources processed | Every source has extracted findings |
| Findings categorized | Organized by theme and question |
| Patterns identified | Cross-source patterns noted |
| Evidence linked | Each claim linked to source |
| Contradictions noted | Conflicting findings identified |
| Excerpts sanitized | All quoted content passed security check |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Analyzed findings | `output/findings-analyzed.md` | Categorized findings, patterns, contradictions |
