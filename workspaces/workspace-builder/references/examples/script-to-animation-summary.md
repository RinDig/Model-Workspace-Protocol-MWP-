# Example Workspace: Script-to-Animation

A condensed summary of the script-to-animation workspace. Use this as a reference when building new workspaces to understand what a completed MWP workspace looks like.

---

## Overview

**What it does:** Takes a content idea through three stages to produce an animated video.
**Stages:** 3 (script writing, animation specification, code build)
**Target user:** Content creators who produce educational/explainer video content
**Bundled skills:** remotion-best-practices (Remotion API, 35 rule files), frontend-design (design philosophy)

---

## Stage Summary

### 01-script: Topic to Finished Script
- **Input:** A topic or content idea from the user
- **References loaded:** Voice rules (Hard Constraints, Sentence Rules, Pacing), brand identity, hook system, script templates, content pillars (relevant pillar only), value framework, platform specs
- **Checkpoints:**
  - After ideation: agent presents 3-5 concept angles with value slot tags, human picks direction
  - After value brief: agent presents concept + value slots + format + hook + close, human confirms
- **Audit:** Voice constraint violations, value delivery, hook timing, close quality, retention beats (no 5s gap without a beat), share test
- **Output:** A markdown script with metadata header (pillar, hook type, template, value slots, duration, platform)
- **Human edit surface:** The finished script. User can rewrite lines, change the hook, adjust timing.

### 02-spec: Script to Animation Specification
- **Input:** The finished script from 01-script/output/
- **References loaded:** Spec format (contract style), design system (colors, typography), animation guide, frontend-design skill
- **Audit:** Mute test, one concept per beat, contract purity (zero component names or frame numbers), key moments identified, audio sync points, color flow
- **Output:** Contract-format spec with beat map, visual philosophy, key moments, audio sync points, color flow
- **Human edit surface:** The spec file. User can adjust timing, change visual concepts, refine the color arc.
- **Key principle:** The spec defines WHAT and WHEN, not HOW. No component names, frame numbers, pixel positions, or prop definitions.

### 03-build: Spec to Remotion Code
- **Input:** The animation spec from 02-spec/output/
- **References loaded:** Build conventions, remotion-best-practices skill (loads rule files as needed), frontend-design skill, component registry (from stage 02), design system with recipes (from stage 02), remotion-setup.md
- **Audit:** Spec coverage, design system compliance (shared constants), platform specs, transitions (no hard cuts), mobile readability, safe zones
- **Output:** A folder of Remotion/React components (.tsx files) with shared constants
- **Human edit surface:** The code files. User can tweak animations directly.
- **Note:** This stage is optional. Some users stop at the spec stage.
- **Key principle:** The builder has creative freedom for HOW within the spec (WHAT/WHEN) and design system (quality floor). Does not read other output/ files to learn patterns.

---

## Shared Context

### Brand Vault (brand-vault/)
Two files, each with selectively loaded sections:
- **voice-rules.md** -- Structured as Hard Constraints (numbered error list), Sentence Rules (wrong/right pairs with verbatim examples), and Pacing. Plus "What the Voice Is NOT" and "Strategic Rationale". Agents load the rules sections, not the strategic rationale.
- **identity.md** -- Brand name, audience, positioning, content mission.

The brand vault has its own CONTEXT.md that tells agents which sections of which files to load.

### Shared Files (shared/)
- **platform-specs.md** -- Resolution, duration, format per platform. Used by stage 01 (for duration constraints) and implicitly by stages 02-03 (for visual constraints).

---

## Bundled Skills (skills/)

Skills are copied from local installations or cloned from GitHub during workspace scaffolding. They replace custom reference docs when the skill covers the same ground.

- **remotion-best-practices/** -- SKILL.md index + 35 rule files covering animations, timing, sequencing, transitions, fonts, audio, charts, text animations, 3D, captions, and more. Includes example .tsx assets. Replaces what would have been a hand-written Remotion API reference.
- **frontend-design/** -- SKILL.md with design philosophy, aesthetics guidelines, avoiding generic AI look. Referenced by stages 02 and 03 for visual direction.

Stage CONTEXT.md files reference skills in their Inputs table:
```
| Skill | `../../skills/remotion-best-practices/SKILL.md` | Index, then load rules as needed | Remotion APIs |
| Skill | `../../skills/frontend-design/SKILL.md` | Full file | Design thinking |
```

---

## Reference File Strategy

Each stage has its own `references/` folder with workspace-specific files:
- 01-script: hook-system.md, script-templates.md, content-pillars.md, value-framework.md
- 02-spec: spec-format.md, component-registry.md, design-system.md (with recipes + anti-patterns + production checklist), animation-guide.md
- 03-build: build-conventions.md, remotion-setup.md

**Key design decisions:**
- component-registry.md lives in stage 02. Stage 03 references it via a one-way path (`../02-spec/references/component-registry.md`). One canonical source, no duplication.
- design-system.md includes Recipes (depth stack, surface treatment, beat orchestration, transitions), Anti-Patterns table, and Production Checklist. The build stage audit references this checklist.
- Spec format uses contract style (beat map, visual philosophy, key moments, audio sync points, color flow). No component names or frame numbers.
- Build conventions establish creative freedom: spec = WHAT/WHEN, design system = quality floor, builder = HOW.

**Skills vs. references:** The remotion-best-practices skill handles all Remotion API knowledge (interpolate, spring, Sequence, etc.). The workspace-specific build-conventions.md handles folder structure, beat patterns, and shared constants integration that are unique to this workflow.

---

## Placeholder Strategy

**What got placeholders:** Brand name, voice hard constraints (3), voice examples (2 wrong/right pairs), voice pacing description, voice anti-pattern, target audience, brand mission, content pillars, value type descriptions (4), hook style, primary platform, target duration, colors (5 values), fonts (2 values), positioning, content mission.

**What was hardcoded:** File structure, process steps, section headings, the stage contract pattern, component registry entries, spec format structure, build conventions, audit checks, checkpoint tables, design system recipes.

**Rule of thumb:** If it varies from one user to another, it is a placeholder. If it is part of the framework's structure, it is hardcoded.

---

## Conditional Sections

Two types of optional content:
- **Stage removal:** If the user does not need the build stage, the entire `stages/03-build/` folder is removed during onboarding. The workspace CONTEXT.md has a `{{?BUILD_STAGE}}...{{/BUILD_STAGE}}` block around the build stage routing entry.
- **Partial content:** If the user has fewer than 5 content pillars, the unused pillar sections in content-pillars.md are removed via `{{?PILLAR_4}}...{{/PILLAR_4}}` and `{{?PILLAR_5}}...{{/PILLAR_5}}`.

Both conditional blocks wrap entire sections (heading + content), following the conditional section rule.

---

## Onboarding

14 flat questions asked all at once. The user answers in a single message:
- Brand name, example sentences (right + wrong), error patterns, adjectives, audience, mission, content pillars, value types, hook style, platform/duration, colors, fonts, Remotion yes/no

Voice questions extract concrete rules, not descriptions. "Give me 2-3 sentences that sound like your brand" produces pattern-matchable examples. "Describe your voice" produces an abstraction the agent must interpret.

**Two-pass process:** After collecting answers, the agent populates voice rules and presents the Hard Constraints, Sentence Rules, and Pacing sections to the user for review. The user edits before rules are finalized. This catches misinterpretations and produces better constraints than one-shot derivation.

Post-onboarding: the agent scans for remaining `{{` patterns to catch anything missed.
