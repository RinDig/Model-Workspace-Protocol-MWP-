# [Workspace Name]

[One sentence: what this workspace does.]

## Folder Map

```
[workspace-name]/
├── CLAUDE.md          (you are here)
├── CONTEXT.md         (start here for task routing)
├── setup/             (onboarding questionnaire)
├── skills/            (bundled Claude skills for domain knowledge)
├── [context-folder]/  (shared context files)
├── stages/
│   ├── 01-[name]/     ([brief description])
│   ├── 02-[name]/     ([brief description])
│   └── 03-[name]/     ([brief description])
└── shared/            (cross-stage reference files)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding questionnaire |
| `status` | Show pipeline completion for all stages |

## Routing

| Task | Go To |
|------|-------|
| [Task type 1] | `stages/01-[name]/CONTEXT.md` |
| [Task type 2] | `stages/02-[name]/CONTEXT.md` |
| [Task type 3] | `stages/03-[name]/CONTEXT.md` |

## What to Load

<!-- Map each task to its minimal file set. Loading more files dilutes quality.
     The context window is working memory, not storage. -->

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| [Task 1] | [minimal file list] | [what to skip and why] |
| [Task 2] | [minimal file list] | [what to skip and why] |

## Stage Handoffs

Each stage writes its output to its own `output/` folder. The next stage reads from there. If you edit an output file, the next stage picks up your edits.
