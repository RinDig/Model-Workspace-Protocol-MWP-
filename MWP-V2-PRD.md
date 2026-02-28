# PRD: MWP v2 -- Battle-Tested Patterns

## Context

MWP v1 was built as a generalized framework for structured AI workflows. It works architecturally -- the 4-layer routing, stage handoffs, one-way references, placeholder system, and workspace builder are all sound.

But v1 was built from theory. The Content Writing workspace (the system MWP was abstracted from) has been in daily production use for months and has evolved significantly. The patterns that emerged from real use -- what actually makes agent output good vs mediocre -- never made it back into MWP.

This PRD defines 12 changes that bring MWP's conventions, templates, and example workspaces up to the standard of the production system. The goal: someone cloning MWP and running `setup` should get a workspace that produces output close to what the battle-tested system produces.

MWP should remain a simplified starting point, not a clone of the Content Writing workspace. These changes are about encoding the structural patterns that make agent output good, not copying domain-specific content.

---

## Reference System

The production system that these patterns were learned from lives at:

```
../                                (Content Writing workspace root)
├── CLAUDE.md                      Layer 0 routing
├── CONTEXT.md                     Layer 1 routing
├── script-lab/                    Script writing workspace
│   ├── CONTEXT.md
│   └── Script-Docs/               The 4-doc framework
│       ├── 01-voice.md            Hard constraints + verbatim examples
│       ├── 02-audience.md         Decision rules, not analytics
│       ├── 03-reel-format.md      Formats, value slots, hook rules
│       └── 04-workflow.md         3-step process with injection points
└── animation-studio/              Production workspace
    ├── CONTEXT.md
    ├── docs/
    │   ├── design-system.md       382 lines of code recipes + quality floor
    │   └── component-registry.md  Available components + conventions
    └── workflows/
        ├── CONTEXT.md             Pipeline routing + builder freedom rules
        └── 02-specs/
            └── spec-template.md   The contract-style spec format
```

When implementing these changes, read the corresponding file from the reference system to understand the pattern before modifying MWP. Do not copy content verbatim -- extract the structural pattern and make it domain-agnostic.

---

## Change 1: Spec Format -- Contracts, Not Blueprints

**Priority: 1 (highest -- cascades into changes 6, 9)**

### Problem

`workspaces/script-to-animation/stages/02-spec/references/spec-format.md` uses frame-range specs with explicit component names and props:

```markdown
### Beat 1 [0-90]
**Components:** PhoneFrame, TapRipple, TextReveal
**Props:**
- PhoneFrame: { screen: "message-app", scale: 0.8 }
```

This prescribes HOW, which removes creative freedom from the build stage and produces rigid, uncreative output.

### What the production system does

Specs define WHAT and WHEN. The builder decides HOW. A spec contains:

- **Beat Map** -- timing contract with approximate durations, narration text, and mood (not frame numbers)
- **Visual Philosophy** -- 3-5 paragraphs on what a muted viewer should understand, what visual density the video calls for
- **Key Moments** -- the 2-3 animations that MUST land for the piece to work, and WHY each matters
- **Persistent Elements** -- anything spanning multiple scenes
- **Audio Sync Points** -- specific narration words mapped to visual events
- **Color Flow** -- scene-by-scene dominant color and mood (not hex codes for every element)

No frame numbers. No component names. No pixel positions. No spring configs. No prop definitions.

Reference: `../animation-studio/workflows/02-specs/spec-template.md`

### What to change

1. Rewrite `spec-format.md` to use the contract-style format above
2. Make it domain-agnostic -- replace "animation" language with general "build" language where appropriate, but keep a concrete example that shows the pattern in action
3. Update the `02-spec` stage CONTEXT.md Process section to match: "define visual concepts and timing, not implementation"
4. Add the principle to CONVENTIONS.md as a new pattern: **Pattern 10: Specs Are Contracts** -- "Specification stages define WHAT the output should achieve and WHEN things happen. They do not prescribe HOW to implement. The build stage has creative freedom within the quality floor defined by the design system."

---

## Change 2: Add Checkpoints to Stage Contracts

**Priority: 2 (structural change to CONVENTIONS.md)**

### Problem

The stage contract template has Inputs / Process / Outputs. The Process section is a linear numbered list. There is no concept of pausing for human input within a stage.

### What the production system does

The script workflow has 3 steps with injection points BETWEEN them. Claude does a complete pass (e.g., generates 3-5 concept angles), then the human picks a direction, then Claude does the next pass. The key insight: injection points are between steps, not within them. The agent completes a unit of work, presents it, and the human steers.

Reference: `../script-lab/Script-Docs/04-workflow.md`

