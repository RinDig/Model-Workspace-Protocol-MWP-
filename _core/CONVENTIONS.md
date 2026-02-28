# MWP Conventions

The rules for building and maintaining MWP workspaces. This is the canonical source. Every workspace follows these patterns.

---

## Four-Layer Routing Architecture

Agents read down the layers. They stop as soon as they have what they need.

```
Layer 0: CLAUDE.md        -> "Where am I?"       (always loaded, ~800 tokens)
Layer 1: CONTEXT.md       -> "Where do I go?"     (read on entry, ~300 tokens)
Layer 2: Stage CONTEXT.md -> "What do I do?"      (read per-task, ~200-500 tokens)
Layer 3: Content files    -> "What do I need?"    (loaded selectively, varies)
```

**Layer 0 -- CLAUDE.md** is auto-loaded by Claude Code into every conversation. It contains the folder map, naming conventions, and a routing table that points to workspace-level files. One per workspace.

**Layer 1 -- Top-level CONTEXT.md** is the first thing an agent reads when entering the workspace. It contains a task routing table that maps task types to specific stage folders. One per workspace.

**Layer 2 -- Stage CONTEXT.md files** live inside each stage folder. They contain the scope definition, what-to-load tables, and step-by-step process. One per stage.

**Layer 3 -- Content files** are the actual reference material (voice rules, templates, specs, design systems). They are loaded only when a Layer 2 CONTEXT.md table says to load them. Agents load specific sections, not entire files, whenever possible.

A rendering agent might only need Layers 0-1. A script-writing agent reads down to Layer 3. No agent reads everything.

Every token of irrelevant context is a token of diluted attention. Workspace CLAUDE.md files should explicitly map each task to its minimal required files. Loading more context does not make output better. It makes it worse.

---

## Pattern 1: Stage Contracts

Every stage CONTEXT.md follows the same three-section shape:

```markdown
## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| ... | ... | ... | ... |

## Process

1. Step one
2. Step two
3. Step three

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| ... | ... | ... |
```

This is the contract. It is simple enough that a non-technical user can read it and understand what is happening. It is structured enough that an agent can follow it reliably. Every stage follows this exact shape. No exceptions.

---

## Pattern 2: Stage Handoffs via Output Folders

Every stage has an `output/` subfolder. The agent writes its artifact there. The next stage reads from the previous stage's `output/` folder.

The convention:
- Stage N produces: `stages/0N-name/output/artifact-name.md`
- Stage N+1's CONTEXT.md says: "Read `../0N-name/output/artifact-name.md` as your input"

This is the handoff. A human can open the output file, edit it, and the next stage picks up the edited version. No state management. No orchestration layer. Just files in predictable places.

File naming in output folders: `[topic-slug]-[stage-artifact].md`
- Example: `hello-world-script.md`, `hello-world-spec.md`

---

## Pattern 3: One-Way Cross-References

Every folder points outward to what it needs. No folder points back.

If Stage 03 references Stage 02's component registry, Stage 02 does NOT reference anything in Stage 03. If the brand-vault is referenced by multiple stages, the brand-vault does NOT reference any stage.

This prevents reference growth from going N-squared as the system scales. When adding a new reference, check: "Does the target file already reference my folder?" If yes, restructure.

---

## Pattern 4: Selective Section Routing

CONTEXT.md Inputs tables do not just say "read voice-rules.md." They say "read the Voice Rules section of voice-rules.md."

This keeps token cost low. A 150-line file might have only 60 lines of actionable rules for a specific stage. The other 90 lines of strategic rationale stay unloaded.

Format in CONTEXT.md Inputs tables:

```
| File | Section to Load | Why |
|------|----------------|-----|
| voice-rules.md | "Voice Rules" through "What the Voice Is NOT" | Tone guidance |
| identity.md | "One-Sentence Brand" and "Audience" sections | Audience context |
```

When a full file is needed, write "Full file" in the Section/Scope column.

---

## Pattern 5: Canonical Sources

Every piece of information has ONE home. Other files point there. They do not duplicate it.

If you need to update a rule, you update it in one place. Every other file has a pointer. If you find the same information in two files, one of them should be replaced with a reference to the other.

Smell test: search the repo for a specific phrase. If it appears in more than one file and both instances are meant to be authoritative, one needs to become a pointer.

