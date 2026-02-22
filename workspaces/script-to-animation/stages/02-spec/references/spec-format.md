# Spec Format Reference

How to write an animation specification. This defines the BEATS system, frame-range syntax, and the structure every spec file must follow.

---

## BEATS System

A BEAT is one logical visual segment. Each beat gets exactly one concept, one visual treatment, and one piece of narration.

Timing reference at 30fps:
- 1 second = 30 frames
- Short beat (a label or transition): 60-90 frames (2-3 seconds)
- Standard beat (one concept): 150-240 frames (5-8 seconds)
- Long beat (complex visual): 240-360 frames (8-12 seconds)

Total frame budget depends on target duration. A 60-second video is 1,800 frames.

---

## Frame Range Syntax

Every beat starts with a frame range in brackets:

```
### Beat 1 [0-90]
### Beat 2 [91-240]
### Beat 3 [241-420]
```

Frame ranges are inclusive. No gaps between beats. The end frame of Beat N is one less than the start frame of Beat N+1.

---

## Beat Structure

Every beat in a spec file contains these fields:

```markdown
### Beat [N] [start-end]

**Narration:** "The exact words spoken during this beat."

**Visual:** A description of what appears on screen. What moves, what appears, what transforms. Write this as if describing to an animator.

**Components:** List the components from the component registry used in this beat.

**Props:**
- component-name: { prop: value, prop: value }

**Transition:** How this beat connects to the next. Crossfade, cut, slide, etc. Include duration in frames.
```

---

## Example Beat

```markdown
### Beat 1 [0-90]

**Narration:** "You tapped send."

**Visual:** A phone screen centered in frame. A finger taps the send button. On tap, a ripple of light expands outward from the button, suggesting hidden complexity.

**Components:** PhoneFrame, TapRipple, TextReveal

**Props:**
- PhoneFrame: { screen: "message-app", scale: 0.8 }
- TapRipple: { origin: "send-button", color: "{{PRIMARY_COLOR}}", expandTo: 1.5 }
- TextReveal: { text: "You tapped send.", position: "bottom-third" }

**Transition:** Crossfade to Beat 2 over 15 frames.
```

---

## Spec File Header

Every spec file starts with metadata:

```markdown
---
source-script: [filename from 01-script/output/]
total-beats: [number]
total-frames: [number]
target-duration: [seconds]
fps: 30
platform: [platform name]
---
```

---

## Rules

1. One concept per beat. If a beat explains two things, split it.
2. Only reference components that exist in the component registry.
3. Frame ranges must be continuous. No gaps, no overlaps.
4. The narration must work as spoken audio. Read it out loud.
5. The visual must carry the argument. If you muted the audio, the viewer should still follow the core idea from visuals alone.
6. Props must use exact values from the design system (colors, fonts, sizes).
