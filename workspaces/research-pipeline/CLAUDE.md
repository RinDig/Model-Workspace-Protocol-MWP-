# Research Pipeline

A configurable, general-purpose research workflow that transforms any starting input into structured deliverables.

## Folder Map

```
research-pipeline/
├── CLAUDE.md              (you are here)
├── CONTEXT.md             (start here for task routing)
├── PROGRESS.md            (session state)
├── QUALITY-GATES.md       (inter-stage verification)
├── brand-vault.md         (research style and quality preferences)
├── setup/                 (onboarding questionnaire)
├── skills/                (bundled Claude skills)
│   ├── mcp-search-tools/  (web search capability)
│   └── prompt-injection-defense/ (security)
├── stages/
│   ├── 01-scoping/        (define goal and methodology)
│   ├── 02-discovery/      (gather information)
│   ├── 03-analysis/       (process and extract insights)
│   ├── 04-synthesis/      (combine and conclude)
│   └── 05-output/         (generate deliverable)
├── shared/                (cross-stage reference files)
└── archive/               (research outputs by quality)
    ├── high-value/        (exceptional quality)
    ├── reviewed/          (acceptable quality)
    └── rejected/          (below threshold)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `research [topic]` | Run full pipeline from scoping through output |
| `setup` | Run onboarding questionnaire |
| `status` | Show pipeline completion for all stages |
| `resume` | Read PROGRESS.md and continue from last checkpoint |

## Routing

| Task | Go To |
|------|-------|
| Define research scope and methodology | `stages/01-scoping/CONTEXT.md` |
| Gather information from sources | `stages/02-discovery/CONTEXT.md` |
| Process and analyze findings | `stages/03-analysis/CONTEXT.md` |
| Synthesize conclusions | `stages/04-synthesis/CONTEXT.md` |
| Generate final deliverable | `stages/05-output/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Scope research | `stages/01-scoping/CONTEXT.md`, `brand-vault.md`, `shared/methodology-guide.md` | stages 02-05 |
| Gather sources | `stages/02-discovery/CONTEXT.md`, `01-scoping/output/`, `skills/mcp-search-tools/SKILL.md` | stages 03-05, brand-vault |
| Analyze findings | `stages/03-analysis/CONTEXT.md`, `02-discovery/output/`, `01-scoping/output/` | stages 04-05, skills |
| Synthesize | `stages/04-synthesis/CONTEXT.md`, `03-analysis/output/`, `brand-vault.md` | stages 01-02, 05, skills |
| Generate output | `stages/05-output/CONTEXT.md`, `04-synthesis/output/`, `brand-vault.md` | stages 01-03, skills |

## Stage Handoffs

Each stage writes its output to its own `output/` folder. The next stage reads from there. If you edit an output file, the next stage picks up your edits.

**Full pipeline flow:**
01-scoping → 02-discovery → 03-analysis → 04-synthesis → 05-output

You can pause between any stage to review or edit.

## Ownership Protocol

> **Own the whole system. No artificial boundaries.**

- **All bugs are your responsibility** - No issue is "separate" or "out of scope" without approval
- **Verify before assuming** - Never say "this existed before" without checking
- **Fix before declaring done** - A bug found during testing MUST be fixed before claiming completion
- **Test end-to-end** - "Done" means the system works, not just that code was written

**Red Flags (self-catch):**
- "That's a separate issue" → NO IT ISN'T
- "This existed before my changes" → DID YOU VERIFY?
- "Out of scope" → WHOSE SCOPE? MINE.
- "Someone else's problem" → WHO? NO ONE? THEN MINE.

## Direct Action Rule

Before building any script/abstraction:

1. Do the task directly once
2. If repeating, ask: "Is this actually repetitive or imagined?"
3. Only abstract after **3+ real repetitions observed**
4. Default: Just do the work

## Git Setup

Each workspace is an independent git repository. After creating a new workspace:

```bash
cd workspaces/research-pipeline
git init
git add .
git commit -m "Initialize research-pipeline workspace"
```


