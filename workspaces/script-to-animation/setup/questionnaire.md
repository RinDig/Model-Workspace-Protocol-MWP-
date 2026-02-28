# Onboarding Questionnaire: Script-to-Animation

Read this file when the user types "setup". Ask ALL questions below in a single conversational pass. The user should be able to answer everything in one message. These configure the production system, not a specific video. Individual video topics are provided at the start of each pipeline run.

---

### Q1: What is your brand or project name?
- Placeholder: `{{BRAND_NAME}}`
- Files: `brand-vault/identity.md`, `brand-vault/voice-rules.md`, `stages/01-script/references/content-pillars.md`, `stages/01-script/references/script-templates.md`, `stages/01-script/references/hook-system.md`, `stages/02-spec/references/design-system.md`
- Type: free text

### Q2: Give me 2-3 sentences that sound exactly like your brand.
- Placeholders: `{{VOICE_RIGHT_EXAMPLE_1}}`, `{{VOICE_RIGHT_EXAMPLE_2}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text
- Example: "Same story. Three layers of abstraction. Each one harder to copy." / "They spent six months building a custom pipeline. Then the platform added it natively."
- Note: These become the positive examples in the Sentence Rules table.

### Q3: Give me 2-3 sentences your brand would never say.
- Placeholders: `{{VOICE_WRONG_EXAMPLE_1}}`, `{{VOICE_WRONG_EXAMPLE_2}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text
- Example: "The commoditization of basic services has accelerated dramatically." / "In this comprehensive guide, we'll explore the transformative power of..."
- Note: These become the negative examples in the Sentence Rules table.

### Q4: List things that are always errors in your content. Patterns, phrases, or habits to avoid.
- Placeholders: `{{VOICE_HARD_CONSTRAINT_1}}`, `{{VOICE_HARD_CONSTRAINT_2}}`, `{{VOICE_HARD_CONSTRAINT_3}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text
- Example: "Em dashes. Never." / "Rhetorical questions that sound like a documentary narrator." / "More than one 'not X, but Y' structure per script."
- Note: These become the numbered error list in Hard Constraints. If the user gives fewer than 3, agent derives additional constraints from Q2/Q3 examples.

### Q5: How should your content sound? (2-3 adjectives as a supplement)
- Placeholders: `{{VOICE_ADJECTIVES}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text
- Example: "Grounded, curious, direct"
- Note: Supplementary to Q2-Q4. The concrete examples are primary. Adjectives help fill gaps.
- Agent derives from Q2-Q5 combined (no extra questions needed):
  - `{{VOICE_PACING_DESCRIPTION}}` -- rhythm and density description
  - `{{VOICE_ANTI_PATTERN}}`, `{{VOICE_ANTI_PATTERN_DESCRIPTION}}` -- the opposite of the described voice

### Q6: Who is your audience, what do they care about, and what do they already know?
- Placeholders: `{{TARGET_AUDIENCE}}`, `{{AUDIENCE_CARES_ABOUT}}`, `{{AUDIENCE_KNOWLEDGE_LEVEL}}`
- Files: `brand-vault/identity.md`, `brand-vault/voice-rules.md`, `stages/01-script/references/content-pillars.md`
- Type: free text
- Example: "Tech-curious millennials who care about building things. They know basics but not deep theory."

### Q7: What does your brand do, in one sentence?
- Placeholder: `{{BRAND_MISSION}}`
- Files: `brand-vault/identity.md`
- Type: free text
- Agent derives from this + Q1 + Q6 (no extra questions needed):
  - `{{BRAND_POSITIONING}}` -- positioning statement
  - `{{CONTENT_MISSION}}` -- per-content goal reframed from brand mission

### Q8: What are your content pillars? (3-5 recurring themes you create around)
- Placeholders: `{{CONTENT_PILLAR_1}}` through `{{CONTENT_PILLAR_5}}`, plus per-pillar: `{{PILLAR_N_ANGLE}}`, `{{PILLAR_N_TOPICS}}`, `{{PILLAR_N_AUDIENCE_FIT}}`, `{{PILLAR_N_TEMPLATE}}`
- Files: `stages/01-script/references/content-pillars.md`
- Type: free text (comma-separated list)
- Example: "AI explainers, creative coding, design systems"
- Agent derives per-pillar details (angle, typical topics, audience fit, default template) from the pillar names + Q6 audience context. If fewer than 4 pillars, remove `{{?PILLAR_4}}` section. If fewer than 5, remove `{{?PILLAR_5}}` section.

### Q9: What kinds of value does your content typically deliver? (pick at least 2)
- Placeholders: `{{VALUE_NOVEL_DESCRIPTION}}`, `{{VALUE_USABLE_DESCRIPTION}}`, `{{VALUE_QUESTION_DESCRIPTION}}`, `{{VALUE_INTERESTING_DESCRIPTION}}`
- Files: `stages/01-script/references/value-framework.md`
- Type: free text
- Example: "We teach something new (NOVEL) and give a tool or mental model to use immediately (USABLE)."
- Note: Agent fills in descriptions for all four value types, marking which ones the brand leans toward. Any value type the user does not mention still gets a short generic description so the framework stays complete.

### Q10: Default hook style?
- Placeholder: `{{HOOK_STYLE}}`
- Files: `stages/01-script/references/hook-system.md`
- Type: selection
- Options: Ritual Entry (start with a familiar action), Bold Claim (challenge an assumption), Impossible Question (pose a puzzle), Semantic Paradox (combine unlikely concepts), No default (choose per topic)

### Q11: What platform and target duration?
- Placeholders: `{{PRIMARY_PLATFORM}}`, `{{TARGET_DURATION}}`
- Files: `shared/platform-specs.md`, `stages/01-script/CONTEXT.md`
- Type: free text
- Example: "YouTube, 5-8 minutes" or "TikTok/Reels, 30-60 seconds"

### Q12: Brand colors? (primary, secondary, accent, background, text as hex)
- Placeholders: `{{PRIMARY_COLOR}}`, `{{SECONDARY_COLOR}}`, `{{ACCENT_COLOR}}`, `{{BACKGROUND_COLOR}}`, `{{TEXT_COLOR}}`
- Files: `stages/02-spec/references/design-system.md`, `stages/02-spec/references/component-registry.md`, `stages/03-build/references/build-conventions.md`
- Type: free text (hex codes)
- If the user only gives 1-2 colors, fill sensible defaults for the rest.

### Q13: Heading font and body font?
- Placeholders: `{{HEADING_FONT}}`, `{{BODY_FONT}}`
- Files: `stages/02-spec/references/design-system.md`, `stages/02-spec/references/component-registry.md`, `stages/03-build/references/build-conventions.md`
- Type: free text
- Default: Inter for body, bold sans-serif for headings.

### Q14: Do you want the pipeline to generate animation code with Remotion?
- Type: yes/no
- If YES: Keep `stages/03-build/` and `{{?BUILD_STAGE}}` section. Point user to `stages/03-build/references/remotion-setup.md`.
- If NO: Remove `stages/03-build/` folder entirely. Remove `{{?BUILD_STAGE}}...{{/BUILD_STAGE}}` from `CONTEXT.md`.

---

## After Onboarding (Two-Pass Process)

**Pass 1:** Collect all answers above and replace direct placeholders.

**Pass 2 (Voice Review):** After replacing placeholders, present the generated voice rules to the user:

"Here are the voice rules I derived from your examples. Review these and edit anything that does not match how you actually sound:"

Show the populated Hard Constraints, Sentence Rules table, and Pacing section. The user edits before the rules are finalized. This produces better rules than one-shot derivation because the user can catch misinterpretations.

**After both passes:** Derive and fill remaining fields:
1. Pacing description and anti-patterns (from Q2-Q5)
2. Brand positioning and content mission (from Q1, Q6, Q7)
3. Per-pillar details: angle, topics, audience fit, template (from Q8 + Q6)
4. Value framework descriptions (from Q9)

Then scan every `.md` file for remaining `{{` patterns. If any remain, resolve them. Tell the user:

"You are set up. Your production system is configured with [brand name]'s voice, [palette], and [platform]. To make a video, just give me a topic."
