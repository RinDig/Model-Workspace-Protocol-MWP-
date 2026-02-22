# Stage 03: Build

Take an animation spec and produce Remotion component code.

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
3. Implement each beat as a separate component
4. Use exact values from the design system for all colors, fonts, and sizes
5. Map spec components to Remotion implementations per build conventions
6. Stitch beats together in the index composition file
7. Follow file naming conventions
8. Save to output/

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Remotion composition | `output/[topic-slug]/` | Folder with index.tsx, beats/*.tsx, and assets/ |

The code files in `output/` are the human edit surface. Tweak animations, adjust timing, modify component props directly.
