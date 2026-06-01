# Onboarding Questionnaire: Workspace Builder

Read this file when the user types "setup". Ask ALL questions below in a single conversational pass. The user should be able to answer everything in one message. These answers inform the discovery conversation in Stage 01 -- they are not placeholder replacements.

Before you ask, read [`/_core/principles.md`](../../../_core/principles.md). The three principles there are what these questions are reaching for. Questions 5 through 7 each map to one principle and feed directly into Stage 01.

---

### Q1: What domain is this workspace for?
- Examples: "podcast production", "blog writing", "course creation", "design system management"
- Type: free text
- Purpose: Names the workspace and sets the scope.

### Q2: Describe the end-to-end workflow in one sentence.
- Examples: "Take a topic idea through research, outlining, drafting, and editing to produce a published blog post."
- Type: free text
- Purpose: Gives Stage 01 a starting point for deeper discovery.

### Q3: Who will use this workspace, and what is their skill level with AI tools?
- Type: free text
- Purpose: Calibrates complexity. Include what tools they already use if relevant.

### Q4: Roughly how many stages, and are any skippable?
- Type: free text (a number or brief list, plus which stages are optional)
- Purpose: Helps Stage 01 ask the right depth of questions.
- Note: This is an estimate. The actual stages will be refined during discovery.

### Q5: Have you actually run this workflow end to end at least once? (Principle 3)
- Type: selection
- Options: "Never (concept only)", "Once or twice (rough experience)", "Many times (deep scars)"
- Purpose: Calibrates how strong the Audit sections should be in the generated workspace.
  - Never -> Audits start minimal with a note "expand after first runs"; the builder does not invent checks.
  - Once or twice -> Audits include the few real failures the user names.
  - Many times -> Audits are full and specific; the builder presses for concrete incidents.
- Why this matters: Audits invented from imagination are decorative. Audits earned from real failures prevent reshipping the same mistake. See [`/_core/principles.md`](../../../_core/principles.md) Principle 3.

### Q6: For each rough stage, what is mechanical and what is judgment? (Principle 2)
- Examples:
  - Mechanical (could a script do it): extracting a delimited block from a file, computing a checksum, transcribing audio, calculating frame counts.
  - Judgment (needs taste): writing the next line, choosing which finding to ship, naming the angle, picking the right hook.
- Type: free text (one or two bullets per rough stage)
- Purpose: Decides what becomes a `skills/[name]/scripts/` candidate vs what stays in dialogue as Process steps and Checkpoints. The builder will not put judgment work in a script, and will not leave mechanical work in dialogue.
- Test the user can apply: "Could a Python function do this reliably given the inputs?" If yes, mechanical. If no, judgment. See Principle 2.

### Q7: Where in the flow do you want to stop and look at the work before continuing? (Principle 1)
- Examples:
  - "After research, before writing: I want to see the source list and the angle."
  - "After the first draft, before audio generation: I want to hear it in my head before spending API credits."
  - "After every stage, frankly."
- Type: free text (named moments)
- Purpose: Defines explicit Checkpoint table entries in the generated stage CONTEXT.md files. The builder will not invent checkpoints the user did not name.
- Why this matters: Dialogue is the control mechanism. Checkpoints are where the human steers. They belong where the human actually wants to look, not where the framework thinks they should be. See Principle 1.

---

## After Onboarding

Tell the user: "Got it. When you are ready, start with Stage 01 -- Discovery. I will walk you through a deeper conversation to map out the full workflow. Your answers to Q5 through Q7 are already loaded; Stage 01 builds on them."

Then point them to `stages/01-discovery/CONTEXT.md`.
