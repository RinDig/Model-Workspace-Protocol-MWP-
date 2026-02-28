# Build Conventions

How to turn an animation spec into Remotion code. The spec defines WHAT and WHEN. The design system defines the quality floor. You decide HOW.

---

## Creative Freedom

The builder has full creative latitude for implementation:

- **Animation approach** -- which Remotion APIs, spring configs, easing curves
- **Layout** -- pixel positions, element sizing, composition within safe zones
- **Component choices** -- reuse, customize, or build new
- **Visual interpretation** -- how to realize the spec's visual concepts in actual animation
- **Transitions** -- fade, slide, wipe, light leaks, or custom

The spec's timing is approximate. Calculate exact frames from the beat map durations. The design system's production standard (depth stack, surface treatment, motion patterns) is the quality floor: creative freedom means choosing how to implement those requirements, not whether to implement them.

---

## Shared Constants

Import values from the shared constants file. Do not hardcode colors, fonts, or timing values in beat components.

```tsx
import { COLORS, FONTS } from "../constants";
```

After onboarding, the constants file contains the brand's exact values. Every build output imports from this single source.

If the workspace does not have a constants file yet, define values at the top of your index file and note that they should be extracted to shared constants.

---

## Project Structure

```
output/
├── [slug]/
│   ├── index.tsx              (main composition -- stitches beats together)
│   ├── beats/
│   │   ├── Beat01.tsx         (first beat component)
│   │   ├── Beat02.tsx
│   │   └── ...
│   ├── constants.ts           (shared values: colors, fonts, timing)
│   └── assets/                (images, fonts, audio if needed)
```

Each spec becomes its own folder. Beats are individual components composed into the main index file.

---

## File Naming

- Composition folder: `[topic-slug]/` (lowercase-with-hyphens, matches the script slug)
- Beat files: `Beat01.tsx`, `Beat02.tsx` (PascalCase with zero-padded number)
- Main composition: `index.tsx`
- Constants: `constants.ts`
- Asset files: `[descriptive-name].[ext]` (lowercase-with-hyphens)

---

## Beat Component Pattern

Every beat component follows this structure:

```tsx
import { useCurrentFrame, interpolate, spring } from "remotion";
import { COLORS, FONTS } from "../constants";

interface Beat01Props {
  startFrame: number;
  endFrame: number;
}

export const Beat01: React.FC<Beat01Props> = ({ startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;
  const duration = endFrame - startFrame;

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
- Import colors and fonts from shared constants

---

## Composition Pattern

The index file stitches beats together. Calculate frame ranges from the spec's approximate durations:

```tsx
import { Beat01 } from "./beats/Beat01";
import { Beat02 } from "./beats/Beat02";

// Calculated from spec beat map (~3s hook, ~8s build at 30fps)
const BEATS = {
  HOOK: { start: 0, end: 89 },
  BUILD: { start: 90, end: 329 },
};

export const MainComposition: React.FC = () => {
  return (
    <>
      <Beat01 startFrame={BEATS.HOOK.start} endFrame={BEATS.HOOK.end} />
      <Beat02 startFrame={BEATS.BUILD.start} endFrame={BEATS.BUILD.end} />
    </>
  );
};
```

---

## Timing Conventions

- 30fps throughout. Do not change this.
- The spec's beat durations are approximate. Calculate exact frame ranges from them.
- Use `<TransitionSeries>` for scene transitions. No hard cuts unless the spec specifically calls for one.
- Write timing in seconds x fps for readability: `2 * 30` not `60`.

---

## Remotion API Reference

For all Remotion APIs, see the bundled skill:
- `../../skills/remotion-best-practices/SKILL.md` -- index of all rule files
- Load `rules/timing.md`, `rules/sequencing.md`, `rules/transitions.md` for every build
- Load other rule files as needed (fonts, audio, charts, text animations, light leaks)

Do not hand-code what a Remotion package already does. Check `@remotion/paths`, `@remotion/transitions`, `@remotion/light-leaks` before writing custom implementations.

---

## Testing

- Preview individual beats by temporarily setting their frame range as the composition's duration
- Preview the full composition to check flow and transitions
- Watch at 1x speed to verify pacing matches intended duration
- Check on a mobile viewport (vertical if the platform is TikTok/Reels)
- Render final video: `npx remotion render MyVideo output.mp4`
- See `remotion-setup.md` for project setup and troubleshooting
