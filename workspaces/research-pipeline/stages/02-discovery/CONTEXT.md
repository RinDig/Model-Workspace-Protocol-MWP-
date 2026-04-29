# Stage 02: Discovery

Gather information from web, documents, and other sources with credibility scoring.

## Inputs

| Source | File/Location | Why |
|--------|---------------|-----|
| Previous stage | `../01-scoping/output/research-goal.md` | Research plan |
| Brand vault | `../../brand-vault.md` | Source standards |
| Skill | `../../skills/mcp-search-tools/SKILL.md` | Search capability |
| Skill | `../../skills/prompt-injection-defense/SKILL.md` | Security |
| Reference | `references/credibility-scoring.md` | Scoring system |

## Process

1. Read research goal and key questions from previous stage
2. Plan search strategy for each key question
3. Execute searches using mcp-search-tools skill
4. **[Security]** Sanitize fetched content using prompt-injection-defense skill
5. For each source: calculate credibility score and assign tier
6. Filter sources below threshold (default: 40 points)
7. Collect sources with annotations (relevance, credibility)
8. Organize sources by question coverage
9. **[Checkpoint]** Present source summary with credibility assessment
10. Run audit checks, revise if needed
11. Write collected sources document to output/

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 8 | Source collection with credibility ratings and coverage map | Whether sources are sufficient |

## Verifiability

**Classification:** EXPERT-VERIFIABLE

**Verification Method:** Credibility score validation, source diversity check

**Human Review Trigger:** Always required (source review checkpoint)

## Audit

| Check | Pass Condition |
|-------|---------------|
| Source diversity | Sources from multiple domains/types |
| Credibility verified | Each source has credibility score and tier |
| Question coverage | Every key question has relevant sources |
| Proper attribution | All sources have complete citations |
| Content sanitized | All external content passed security validation |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Collected sources | `output/sources-collected.md` | Annotated list with credibility scores |
