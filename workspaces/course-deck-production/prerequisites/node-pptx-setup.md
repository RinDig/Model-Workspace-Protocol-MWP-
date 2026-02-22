# Node.js + html2pptx Setup

The deck generation pipeline converts HTML slides to PowerPoint using PptxGenJS, rendered by Playwright's headless Chromium browser.

## Prerequisites

- **Node.js 18+** -- JavaScript runtime
- **npm** -- Package manager (comes with Node.js)

## Install Node.js

### Windows
Download from https://nodejs.org (LTS version). The installer includes npm.

### macOS
```bash
brew install node
```

### Linux
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Install npm Packages

From the workspace root (or any working directory where you will run generation):

```bash
npm install pptxgenjs playwright sharp react react-dom react-icons
npx playwright install chromium
```

## Install QA Tools

### LibreOffice (for .pptx to PDF conversion)

- **Windows:** Download from https://www.libreoffice.org/download
- **macOS:** `brew install --cask libreoffice`
- **Linux:** `sudo apt-get install libreoffice`

### Poppler (for PDF to image conversion)

- **Windows:** Download from https://github.com/oswaldobapvicjr/freedesktop-sdk-images or use `choco install poppler`
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt-get install poppler-utils`

## Verify Installation

```bash
node --version          # Should print v18+
npm --version           # Should print 9+
npx playwright --version  # Should print version
soffice --version       # Should print LibreOffice version
pdftoppm -v             # Should print version
```

## How the Workspace Uses These Tools

1. **Stage 04 (Generation):** Runs `node [session].js` which uses html2pptx to convert HTML slide files into .pptx presentations
2. **Stage 05 (QA):** Runs `soffice --headless --convert-to pdf` to render .pptx as PDF, then `pdftoppm` to create slide thumbnail images for visual inspection