---

## Pattern 6: CONTEXT.md = Routing, Not Content

CONTEXT.md files answer three questions:
1. What is this folder?
2. What do I load?
3. What is the process?

They never contain the actual reference material. No definitions. No rules. No extended examples. No voice guidelines. This keeps them small (25-80 lines) and prevents them from going stale when the content they would otherwise duplicate gets updated.

If you find yourself writing more than a one-sentence description in a CONTEXT.md, that content belongs in a separate file that the CONTEXT.md points to.

---

## Pattern 7: Tool Prerequisites

Some stages require external tools (Node.js, LibreOffice, ffmpeg, etc.). Setup guides for these tools live in the `references/` folder of the stage that uses them (e.g., `stages/03-build/references/remotion-setup.md`).

Setup guides are written for someone who has never installed the tool: what it is (one sentence), installation steps, how to verify it works, and how the workspace uses it.

If a tool is needed by multiple stages, it can live in `shared/` instead. The `setup` onboarding process should check which tools are needed based on the user's answers and point them to the right setup guide.

Note: When a workspace bundles skills (Pattern 9), many tools that would have needed separate prerequisites (scripts, libraries, utilities) come bundled inside the skill folder. Only tools that require system-level installation (Node.js, Python, LibreOffice) still need setup guides.

---

## Trigger Keywords

Every workspace recognizes these triggers:

**`setup`** -- Starts the onboarding questionnaire. The agent reads `setup/questionnaire.md`, asks the questions conversationally, collects answers, replaces placeholders across the workspace, and verifies no placeholders remain.

**`status`** -- Shows pipeline completion. The agent scans all `stages/*/output/` folders and renders an ASCII pipeline diagram:

```
Pipeline Status: [workspace-name]

  [01-stage-name]  ------>  [02-stage-name]  ------>  [03-stage-name]
     COMPLETE                  PENDING                  PENDING
  (artifact.md)              (empty)                  (empty)
```

For each stage: if the output folder contains files (other than .gitkeep), the stage is COMPLETE and the filenames are listed. If the output folder is empty or contains only .gitkeep, the stage is PENDING.

Workspaces can define additional trigger keywords in their own CLAUDE.md.

---

## Naming Conventions

- Folders and files: `lowercase-with-hyphens`
- Stage folders: zero-padded numbers prefix: `01-`, `02-`, `03-`
- Placeholders: `{{SCREAMING_SNAKE_CASE}}`
- Output artifacts: `[topic-slug]-[artifact-type].md`
- No spaces in file or folder names

---

## Pattern 8: Questionnaire Design

Onboarding questionnaires configure the production system, not a specific run. They follow these rules:

1. **Flat structure.** No category groupings. Just a numbered list of questions.
2. **All at once.** Every question appears in one pass. The user should be able to answer everything in a single message.
3. **System-level only.** Questions configure things that stay the same across runs: identity, brand, design, tool preferences, default workflow. Per-run details (project name, topic, audience, scope) are collected conversationally at the start of each pipeline run by the entry stage.
4. **Derive, do not ask.** If a field can be inferred from another answer, the agent fills it in. List derived fields under the question they depend on. Do not add a separate question.
5. **Sensible defaults.** Every question should have a default or example so the user can skip what they do not care about.
6. **Ask once, never again.** After setup, the user should never see these questions again. The answers are baked into the workspace files permanently.

The questionnaire template at `_core/templates/questionnaire-template.md` encodes these rules.

---

## Pattern 9: Bundled Skills

Workspaces can bundle Claude Code skills directly into a `skills/` folder. This gives agents domain-specific knowledge (APIs, best practices, code examples) without requiring the user to have the skills installed globally.

```
workspace/
├── skills/
│   ├── [skill-name]/          (copied from ~/.claude/skills/ or cloned from GitHub)
│   │   ├── SKILL.md           (skill entry point)
│   │   ├── rules/             (detailed rule files, if any)
│   │   └── scripts/           (utility scripts, if any)
│   └── [another-skill]/
│       └── SKILL.md
```

**Discovery:** During workspace building (Stage 01), the builder identifies relevant skills by:
1. Scanning `~/.claude/skills/` and `~/.agents/skills/` for locally installed skills
2. Searching GitHub for skill repos matching the workspace domain (e.g., "remotion skill", "pptx skill")
3. Presenting candidates to the user for selection

