# Product Requirements Document: Model Workspace Protocol (MWP)

## What This Is

MWP is an open-source framework for building structured, multi-stage AI workflows out of markdown files and folder conventions. Each "workspace" is a self-contained workflow scaffold that gives AI agents (specifically Claude Code agents) exactly the right context at each stage of a task, and gives humans clear edit surfaces between stages.

Think of it as development environments for AI work. The folder structure IS the product. The markdown files route agents to the right context, define stage boundaries, and create natural intervention points where a human can step in, edit outputs, and let the next stage pick up the edited version.

The repo ships as a collection of domain-specific workspaces that people clone and configure for their own use. Each workspace has an onboarding questionnaire that hydrates placeholder variables across the markdown files with real details (brand voice, target audience, project specifics, etc).

## Why This Exists

The core problem: most AI tooling gives you one shot. You prompt, you get output, you like it or you redo the whole thing. There is no way to isolate problems at specific stages of a multi-step workflow. If step 3 of 5 goes wrong, you often have to re-run from scratch.

MWP solves this by breaking workflows into discrete stages where each stage has its own agent context, its own output artifact, and its own edit surface. An agent at stage 3 knows what stages 1 and 2 produced because the routing tells it where to look. If stage 3 produces something off, you fix stage 3. You do not re-run the pipeline.

The secondary problem: context window management. Loading your entire content system into one conversation burns tokens on files the agent does not need and dilutes the context that matters. MWP gives each agent exactly the right context for its job and nothing else, through a tiered routing architecture.

## Target Users

Vibe coders and builders who use Claude Code. They can run terminal commands and navigate repos but may not have deep software engineering backgrounds. The system needs to be readable and navigable by someone who understands markdown and git basics. Every design decision should favor clarity over cleverness.

## The Three-Layer Routing Architecture

This is the core pattern that every workspace follows. Agents read down the layers, stopping as soon as they have what they need.

### Layer 0: CLAUDE.md (always loaded)
- Auto-loaded by Claude Code into every conversation
- Contains: folder map, ID systems, naming conventions, and a routing table that says "doing X? go to Y/CONTEXT.md"
- Purpose: orientation ("where am I?")
- Token cost: ~800 tokens, always present

### Layer 1: Top-level CONTEXT.md (read on entry)
- The first thing an agent reads when entering the workspace
- Contains: a task routing table that maps task types to specific stage folders
- Purpose: navigation ("where do I go?")
- Token cost: ~300 tokens, read once

### Layer 2: Stage-level CONTEXT.md files (read per-task)
- Each stage folder has its own CONTEXT.md
- Contains: scope definition, what-to-load tables (which files, which sections), and step-by-step process
- Purpose: instruction ("what do I do?")
- Token cost: ~200-500 tokens each

### Layer 3: Content files (loaded selectively)
- The actual reference material, loaded only when a CONTEXT.md table says to
- Contains: voice rules, templates, specs, whatever the stage needs
- Purpose: knowledge ("what do I need to know?")
- Token cost: varies, 500-3000 tokens each

An agent reads down the layers and stops when it has what it needs. A rendering agent might only need Layers 0-1. A script-writing agent reads down to Layer 3. No agent reads everything.

## Key Design Patterns to Enforce Across All Workspaces

### Pattern 1: Stage Contracts

Every stage CONTEXT.md follows the same three-section shape:

```markdown
## Inputs
What files to read and where to find them.

## Process
What the agent does, step by step.

## Outputs
What it produces and where it goes.
```

This is the contract. It is simple enough that a non-technical user can read it and understand what is happening, and structured enough that an agent can follow it reliably.

### Pattern 2: Stage Handoffs via Output Folders

Every stage has an `output/` subfolder. The agent writes its artifact there. The next stage's CONTEXT.md points to the previous stage's `output/` folder for its input. The convention:

- Stage N produces: `stages/0N-name/output/artifact-name.md`
- Stage N+1's CONTEXT.md says: "Read `../0N-name/output/artifact-name.md` as your input"

This is the handoff. A human can open the output file, edit it, and the next stage picks up the edited version because it just reads the file. No state management, no orchestration layer, just files in predictable places.

### Pattern 3: One-Way Cross-References

Every workspace folder points outward to what it needs. No folder points back. If workspace A references workspace B, workspace B does NOT reference workspace A. This prevents N-squared reference growth as the system scales.

### Pattern 4: Selective Section Routing

CONTEXT.md files do not just say "read voice-rules.md." They say "read the Voice Rules section of voice-rules.md." This way a 174-line file gets loaded as 80 lines of actionable rules. The other 94 lines of strategic rationale stay unloaded.

