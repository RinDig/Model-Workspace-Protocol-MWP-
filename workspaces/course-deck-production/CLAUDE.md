# Course Deck Production

A production system for turning unstructured source material (PDFs, papers, notes, scripts) into polished PowerPoint slide decks. Run `setup` once to configure your identity and design. Then start a new course anytime -- just provide source material and a topic.

## Folder Map

```
course-deck-production/
├── CLAUDE.md              (you are here)
├── CONTEXT.md             (start here for task routing)
├── setup/
│   └── questionnaire.md   (one-time onboarding -- identity and design)
├── prerequisites/
│   ├── CONTEXT.md         (tool requirements)
│   └── node-pptx-setup.md (Node.js + html2pptx setup guide)
├── design-system/         (colors, typography, layout rules)
│   ├── CONTEXT.md
│   ├── palette.md
│   ├── typography.md
│   └── layout-rules.md
├── references/            (pptx skill docs from claude-office-skills)
│   ├── CONTEXT.md
│   ├── pptx-skill.md
│   └── html2pptx-guide.md
├── shared/
│   ├── producer-identity.md  (who you are -- set during setup)
│   └── course-meta.md        (template for per-course metadata)
├── stages/
│   ├── 01-extraction/     (source material to structured content)
│   ├── 02-curriculum/     (structured content to course plan)
│   ├── 03-outline/        (course plan to slide-by-slide outlines)
│   ├── 04-generation/     (outlines to .pptx via html2pptx)
│   └── 05-qa-delivery/    (visual QA, fix, deliver)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run one-time onboarding -- configures identity, design system, default workflow |
| `status` | Show pipeline completion for all five stages |

### How `status` works

Scan `stages/*/output/` folders. For each stage, if the output folder contains files (other than .gitkeep), the stage is COMPLETE. Otherwise PENDING. Render:

```
Pipeline Status: course-deck-production

  [01-extraction]  -->  [02-curriculum]  -->  [03-outline]  -->  [04-generation]  -->  [05-qa-delivery]
      STATUS               STATUS               STATUS              STATUS               STATUS
```

## Starting a New Course

Each course is a new run through the pipeline. Provide source material and a topic. The agent collects course details (name, audience, session count) conversationally at the start of whichever stage you enter, and writes a `[course-slug]-meta.md` to that stage's output. This metadata travels forward through the pipeline.

Your default starting stage is set during setup (see `shared/producer-identity.md`). You can always override per course.

To start a fresh run, clear the output folders from the previous course.

## Routing

| Task | Go To |
|------|-------|
| Extract content from source material | `stages/01-extraction/CONTEXT.md` |
| Design the course curriculum | `stages/02-curriculum/CONTEXT.md` |
| Create slide outlines for sessions | `stages/03-outline/CONTEXT.md` |
| Generate PowerPoint decks | `stages/04-generation/CONTEXT.md` |
| Run visual QA and deliver | `stages/05-qa-delivery/CONTEXT.md` |

## Stage Handoffs

Each stage writes its output to its own `output/` folder. The next stage reads from there. If you edit an output file between stages, the next stage picks up your edits.

The typical flow is sequential (01 through 05). Users can enter at any stage depending on what they already have.
