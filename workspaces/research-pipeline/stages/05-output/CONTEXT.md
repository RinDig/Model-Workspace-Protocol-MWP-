# Stage 05: Output

Format synthesized knowledge into final deliverable.

## Inputs

| Source | File/Location | Why |
|--------|---------------|-----|
| Previous stage | `../04-synthesis/output/knowledge-synthesized.md` | Content to format |
| Previous stage | `../02-discovery/output/sources-collected.md` | Credibility scores |
| Brand vault | `../../brand-vault.md` | Format preferences |
| Skill | `../../skills/prompt-injection-defense/SKILL.md` | Security |
| Reference | `references/output-templates.md` | Report formats |

## File Naming

All outputs follow: `report-YYYY-MM-DD-{topic-slug}.md` (lowercase, hyphens, max 30 chars)

## Process

1. Read synthesized knowledge and source credibility data
2. Determine output format (report, dataset, or documentation)
3. Load appropriate template, generate topic slug
4. **[Security]** Sanitize any source excerpts before inclusion
5. Format content, apply citation style from brand vault
6. **[Reflection]** Run reflection critique (5 criteria, see PROGRESS.md)
7. Revise if 2+ criteria fail (max 2 iterations)
8. Add metadata (date, methodology, source count, avg credibility)
9. **[Checkpoint]** Present formatted report for approval
10. Write markdown and JSON files, run audit

## Reflection Criteria (log in PROGRESS.md)

| Criterion | Pass Question |
|-----------|---------------|
| Answers Goal | Does this directly answer the research goal? |
| Sources Support Claims | Is every major claim backed by a source? |
| Actionable | Can someone act on this? |
| No Gaps | Are there questions unaddressed? |
| Assumptions Stated | Are key assumptions explicit? |

**Decision:** All 5 pass → finalize | 1 fail → minor fix | 2+ fail → major revision

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 9 | Formatted report content | Approve before finalizing |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Format compliance | Matches template structure |
| Citation accuracy | All properly formatted |
| Metadata present | Date, sources, methodology documented |
| File naming | `report-YYYY-MM-DD-slug.md` format |
| Reflection logged | Criteria logged in PROGRESS.md |

## Outputs

| Artifact | Location |
|----------|----------|
| Markdown report | `output/report-YYYY-MM-DD-{slug}.md` |
| Source data | `output/sources-YYYY-MM-DD-{slug}.json` |