Format in CONTEXT.md tables:
```
| File | Section to Load | Why |
|------|----------------|-----|
| voice-rules.md | "Voice Rules" through "What the Voice Is NOT" | Tone guidance for writing |
```

### Pattern 5: Canonical Sources

Every piece of information has ONE home. Other files point there, they do not duplicate it. If you need to update a rule, you update it in one place. Every other file just has a pointer.

### Pattern 6: CONTEXT.md = Routing, Not Content

CONTEXT.md files answer three questions: What is this folder? What do I load? What is the process? They never contain the actual reference material. This keeps them small (25-80 lines) and prevents them from going stale.

## Placeholder and Onboarding System

### How Placeholders Work

Throughout the workspace markdown files, configurable details use double-brace placeholders:

```
{{BRAND_NAME}}
{{TARGET_AUDIENCE}}
{{VOICE_DESCRIPTION}}
{{PRIMARY_PLATFORM}}
```

These are NOT code variables. They are literal strings in markdown files that the onboarding agent finds and replaces with real content.

### How Onboarding Works

Each workspace has a `setup/` folder containing:

- `questionnaire.md`: Defines the questions the onboarding agent asks, grouped by category. Each question maps to one or more placeholders and specifies which files those placeholders appear in.
- `defaults.md` (optional): Default values for placeholders if the user wants to skip certain questions.

The onboarding flow:

1. User opens the workspace in Claude Code
2. User types `setup` (or whatever trigger keyword is in the workspace CLAUDE.md)
3. The agent reads `setup/questionnaire.md`
4. The agent asks the questions conversationally, collecting answers
5. The agent replaces placeholders across all specified files with the collected answers
6. If any answers indicate entire workflow branches are irrelevant (e.g., "I don't do short-form video"), the agent removes those stage folders entirely
7. The agent confirms completion and summarizes what was configured

### Questionnaire.md Format

```markdown
# Onboarding Questionnaire

## Brand Identity
These questions configure your brand-vault files.

### Q1: What is your brand or project name?
- Placeholder: {{BRAND_NAME}}
- Files: brand-vault/identity.md, stages/01-script/references/templates.md
- Type: free text

### Q2: Describe your voice in one sentence.
- Placeholder: {{VOICE_DESCRIPTION}}
- Files: brand-vault/voice-rules.md
- Type: free text
- Follow-up: If the answer is vague, ask for 2-3 adjectives that describe the tone.

### Q3: Who is your primary audience?
- Placeholder: {{TARGET_AUDIENCE}}
- Files: brand-vault/identity.md, stages/01-script/CONTEXT.md
- Type: free text

## Workflow Configuration
These questions determine which stages are active.

### Q4: Does your workflow include animation/video production?
- If NO: Remove stages/03-build/ entirely
- If YES: Continue to Q5

### Q5: What platform are you primarily creating for?
- Placeholder: {{PRIMARY_PLATFORM}}
- Files: stages/01-script/references/platform-specs.md
- Options: TikTok/Reels (vertical, 30-90s), YouTube (horizontal, 3-15min), Both
```

## Repo Structure

