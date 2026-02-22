# Stage 04: Generation

Build .pptx files from session outlines using the html2pptx pipeline. One JS file per session.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-outline/output/[session-slug]-outline.md` | Full file | Slide content to generate |
| Design system | `../../design-system/CONTEXT.md` | Routes to palette, typography, layout rules | Colors, fonts, spacing values |
| Reference | `../../references/pptx-skill.md` | "Creating a new PowerPoint presentation without a template" section | html2pptx workflow |
| Reference | `../../references/html2pptx-guide.md` | Full file | HTML syntax, PptxGenJS API, chart/table examples |
| Reference | `references/build-conventions.md` | Full file | JS file structure and naming |

## Process

1. Read the session outline
2. Read the pptx skill reference and html2pptx guide in full
3. Load the design system (palette, typography, layout rules)
4. If any slides need gradients or icons, rasterize them to PNG using Sharp first
5. Create one HTML file per slide in `output/[session-slug]/` (720pt x 405pt)
6. Follow all HTML rules: text in `<p>`/`<h1>`-`<h6>`/`<ul>`/`<ol>` only, no `<br>`, no CSS gradients, web-safe fonts only
7. Create one JS file (`output/[session-slug]/[session-slug].js`) that:
   - Creates a PptxGenJS presentation (LAYOUT_16x9)
   - Calls `html2pptx()` for each HTML slide
   - Adds charts/tables to placeholder areas using PptxGenJS API
   - Saves to `output/[session-slug]/[session-slug].pptx`
8. Run `node [session-slug].js` to generate the .pptx
9. Repeat for each session in the curriculum

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Session deck files | `output/[session-slug]/` | Folder: HTML files, JS file, images/, .pptx |
