# Contradiction Resolution

Handle conflicting findings systematically.

---

## Resolution Framework

### Step 1: Classify Contradiction Type

| Type | Definition | Resolution Strategy |
|------|------------|---------------------|
| **Direct** | A says X, B says not-X | Credibility-weighted choice |
| **Partial** | A says X always, B says X sometimes | Nuanced synthesis |
| **Contextual** | A says X in context C1, B says not-X in C2 | Context-dependent answer |
| **Temporal** | A said X earlier, B says not-X later | Timeline-dependent answer |
| **Methodological** | Different methods yield different results | Document both, explain why |

### Step 2: Apply Resolution Hierarchy

```
1. Credibility Score
   └─► Higher score wins (if >20 point gap)
   
2. Recency
   └─► More recent wins (if >2 year gap)
   
3. Primary vs Secondary
   └─► Primary source wins
   
4. Peer Review Status
   └─► Peer-reviewed wins
   
5. Sample Size (for studies)
   └─► Larger sample wins

If still tied → Mark as "Uncertain" with both positions
```

### Step 3: Document Resolution

```markdown
## [Topic]

**Conflict:** [Source A] claims X. [Source B] claims Y.

**Analysis:**
- Source A: Score [n], [date], [type]
- Source B: Score [n], [date], [type]

**Resolution:** [Position accepted]

**Reasoning:** [2-3 sentences explaining why]

**Confidence:** [High/Medium/Low]

**Caveat:** [If any uncertainty remains]
```

---

## When to Escalate

Escalate to human review when:
1. Credibility scores within 5 points
2. Both sources are high-credibility
3. Contradiction affects major conclusion
4. Resolution requires domain expertise
5. User has specific preference on debate topic

---

## Partial Resolution Template

When you cannot fully resolve:

```markdown
## [Topic]

**State of Evidence:** Mixed

**Position A:** [Summary] (supported by [sources])
**Position B:** [Summary] (supported by [sources])

**Current Consensus:** [If any exists in literature]

**Recommended Position:** [Tentative conclusion with caveat]

**Further Research Needed:** [What would resolve this]
```
