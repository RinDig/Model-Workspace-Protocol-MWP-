# Stage 03: Build

Take an animation spec and produce Remotion component code.

<!-- After loading the reference docs and skill rules below, you have the complete
     reference. Do not read other output/ files to learn patterns. -->

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-spec/output/` | Most recent spec file (full) | The spec to implement |
| Reference | `references/build-conventions.md` | Full file | File structure, naming, beat/composition patterns |
| Skill | `../../skills/remotion-best-practices/SKILL.md` | Index, then load rule files as needed | Remotion APIs, animations, timing, sequencing, transitions |
| Skill | `../../skills/frontend-design/SKILL.md` | Full file | Design thinking, aesthetics |
| Stage 02 reference | `../02-spec/references/component-registry.md` | Full file | Component implementation reference |
| Stage 02 reference | `../02-spec/references/design-system.md` | "Colors" and "Typography" sections | Exact values for code |
| Reference | `references/remotion-setup.md` | Full file | Project setup, rendering, troubleshooting |

## Process

1. Read the spec from `../02-spec/output/`
2. Create the composition folder structure per build conventions
3. Interpret the spec's visual concepts and implement each beat as a separate component. The spec defines WHAT and WHEN; choose HOW (animation approach, layout, component choices, transitions)
4. Use exact values from the design system for all colors, fonts, and sizes
5. Stitch beats together in the index composition file with transitions (no hard cuts unless the spec specifically calls for one)
6. Follow file naming conventions
7. Run the audit checks below. If any fail, revise before saving
8. Save to output/

## Audit

| Check | Pass Condition |
|-------|---------------|
| Spec coverage | Every beat from the spec has a corresponding implementation |
| Design system compliance | Colors, fonts, and sizes reference shared constants, not hardcoded values |
| Platform specs | Output dimensions and duration match platform requirements |
| Transitions | No hard cuts between beats (unless spec specifically calls for it) |
| Mobile readability | All text is readable at phone resolution |
| Safe zones | No critical content in the outer 5% of frame |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Remotion composition | `output/[topic-slug]/` | Folder with index.tsx, beats/*.tsx, and assets/ |

The code files in `output/` are the human edit surface. Tweak animations, adjust timing, modify component props directly.
