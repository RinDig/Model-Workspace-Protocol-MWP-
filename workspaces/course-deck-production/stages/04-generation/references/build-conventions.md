# Build Conventions

How to structure the JS file and HTML files for each session deck.

## File Naming

```
output/
└── session-01-intro/
    ├── slide-01-title.html
    ├── slide-02-overview.html
    ├── slide-03-concepts.html
    ├── ...
    ├── images/
    │   ├── gradient-bg.png
    │   └── icon-check.png
    ├── session-01-intro.js
    └── session-01-intro.pptx
```

- Session folders: `[session-slug]/` matching the outline file name
- HTML files: `slide-[NN]-[short-name].html` (zero-padded, two digits)
- Images: all rasterized PNGs go in `images/` subfolder
- JS file: same name as session folder
- Output pptx: same name as session folder

## JS File Structure

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('[path-to-html2pptx]');
const sharp = require('sharp');

async function build() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = '[INSTRUCTOR_NAME]';
    pptx.title = '[SESSION_TITLE]';

    // Step 1: Rasterize any gradients or icons
    // await createGradient(...);
    // await rasterizeIcon(...);

    // Step 2: Convert HTML slides to PowerPoint
    await html2pptx('slide-01-title.html', pptx);
    const { slide: s2, placeholders: p2 } = await html2pptx('slide-02-data.html', pptx);

    // Step 3: Add charts/tables to placeholder areas
    if (p2.length > 0) {
        s2.addChart(pptx.charts.BAR, chartData, { ...p2[0] });
    }

    // Step 4: Save
    await pptx.writeFile({ fileName: '[session-slug].pptx' });
    console.log('Done');
}

build().catch(console.error);
```

## HTML Template

Every HTML slide starts from this base:

```html
<!DOCTYPE html>
<html>
<head>
<style>
html { background: #ffffff; }
body {
    width: 720pt; height: 405pt; margin: 0; padding: 0;
    font-family: [BODY_FONT], Arial, sans-serif;
    display: flex;
}
</style>
</head>
<body>
<!-- Slide content here -->
</body>
</html>
```

## Checklist Before Running

- [ ] All text is inside `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>`
- [ ] No `<br>` tags anywhere
- [ ] No CSS gradients (all gradients are PNG images)
- [ ] No manual bullet symbols
- [ ] All fonts are web-safe
- [ ] Hex colors in PptxGenJS do NOT have `#` prefix
- [ ] Chart/table areas use `class="placeholder"`
- [ ] Body dimensions match: 720pt x 405pt