### What to change

1. Add a **Checkpoints** section to `_core/templates/stage-context-template.md`:

```markdown
## Checkpoints

<!-- Points where the agent pauses for human input before continuing.
     Not every stage needs checkpoints. Linear stages (extract, render, validate)
     often run straight through. Creative stages (writing, design, ideation)
     benefit from at least one.

     Format: after which process step, what the agent presents, what the human decides. -->

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| [step #] | [what options/output to show] | [what direction to choose] |
```

2. Add to CONVENTIONS.md as **Pattern 11: Checkpoints** -- "Creative stages should include at least one checkpoint where the agent pauses and the human steers. The agent completes a full unit of work, presents options or a draft, and the human redirects before the next unit begins. Checkpoints go between process steps, not within them."

3. Update the script-to-animation `01-script` stage CONTEXT.md to demonstrate the pattern: a checkpoint between ideation and drafting.

---

## Change 3: Voice Rules as Error Conditions

**Priority: 4 (template change)**

### Problem

`voice-rules.md` template has `{{VOICE_TONE_RULE}}` -- a single placeholder sentence. The agent derives constraints from a vague description. Descriptions are abstractions the agent has to interpret. Rules with examples are pattern-matchable.

### What the production system does

Voice rules have three structural sections:

1. **Hard Constraints** -- numbered list of things that are always errors. "If the output contains any of these, rewrite." Each constraint is specific and checkable (e.g., "Antithesis pattern. Maximum one per script.", "Em dashes. Never.", "Filler transitions. Just start the next thought.").

2. **Sentence Rules** -- do-this/not-this pairs with verbatim examples. "Wrong: 'commoditization of basic services'. Right: 'you can prompt a landing page into existence now for a couple hundred dollars.'"

3. **Pacing** -- rhythm description with notation. "The rhythm alternates: setup, dense, dense, breath, dense. Not metronomic. Natural."

Reference: `../script-lab/Script-Docs/01-voice.md`

### What to change

1. Restructure `brand-vault/voice-rules.md` template to have three sections:

   - **Hard Constraints** -- "These are errors. If the output contains any of these, rewrite." Placeholder list items populated from questionnaire.
   - **Sentence Rules** -- Do/Don't pairs with example sentences. Populated from questionnaire.
   - **Pacing** -- Rhythm and density description. Populated from questionnaire.

   Keep the existing "Strategic Rationale" and "What the Voice Is NOT" sections.

2. Update the questionnaire (Change 11) to extract concrete rules, not descriptions.

---

## Change 4: Add Audit Section to Stage Contracts

**Priority: 2 (structural change to CONVENTIONS.md)**

### Problem

Stages have Inputs / Process / Outputs. There is no quality check before output is considered done. The agent writes output and moves on.

### What the production system does

Multiple quality audits built into the workflow:

- **Retention beat audit** (script stage) -- map every beat, tag it by type (Recognition, Surprise, Stack, Reversal, New Voice, Reframe, Implication), check that no gap exceeds 5 seconds without a beat
- **Share test** (script stage) -- "would someone who learned this 5 minutes ago feel confident sharing it?"
- **Mute test** (script/spec stage) -- "does the visual create curiosity without audio?"
- **Pre-flight checklist** (build stage) -- 15-item checklist covering hook, depth stack, surface treatment, typography, safe zones, motion

Reference: `../script-lab/Script-Docs/04-workflow.md` (retention beat audit), `../animation-studio/docs/design-system.md` (pre-flight checklist)

### What to change

1. Add an **Audit** section to `_core/templates/stage-context-template.md`, between Process and Outputs:

```markdown
## Audit

<!-- Quality checks before the output is considered done. The agent runs these
     after completing the process steps. If any check fails, revise before saving.

     Not every stage needs an audit. Data extraction or file conversion stages
     may not benefit. Creative and build stages almost always do. -->

| Check | Pass Condition |
|-------|---------------|
| [Check name] | [What "passing" looks like] |
```

2. Add to CONVENTIONS.md as **Pattern 12: Stage Audits** -- "Creative and build stages should include an Audit section: a checklist the agent runs after completing the process but before writing to output/. Audits catch quality issues before they propagate downstream. Each check should be specific enough that pass/fail is unambiguous."

3. Add audit sections to the script-to-animation workspace stages:
   - `01-script`: content quality checks (voice constraint violations, value delivery, hook timing)
   - `03-build`: production quality checklist (adapted from the design system pre-flight)

---

## Change 5: Value Framework

**Priority: 9 (conventions addition)**

### Problem

