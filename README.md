# Model Workspace Protocol (MWP)

Structured markdown files that turn AI agents into controlled, multi-stage production systems.

No code. No app. The folder structure is the product. Markdown files route agents to the right context at each stage, define handoff points where humans can intervene, and create repeatable workflows you run over and over -- set up once, produce forever.

**Created by [Jake Van Clief](https://github.com/arro1)**

## The Problem

Most AI tooling gives you one shot. You prompt, you get output, you like it or you redo the whole thing. If step 3 of 5 goes wrong, you re-run from scratch.

MWP breaks workflows into discrete stages. Each stage has its own context, its own output, and its own edit surface. If stage 3 produces something off, you fix stage 3. You do not re-run the pipeline.

The workspace is a production system, not a single-use template. You configure it once (brand, design, preferences), then run it repeatedly -- each run produces a new deliverable using the same pipeline.

## How It Works

Agents read down four layers and stop when they have what they need.

```
Layer 0: CLAUDE.md         "Where am I?"      Always loaded (~800 tokens)
Layer 1: CONTEXT.md        "Where do I go?"    Read on entry (~300 tokens)
Layer 2: Stage CONTEXT.md  "What do I do?"     Read per-task (~200-500 tokens)
Layer 3: Content files     "What do I need?"   Loaded selectively (varies)
```

A rendering agent might only need Layers 0-1. A script-writing agent reads down to Layer 3. No agent reads everything. This keeps token cost low and context focused.

## Getting Started

1. Clone this repo
2. `cd workspaces/script-to-animation` (or any workspace)
3. Open [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
4. Type `setup`
5. Answer a handful of questions about your brand, design, and workflow -- all at once, one pass
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

Use the workspace-builder to create a workspace for any domain:

1. `cd workspaces/workspace-builder`
2. Type `setup` to describe your domain
3. Walk through the five stages: discovery, mapping, scaffolding, questionnaire design, and validation
4. The output is a complete, ready-to-use MWP workspace

The workspace-builder itself follows MWP conventions, so the workspaces it produces are automatically consistent.

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
- **System-level setup.** The questionnaire configures the production system (identity, design, preferences), not a specific run. Per-run details are collected at the start of each pipeline run.
- **Follows MWP conventions.** The workspace-builder enforces this automatically. See [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md) for the full spec.

### PR checklist

- [ ] Workspace was built using the workspace-builder (not hand-assembled)
- [ ] `setup` runs cleanly and all placeholders resolve
- [ ] At least one end-to-end run completed successfully
- [ ] No stage outputs committed (output folders should only contain `.gitkeep`)
- [ ] All CONTEXT.md files are under 80 lines
- [ ] All reference files are under 200 lines (or documented exception for bundled external docs)
- [ ] No circular dependencies between stages
- [ ] Root CLAUDE.md routing table updated to include your workspace

### Other contributions

- **Bug fixes** to existing workspaces or conventions
- **Improvements** to the workspace-builder itself
- **New patterns** for `_core/CONVENTIONS.md` (propose in an issue first)

## Core Patterns

Every workspace follows the conventions defined in [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md):

- **Stage contracts** -- Every stage has Inputs, Process, and Outputs sections
- **Stage handoffs** -- Output folders connect stages. Edit any output and the next stage picks up your changes
- **One-way references** -- Folders point outward to what they need. No circular dependencies
- **Selective section routing** -- Agents load specific sections of files, not entire files
- **Canonical sources** -- Every piece of information has one home. Other files point there
- **CONTEXT.md = routing only** -- CONTEXT files tell agents where to go, not what to know
- **Tool prerequisites** -- External tools get setup guides and are listed in a prerequisites table
- **Questionnaire design** -- Flat, all-at-once, system-level only. Configure the factory, not the product.

## License

MIT License. See [LICENSE](LICENSE) for details.
