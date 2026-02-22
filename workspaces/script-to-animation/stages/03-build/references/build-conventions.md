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

## Remotion API Reference

For all Remotion APIs (animations, timing, sequencing, transitions, fonts, audio, charts, etc.), see the bundled skill:
- `../../skills/remotion-best-practices/SKILL.md` -- index of all rule files
- `../../skills/remotion-best-practices/rules/animations.md` -- core animation patterns
- `../../skills/remotion-best-practices/rules/timing.md` -- interpolation and spring physics
- `../../skills/remotion-best-practices/rules/sequencing.md` -- Sequence nesting and staggering
- `../../skills/remotion-best-practices/rules/transitions.md` -- scene transitions

Read individual rule files as needed for specific topics (fonts, audio, charts, text animations, etc.).

---

## Testing

- Preview individual beats by temporarily setting their frame range as the composition's duration
- Preview the full composition to check flow and transitions
- Watch at 1x speed to verify pacing matches intended duration
- Check on a mobile viewport (vertical if the platform is TikTok/Reels)
- Render final video: `npx remotion render MyVideo output.mp4`
- See `remotion-setup.md` for project setup and troubleshooting
