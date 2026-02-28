# [Stage Name]

[One sentence: what this stage does.]

## Inputs

<!-- List every file the agent needs. Be specific about which sections. -->

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../0N-prev/output/artifact.md` | Full file | The artifact to work from |
| Reference | `references/example.md` | "Relevant Section" | What it provides |

## Process

<!-- Numbered steps. Each step is one concrete action. Be specific enough that
     two different agents following these steps would produce structurally similar
     outputs.

     Too vague: "Write the script"
     Good: "Write the full script in one pass, then audit against the voice
            hard constraints and value brief"

     Too vague: "Generate ideas"
     Good: "Propose 3-5 concept angles, each as a single sentence. Tag each
            with its value type and format." -->

1. Read the input artifact from the previous stage
2. [Step two]
3. [Step three]
4. Save to output/

## Checkpoints

<!-- Points where the agent pauses for human input before continuing.
     Not every stage needs checkpoints. Linear stages (extract, render, validate)
     often run straight through. Creative stages (writing, design, ideation)
     benefit from at least one.

     Format: after which process step, what the agent presents, what the human decides.
     Delete this section if the stage runs straight through. -->

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| [step #] | [what options/output to show] | [what direction to choose] |

## Audit

<!-- Quality checks before the output is considered done. The agent runs these
     after completing the process steps. If any check fails, revise before saving.

     Not every stage needs an audit. Data extraction or file conversion stages
     may not benefit. Creative and build stages almost always do.
     Delete this section if no audit applies. -->

| Check | Pass Condition |
|-------|---------------|
| [Check name] | [What "passing" looks like] |

## Outputs

<!-- What this stage produces and where it goes. -->

| Artifact | Location | Format |
|----------|----------|--------|
| [Name] | `output/[slug]-[type].md` | [Description of the format] |

<!-- Target: keep this file under 80 lines. -->
