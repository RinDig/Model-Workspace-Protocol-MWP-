# Slide Patterns

Common slide types for course decks. Use these as building blocks when outlining sessions.

## Pattern Library

### title-slide
**When:** First slide of every session.
**Layout:** Centered content, full-slide background (primary color or gradient PNG).
**Content:** Course name (14pt), session title (32-36pt bold), session number, instructor name (14pt).

### section-divider
**When:** Transitioning between major topics within a session.
**Layout:** Full-slide color block, centered title.
**Content:** Section name only. No bullets.

### content-bullets
**When:** Teaching concepts, listing items, explaining steps.
**Layout:** Header bar (primary color, white text) + bullet list below.
**Content:** Title in header, 4-6 bullet points maximum. Each bullet one line.

### content-two-column
**When:** Comparing two things, or pairing text with an image/chart.
**Layout:** Header bar + two columns (40/60 or 60/40 split).
**Content:** Title in header, left column for text, right column for visual.

### key-metric
**When:** Highlighting a single important number or statistic.
**Layout:** Oversized number centered (48-72pt bold), brief label below (16pt).
**Content:** One number, one label, optional source citation.

### definition
**When:** Introducing a key term.
**Layout:** Term in large text (28pt bold), definition below (16pt), optional example.
**Content:** Keep to one term per slide. Include a concrete example if possible.

### example-walkthrough
**When:** Walking through a concrete example step by step.
**Layout:** Header bar + numbered steps or sequential content.
**Content:** Title, 3-5 numbered steps with brief explanations.

### chart-slide
**When:** Showing data, trends, comparisons.
**Layout:** Full-slide chart or two-column (text left, chart right).
**Content:** Title, chart placeholder, brief interpretation below or beside chart.
**Note:** Mark the chart area as `class="placeholder"` in Stage 04.

### table-slide
**When:** Showing structured comparisons, feature matrices.
**Layout:** Full-slide table or two-column.
**Content:** Title, table placeholder.
**Note:** Mark the table area as `class="placeholder"` in Stage 04.

### image-slide
**When:** Showing a diagram, screenshot, or illustration.
**Layout:** Full-slide image with text overlay, or two-column.
**Content:** Title, image reference, brief caption.

### summary-slide
**When:** Last content slide of each session. Recap key takeaways.
**Layout:** Header bar + bullet list of 3-5 key points.
**Content:** "Key Takeaways" header, concise recap bullets matching learning objectives.

### end-slide
**When:** Final slide of every session.
**Layout:** Centered, minimal. Course name, session title, "Questions?" or call to action.

## Outline Format

Use this format for each slide in the outline:

```markdown
### Slide [N]: [Slide title]
- **Pattern:** [pattern-name from above]
- **Content:**
  - [Bullet or text content for this slide]
- **Speaker notes:** [What the presenter says -- 2-4 sentences]
- **Visual:** [Color, layout variant, chart/image flag if needed]
```
