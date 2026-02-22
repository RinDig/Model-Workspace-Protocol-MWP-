# Script-to-Animation

This workspace guides you from a content idea through script writing, animation specification, and build -- one stage at a time.

## Folder Map

```
script-to-animation/
├── CLAUDE.md              (you are here)
├── CONTEXT.md             (start here for task routing)
├── setup/
│   └── questionnaire.md   (onboarding -- run with "setup")
├── skills/                (bundled Claude skills for build and design)
│   ├── remotion-best-practices/  (full Remotion skill: SKILL.md + 35 rule files)
│   └── frontend-design/   (design philosophy and aesthetics: SKILL.md)
├── brand-vault/
│   ├── CONTEXT.md         (routes to voice and identity files)
│   ├── voice-rules.md     (writing voice and tone)
│   └── identity.md        (brand name, audience, positioning)
├── stages/
│   ├── 01-script/         (topic -> finished script)
│   │   ├── CONTEXT.md
│   │   ├── output/
│   │   └── references/    (hook system, templates, pillars)
│   ├── 02-spec/           (script -> animation spec)
│   │   ├── CONTEXT.md
│   │   ├── output/
│   │   └── references/    (spec format, components, design system)
│   └── 03-build/          (spec -> Remotion code)
│       ├── CONTEXT.md
│       ├── output/
│       └── references/    (build conventions)
└── shared/
    └── platform-specs.md  (resolution, duration, format per platform)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding questionnaire -- configures brand, voice, audience, platform |
| `status` | Show pipeline completion for all three stages |

### How `status` works

Scan `stages/*/output/` folders. For each stage, if the output folder contains files (other than .gitkeep), the stage is COMPLETE. Otherwise it is PENDING. Render:

```
Pipeline Status: script-to-animation

  [01-script]  ------>  [02-spec]  ------>  [03-build]
     STATUS               STATUS              STATUS
  (files...)            (files...)           (files...)
```

## Routing

| Task | Go To |
|------|-------|
| Write a script | `stages/01-script/CONTEXT.md` |
| Create an animation spec | `stages/02-spec/CONTEXT.md` |
| Build Remotion code | `stages/03-build/CONTEXT.md` |
| Configure this workspace | `setup/questionnaire.md` |

## Stage Handoffs

Each stage writes its output to its own `output/` folder. The next stage reads from there. If you edit an output file between stages, the next stage picks up your edits. This is the primary way to steer the pipeline.
