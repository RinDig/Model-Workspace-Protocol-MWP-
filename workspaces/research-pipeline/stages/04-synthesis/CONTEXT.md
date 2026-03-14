# Stage 04: Synthesis

Combine findings into coherent conclusions through multi-pass analysis.

## Inputs

| Source | File/Location | Why |
|--------|---------------|-----|
| Previous stage | `../03-analysis/output/findings-analyzed.md` | Findings to synthesize |
| Previous stage | `../02-discovery/output/sources-collected.md` | Credibility scores |
| Previous stage | `../01-scoping/output/research-goal.md` | Goal, questions |
| Reference | `references/synthesis-process.md` | Multi-pass process |
| Reference | `references/contradiction-resolution.md` | Conflict handling |

## Process

See `references/synthesis-process.md` for detailed workflow:

1. **[Pass 1]** Gather and score findings by credibility
2. **[Pass 2]** Detect contradictions between sources
3. **[Pass 3]** Resolve contradictions using credibility hierarchy
4. **[Pass 4]** Identify knowledge gaps
5. **[Pass 5]** Structure narrative with confidence levels
6. **[Checkpoint]** Present key conclusions with evidence
7. Run audit checks, revise if needed
8. Write synthesized knowledge document to output/

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 5 | Key conclusions with evidence, contradictions resolved, gaps | Whether conclusions are well-supported |

## Verifiability

**Classification:** EXPERT-VERIFIABLE

**Verification Method:** Evidence quality, logical conclusion flow

**Human Review Trigger:** Always required (conclusion review checkpoint)

## Audit

| Check | Pass Condition |
|-------|---------------|
| Evidence supports conclusions | Each conclusion has 2+ supporting sources |
| Contradictions addressed | All conflicts documented with resolution |
| Gaps acknowledged | Unanswered questions stated |
| Confidence levels | Each conclusion has confidence rating |
| Questions answered | Each key question has response |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Synthesized knowledge | `output/knowledge-synthesized.md` | Conclusions, contradictions, gaps, confidence |