```
model-workspace-protocol/
├── README.md                              ← project overview, philosophy, getting started
├── LICENSE
├── CLAUDE.md                              ← meta-level: orients Claude Code to the repo itself
│
├── _core/                                 ← shared conventions and templates
│   ├── CONVENTIONS.md                     ← the rules above (stage contracts, handoffs, naming)
│   ├── placeholder-syntax.md              ← how {{VARIABLES}} work, replacement rules
│   └── templates/                         ← blank starting points for building new workspaces
│       ├── stage-context-template.md      ← the Inputs/Process/Outputs skeleton
│       ├── questionnaire-template.md      ← the onboarding question format
│       ├── workspace-claude-template.md   ← CLAUDE.md template for new workspaces
│       └── workspace-context-template.md  ← top-level CONTEXT.md template
│
├── workspaces/
│   │
│   ├── script-to-animation/               ← WORKSPACE 1: content script → animation pipeline
│   │   ├── CLAUDE.md                      ← workspace orientation + trigger keywords
│   │   ├── CONTEXT.md                     ← routing table for this workflow
│   │   ├── setup/
│   │   │   └── questionnaire.md           ← onboarding questions for this domain
│   │   ├── brand-vault/                   ← hydrated during onboarding
│   │   │   ├── CONTEXT.md                 ← routes agents to correct sections
│   │   │   ├── voice-rules.md             ← writing voice, tone, style constraints
│   │   │   └── identity.md                ← brand name, audience, positioning
│   │   ├── stages/
│   │   │   ├── 01-script/
│   │   │   │   ├── CONTEXT.md             ← Inputs/Process/Outputs contract
│   │   │   │   ├── output/                ← where finished scripts land
│   │   │   │   │   └── .gitkeep
│   │   │   │   └── references/            ← hook system, templates, pillar docs
│   │   │   │       ├── hook-system.md
│   │   │   │       ├── script-templates.md
│   │   │   │       └── content-pillars.md
│   │   │   ├── 02-spec/
│   │   │   │   ├── CONTEXT.md
│   │   │   │   ├── output/
│   │   │   │   │   └── .gitkeep
│   │   │   │   └── references/
│   │   │   │       ├── spec-format.md     ← BEATS constants, frame ranges, etc
│   │   │   │       ├── component-registry.md
│   │   │   │       └── design-system.md
│   │   │   └── 03-build/
│   │   │       ├── CONTEXT.md
│   │   │       ├── output/
│   │   │       │   └── .gitkeep
│   │   │       └── references/
│   │   │           └── build-conventions.md  ← Remotion patterns, file naming, etc
│   │   └── shared/                        ← files used across multiple stages
│   │       └── platform-specs.md          ← resolution, duration, format per platform
│   │
│   └── workspace-builder/                 ← WORKSPACE 2: builds new MWP workspaces
│       ├── CLAUDE.md
│       ├── CONTEXT.md
│       ├── setup/
│       │   └── questionnaire.md           ← asks about the domain being built for
│       ├── stages/
│       │   ├── 01-discovery/
│       │   │   ├── CONTEXT.md
│       │   │   └── output/
│       │   │       └── .gitkeep
│       │   ├── 02-mapping/
│       │   │   ├── CONTEXT.md
│       │   │   └── output/
│       │   │       └── .gitkeep
│       │   ├── 03-scaffolding/
│       │   │   ├── CONTEXT.md
│       │   │   └── output/
│       │   │       └── .gitkeep
│       │   └── 04-questionnaire-design/
│       │       ├── CONTEXT.md
│       │       └── output/
│       │           └── .gitkeep
│       └── references/
│           ├── conventions-reference.md   ← points to /_core/CONVENTIONS.md
│           └── examples/                  ← completed workspace examples to learn from
│               └── script-to-animation-summary.md
```

## Workspace 1: Script-to-Animation

This is the first domain workspace and serves as the reference implementation. It covers the workflow of turning a content idea into a finished animated video through three stages.

### Stage 01-script

**Purpose:** Take a topic/idea and produce a finished script ready for animation spec work.

**Inputs:**
- Topic or content idea (from user)
- brand-vault/voice-rules.md (the "Voice Rules" and "What the Voice Is NOT" sections)
- brand-vault/identity.md (the "One-Sentence Brand" and "Audience" sections)
- references/hook-system.md (hook patterns and examples)
- references/script-templates.md (structural templates for different content types)
- references/content-pillars.md (only the relevant pillar section)
- shared/platform-specs.md (duration and format constraints)

**Process:**
1. Identify which content pillar this topic falls under
2. Select a hook pattern from the hook system
3. Choose a script template based on content type
4. Write the script following voice rules
5. Check against platform specs for length/format
6. Save to output/

**Outputs:**
- A markdown file in `output/` containing the finished script with metadata header (pillar, hook type, target duration, platform)

**Human edit surface:** The finished script in `output/`. A user can open this, rewrite lines, adjust timing notes, change the hook, whatever they want. Stage 02 reads whatever is in that file.

### Stage 02-spec

**Purpose:** Take a finished script and produce an animation specification that defines the visual treatment for every line.

**Inputs:**
- stages/01-script/output/ (the finished script)
- references/spec-format.md (BEATS constants, frame-range syntax, inline prop format)
- references/component-registry.md (available animation components)
- references/design-system.md (colors, typography, motion rules)

**Process:**
1. Read the script from 01-script/output/
2. Break script into beats (logical visual segments)
3. For each beat, define: frame range, components used, props, transitions
4. Follow the spec format conventions
5. Reference only components that exist in the registry
6. Save to output/

**Outputs:**
- A markdown spec file in `output/` with beat-by-beat animation instructions

**Human edit surface:** The spec file. User can adjust timing, swap components, change visual treatments. Stage 03 reads whatever is in that file.

### Stage 03-build

**Purpose:** Take an animation spec and produce the actual code/build files.

**Inputs:**
- stages/02-spec/output/ (the animation spec)
- references/build-conventions.md (Remotion patterns, file structure, naming)
- references/component-registry.md (same as stage 02, for implementation reference)
- references/design-system.md (for exact values: hex colors, font sizes, easing curves)