**Bundling:** Selected skills are copied (local) or cloned (GitHub) into the workspace's `skills/` folder during scaffolding (Stage 03). This makes the workspace self-contained.

**Referencing:** Stage CONTEXT.md files reference skills in their Inputs table:

```
| Skill | `../../skills/[name]/SKILL.md` | Index, then load rules as needed | [What it provides] |
```

Skills replace custom reference docs when an official skill covers the same ground. Keep workspace-specific files (design systems, brand config, build conventions) alongside skills, not inside them.

**When NOT to bundle:** Do not bundle skills that are purely about Claude Code itself (e.g., skill-creator, mcp-builder). Only bundle skills that provide domain knowledge the workspace's agents need at runtime.

---

## Pattern 10: Specs Are Contracts

Specification stages define WHAT the output should achieve and WHEN things happen. They do not prescribe HOW to implement. The build stage has creative freedom within the quality floor defined by the design system.

A spec contains:
- **Beat map** with approximate durations, narration, and mood
- **Visual philosophy** describing what a muted viewer should understand
- **Key moments** that MUST land, and why each matters
- **Audio sync points** mapping narration words to visual events
- **Color flow** with per-scene dominant color and mood

A spec does NOT contain: frame numbers, component names, pixel positions, spring configs, or prop definitions. These are implementation decisions that belong to the build stage.

---

## Pattern 11: Checkpoints

Creative stages should include at least one checkpoint where the agent pauses and the human steers. The agent completes a full unit of work, presents options or a draft, and the human redirects before the next unit begins. Checkpoints go between process steps, not within them.

Not every stage needs checkpoints. Linear stages (extract, render, validate) often run straight through. Creative stages (writing, design, ideation) benefit from at least one.

The Checkpoints section in a stage CONTEXT.md is a table:

```
| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| [step #] | [what to show] | [what to choose] |
```

---

## Pattern 12: Stage Audits

Creative and build stages should include an Audit section: a checklist the agent runs after completing the process but before writing to output/. Audits catch quality issues before they propagate downstream. Each check should be specific enough that pass/fail is unambiguous.

Not every stage needs an audit. Data extraction or file conversion stages may not benefit. Creative and build stages almost always do.

The Audit section in a stage CONTEXT.md is a table:

```
| Check | Pass Condition |
|-------|---------------|
| [Check name] | [What "passing" looks like] |
```

If any check fails, the agent revises before saving to output/.

---

## Pattern 13: Value Validation

Content-producing stages should define what types of value their output can deliver. Before the main creative work begins (ideally at a checkpoint), the agent and human should agree on which value types this specific piece will hit. This prevents "interesting but doesn't DO anything" output.

Value types are workspace-specific. A content workspace might use NOVEL, USABLE, QUESTION-GENERATING, INTERESTING. A course workspace might use TEACHES, PRACTICES, CHALLENGES. The framework is defined once in a reference file and used at every checkpoint.

---

## Pattern 14: Docs Over Outputs

Reference docs (design system, build conventions, skill rules) are the authoritative source for how to build. Previous stage outputs in `output/` folders are artifacts, not templates. Agents should not read other outputs to learn patterns.

This prevents copying from older, lower-quality work and ensures docs remain the single source of truth for quality standards. Early outputs are the worst outputs. If future agents learn from them, quality never improves.

---

## Pattern 15: Shared Constants

Workspaces that produce code should define a constants pattern. Configurable values (colors, fonts, timing, layout) live in shared files that all build outputs import from. The questionnaire populates these files once during onboarding. Change a value once, it updates everywhere.

This is Pattern 5 (Canonical Sources) applied to code values. Without shared constants, the same hex code or font name is hardcoded in every output file. Changing the brand color means a find-and-replace across every file ever built.

For non-code workspaces (content writing, course design), this pattern does not apply. Shared values live in reference docs instead.

---

## Quality Guardrails

- CONTEXT.md files: under 80 lines
- Reference files: under 200 lines (if longer, split into multiple files)
- Use plain English. Avoid jargon. If a term needs explaining, it is too specialized.
- No em dashes anywhere in the repo
- Every folder that should persist but starts empty gets a `.gitkeep` file
- Every markdown file should be readable by someone who understands markdown and git basics but does not have a deep engineering background
