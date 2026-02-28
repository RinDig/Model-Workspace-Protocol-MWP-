# Onboarding Questionnaire

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions
     in a single conversational pass. The user should be able to answer everything in one
     message. Collect answers. Replace placeholders across the specified files. After all
     replacements, verify no {{PLACEHOLDER}} patterns remain in the workspace. -->

<!-- Questionnaire design rules:
     1. FLAT STRUCTURE: No category groupings. Just a numbered list of questions.
     2. ALL AT ONCE: Every question appears in one pass. The user answers in one message.
     3. SYSTEM-LEVEL ONLY: Questions configure the production system, not a specific run.
        Per-run details (project name, topic, audience) are collected conversationally
        at the start of each pipeline run by the entry stage.
     4. DERIVE, DON'T ASK: If a field can be derived from other answers, the agent fills
        it in without asking. List derived fields under the question they depend on.
     5. SENSIBLE DEFAULTS: Every question should have a default or example so the user
        can skip what they don't care about.
     6. ASK ONCE, NEVER AGAIN: After setup, the user should never be asked these questions
        again. The answers are baked into the workspace files permanently.
     7. EXAMPLES OVER DESCRIPTIONS: For voice/style questions, ask for concrete examples
        (sentences that sound right, sentences that sound wrong, specific error patterns)
        rather than abstract descriptions. Examples are pattern-matchable. Descriptions
        require interpretation and produce weaker constraints. -->

### Q1: [Question text]
- Placeholder: `{{PLACEHOLDER_NAME}}`
- Files: `path/to/file1.md`, `path/to/file2.md`
- Type: free text
- Default: [Default value if user wants to skip]

### Q2: [Question text]
- Placeholder: `{{PLACEHOLDER_NAME}}`
- Files: `path/to/file.md`
- Type: selection
- Options: Option A, Option B, Option C

### Q3: [Question about an optional feature -- yes/no]
- Type: yes/no
- If NO: Remove `stages/0N-name/` entirely
- If YES: Keep it

---

## After Onboarding

[Tell the user what was configured and where to start.]

After all replacements, scan the entire workspace for remaining `{{` patterns. If any remain, ask for the missing info.