**Process:**
1. Read the spec from 02-spec/output/
2. Create the Remotion component structure
3. Implement each beat as defined in the spec
4. Follow build conventions for file naming and organization
5. Save to output/

**Outputs:**
- Remotion/React component files in `output/`

**Human edit surface:** The actual code files. User can tweak animations, adjust timing, modify components directly.

## Workspace 2: Workspace Builder

This is the meta-workspace. It guides an agent through the process of creating a new MWP workspace for any domain. This proves the concept: if MWP can describe how to build MWP workspaces, the abstraction is general enough to describe anything.

### Stage 01-discovery

**Purpose:** Understand the domain workflow through conversation with the user.

**Inputs:**
- User conversation (the agent asks questions about the workflow being built)
- references/conventions-reference.md (so the agent knows MWP patterns)
- references/examples/script-to-animation-summary.md (concrete example to reference)

**Process:**
1. Ask the user to describe their workflow end to end
2. Identify the distinct stages (where does one task end and another begin?)
3. For each stage, ask: what goes in? what comes out? what does the agent need to know?
4. Identify what context is shared across stages vs. stage-specific
5. Identify what details are user-specific (these become questionnaire items)
6. Produce a workflow map document

**Outputs:**
- `output/workflow-map.md`: A structured document listing all stages, their inputs/outputs, shared context, and user-specific variables

### Stage 02-mapping

**Purpose:** Turn the workflow map into formal stage contracts and a dependency graph.

**Inputs:**
- stages/01-discovery/output/workflow-map.md
- /_core/CONVENTIONS.md (the rules for stage contracts)

**Process:**
1. Read the workflow map
2. For each stage, write the Inputs/Process/Outputs contract
3. Map cross-references (which stages read from which other stages)
4. Identify canonical sources (where does each piece of info live?)
5. Verify one-way references (no circular dependencies)
6. Produce the contracts document

**Outputs:**
- `output/stage-contracts.md`: Formal Inputs/Process/Outputs blocks for every stage, plus a dependency diagram

### Stage 03-scaffolding

**Purpose:** Generate the actual folder tree and CONTEXT.md files for the new workspace.

**Inputs:**
- stages/02-mapping/output/stage-contracts.md
- /_core/templates/ (all the template files)

**Process:**
1. Read the stage contracts
2. Create the folder structure (CLAUDE.md, CONTEXT.md, setup/, brand-vault or equivalent, stages/, shared/)
3. Populate each CONTEXT.md using the stage-context-template, filled with the contract info
4. Create placeholder reference files for each stage
5. Create the workspace CLAUDE.md with trigger keywords
6. Create the top-level CONTEXT.md routing table
7. Output the complete workspace folder

**Outputs:**
- `output/` contains the entire generated workspace folder structure, ready for the next stage to add the questionnaire

### Stage 04-questionnaire-design

**Purpose:** Build the onboarding questionnaire for the new workspace.

**Inputs:**
- stages/01-discovery/output/workflow-map.md (for the user-specific variables identified)
- stages/03-scaffolding/output/ (the generated workspace, to know which files contain placeholders)
- /_core/templates/questionnaire-template.md

**Process:**
1. Read the workflow map for user-specific variables
2. Read the scaffolded workspace to find all {{PLACEHOLDER}} instances
3. For each placeholder, write a clear question with context
4. Group questions by category (identity, workflow config, stage-specific)
5. Add conditional logic (if answer X, remove stage Y)
6. Map each question to the files and locations where its placeholder appears
7. Write the questionnaire.md

**Outputs:**
- `output/questionnaire.md`: The complete onboarding questionnaire, ready to be placed in the workspace's setup/ folder

After all four stages complete, the builder has produced a new, fully functional MWP workspace with onboarding.

## File Content Specifications

### Root CLAUDE.md

This file orients Claude Code to the entire repo. It should contain:

- One paragraph explaining what MWP is
- A folder map showing the repo structure (workspaces and core)
- A routing table: "Working on X? Go to workspaces/X/CLAUDE.md"
- A note that each workspace is self-contained and has its own CLAUDE.md
- The trigger keyword convention: typing `setup` in any workspace starts onboarding

### Root README.md

This is the GitHub-facing README. It should contain:

- What MWP is (the "app without code" pitch: structured markdown files that turn AI agents into controlled, multi-stage workflows)
- The core value: control at every stage, not just one-shot prompting
- The three-layer routing architecture explained simply
- How to get started (clone the repo, cd into a workspace, open in Claude Code, type `setup`)
- List of available workspaces with one-line descriptions
- How to build your own workspace (use workspace-builder)
- Link to CONVENTIONS.md for the full spec
- License info

