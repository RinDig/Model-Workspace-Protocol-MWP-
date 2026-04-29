# Credibility Scoring

Evaluate source reliability systematically.

## Scoring Factors

| Factor | Points |
|--------|--------|
| Trusted domain (.edu, .gov, .org) | +30 |
| Academic/research path in URL | +10 |
|HTTPS enabled | +5 |
| Recent content (< 1 year) | +5 |
| Author credentials verifiable | +10 |
| Peer-reviewed publication | +20 |
| Primary source (original data) | +15 |
| Suspicious TLD (.xyz, .tk, .top) | -20 |
| No HTTPS | -10 |
| No author attribution | -10 |
| No publication date | -5 |

## Tiers
| Tier | Score Range | Usage |
|------|-------------|-------|
| High | 70+ | Primary evidence, cited directly |
| Medium | 40-69 | Supporting evidence, noted with caveat |
| Low | 20-39 | Background only, not cited |
| Unreliable | <20 | Exclude entirely |

## Domain Trust List
**High Trust (+30):**
- .edu, .gov, .org (established)
- Academic journal domains
- Major news outlets with editorial standards

**Medium Trust (+10):**
- .com (established companies)
- .io, .co (tech startups)
- .substack.com, .medium.com (known platforms)

**Low Trust (+0):**
- Personal blogs
- Forum posts
- Social media

**Negative (-20):**
- .xyz, .tk, .top
- Unknown TLDs
- Domains < 1 year old
