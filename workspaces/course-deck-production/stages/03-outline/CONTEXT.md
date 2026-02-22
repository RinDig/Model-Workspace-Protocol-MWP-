# Stage 03: Outline

Create a detailed slide-by-slide outline for each session in the curriculum.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-curriculum/output/[course-slug]-curriculum.md` | Full file | Session structure and content allocation |
| Previous stage | `../02-curriculum/output/[course-slug]-meta.md` | Full file | Course name, audience, session count |
| Shared | `../../shared/producer-identity.md` | Full file | Producer name |
| Template | `../../shared/course-meta.md` | Full file | Template for collecting course details (if entering here) |
| Design system | `../../design-system/CONTEXT.md` | Routes to palette, typography | Visual direction |
| Skill | `../../skills/pptx/SKILL.md` | Design principles, layout constraints | Slide layout rules |
| Skill | `../../skills/frontend-design/SKILL.md` | Full file | Design thinking, aesthetics |
| Reference | `references/slide-patterns.md` | Full file | Common slide types and when to use each |

## Process

1. If this is the entry stage (no Stage 02 output exists), collect course metadata from the user and write it to `output/[course-slug]-meta.md`. Also ask for the curriculum or have the user provide it directly.
2. Read the curriculum document
3. Load the design system via its CONTEXT.md
4. For each session in the curriculum:
   a. Determine slide count (target 15-25)
   b. Choose a slide type for each slide from the patterns library
   c. Write the content for each slide (title, bullets, speaker notes)
   d. Add visual direction (which colors, layout variant, chart/image needed)
   e. Flag any slide that needs a chart, table, or image (becomes a `class="placeholder"` in Stage 04)
5. Verify no single-column chart-below-text layouts (pptx SKILL.md constraint)
6. Ask the user to review outlines before generation
7. Save one outline file per session

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Course metadata | `output/[course-slug]-meta.md` | Carried forward or newly collected |
| Session outlines | `output/[session-slug]-outline.md` (one per session) | Markdown: slide-by-slide with type, content, notes, visual direction |
