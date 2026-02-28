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

---

## Recipes

Concrete patterns for common build tasks. Copy and adapt these.

### Scene Depth Stack

Build scenes from back to front. Every scene should have atmospheric layers behind the content:

```
Background    -- Base color, gradient, grid pattern, particle field, vignette
Mid-ground    -- Focal content: diagram, SVG illustration, data viz, animation
Foreground    -- Annotation: text labels, numbers, callouts, film grain
```

Mid-ground is the focal layer. Background and foreground should be rich, not sparse. A flat-colored background with nothing in it looks cheap. A mid-ground with no visual content is a text slide.

### Surface Treatment

Visual blocks (cards, panels, diagram elements) should have layered surfaces, not flat-colored rectangles. A basic surface treatment includes:

1. Base gradient (subtle, using the element's color at low opacity)
2. Edge highlight (thin line along top edge for glass/depth effect)
3. Border radius (consistent across all elements)

A flat-colored rect with text inside it is the most common quality failure. Even minimal surface treatment (gradient + edge) fixes it.

### Beat Orchestration

Stagger element entrances within a beat. Everything appearing at once feels cheap. Everything entering one at a time with small delays feels choreographed:

```
Element A enters at beat start
Element B enters 10-15 frames later
Element C enters 10-15 frames after B
Label appears 5 frames after its parent element
```

### Transition Patterns

Use scene transitions between beats, not hard cuts. Common patterns:
- **Crossfade** -- standard, works for most transitions
- **Slide** -- one scene pushes the other out, good for linear progression
- **Wipe** -- revealing the next scene, good for reveals
- **Scale** -- zoom into or out of an element to bridge scenes

---

## Anti-Patterns

| Error | Why It Fails |
|-------|-------------|
| **Text slide** | No mid-ground visual. Scene is just text on a background. No content, no argument. |
| **Fade-from-black open** | Frame 1 is dead. Viewer scrolls past before anything appears. |
| **Audio-dependent hook** | Most viewers scroll muted. Visual + text must work alone. |
| **Flat scene** | Background is a solid color, no atmospheric layers, no surface treatment. Looks amateur. |
| **Single animation track** | One thing moving while everything else is static. Multiple simultaneous tracks create life. |
| **Everything at once** | All elements appear in the same frame. Stagger entrances for choreographed feel. |
| **Code as focal element** | Gates non-programmers. Code is texture or authenticity marker, not content. |
| **Static frame + voiceover** | Dead screen. Always have motion, even subtle camera drift or element pulse. |

---

## Production Checklist

Run this before considering a build done. Referenced by the build stage audit.

- [ ] Hook works on mute (visual creates curiosity without audio)
- [ ] Frame 1 has active motion (no fade-from-black)
- [ ] Every scene has a mid-ground visual (no text slides)
- [ ] Every scene has atmospheric depth (not a flat-colored background)
- [ ] Visual blocks have surface treatment (not flat-colored rectangles)
- [ ] Multiple animation tracks running per scene (not just one thing moving)
- [ ] Beat entrances are staggered (not everything appearing at once)
- [ ] Type meets scale minimums for target format
- [ ] Critical content within safe zones
- [ ] One focal concept per beat
- [ ] Scene transitions between beats (no hard cuts)
- [ ] All motion via spring/interpolate (no CSS animations)
