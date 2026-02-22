# Stage 01: Discovery

Understand the domain workflow through conversation with the user.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | Full workflow description | The domain to build a workspace for |
| Reference | `../../references/conventions-reference.md` | Full file | Know the MWP patterns to discover toward |
| Reference | `../../references/examples/script-to-animation-summary.md` | Full file | Concrete example of a completed workspace |

## Process

1. Ask the user to describe their workflow end to end. What do they start with? What do they end with?
2. Identify the distinct stages. Where does one task end and another begin? Look for natural handoff points where a human might want to review or edit before continuing.
3. For each stage, ask:
   - What goes in? (files, user input, previous stage output)
   - What comes out? (the artifact this stage produces)
   - What does the agent need to know? (reference material, rules, constraints)
4. Identify shared context. What information is used across multiple stages? (brand voice, design system, audience data)
5. Identify user-specific details. What varies from one user to another? (brand name, colors, audience, platform). These become placeholder variables.
6. Identify optional stages. Are there stages some users might skip? These become conditional sections.
7. Identify tool prerequisites. For each stage, ask: does this stage need any external tools to work? (e.g., Remotion for video code, ffmpeg for rendering, Python for data processing, a specific npm package, a CLI tool). For each tool, note: which stage needs it, whether it is required or optional, and what it does. These become setup guides in the generated workspace.
8. Write the workflow map summarizing everything discovered.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Workflow map | `output/workflow-map.md` | Structured doc: stages with inputs/outputs, shared context, user-specific variables, optional stages, tool prerequisites |