The script stage produces content but has no mechanism to validate what value that content delivers. Scripts can be structurally correct but not actually do anything for the viewer/reader.

### What the production system does

Four value slots: NOVEL, USABLE, QUESTION-GENERATING, INTERESTING. Every script must hit at least 2. The value is locked in Step 2 (before writing begins) so the draft has a clear target.

Reference: `../script-lab/Script-Docs/03-reel-format.md` (value slots section)

### What to change

1. Add to CONVENTIONS.md as **Pattern 13: Value Validation** -- "Content-producing stages should define what types of value their output can deliver. Before the main creative work begins (ideally at a checkpoint), the agent and human should agree on which value types this specific piece will hit. This prevents 'interesting but doesn't DO anything' output."

2. Add a `references/value-framework.md` file to the script-to-animation `01-script` stage with a placeholder-populated value framework. The questionnaire asks what kinds of value the user's content typically delivers (e.g., teaches something new, gives a usable tool, raises a question, shifts perspective).

3. Wire it into the script stage process: after the ideation checkpoint, the agent proposes which value types the piece will hit before drafting begins.

---

## Change 6: Builder Creative Freedom Within Quality Floor

**Priority: 5 (build-conventions template change)**

### Problem

`build-conventions.md` says "Frame ranges from the spec are authoritative. Do not adjust timing in the build." The build stage is positioned as a translator (spec to code) rather than a creator. The spec prescribes components and props, so the builder just implements what it is told.

### What the production system does

The spec is the creative contract (WHAT/WHEN). The design system is the quality floor (the production standard every output must meet). The builder has full creative latitude for HOW:

