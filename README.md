# Model Workspace Protocol (MWP)

A folder structure that routes AI agents through multi-stage workflows. Each stage has bounded context, a defined contract, and an output a human can edit before the next stage reads it.

No code. No app. Markdown files are the instructions. Output folders are the state. The AI agent is the runtime. Your editor is the UI.

**Created by Jake Van Clief**

## What Problem This Solves

The context window is working memory. When you load 15,000 tokens into an agent that needs 4,000, the extra 11,000 aren't neutral. They're noise. The agent blends rules from files it shouldn't be reading, confuses voice guidelines with animation timing, pulls from brand strategy when it should be writing code.

Most people experiencing "AI isn't good enough" are experiencing a context architecture problem. They're recreating the monolith: every file loaded into every conversation, just like a monolithic app where every module sees every other module.

MWP fixes this by breaking workflows into discrete stages where each stage has bounded context. An agent at stage 3 loads what stage 3 needs. Nothing else.

## How the Folder Structure Works

Agents read down four layers and stop when they have what they need.

```
Layer 0: CLAUDE.md         "Where am I?"      Always loaded (~800 tokens)
Layer 1: CONTEXT.md        "Where do I go?"    Read on entry (~300 tokens)
Layer 2: Stage CONTEXT.md  "What do I do?"     Read per-task (~200-500 tokens)
Layer 3: Content files     "What do I need?"   Loaded selectively (varies)
```

A rendering agent might only need Layers 0-1. A script-writing agent reads down to Layer 3. No agent reads everything.

Each stage is a folder containing:
- A **CONTEXT.md** file (the contract): declares what files to read, what the agent does with them, and what it produces
- An **output/** directory: where the finished artifact lands
- A **references/** directory: supporting material the agent needs for this stage only

The output of stage N sits in a known location. The CONTEXT.md of stage N+1 points to that location. That's the entire handoff mechanism. No orchestration code. No state management. Just files in predictable places and routing docs that point to them.

If stage 3 produces bad output, you fix stage 3. You edit the output file in a text editor, and stage 4 picks up your edited version because it just reads from stage 3's output folder.

## Getting Started

1. Clone this repo
2. `cd workspaces/script-to-animation` (or any workspace)
3. Open [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
4. Type `setup`
5. Answer the onboarding questions -- all at once, one pass
6. Your answers populate across the workspace files
7. Start producing -- give the agent a topic and walk through the stages

Each stage produces an output file. You can edit that file before moving on. The next stage reads whatever you left there.

## Available Workspaces

| Workspace | What it does | Stages |
|-----------|-------------|--------|
| [script-to-animation](workspaces/script-to-animation/) | Content idea through script writing, animation spec, and Remotion code | 3 |
| [course-deck-production](workspaces/course-deck-production/) | Unstructured material (PDFs, papers, notes) into polished PowerPoint slide decks | 5 |
| [workspace-builder](workspaces/workspace-builder/) | Build a new MWP workspace for any domain | 5 |

## Build Your Own Workspace

The workspace-builder builds new MWP workspaces. It follows MWP conventions to produce workspaces that follow MWP conventions. Same logic as a compiler that can compile itself.

1. `cd workspaces/workspace-builder`
2. Type `setup` to describe your domain
3. Walk through the five stages: discovery, mapping, scaffolding, questionnaire design, and validation
4. The output is a complete, ready-to-use workspace

The pattern transfers to any repeatable multi-step workflow where AI agents need structured context: report generation, audit procedures, curriculum development, code documentation, or any process where someone currently does the same sequence of steps with different input material each time.

## The Patterns

Every workspace follows the conventions defined in [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md). These are old ideas (separation of concerns, one-way dependencies, canonical sources) applied to a new problem (AI context management).

### Architecture

- **Stage contracts** -- Every stage CONTEXT.md has Inputs, Process, and Outputs. Simple enough for anyone to read. Structured enough for an agent to follow.
- **Stage handoffs** -- Output folders connect stages. Edit any output and the next stage picks up your changes.
- **One-way references** -- If A references B, B does not reference A. Prevents circular dependencies and scales linearly.
- **Selective section routing** -- CONTEXT.md tables specify which sections of which files to load. 80 lines instead of 174 compounds across every conversation.
- **Canonical sources** -- Every piece of information has one home. Other files point there. The moment the same rule exists in two files, they drift.

### Quality

- **Specs are contracts** -- Specification stages define WHAT and WHEN. They do not prescribe HOW. The build stage has creative freedom within the quality floor defined by the design system.
- **Checkpoints** -- Creative stages pause for human steering between steps. The agent completes a unit of work, presents options, and the human redirects before the next unit begins.
- **Stage audits** -- Quality checklists the agent runs after completing a stage but before writing output. Each check has an unambiguous pass condition.
- **Value validation** -- Content stages define what types of value their output delivers. The value is locked before drafting begins.
- **Docs over outputs** -- Reference docs are the authoritative source for how to build. Agents do not read previous outputs to learn patterns.

### Onboarding

- **Questionnaire design** -- Flat, all-at-once, system-level only. Configure the factory, not the product. Voice questions extract concrete examples, not descriptions.
- **Shared constants** -- Code-producing workspaces define shared constant files that all outputs import from. Change a value once, it updates everywhere.

## Contributing

**New workspaces are the main contribution.** If you have a repeatable workflow that benefits from staged human-in-the-loop AI automation, it probably belongs here.

### How to contribute a workspace

1. Fork the repo
2. Use the workspace-builder to create your workspace:
   ```
   cd workspaces/workspace-builder
   # Type "setup", describe your domain, walk through all 5 stages
   ```
3. The builder outputs a validated workspace to `workspaces/[your-workspace]/`
4. Test it: run `setup` in your new workspace, then run through the pipeline at least once
5. Open a PR

### What makes a good workspace

- **Repeatable workflow.** Something you or others will run many times, not a one-off task.
- **Clear stage boundaries.** Each stage produces a distinct artifact that a human might want to review or edit before proceeding.
- **System-level setup.** The questionnaire configures the production system (identity, design, preferences), not a specific run.
- **Follows MWP conventions.** The workspace-builder enforces this automatically. See [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md) for the full spec (15 patterns).

### PR checklist

- [ ] Workspace was built using the workspace-builder (not hand-assembled)
- [ ] `setup` runs cleanly and all placeholders resolve
- [ ] At least one end-to-end run completed successfully
- [ ] No stage outputs committed (output folders should only contain `.gitkeep`)
- [ ] All CONTEXT.md files are under 80 lines
- [ ] All reference files are under 200 lines
- [ ] Creative stages have at least one checkpoint and an audit section
- [ ] No circular dependencies between stages

### Other contributions

- **Bug fixes** to existing workspaces or conventions
- **Improvements** to the workspace-builder itself
- **New patterns** for `_core/CONVENTIONS.md` (propose in an issue first)

## Origin

MWP grew out of a [content production routing architecture](https://github.com/RinDig/Content-Agent-Routing-Promptbase) that applies separation of concerns to AI context windows instead of code modules. That system runs a full content operation: scripting, animation specs, Remotion builds, brand management. MWP is the general-purpose version -- the structural patterns extracted so anyone can scaffold their own workflows.

MCP standardizes how models talk to tools. MWP standardizes how models navigate work.

## License

MIT License. See [LICENSE](LICENSE) for details.
