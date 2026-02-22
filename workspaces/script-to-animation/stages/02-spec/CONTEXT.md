# Stage 02: Animation Specification

Take a finished script and produce a beat-by-beat animation specification defining the visual treatment for every line.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-script/output/` | Most recent script file (full) | The script to spec |
| Reference | `references/spec-format.md` | Full file | BEATS constants, frame-range syntax, beat structure |
| Reference | `references/component-registry.md` | Full file | Available animation components and their props |
| Reference | `references/design-system.md` | "Colors", "Typography", "Motion" sections | Visual constraints and exact values |
| Reference | `references/animation-guide.md` | Full file | Motion principles, visual rhythm, common mistakes |

## Process

1. Read the script from `../01-script/output/`
2. Break the script into beats (one concept per beat)
3. For each beat, define: frame range, narration, visual description, components, props, transition
4. Follow the spec format from `spec-format.md`
5. Reference only components that exist in the component registry
6. Use exact values from the design system for colors, fonts, and timing
7. Verify frame ranges are continuous (no gaps, no overlaps)
8. Add the spec metadata header
9. Save to output/

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Animation spec | `output/[topic-slug]-spec.md` | Beat-by-beat markdown with frame ranges, components, and props |

The spec file in `output/` is the human edit surface. Adjust timing, swap components, change visual treatments. Stage 03 reads whatever is in that file.
