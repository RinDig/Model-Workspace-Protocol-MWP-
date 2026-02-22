# Workspace Builder

This workspace guides you through building a new MWP workspace for any domain -- from understanding the workflow through generating a complete, validated workspace scaffold.

## Folder Map

```
workspace-builder/
├── CLAUDE.md              (you are here)
├── CONTEXT.md             (start here for task routing)
├── setup/
│   └── questionnaire.md   (onboarding -- asks about the domain you are building for)
├── stages/
│   ├── 01-discovery/      (understand the domain workflow)
│   ├── 02-mapping/        (formalize stage contracts and dependencies)
│   ├── 03-scaffolding/    (generate the folder tree and files)
│   ├── 04-questionnaire-design/  (build the onboarding questionnaire)
│   └── 05-validation/     (verify against MWP conventions)
└── references/
    ├── conventions-reference.md   (pointer to core MWP conventions)
    └── examples/
        └── script-to-animation-summary.md  (completed workspace example)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding -- asks about the domain you want to build a workspace for |
| `status` | Show pipeline completion for all five stages |

### How `status` works

Scan `stages/*/output/` folders. For each stage, if the output folder contains files (other than .gitkeep), the stage is COMPLETE. Otherwise PENDING. Render:

```
Pipeline Status: workspace-builder

  [01-discovery]  -->  [02-mapping]  -->  [03-scaffolding]  -->  [04-questionnaire]  -->  [05-validation]
      STATUS              STATUS              STATUS                 STATUS                  STATUS
```

## Routing

| Task | Go To |
|------|-------|
| Start building a new workspace | `stages/01-discovery/CONTEXT.md` |
| Formalize stage contracts | `stages/02-mapping/CONTEXT.md` |
| Generate the workspace files | `stages/03-scaffolding/CONTEXT.md` |
| Design the onboarding questionnaire | `stages/04-questionnaire-design/CONTEXT.md` |
| Validate the workspace | `stages/05-validation/CONTEXT.md` |

## Stage Handoffs

Each stage writes its output to its own `output/` folder. The next stage reads from there. If you edit an output file between stages, the next stage picks up your edits.

The typical flow is sequential (01 through 05), but stage 05-validation also reads from stages 03 and 04 directly.
