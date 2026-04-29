# Quality Gates

Inter-stage verification checkpoints for the research pipeline.

---

## Gate Structure

Each gate has two layers:
- **Layer 1 (Structural):** Machine-verifiable checks (file exists, format correct)
- **Layer 2 (Semantic):** Content quality checks (alignment with goals, completeness)

---

## Gate: Pre-Pipeline

**Trigger:** Before research begins

### Layer 1 (Structural)

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Workspace initialized | CLAUDE.md and CONTEXT.md exist | Run `setup` |
| No stale outputs | output/ folders empty or intentionally preserved | Ask user to clear or confirm |

### Layer 2 (Semantic)

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Clear research intent | User stated topic or question | Ask clarifying questions |
| Scope boundaries | What is in/out of scope is understood | Request scope clarification |

---

## Gate: Scoping → Discovery

**Trigger:** After 01-scoping completes

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Goal defined | Research goal clearly stated | Complete scoping |
| Questions actionable | Key questions can guide search | Revise questions |
| Methodology selected | Approach matches topic complexity | Revise methodology |

**Human Gate:** Present research goal for confirmation before proceeding.

---

## Gate: Discovery → Analysis

**Trigger:** After 02-discovery completes

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Sources gathered | Sources documented with credibility scores | Re-run discovery |
| Sufficient coverage | Sources address all key questions | Expand search |

---

## Gate: Analysis → Synthesis

**Trigger:** After 03-analysis completes

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Findings extracted | Key insights surfaced from each source | Deepen analysis |
| Patterns identified | Common themes or contradictions noted | Review analysis |

---

## Gate: Synthesis → Output

**Trigger:** After 04-synthesis completes

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Conclusions drawn | Answers to research questions stated | Complete synthesis |
| Contradictions addressed | Conflicting findings explained or flagged | Address gaps |

**Human Gate:** Present conclusions for review before generating final output.

---

## Gate: Output → Complete

**Trigger:** After 05-output completes

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| Report exists | Output file generated | Re-run output |
| Format correct | Structure follows template | Fix formatting |
| Complete report | All sections populated | Complete missing sections |

**Human Gate:** Final report requires approval.

---

## Quick Reference

| Gate | Human Gate? | Key Check |
|------|-------------|-----------|
| Pre-Pipeline | Yes (if ambiguous) | Clear research intent |
| Scoping → Discovery | Yes | Goal confirmation |
| Discovery → Analysis | No | Sources gathered |
| Analysis → Synthesis | No | Findings extracted |
| Synthesis → Output | Yes | Conclusions reviewed |
| Output → Complete | Yes | Final approval |