- Animation approach (which APIs, spring configs, easing)
- Layout (pixel positions, element sizing, composition)
- Component choices (reuse, customize, or build new)
- Visual interpretation (how to realize the spec's concepts in actual output)
- Transitions (fade, slide, wipe, custom)

The design system defines required quality patterns (e.g., depth stack, surface treatment) that every scene must have. Creative freedom means choosing how to implement those requirements, not whether to implement them.

Reference: `../animation-studio/workflows/CONTEXT.md` (Builder Creative Freedom section), `../animation-studio/docs/CONTEXT.md` (For Build Agents section)

### What to change

1. Rewrite `build-conventions.md` to establish the separation:
   - The spec defines the creative contract (what to achieve, when things happen)
   - The design system defines the quality floor (the minimum production standard)
   - The builder has creative freedom within both
   - Remove "do not adjust timing" -- replace with "the spec's timing is approximate; the builder calculates exact implementation"

2. Add the principle to the `03-build` stage CONTEXT.md Process section.

3. This change depends on Change 1 (spec format). The spec must stop prescribing components/props before the builder can have freedom.

---

## Change 7: Don't Learn From Existing Outputs

**Priority: 6 (one line in CONVENTIONS.md)**

### Problem

No guidance on whether agents should read other outputs in `output/` folders to learn patterns. Early outputs will be lower quality. If future agents copy from them, quality doesn't improve.

### What the production system does

"Do not explore existing clips or compositions. The docs above are the complete reference." This is enforced in 4 separate files. The docs (design system, component registry, skill rules) are the authoritative source. Previous outputs are artifacts, not templates.

Reference: `../animation-studio/docs/CONTEXT.md` (the "Do not explore existing clips" section)

### What to change

1. Add to CONVENTIONS.md as **Pattern 14: Docs Over Outputs** -- "Reference docs (design system, build conventions, skill rules) are the authoritative source for how to build. Previous stage outputs in output/ folders are artifacts, not templates. Agents should not read other outputs to learn patterns. This prevents copying from older, lower-quality work and ensures docs remain the single source of truth for quality standards."

2. Add a note to the build stage CONTEXT.md template: "After loading the reference docs and skill rules, you have the complete reference. Do not read other output/ files to learn patterns."

---

## Change 8: Constants as Shared Files

**Priority: 11 (conventions addition for code workspaces)**

### Problem

`build-conventions.md` has hardcoded color/font constants inline. After onboarding, these values are baked into each build output file separately. No shared source of truth for code values.

### What the production system does

A `constants/` folder with small, focused files (`colors.ts`, `timing.ts`, `typography.ts`, ~170 lines total). Every build imports from these. Change a color once, it updates everywhere.

Reference: `../animation-studio/src/compositions/Eduba/constants/`

### What to change

1. Add to CONVENTIONS.md as **Pattern 15: Shared Constants** -- "Workspaces that produce code should define a constants pattern. Configurable values (colors, fonts, timing, layout) live in shared files that all build outputs import from. The questionnaire populates these files once during onboarding. This is canonical sources (Pattern 5) applied to code values."

2. Update `build-conventions.md` to reference a shared constants file instead of inline values. The onboarding questionnaire writes color/font answers to a constants file, not scattered across build convention docs.

3. This is only relevant for code-producing workspaces (like script-to-animation with Remotion). Non-code workspaces can skip this pattern.

---

## Change 9: Design System as Code Recipes

**Priority: 12 (design system template addition)**

### Problem

The design system reference would contain generic rules and placeholder colors after onboarding. No concrete, copy-paste patterns for common build tasks.

### What the production system does

382 lines of concrete code examples:
- Depth stack recipe (9 layers, each with code)
- Surface treatment recipe (5 layers, full JSX)
- Camera drift code (copy-paste ready)
- Deterministic particle code (copy-paste ready)
- Spring configs table (by semantic meaning)
- Anti-patterns table (with "why it fails" column)
- Pre-flight checklist (15 items)

An agent can literally copy a recipe and adapt it. No interpretation required.

Reference: `../animation-studio/docs/design-system.md`

### What to change

1. Add a **Recipes** section to the design system reference template. Recipes are concrete, copy-paste patterns for common tasks. For the script-to-animation workspace, this means scene structure patterns, transition patterns, and timing patterns.

2. Add an **Anti-Patterns** table: what to avoid and why it fails. This is a quality guardrail that works across domains.

3. Add a **Production Checklist** at the end: a quick pre-flight the agent runs before considering a build done. (This connects to Change 4 -- the checklist can be referenced from the build stage audit.)

4. The design system template for new workspaces should include skeleton sections for Recipes, Anti-Patterns, and Production Checklist, even if the specific entries are domain-dependent.

---

## Change 10: Token Management Guidance

**Priority: 10 (CLAUDE.md template addition)**

### Problem

The workspace CLAUDE.md template has a routing table but no explicit guidance on what NOT to load. Users and agents don't understand that loading extra files actively degrades output quality.

### What the production system does

CLAUDE.md has a "Token Management" section:

```
- Writing a script? -> Load all 4 files in Script-Docs/
- Generating a spec? -> Load the script only
- Building animation? -> Follow this specific load order
- Rendering? -> Just the composition name and render settings
```

Plus the principle: "Each workspace is siloed. You don't need to load everything."

Reference: `../CLAUDE.md` (Token Management section)

### What to change

1. Add a **What to Load** section to `_core/templates/workspace-claude-template.md`:

```markdown
## What to Load

<!-- Map each task to its minimal file set. Loading more files dilutes quality.
     The context window is working memory, not storage. -->

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| [Task 1] | [minimal file list] | [what to skip and why] |
| [Task 2] | [minimal file list] | [what to skip and why] |
```

2. Add a note to CONVENTIONS.md under the routing architecture section: "Every token of irrelevant context is a token of diluted attention. Workspace CLAUDE.md files should explicitly map each task to its minimal required files."

---

## Change 11: Questionnaire Extracts Rules, Not Descriptions

**Priority: 7 (questionnaire template change)**

### Problem

The current questionnaire asks Q2: "How should your content sound? (describe your voice and give 2-3 adjectives)." The agent then derives tone rules, personality markers, and anti-patterns from a thin description. The most critical constraints in the system come from the weakest input signal.

### What the production system does

The voice rules are concrete: verbatim example sentences, numbered error conditions, do/don't pairs. These were built from real examples over months.

### What to change

1. Restructure the voice questions in the questionnaire to extract concrete rules:

   - "Give me 2-3 sentences that sound exactly like your brand." (extracts positive examples)
   - "Give me 2-3 sentences your brand would never say." (extracts anti-patterns)
   - "List things that are always errors in your content -- patterns, phrases, or habits to avoid." (extracts hard constraints)
   - Keep the adjective question as supplementary, not primary.

2. Consider making the questionnaire a **two-pass process**: quick answers first, then the agent generates draft voice rules and the human edits them before they are baked in. This mirrors the checkpoint pattern (Change 2) and produces better rules than one-shot derivation.

3. Update the questionnaire template in `_core/templates/questionnaire-template.md` to note: "For voice/style questions, ask for concrete examples (sentences that sound right, sentences that sound wrong) rather than abstract descriptions. Examples are pattern-matchable. Descriptions require interpretation."

---

## Change 12: Specific Process Steps

**Priority: 8 (template guidance)**

### Problem

Stage process sections use generic verbs: "Write the script following voice rules." "Break script into beats." Two different agents following these steps would produce structurally different outputs.

### What the production system does

Process steps are specific enough that agents produce structurally consistent output:

- "Offer 3-5 concept angles, each framed as a single sentence a viewer could repeat to a friend"
- "For each angle, tag which value slots it naturally hits and which format it leans toward"
- "Claude writes the full script in one pass, then immediately audits against: voice hard constraints, value delivery, hook timing, close quality, share test"

Reference: `../script-lab/Script-Docs/04-workflow.md`

### What to change

1. Add guidance to the stage-context-template.md comments:

```markdown
## Process

<!-- Numbered steps. Each step is one concrete action. Be specific enough that
     two different agents following these steps would produce structurally similar
     outputs.

     Too vague: "Write the script"
     Good: "Write the full script in one pass, then audit against the voice
            hard constraints and value brief"

     Too vague: "Generate ideas"
     Good: "Propose 3-5 concept angles, each as a single sentence. Tag each
            with its value type and format."  -->
```

2. Update the script-to-animation `01-script` process steps to demonstrate the level of specificity expected. Replace "Write the script following voice rules" with the actual multi-step process: propose angles (with tags) -> checkpoint -> propose value brief -> checkpoint -> write full draft -> run audit.

3. This is guidance, not a strict rule. Some stages (data extraction, file conversion) genuinely are simple steps. The specificity matters most for creative and build stages.

---

## Implementation Order

The changes have dependencies. Implement in this order:

### Phase 1: Structural Changes to CONVENTIONS.md

These add new patterns that all workspaces follow.

1. **Change 4** -- Add Audit section to stage contract template
2. **Change 2** -- Add Checkpoints section to stage contract template
3. **Change 7** -- Add "Docs Over Outputs" pattern
4. **Change 5** -- Add "Value Validation" pattern
5. **Change 10** -- Add token management note

After Phase 1, `CONVENTIONS.md` has 5 new patterns (10-14) and the stage-context-template has two new optional sections (Checkpoints, Audit).

### Phase 2: Template Updates

These improve the templates that new workspaces are built from.

6. **Change 3** -- Restructure voice-rules.md template
7. **Change 11** -- Restructure questionnaire to extract rules
8. **Change 12** -- Add specificity guidance to stage-context-template
9. **Change 10** -- Add "What to Load" section to workspace-claude-template

### Phase 3: Script-to-Animation Workspace Updates

These update the reference workspace to demonstrate all new patterns.

10. **Change 1** -- Rewrite spec-format.md (contract style)
11. **Change 6** -- Rewrite build-conventions.md (creative freedom + quality floor)
12. **Change 8** -- Add shared constants pattern
13. **Change 9** -- Add code recipes to design system reference
14. Update all three stage CONTEXT.md files to use Checkpoints, Audits, and specific process steps
15. Update the questionnaire with new voice questions

### Phase 4: Workspace Builder Updates

16. Update the workspace-builder's scaffolding stage to generate workspaces with the new template sections (Checkpoints, Audits)
17. Update the workspace-builder's references/examples to reflect the updated script-to-animation workspace

### Phase 5: Validation

18. Run through the script-to-animation workspace end-to-end (setup -> script -> spec -> build) and verify the new patterns produce better output
19. Verify all cross-references still point to real files
20. Verify CONVENTIONS.md, templates, and example workspace are internally consistent

---

## What NOT to Change

These parts of MWP v1 are working and should be preserved:

- The 4-layer routing architecture (Layers 0-3)
- The placeholder and onboarding system (`{{VARIABLE}}` syntax, conditional sections)
- Stage handoffs via output folders
- One-way cross-references (Pattern 3)
- Selective section routing (Pattern 4)
- Canonical sources (Pattern 5)
- CONTEXT.md = routing only (Pattern 6)
- Trigger keywords (setup, status)
- Naming conventions
- Quality guardrails (line limits, no em dashes, plain English)
- The workspace-builder's 5-stage structure
- Bundled skills pattern (Pattern 9)
- The overall repo structure (_core/, workspaces/)

---

## Success Criteria

After all changes:

1. A new user can clone MWP, run `setup` in script-to-animation, answer 10 questions, and get a workspace where:
   - The script stage has a collaborative workflow with checkpoints, not a linear checklist
   - Voice rules are concrete constraints with examples, not derived from adjectives
   - The spec stage produces contracts (WHAT/WHEN), not blueprints (HOW)
   - The build stage has creative freedom within a documented quality floor
   - Every stage has quality audits before output is written

2. The workspace-builder produces new workspaces that automatically include Checkpoint and Audit sections in their stage templates.

3. CONVENTIONS.md is the complete reference for all MWP patterns (original 9 + new 5 = 14 patterns, plus the shared constants pattern for code workspaces).
