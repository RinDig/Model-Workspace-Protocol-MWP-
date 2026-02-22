# Course Deck Production

A production system for building polished PowerPoint decks from unstructured source material. Set up once, run per course.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Extract source content | `stages/01-extraction/CONTEXT.md` | Pull structured teaching points from PDFs, papers, notes |
| Design curriculum | `stages/02-curriculum/CONTEXT.md` | Organize content into modules, sessions, and learning objectives |
| Outline slides | `stages/03-outline/CONTEXT.md` | Create slide-by-slide outlines for each session |
| Generate decks | `stages/04-generation/CONTEXT.md` | Build .pptx files from outlines via html2pptx |
| QA and deliver | `stages/05-qa-delivery/CONTEXT.md` | Visual QA, fix issues, deliver final decks |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Producer identity | `shared/producer-identity.md` | Name/org, typical sources, default start stage |
| Course meta template | `shared/course-meta.md` | Template for per-course metadata (filled each run) |
| Design system | `design-system/CONTEXT.md` | Color palette and typography for all decks |
| Pptx skill | `skills/pptx/SKILL.md` | Full pptx creation workflow, html2pptx guide, scripts, OOXML editing |
| Frontend design skill | `skills/frontend-design/SKILL.md` | Design philosophy, aesthetics, avoiding generic AI look |
