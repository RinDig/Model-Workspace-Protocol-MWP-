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

## Clone the claude-office-skills Repository

The html2pptx library (which converts HTML slides to PowerPoint) is not available as an npm package. It lives in the claude-office-skills repo.

```bash
git clone https://github.com/tfriedel/claude-office-skills.git
```

This gives you:
- `claude-office-skills/html2pptx-local.cjs` -- the html2pptx conversion library
- `claude-office-skills/public/pptx/scripts/` -- thumbnail, inventory, replace, and rearrange utilities

## Install npm Packages

From the claude-office-skills directory (it has the package.json with correct dependencies):

```bash
cd claude-office-skills
npm install
npx playwright install chromium
```

Or from any other working directory:

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
