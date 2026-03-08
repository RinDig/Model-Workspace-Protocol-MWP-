# Interpreted Context Methdolog (ICM)

Folder structure as agent architecture.

ICM replaces framework-level orchestration with filesystem structure. Numbered folders represent stages. Markdown files carry the prompts and context that tell a single AI agent what role to play at each step. The result is a system where one agent, reading the right files at the right moment, does the work that would otherwise require a multi-agent framework.

**Created by Jake Van Clief**

---

## Why This Exists

There are genuinely good agentic frameworks available today. CrewAI, LangChain, AutoGen, and others handle multi-step orchestration, memory management, tool use, and error recovery. They work. But they work within their own structures, and adjusting those structures requires development work. Changing the order of steps, swapping a prompt, adding or removing a stage: these actions typically mean editing code, understanding abstractions, and redeploying.

For practitioners whose workflows are sequential and need human review at each step, the control surface can be much simpler.

MWP is built on an observation that is almost too simple to write down: if the prompts and context for each stage of a workflow already exist as files in a well-organized folder hierarchy, you do not need multiple agents or a coordination framework. You need one agent that reads the right files at the right moment. The folder structure tells it what to do at each step.

This is going backward before going forward. The principles that made Unix pipelines effective in the 1970s -- programs that do one thing, output of one becomes input of another, plain text as universal interface -- apply directly to AI agent orchestration today.

## Design Principles

Five ideas, each borrowed from established practice.

**One stage, one job.** Each stage handles a single step. A stage that researches does not also write. A stage that writes does not also build. This follows the Unix principle and Parnas's information-hiding criterion.

**Plain text as the interface.** Stages communicate through markdown files. No binary formats, no database connections, no proprietary serialization. Any tool that can read a text file can participate. Any human who can open a text editor can inspect or modify any artifact.

**Layered context loading.** Agents load only the context they need for the current stage. Less irrelevant context means better model performance. This is prevention rather than compression.

**Every output is an edit surface.** The intermediate output of each stage is a file a human can open, read, edit, and save before the next stage runs. The system picks up whatever the human left there.

**Configure the factory, not the product.** A workspace is set up once with the user's preferences, brand, style, and structural decisions. After that, each run of the pipeline produces a new deliverable using the same configuration.

## How It Works

Agents read down five layers and stop when they have what they need.

```
Layer 0: CLAUDE.md           "Where am I?"            Always loaded (~800 tokens)
Layer 1: CONTEXT.md          "Where do I go?"          Read on entry (~300 tokens)
Layer 2: Stage CONTEXT.md    "What do I do?"            Read per-task (~200-500 tokens)
Layer 3: Reference material  "What rules apply?"        Loaded selectively (varies)
Layer 4: Working artifacts   "What am I working with?"  Loaded selectively (varies)
```

Layers 3 and 4 are both content the agent loads while executing a stage, but they represent different kinds of context. Layer 3 is reference material -- design systems, voice rules, build conventions, domain knowledge. These files are configured once during setup and stay the same across every run. They are the factory. Layer 4 is working artifacts -- previous stage output, user-provided source material, anything specific to this run. These change every time.

The distinction matters because these layers require different things from the model. Layer 3 material needs to be internalized as constraints and patterns -- write *like this*, use *these colors*, follow *these conventions*. Layer 4 material needs to be processed as input -- transform *this research* into a script, convert *this script* into a specification.

A rendering agent might only need Layers 0 through 2. A script-writing agent reads down to Layer 4 to access both voice rules (Layer 3) and source material (Layer 4). No agent reads everything. The total context delivered at any given stage typically ranges from 2,000 to 8,000 tokens -- well within the range where current models perform at their best.

Contrast this with a monolithic approach where all stage instructions, all reference files, and all prior outputs are loaded into a single prompt. That approach can easily reach 30,000 to 50,000 tokens, pushing into the range where models start losing track of what matters.

A workspace looks like this:

