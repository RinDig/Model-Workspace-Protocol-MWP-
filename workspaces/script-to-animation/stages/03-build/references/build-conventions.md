# Build Conventions

How to turn an animation spec into Remotion code. Follow these patterns for file structure, naming, and component implementation.

---

## Project Structure

```
output/
├── [slug]/
│   ├── index.tsx              (main composition -- stitches beats together)
│   ├── beats/
│   │   ├── Beat01.tsx         (first beat component)
│   │   ├── Beat02.tsx         (second beat component)
│   │   └── ...
│   └── assets/                (images, fonts, audio if needed)
```

Each spec becomes its own folder. Beats are individual components composed into the main index file.

---

## File Naming

- Composition folder: `[topic-slug]/` (lowercase-with-hyphens, matches the script slug)
- Beat files: `Beat01.tsx`, `Beat02.tsx` (PascalCase with zero-padded number)
- Main composition: `index.tsx`
- Asset files: `[descriptive-name].[ext]` (lowercase-with-hyphens)

---

## Beat Component Pattern

Every beat component follows this structure:

```tsx
import { useCurrentFrame, interpolate } from "remotion";

interface Beat01Props {
  startFrame: number;
  endFrame: number;
}

export const Beat01: React.FC<Beat01Props> = ({ startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;
  const duration = endFrame - startFrame;

  // Animation logic using localFrame and duration
  const opacity = interpolate(localFrame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ opacity }}>
      {/* Beat content */}
    </div>
  );
};
```

Key patterns:
- Every beat receives `startFrame` and `endFrame` as props
- Calculate `localFrame` by subtracting `startFrame` from the global frame
- Use `interpolate()` for all animated values
- Always set `extrapolateRight: "clamp"` to prevent values going past their target

---

## Composition Pattern

The index file stitches beats together:

```tsx
import { Composition } from "remotion";
import { Beat01 } from "./beats/Beat01";
import { Beat02 } from "./beats/Beat02";

export const MainComposition: React.FC = () => {
  return (
    <>
      <Beat01 startFrame={0} endFrame={90} />
      <Beat02 startFrame={91} endFrame={240} />
    </>
  );
};
```

Frame ranges come directly from the spec. Do not recalculate them.

---

## Using the Design System

Import values from the design system as constants at the top of each file:

```tsx
const COLORS = {
  primary: "{{PRIMARY_COLOR}}",
  secondary: "{{SECONDARY_COLOR}}",
  accent: "{{ACCENT_COLOR}}",
  background: "{{BACKGROUND_COLOR}}",
  text: "{{TEXT_COLOR}}",
};

const FONTS = {
  heading: "{{HEADING_FONT}}",
  body: "{{BODY_FONT}}",
};
```

After onboarding, these placeholders become real values. Before onboarding, they serve as clear markers for where values go.

---

## Component Mapping

Map spec components to Remotion implementations:

| Spec Component | Implementation | Notes |
|----------------|---------------|-------|
| TextReveal | Custom component with character-by-character interpolation | Use spring() for natural feel |
| BackgroundGradient | CSS linear-gradient or radial-gradient | Static, no animation needed |
| LayerDiagram | Stacked divs with staggered entrance animations | Core component for Layered Reveal |
| SlideIn | translateX/translateY with interpolate() | Direction maps to axis |
| FadeTransition | opacity interpolation | Simplest transition |
| ScaleUp | transform: scale() with interpolate() | Use spring() for bounce |

---

## Timing Conventions

- 30fps throughout. Do not change this.
- Frame ranges from the spec are authoritative. Do not adjust timing in the build.
- Transitions between beats: implement as overlap. Beat N's exit and Beat N+1's entrance share frames.
- If the spec says "crossfade over 15 frames," both beats render during those 15 frames with opposing opacity interpolations.

---

## Key Remotion APIs

The essential functions for building animations:

**`useCurrentFrame()`** -- Returns the current frame number. Inside a `<Sequence>`, this resets to 0 at the Sequence start.

**`useVideoConfig()`** -- Returns `{ width, height, fps, durationInFrames }`. Use `fps` for time-based calculations.

**`interpolate(frame, inputRange, outputRange, options)`** -- Maps frame values to animation values. Always pass `{ extrapolateRight: "clamp" }` to prevent values going past their target.

```tsx
const opacity = interpolate(frame, [0, 20], [0, 1], {
  extrapolateRight: "clamp",
});
```

**`spring({ frame, fps, config })`** -- Physics-based animation (0 to 1). Config options: `mass`, `damping`, `stiffness`. Use for entrances and anything that should feel physical.

```tsx
const scale = spring({
  frame,
  fps,
  config: { mass: 1, damping: 10, stiffness: 100 },
});
```

**`<Sequence from={N} durationInFrames={M}>`** -- Mounts children at frame N for M frames. Children see frame 0 at their own start. Use for organizing beats and staggering elements.

**`Easing`** -- Custom timing curves. `Easing.inOut(Easing.quad)` for smooth acceleration. `Easing.bezier()` for custom curves.

---

## Remotion Skills Integration

If the Remotion project was set up with Skills installed (`npx create-video@latest` with Skills enabled), Claude Code has access to Remotion-specific animation knowledge. This means it can:

- Generate spring-based animations with appropriate damping/stiffness values
- Structure compositions with proper Sequence nesting
- Handle async data loading with `delayRender()`/`continueRender()`
- Use TailwindCSS for styling (if installed during setup)

When building from a spec, let Claude Code handle the implementation details. Focus your edits on the visual result, not the code structure.

---

## Testing

- Preview individual beats by temporarily setting their frame range as the composition's duration
- Preview the full composition to check flow and transitions
- Watch at 1x speed to verify pacing matches intended duration
- Check on a mobile viewport (vertical if the platform is TikTok/Reels)
- See `remotion-setup.md` for rendering the final video
