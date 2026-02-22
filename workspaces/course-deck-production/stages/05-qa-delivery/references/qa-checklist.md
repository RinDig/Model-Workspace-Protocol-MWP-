# QA Checklist

What to inspect when reviewing thumbnail grids or PDF renders of generated decks.

## Critical Issues (must fix)

- [ ] **Text cutoff:** Text visibly cut off by header bars, shapes, or slide edges
- [ ] **Text overflow:** Content extending beyond its container boundaries
- [ ] **Missing text:** Expected content not appearing (likely bare `<div>` or `<span>` without text tags)
- [ ] **Broken layout:** Overlapping elements, misaligned columns, collapsed flex containers
- [ ] **Chart/table overlap:** Data visualizations overlapping with text or other elements
- [ ] **Unreadable text:** Text too small, too light, or insufficient contrast against background

## Warning Issues (should fix)

- [ ] **Inconsistent spacing:** Margins or padding varying between similar slide types
- [ ] **Wrong colors:** Colors not matching the design system palette
- [ ] **Font fallback:** Non-web-safe font caused a substitution
- [ ] **Excessive whitespace:** Large empty areas that could use better content distribution
- [ ] **Bullet alignment:** Bullets at inconsistent indentation levels
- [ ] **Slide count:** Session significantly over or under the 15-25 target

## Design Compliance

- [ ] Header bars use primary color consistently
- [ ] Text colors match design system
- [ ] Font sizes follow the typography hierarchy
- [ ] Charts use the designated chart color palette
- [ ] Section dividers use correct layout pattern
- [ ] First slide matches title-slide pattern
- [ ] Last slide matches end-slide pattern

## Process

For each issue found:

1. Note the session, slide number, and issue type
2. Open the corresponding HTML file in Stage 04 output
3. Fix the CSS/HTML
4. Re-run the JS file
5. Re-generate thumbnails
6. Verify the fix
7. Mark the issue as resolved in the QA report