```
workspace/
  CONTEXT.md               # Layer 1: task routing
  stages/
    01-research/
      CONTEXT.md            # Layer 2: stage contract
      references/           # Layer 3: reference material for this stage
      output/               # Layer 4: working artifacts
    02-script/
      CONTEXT.md
      references/
      output/
    03-production/
      CONTEXT.md
      references/
      output/
  _config/                  # Layer 3: brand, voice, design system
  shared/                   # Layer 3: cross-stage resources
  skills/                   # Layer 3: bundled domain knowledge
  setup/
    questionnaire.md        # One-time onboarding
```

The numbering encodes execution order. The folder boundaries enforce separation of concerns. The `output/` directories are the Layer 4 handoff points: the output of stage 01 becomes available as input to stage 02. If a human edits a file in `01-research/output/` before running stage 02, the agent picks up the edited version. The `references/` directories and `_config/` folder hold Layer 3 material -- stable knowledge that persists across runs.

Layer 2 is the control point. Each stage contract includes an Inputs table that specifies exactly which files from Layers 3 and 4 to load, and which sections of those files are relevant. Without this scoping, an agent would either load everything or guess. The Inputs table makes the selection explicit, editable, and auditable.

The filesystem is doing the work that a framework would otherwise do in code. Stage sequencing is the folder numbering. Context scoping is the folder hierarchy. State management is the files on disk. Coordination between stages is one folder's output being another folder's input.

## Stage Contracts

Each stage defines a contract in its CONTEXT.md with three parts: what it reads, what it does, and what it writes.

```markdown
## Inputs
| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | ../01-research/output/ | Full file | Source material |
| Style guide | ../../brand-vault/voice-rules.md | Voice Rules section | Tone guidance |

## Process
1. Read the research output
2. Identify the narrative angle
3. Write the script following voice-rules
4. Run audit checks
5. Save to output/

## Outputs
| Artifact | Location | Format |
|----------|----------|--------|
| Script | output/[slug]-script.md | Markdown with metadata header |
```

Creative stages also include **checkpoints** (where the agent pauses for human steering) and **audits** (quality checklists the agent runs before writing output). Not every stage needs these. Linear stages like extraction or rendering often run straight through. But any stage where the model is making creative decisions benefits from at least one checkpoint and a quality gate.

## Observability

The most useful property of this approach may be one that was not designed as a feature. Because every intermediate output is a plain file, the system is observable by default. There is no logging layer to build, no dashboard to configure, no special tooling to inspect pipeline state. You open a folder and read the files.

This is a glass-box AI workflow. It did not become transparent through the addition of an explanation layer. It was never opaque in the first place, because every artifact is a plain-text file that a human can read.

If stage 3 produces bad output, you know exactly where to look. You can read the stage's CONTEXT.md to see what instructions it received. You can read the input files to see what it was working with. You can edit the output and re-run the next stage. The entire system state is visible at all times because the system state is the filesystem.

## Portability

A workspace is a folder. It can be copied to another machine, committed to Git, emailed as a zip file, or synced through any cloud storage service. It carries its own prompts, its own context structure, its own stage definitions. There is no server to configure, no environment to replicate, no deployment step.

Every change to a prompt, every edit to a stage output, every configuration adjustment is diffable and reversible through standard version control. Stage outputs can be committed after each run, creating a version history of the entire pipeline's behavior over time.

If you build a workspace for a client's weekly reporting workflow, handing it over means copying a folder. The client can run it, edit the prompts to match their evolving needs, and adjust stages without involving a developer.

## Where This Works

MWP handles sequential multi-step workflows where a human reviews output at each stage. Content production pipelines. Research and analysis workflows. Monitoring and digest systems. Reporting processes. Training material development.

