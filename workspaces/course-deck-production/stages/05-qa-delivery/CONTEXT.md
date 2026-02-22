# Stage 05: QA and Delivery

Visually validate generated decks, fix issues, and package for delivery.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../04-generation/output/[session-slug]/` | .pptx files and JS source | Decks to validate and fix |
| Design system | `../../design-system/CONTEXT.md` | Routes to palette, layout rules | Check design compliance |
| Reference | `../../references/pptx-skill.md` | "Creating Thumbnail Grids" and "Converting Slides to Images" sections | Thumbnail generation commands |
| Reference | `references/qa-checklist.md` | Full file | What to inspect for |

## Process

1. For each session .pptx:
   a. Generate thumbnail grid: `python scripts/thumbnail.py [session].pptx [session]-thumbnails`
   b. Or convert to PDF + images: `soffice --headless --convert-to pdf [session].pptx` then `pdftoppm -jpeg -r 150 [session].pdf slide`
2. Read and inspect every thumbnail for issues (see qa-checklist.md)
3. If issues found:
   a. Fix the HTML source file for the broken slide
   b. Re-run the JS file: `node [session].js`
   c. Re-generate thumbnails
   d. Repeat until clean
4. Collect all passing .pptx files into `output/final/`
5. Write the delivery manifest and QA report
6. Present final decks to user for approval

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| QA report | `output/qa-report.md` | Pass/fail per session, issues found and fixed |
| Final decks | `output/final/` | All validated .pptx files |
| Delivery manifest | `output/delivery-manifest.md` | Session list with slide counts and file sizes |
