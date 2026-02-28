# Spec Format Reference

How to write an animation specification. A spec is a contract between voice recording and animation. It defines WHAT the output achieves and WHEN things happen. It does NOT prescribe HOW to implement. The build stage has creative freedom within the design system's quality floor.

---

## Spec File Header

Every spec file starts with metadata:

```markdown
---
title: [Video Title]
format: short-form | long-form
resolution: 1080x1920 | 1920x1080
fps: 30
core-metaphor: [One sentence -- the visual idea the whole video is built around]
color-arc: [Scene-by-scene color/mood progression, e.g., "Blue (revelation) > Amber (comparison) > Red (concession) > Blue (mirror)"]
source-script: [filename from 01-script/output/]
---
```

---

## Required Sections

### Beat Map

The timing contract. Each beat has a name, approximate duration, the narration text, and the mood. Durations are approximate. The builder calculates exact frames.

```markdown
| Beat | ~Duration | Narration (key lines) | Mood |
|------|-----------|----------------------|------|
| Hook | ~3s | "You tapped send." | Tension, intrigue |
| Build | ~8s | "That triggered 12,000 operations..." | Escalation, revelation |
| Core | ~12s | "Here is what actually happens." | Clarity, density |
| Close | ~4s | "The question was never..." | Resolution, compression |
```

**Timing reference at 30fps:**
- Short beat (label, transition): ~2-3 seconds
- Standard beat (one concept): ~5-8 seconds
- Long beat (complex visual): ~8-12 seconds

### Visual Philosophy

Two things to address in 3-5 paragraphs:

1. **What should a muted viewer understand?** What concepts need visual treatment (diagrams, SVGs, data viz, metaphor illustrations) versus text annotation? If you muted the audio, what is the visual argument?

2. **What visual density does this video call for?** Custom SVG illustrations with animated details? Split-screen comparisons? Morphing transitions between concepts? Layered diagrams that build over time? Signal the ambition level.

### Key Moments

The 2-3 animations that MUST land for the video to work. These are the non-negotiable creative requirements. For each, explain what it is and why it matters to the argument.

```markdown
1. **[Moment name]** -- [What it is and why it matters]
2. **[Moment name]** -- [What it is and why it matters]
```

### Persistent Elements

Anything that spans multiple scenes: a recurring visual, a background element that evolves, a counter that keeps running. Delete this section if nothing persists.

### Audio Sync Points

Specific narration words or phrases mapped to visual events. This is the fine-grained alignment layer between voice and animation.

```markdown
- "exact quote from narration" > [visual event that should happen]
- "exact quote" > [visual event]
```

### Color Flow

Scene-by-scene color and mood. Dominant color and emotional register per beat. Not hex codes for every element.

```markdown
| Scene | Dominant Color | Mood |
|-------|---------------|------|
| Hook | Blue | Tension, mystery |
| Build | Amber | Escalation |
| Close | Blue | Mirror, resolution |
```

---

## What a Spec Does NOT Contain

- **Frame numbers.** Durations are approximate. The builder calculates exact frames.
- **Component names.** The spec describes visual concepts, not which components to use.
- **Pixel positions.** Layout is a build decision.
- **Spring configs or easing values.** Animation implementation is a build decision.
- **Prop definitions.** The spec describes what should happen, not what props to pass.

The build stage has the design system (the quality floor) and skill rules (the API reference). It does not need the spec to tell it which tools to use.

---

## Example Beat (Contract Style)

```markdown
### Hook (~3s)

**Narration:** "You tapped send."

**Visual:** A phone screen centered in frame. A finger taps the send button. On tap, energy radiates outward from the button, suggesting hidden complexity beneath a simple action. The viewer should feel "wait, what just happened?"

**Mood:** Tension, intrigue. Intimate scale (one finger, one screen) about to expand.
```

Compare with what NOT to write:

```markdown
### Beat 1 [0-90]
Components: PhoneFrame, TapRipple, TextReveal
Props:
- PhoneFrame: { screen: "message-app", scale: 0.8 }
- TapRipple: { origin: "send-button", color: "#3B82F6", expandTo: 1.5 }
```

The first version tells the builder the creative intent. The second tells the builder which tools to use. The first produces better output because the builder can choose the best implementation.

---

## Rules

1. One concept per beat. If a beat explains two things, split it.
2. The visual must carry the argument. If you muted the audio, the viewer should still follow the core idea from visuals alone.
3. The narration must work as spoken audio. Read it out loud.
4. Describe visual concepts, not implementation. "Energy radiates outward" not "TapRipple with expandTo: 1.5."
5. Durations are approximate. Do not lock them to exact frames.