The common thread: these workflows are sequential (step 2 follows step 1), reviewable (a human should check each step's output), and repeatable (the same pipeline runs regularly with different input).

## Where This Does Not Work

MWP is not a replacement for multi-agent frameworks in every context.

**Real-time multi-agent collaboration** -- where agents need to communicate dynamically in tight loops -- requires message-passing infrastructure that frameworks like AutoGen provide. File-based handoffs are too slow for this.

**High-concurrency systems** -- where many users hit the same pipeline simultaneously -- need queueing, state isolation, and deployment infrastructure. MWP is local-first by design.

**Complex branching logic** -- where automated decisions mid-pipeline determine the next step -- is awkward in MWP. A human can make branching decisions between stages, but automated branching would require scripting that moves MWP toward being a framework itself.

The claim is not that MWP replaces existing tools across the board. The claim is that for a large and common class of workflows, the existing tools provide more complexity than the problem requires, and that complexity has real costs.

## A Note on MCP

It is worth distinguishing MWP from Anthropic's Model Context Protocol (MCP). MCP standardizes how models access external tools and data sources -- the integration problem between AI systems and the services they need to call. MWP addresses a different layer: how to structure and deliver context to an agent across a multi-stage workflow. The two are complementary. An MWP stage might use MCP connections to access external services, while the stage's folder structure determines what context the agent receives when doing so.

---

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

The workspace-builder is a workspace whose output is a new workspace. It follows MWP conventions to produce workspaces that follow MWP conventions.

1. `cd workspaces/workspace-builder`
2. Type `setup` to describe your domain
3. Walk through the five stages: discovery, mapping, scaffolding, questionnaire design, and validation
4. The output is a complete, ready-to-use workspace

The pattern transfers to any repeatable multi-step workflow: report generation, audit procedures, curriculum development, code documentation, or any process where someone currently does the same sequence of steps with different input material each time.

## The Conventions

Every workspace follows 15 patterns defined in [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md). These are old ideas -- separation of concerns, one-way dependencies, canonical sources, pipe-and-filter architecture -- applied to the specific problem of structuring context for AI agents.

### Architecture

- **Stage contracts** -- Every stage CONTEXT.md has Inputs, Process, and Outputs. Simple enough for anyone to read. Structured enough for an agent to follow.
- **Stage handoffs** -- Output folders connect stages. Edit any output and the next stage picks up your changes.
- **One-way references** -- If A references B, B does not reference A. Prevents circular dependencies and scales linearly.
- **Selective section routing** -- CONTEXT.md tables specify which sections of which files to load. Not the whole file. The section you need.
- **Canonical sources** -- Every piece of information has one home. Other files point there. The moment the same rule exists in two files, they drift.

### Quality

- **Specs are contracts** -- Specification stages define WHAT and WHEN. They do not prescribe HOW. The build stage has creative freedom within the quality floor defined by the design system.
- **Checkpoints** -- Creative stages pause for human steering between steps. The agent completes a unit of work, presents options, and the human redirects before the next unit begins.
- **Stage audits** -- Quality checklists the agent runs after completing a stage but before writing output. Each check has an unambiguous pass condition.
- **Value validation** -- Content stages define what types of value their output delivers. The value is locked before drafting begins.
- **Docs over outputs** -- Reference docs are the authoritative source for how to build. Agents do not read previous outputs to learn patterns. Early outputs are the worst outputs. If future agents learn from them, quality never improves.

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
- **Follows MWP conventions.** The workspace-builder enforces this automatically. See [`_core/CONVENTIONS.md`](_core/CONVENTIONS.md) for the full spec.

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

MWP grew out of a [content production system](https://github.com/RinDig/Content-Agent-Routing-Promptbase) that applies separation of concerns to AI context windows instead of code modules. That system runs a full content operation: scripting, animation specs, Remotion builds, brand management. MWP is the general-purpose version -- the structural patterns extracted so anyone can scaffold their own workflows.

For the academic treatment, see [Model Workspace Protocol: Folder Structure as Agent Architecture](link-to-paper) (Van Clief, 2026).

## License

MIT License. See [LICENSE](LICENSE) for details.
