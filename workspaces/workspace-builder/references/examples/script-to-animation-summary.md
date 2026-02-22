# Example Workspace: Script-to-Animation

A condensed summary of the script-to-animation workspace. Use this as a reference when building new workspaces to understand what a completed MWP workspace looks like.

---

## Overview

**What it does:** Takes a content idea through three stages to produce an animated video.
**Stages:** 3 (script writing, animation specification, code build)
**Target user:** Content creators who produce educational/explainer video content

---

## Stage Summary

### 01-script: Topic to Finished Script
- **Input:** A topic or content idea from the user
- **References loaded:** Voice rules (specific sections), brand identity, hook system, script templates, content pillars (relevant pillar only), platform specs
- **Output:** A markdown script with metadata header (pillar, hook type, template, duration, platform)
- **Human edit surface:** The finished script. User can rewrite lines, change the hook, adjust timing.

### 02-spec: Script to Animation Specification
- **Input:** The finished script from 01-script/output/
- **References loaded:** Spec format (BEATS system, frame ranges), component registry, design system (colors, typography, motion)
- **Output:** Beat-by-beat animation spec with frame ranges, components, props, and transitions
- **Human edit surface:** The spec file. User can adjust timing, swap components, change visuals.

### 03-build: Spec to Remotion Code
- **Input:** The animation spec from 02-spec/output/
- **References loaded:** Build conventions, component registry (from stage 02), design system (from stage 02)
- **Output:** A folder of Remotion/React components (.tsx files)
- **Human edit surface:** The code files. User can tweak animations directly.
- **Note:** This stage is optional. Some users stop at the spec stage.

---

## Shared Context

### Brand Vault (brand-vault/)
Two files, each with selectively loaded sections:
- **voice-rules.md** -- Writing voice, tone, style. Agents load the "Voice Rules" and "What the Voice Is NOT" sections, not the strategic rationale.
- **identity.md** -- Brand name, audience, positioning, content mission.

The brand vault has its own CONTEXT.md that tells agents which sections of which files to load.

### Shared Files (shared/)
- **platform-specs.md** -- Resolution, duration, format per platform. Used by stage 01 (for duration constraints) and implicitly by stages 02-03 (for visual constraints).

---

## Reference File Strategy

Each stage has its own `references/` folder with files specific to that stage:
- 01-script: hook-system.md, script-templates.md, content-pillars.md
- 02-spec: spec-format.md, component-registry.md, design-system.md
- 03-build: build-conventions.md (also references 02-spec's component-registry.md and design-system.md)

**Key design decision:** component-registry.md lives in stage 02 because the spec stage defines which components are available. Stage 03 references it via a one-way path (`../02-spec/references/component-registry.md`). This keeps one canonical source and avoids duplication.

---

## Placeholder Strategy

**What got placeholders:** Brand name, voice description, voice adjectives, target audience, brand mission, content pillars, hook style, primary platform, target duration, colors (5 values), fonts (2 values), positioning, content mission.

**What was hardcoded:** File structure, process steps, section headings, the stage contract pattern, component registry entries, spec format rules, build conventions.

**Rule of thumb:** If it varies from one user to another, it is a placeholder. If it is part of the framework's structure, it is hardcoded.

---

## Conditional Sections

Two types of optional content:
- **Stage removal:** If the user does not need the build stage, the entire `stages/03-build/` folder is removed during onboarding. The workspace CONTEXT.md has a `{{?BUILD_STAGE}}...{{/BUILD_STAGE}}` block around the build stage routing entry.
- **Partial content:** If the user has fewer than 5 content pillars, the unused pillar sections in content-pillars.md are removed via `{{?PILLAR_4}}...{{/PILLAR_4}}` and `{{?PILLAR_5}}...{{/PILLAR_5}}`.

Both conditional blocks wrap entire sections (heading + content), following the conditional section rule.

---

## Tool Prerequisites

The workspace has a `prerequisites/` folder with a CONTEXT.md that lists all external tools:

| Tool | Required By | Required/Optional |
|------|-------------|-------------------|
| Node.js | Stage 03 | Required if using Remotion |
| Remotion | Stage 03 | Optional |

The setup guide for Remotion lives in `stages/03-build/references/remotion-setup.md` (since it is only used by one stage). The prerequisites CONTEXT.md references it there.

During onboarding, Q12 asks whether the user wants animation code generation. If no, Stage 03 is removed and no tools are needed. If yes, the agent points them to the Remotion setup guide.

Stages 01 and 02 require only Claude Code -- no external tools.

---

## Onboarding

12 questions grouped into: Brand Identity (5), Content Strategy (2), Platform and Format (2), Visual Design (2), Workflow Configuration (1).

Some placeholders are derived rather than directly asked. The onboarding agent generates voice tone rules, personality markers, and anti-patterns from the user's voice description and adjectives, then confirms with the user.

Post-onboarding: the agent scans for remaining `{{` patterns to catch anything missed.
