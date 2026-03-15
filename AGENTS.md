# Model Workspace Protocol

MWP is a framework for building structured, multi-stage AI workflows out of markdown files and folder conventions. Each workspace gives AI agents the right context at each stage of a task, and gives humans clear edit surfaces between stages.

## Folder Map

```
model-workspace-protocol/
├── AGENTS.md                          (you are here)
├── CLAUDE.md                          (Claude Code entrypoint)
├── README.md                          (project overview)
├── LICENSE
├── _core/                             (shared conventions and templates)
│   ├── CONVENTIONS.md                 (source of truth for all patterns)
│   ├── placeholder-syntax.md          (how {{VARIABLES}} work)
│   └── templates/                     (blank starting points for new workspaces)
└── workspaces/
    ├── script-to-animation/           (content idea -> animated video)
    ├── course-deck-production/        (unstructured material -> course PowerPoints)
    └── workspace-builder/             (builds new MWP workspaces)
```

## Routing

| You want to... | Go to |
|-----------------|-------|
| Create content with script-to-animation | `workspaces/script-to-animation/AGENTS.md` |
| Build course slide decks from source material | `workspaces/course-deck-production/AGENTS.md` |
| Build a new workspace for any domain | `workspaces/workspace-builder/AGENTS.md` |
| Read the full MWP specification | `/_core/CONVENTIONS.md` |
| Understand the placeholder system | `/_core/placeholder-syntax.md` |
| Use a template for a new workspace | `/_core/templates/` |

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding in whatever workspace you are in |
| `status` | Show pipeline completion for the current workspace |

## How It Works

Each workspace is self-contained with its own `AGENTS.md` and `CLAUDE.md`. Use the file that matches your runtime, then follow its routing table into `CONTEXT.md` and the stage contracts.
