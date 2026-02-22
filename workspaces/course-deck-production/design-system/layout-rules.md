# Layout Rules

Constraints and patterns for slide layouts. These rules prevent common generation failures.

## Slide Dimensions

- Aspect ratio: 16:9
- HTML body: `width: 720pt; height: 405pt`
- PptxGenJS layout: `LAYOUT_16x9`

## Hard Constraints (from pptx skill)

1. **Never stack charts/tables below text in a single column.** Use two-column layout (text left, chart right) or full-slide chart layout.
2. **All text must be inside `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>` tags.** Text in bare `<div>` or `<span>` will not appear in PowerPoint.
3. **Never use `<br>` tags.** Use separate text elements for each line.
4. **Never use manual bullet symbols** (-, *, etc.). Use `<ul>` or `<ol>` lists.
5. **Never use CSS gradients.** Rasterize gradients to PNG using Sharp first.
6. **Hex colors in PptxGenJS must NOT have `#` prefix.** Use `"4472C4"` not `"#4472C4"`.

## Recommended Layouts

### Title Slide
Full-width centered content. Course name large (36pt+), session title below (24pt), instructor name small (14pt).

### Content Slide
Header bar across top (primary color background, white text). Body area below with 30pt left margin.

### Two-Column
Header spanning full width. Two columns below: 40/60 or 60/40 split. Good for text + chart, text + image, or comparison.

### Key Metric
Oversized number (48-72pt bold) centered, with brief label below (16pt).

### Section Divider
Full-slide color block (primary or secondary), centered section title in contrasting color.

### Summary/Recap
Bullet list of key takeaways. Use consistent bullet styling.

## Visual Patterns

- Use consistent header bar height across all content slides (50-60pt)
- Left-align body content; center only titles and section dividers
- Use accent color for emphasis, not bold-and-color together
- Maximum 6-7 bullet points per slide
- Maximum 30-40 words per slide (excluding speaker notes)