### _core/CONVENTIONS.md

The full specification of MWP patterns. This is the source of truth for how workspaces are built. Should cover all six design patterns listed above (stage contracts, handoffs, one-way references, selective section routing, canonical sources, CONTEXT as routing). Include concrete examples for each pattern. This file should be thorough because the workspace-builder references it.

### _core/placeholder-syntax.md

How the placeholder system works:

- Syntax: `{{VARIABLE_NAME}}` with SCREAMING_SNAKE_CASE
- Replacement is literal string substitution in markdown files
- Placeholders can appear in any markdown file within a workspace
- The questionnaire.md maps each placeholder to its target files
- After onboarding, no placeholders should remain (the agent verifies this)
- Conditional placeholders: `{{?SECTION_NAME}}...{{/SECTION_NAME}}` wraps blocks that get removed if the corresponding questionnaire answer indicates they are not needed

### Workspace CLAUDE.md files

Each workspace CLAUDE.md should contain:

- One sentence: what this workspace does
- The folder map for this workspace specifically
- Trigger keywords: `setup` (run onboarding), `status` (show which stages have outputs), and any workspace-specific triggers
- The routing table: "Writing a script? → stages/01-script/CONTEXT.md"
- A note about the stage handoff convention: outputs go in output/ folders, next stage reads from there

### Stage CONTEXT.md files

Every stage CONTEXT.md follows this exact structure:

```markdown
# [Stage Name]

[One sentence: what this stage does]

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | ../0N-prev/output/artifact.md | Full file | The artifact to work from |
| Brand vault | ../../brand-vault/voice-rules.md | "Voice Rules" section | Tone guidance |

## Process

1. [Step one]
2. [Step two]
3. [Step three]
...

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| [Name] | output/[filename].md | [Description of format] |
```

## Build Instructions

Build this repo in the following order:

### Phase 1: Core infrastructure
1. Create the root folder structure
2. Write `_core/CONVENTIONS.md` (this is the source of truth, write it thoroughly)
3. Write `_core/placeholder-syntax.md`
4. Create all template files in `_core/templates/`
5. Write root `CLAUDE.md`
6. Write root `README.md`

### Phase 2: Script-to-animation workspace
1. Create the folder structure under `workspaces/script-to-animation/`
2. Write the workspace `CLAUDE.md`
3. Write the workspace `CONTEXT.md` (routing table)
4. Write `setup/questionnaire.md` with onboarding questions
5. Write `brand-vault/` files with `{{PLACEHOLDER}}` variables
6. Write each stage's `CONTEXT.md` following the Inputs/Process/Outputs contract format
7. Write reference files for each stage with appropriate placeholders
8. Write `shared/platform-specs.md`
9. Add `.gitkeep` files in all `output/` directories

### Phase 3: Workspace-builder workspace
1. Create the folder structure under `workspaces/workspace-builder/`
2. Write the workspace `CLAUDE.md`
3. Write the workspace `CONTEXT.md`
4. Write `setup/questionnaire.md` (asks about the domain being built for)
5. Write each stage's `CONTEXT.md`
6. Write `references/conventions-reference.md` (points to core conventions)
7. Create `references/examples/script-to-animation-summary.md` (summarizes workspace 1 as a learning example)

### Phase 4: Verification
1. Read through the entire repo and verify all cross-references point to real files
2. Verify no CONTEXT.md contains actual content (only routing)
3. Verify every placeholder has a corresponding questionnaire entry
4. Verify the stage handoff chain is unbroken (every stage's output is the next stage's input)
5. Verify no circular references exist

## Quality Standards

- Every markdown file should be readable by a non-technical person
- CONTEXT.md files should stay under 80 lines
- Reference files should stay under 200 lines (if longer, split them)
- Use plain English, avoid jargon
- No em dashes anywhere in the repo
- Folder and file names use lowercase-with-hyphens
- Stage folders use zero-padded numbers: 01-, 02-, 03-
- Every folder that should persist but starts empty gets a .gitkeep

## What Success Looks Like

When complete, a user should be able to:

1. Clone the repo
2. `cd workspaces/script-to-animation`
3. Open Claude Code
4. Type `setup`
5. Answer 8-12 questions about their brand, voice, audience, and platform
6. See their answers populated across all the workspace files
7. Start working through stages, with each stage's agent loading only its required context
8. Edit any intermediate output and have the next stage pick up their edits
9. Use `workspace-builder` to create an entirely new domain workspace from scratch

That is the product.
