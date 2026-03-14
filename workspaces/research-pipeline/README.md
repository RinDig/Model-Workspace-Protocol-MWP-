# Research Pipeline

 A configurable research workspace that transforms any input into structured deliverables.

## Quick Start

1. **Setup**: Type `setup` to configure your research preferences
2. **Run**: Type `research [topic]` to start a full pipeline run
3. **Status**: Type `status` to check pipeline completion

## Pipeline Stages

| Stage | Purpose | Output |
|-------|---------|--------|
| 01-scoping | Define goal, questions, methodology | `research-goal.md` |
| 02-discovery | Gather sources with credibility scores | `sources-collected.md` |
| 03-analysis | Extract findings, patterns, contradictions | `findings-analyzed.md` |
| 04-synthesis | Combine into conclusions | `knowledge-synthesized.md` |
| 05-output | Format final deliverable | `report-YYYY-MM-DD-slug.md` |

## Features
- **Placeholder-based onboarding**: Customize via `brand-vault.md`
- **Credibility scoring**: Systematic source evaluation
- **Quality gates**: Human checkpoints between stages
- **Multiple output formats**: Report, dataset, or documentation

## File Structure
```
research-pipeline/
├── CLAUDE.md          # AI instructions (start here)
├── CONTEXT.md         # Task routing
├── brand-vault.md     # Research preferences
├── stages/            # Pipeline stages
├── skills/            # Bundled AI skills
└── setup/             # Onboarding questionnaire
```

## Part of Model Workspace Protocol

Built for the [Interpreted Context Methodology](https://github.com/RinDig/Interpreted-Context-Methdology).
