# Remotion Setup Guide

How to install and set up Remotion Studio for this workspace. Complete this before running Stage 03 for the first time.

---

## Prerequisites

You need two things installed:

1. **Node.js** (v18 or later) -- download from [nodejs.org](https://nodejs.org)
2. **Claude Code** -- the CLI tool from Anthropic (requires a paid subscription)

Check both are installed:

```bash
node --version
claude --version
```

---

## Create a Remotion Project

Run this from your terminal:

```bash
npx create-video@latest
```

When prompted:
- **Template:** Select "Blank"
- **TailwindCSS:** Say yes (makes styling much easier)
- **Install Skills:** Say yes (gives Claude Code animation-specific knowledge)

This creates a new folder with everything you need.

---

## Install and Start

Go into the project folder and install dependencies:

```bash
cd my-video
npm install
```

Start the preview:

```bash
npm run dev
```

This opens Remotion Studio in your browser. You can preview compositions, scrub through frames, and render final video files.

---

## Project Structure

After setup, your project looks like this:

```
my-video/
├── src/
│   ├── Root.tsx          (registers all compositions)
│   ├── Composition.tsx   (your main video component)
│   └── ...
├── public/               (static assets: images, fonts)
├── package.json
└── remotion.config.ts    (render settings)
```

The key file is `src/Root.tsx`. This is where you register compositions:

```tsx
import { Composition } from "remotion";
import { MyVideo } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
```

Every composition needs four properties:
- `width` and `height` in pixels (match your platform specs)
- `durationInFrames` (total frames -- at 30fps, 900 frames = 30 seconds)
- `fps` (always 30 for this workspace)

---

## How Stage 03 Output Connects

When Stage 03 produces code, it goes in `output/[topic-slug]/`. To use it in your Remotion project:

1. Copy the beat components from `output/[slug]/beats/` into your `src/` folder
2. Copy the index composition from `output/[slug]/index.tsx` into `src/`
3. Register the composition in `Root.tsx`
4. Run `npm run dev` to preview

Or, if you are working inside the Remotion project directly, Stage 03 can write files straight into `src/`.

---

## Rendering Final Video

Once you are happy with the preview:

```bash
npx remotion render MyVideo output.mp4
```

Options:
- `--codec=h264` for MP4 (default)
- `--image-format=jpeg` for faster renders
- `--concurrency=4` to use more CPU cores

---

## Remotion Skills (Claude Code Integration)

If you installed Skills during setup, Claude Code has access to Remotion-specific knowledge when generating animations. This means:

- It knows the correct APIs (`useCurrentFrame`, `interpolate`, `spring`, `Sequence`)
- It follows Remotion best practices (clamp extrapolation, spring physics, proper Sequence nesting)
- It can generate production-quality animation code from your specs

When working in Stage 03, Claude Code will use these Skills automatically if they are installed in your Remotion project.

---

## Troubleshooting

**"Module not found" errors:** Run `npm install` again. Some dependencies may need reinstalling after adding new files.

**Preview is blank:** Check that your composition is registered in `Root.tsx` and that the `id` matches what you are previewing.

**Slow renders:** Lower the resolution for test renders. Render at full resolution only for final output.

**Frame rate looks wrong:** Confirm `fps: 30` in your composition registration. The spec format assumes 30fps throughout.
