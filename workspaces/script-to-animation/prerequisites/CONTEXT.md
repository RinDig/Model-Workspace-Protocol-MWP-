# Prerequisites

External tools this workspace may need. Not all tools are required -- it depends on which stages you use.

## Tools

| Tool | Required By | Required/Optional | Setup Guide |
|------|-------------|-------------------|-------------|
| Node.js (v18+) | Stage 03: Build | Required if using Remotion | `../stages/03-build/references/remotion-setup.md` |
| Remotion | Stage 03: Build | Optional (skip if animating manually) | `../stages/03-build/references/remotion-setup.md` |

## When to Install

During onboarding (`setup`), the questionnaire asks whether you want the pipeline to generate animation code (Q12). If you answer yes, follow the Remotion setup guide before running Stage 03. If you answer no, Stage 03 is removed and no tools are needed.

Stages 01 (Script) and 02 (Spec) require only Claude Code. No external tools.
