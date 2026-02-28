# Stage 02: Animation Specification

Take a finished script and produce a spec that defines visual concepts and timing for each beat. The spec is a contract: it defines WHAT and WHEN, not HOW.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-script/output/` | Most recent script file (full) | The script to spec |
| Reference | `references/spec-format.md` | Full file | Contract format, required sections, rules |
| Reference | `references/design-system.md` | "Colors" and "Typography" sections | Visual values for color flow |
| Reference | `references/animation-guide.md` | Full file | Motion principles, visual rhythm |
| Skill | `../../skills/frontend-design/SKILL.md` | Full file | Design thinking, aesthetics, visual direction |

## Process

1. Read the script from `../01-script/output/`
2. Identify the core visual metaphor: what single visual idea makes this video work on mute?
3. Break the script into beats (one concept per beat) with approximate durations
4. Write the beat map table with narration, approximate timing, and mood
5. Write the visual philosophy: what a muted viewer should understand, and what visual density this video calls for (3-5 paragraphs)
6. Identify the 2-3 key moments that MUST land, and explain why each matters
7. Map audio sync points: specific narration words to visual events
8. Write the color flow: dominant color and mood per scene
9. Run the audit checks below. If any fail, revise before saving
10. Save to output/

## Audit

| Check | Pass Condition |
|-------|---------------|
| Mute test | Visual concepts create curiosity without audio |
| One concept per beat | No beat explains two things |
| Contract purity | Spec contains zero component names, frame numbers, or prop definitions |
| Key moments | 2-3 non-negotiable animations identified with clear rationale |
| Audio sync | At least 3 specific narration words mapped to visual events |
| Color flow | Every scene has a dominant color and mood assigned |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Animation spec | `output/[topic-slug]-spec.md` | Contract-format markdown (beat map, visual philosophy, key moments, sync points, color flow) |

The spec file in `output/` is the human edit surface. Adjust timing, change visual concepts, refine the color arc. Stage 03 reads whatever is in that file.
