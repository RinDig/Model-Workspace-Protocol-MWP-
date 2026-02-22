# Remotion Setup Guide

How to install Remotion and get a project running. Complete this before running Stage 03 for the first time.

## Prerequisites

1. **Node.js** (v18 or later) -- download from [nodejs.org](https://nodejs.org)
2. **Claude Code** -- the CLI tool from Anthropic

Check both are installed:

```bash
node --version
claude --version
```

## Create a Remotion Project

```bash
npx create-video@latest
```

When prompted:
- **Template:** Select "Blank"
- **TailwindCSS:** Say yes
- **Install Skills:** Say yes (gives Claude Code animation-specific knowledge)

## Install and Start

```bash
cd my-video
npm install
npm run dev
```

This opens Remotion Studio in your browser for previewing compositions and rendering video.

## Project Structure

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

Register compositions in `src/Root.tsx` with width, height, fps (30), and durationInFrames.

## Using Stage 03 Output

When Stage 03 produces code, it goes in `output/[topic-slug]/`. To use it:

1. Copy beat components from `output/[slug]/beats/` into your `src/` folder
2. Copy the index composition from `output/[slug]/index.tsx` into `src/`
3. Register the composition in `Root.tsx`
4. Run `npm run dev` to preview

Or, if working inside the Remotion project directly, Stage 03 can write files straight into `src/`.

## Rendering Final Video

```bash
npx remotion render MyVideo output.mp4
```

Options: `--codec=h264`, `--image-format=jpeg`, `--concurrency=4`

## Troubleshooting

- **"Module not found":** Run `npm install` again
- **Preview is blank:** Check composition is registered in `Root.tsx` with matching `id`
- **Slow renders:** Lower resolution for test renders, full resolution for final only
- **Frame rate wrong:** Confirm `fps: 30` in composition registration

For Remotion API reference (animations, timing, sequencing, etc.), see the bundled skill at `../../skills/remotion-best-practices/SKILL.md`.
