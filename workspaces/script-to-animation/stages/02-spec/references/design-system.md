# Design System: {{BRAND_NAME}}

Exact visual values for specs and builds. When a spec says "primary color" or "heading font," these are the values.

---

## Colors

| Role | Value | Usage |
|------|-------|-------|
| Primary | `{{PRIMARY_COLOR}}` | Main brand color. Headings, key UI elements, emphasis. |
| Secondary | `{{SECONDARY_COLOR}}` | Supporting color. Backgrounds, secondary elements. |
| Accent | `{{ACCENT_COLOR}}` | Highlight color. Call-to-action, interactive elements, surprise moments. |
| Background | `{{BACKGROUND_COLOR}}` | Default background. |
| Text | `{{TEXT_COLOR}}` | Default text color. Must have sufficient contrast against Background. |

**Color rules:**
- Primary is for emphasis, not for everything. If more than 30% of the frame is Primary, it loses its impact.
- Accent is for moments of surprise or importance. Use sparingly.
- Text on Background must be legible at phone resolution (minimum 4.5:1 contrast ratio).

---

## Typography

| Role | Font | Weight | Size Range |
|------|------|--------|------------|
| Heading | `{{HEADING_FONT}}` | Bold (700) | 36-64px |
| Body | `{{BODY_FONT}}` | Regular (400) | 24-32px |
| Caption | `{{BODY_FONT}}` | Medium (500) | 18-24px |
| Label | `{{BODY_FONT}}` | Bold (700) | 14-20px |

**Typography rules:**
- All text must be readable on a 6-inch phone screen. If you have to squint, the text is too small.
- Headings use the heading font. Everything else uses the body font. Do not mix additional fonts.
- Line height for body text: 1.4x the font size.
- Maximum line length: 40 characters for video text. Shorter is better.

---

## Motion

| Property | Default | Notes |
|----------|---------|-------|
| Easing | `ease-out` | Most transitions. Fast start, gentle landing. |
| Entrance duration | 15-20 frames | Elements entering the frame. |
| Exit duration | 10-15 frames | Elements leaving. Exits are faster than entrances. |
| Crossfade | 15 frames | Default transition between beats. |
| Hold after entrance | 5-10 frames | Pause after an element appears before anything else moves. |

**Motion rules:**
- Every animation serves the narrative. No motion for decoration.
- Only one thing moves at a time. If two elements enter simultaneously, the viewer does not know where to look.
- Entrances are slower than exits. Elements earn attention arriving; they should not demand attention leaving.
- Layer reveals stack downward. Each new layer appears below the previous one.

---

## Spacing and Layout

| Property | Value | Notes |
|----------|-------|-------|
| Frame safe zone | 5% on all sides | Keep critical content inside this boundary. |
| Element spacing | 20-40px | Between distinct visual elements. |
| Text padding | 16px minimum | Around text blocks and captions. |
| Grid | 12-column | For alignment. Not every element snaps to grid. |

**Layout rules:**
- Phone-first. 80% of viewers are on mobile. Design for vertical or square formats when possible.
- Center of frame is highest attention. Place the most important element there.
- Lower third is for captions and secondary info. Do not put primary visuals there.
