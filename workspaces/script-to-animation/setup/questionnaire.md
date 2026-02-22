# Onboarding Questionnaire: Script-to-Animation

Read this file when the user types "setup". Ask ALL questions below in a single conversational pass. The user should be able to answer everything in one message. These configure the production system -- not a specific video. Individual video topics are provided at the start of each pipeline run.

After collecting answers, the agent derives additional fields (voice tone rules, personality markers, anti-patterns, brand positioning, content mission) from the answers and fills them in without a separate confirmation round.

---

### Q1: What is your brand or project name?
- Placeholder: `{{BRAND_NAME}}`
- Files: `brand-vault/identity.md`, `brand-vault/voice-rules.md`, `stages/01-script/references/content-pillars.md`, `stages/01-script/references/script-templates.md`, `stages/01-script/references/hook-system.md`, `stages/02-spec/references/design-system.md`
- Type: free text

### Q2: How should your content sound? (describe your voice and give 2-3 tone adjectives)
- Placeholders: `{{VOICE_DESCRIPTION}}`, `{{VOICE_ADJECTIVES}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text
- Example: "Casual and curious, like thinking out loud. Adjectives: witty, grounded, surprising."
- Agent derives from this answer (no extra questions needed):
  - `{{VOICE_TONE_RULE}}` -- one-sentence writing instruction capturing the voice
  - `{{VOICE_PERSONALITY_MARKERS}}` -- 2-3 personality traits that show up in the writing
  - `{{VOICE_ANTI_PATTERN_1}}`, `{{VOICE_ANTI_PATTERN_DESCRIPTION_1}}` -- the opposite of the described voice

### Q3: Who is your audience, what do they care about, and what do they already know?
- Placeholders: `{{TARGET_AUDIENCE}}`, `{{AUDIENCE_CARES_ABOUT}}`, `{{AUDIENCE_KNOWLEDGE_LEVEL}}`
- Files: `brand-vault/identity.md`, `brand-vault/voice-rules.md`, `stages/01-script/references/content-pillars.md`
- Type: free text
- Example: "Tech-curious millennials who care about building things. They know basics but not deep theory."

### Q4: What does your brand do, in one sentence?
- Placeholder: `{{BRAND_MISSION}}`
- Files: `brand-vault/identity.md`
- Type: free text
- Agent derives from this + Q1 + Q3 (no extra questions needed):
  - `{{BRAND_POSITIONING}}` -- positioning statement
  - `{{CONTENT_MISSION}}` -- per-content goal reframed from brand mission

### Q5: What are your content pillars? (3-5 recurring themes you create around)
- Placeholders: `{{CONTENT_PILLAR_1}}` through `{{CONTENT_PILLAR_5}}`, plus per-pillar: `{{PILLAR_N_ANGLE}}`, `{{PILLAR_N_TOPICS}}`, `{{PILLAR_N_AUDIENCE_FIT}}`, `{{PILLAR_N_TEMPLATE}}`
- Files: `stages/01-script/references/content-pillars.md`
- Type: free text (comma-separated list)
- Example: "AI explainers, creative coding, design systems"
- Agent derives per-pillar details (angle, typical topics, audience fit, default template) from the pillar names + Q3 audience context. If fewer than 4 pillars, remove `{{?PILLAR_4}}` section. If fewer than 5, remove `{{?PILLAR_5}}` section.

### Q6: Default hook style?
- Placeholder: `{{HOOK_STYLE}}`
- Files: `stages/01-script/references/hook-system.md`
- Type: selection
- Options: Ritual Entry (start with a familiar action), Bold Claim (challenge an assumption), Impossible Question (pose a puzzle), Semantic Paradox (combine unlikely concepts), No default (choose per topic)

### Q7: What platform and target duration?
- Placeholders: `{{PRIMARY_PLATFORM}}`, `{{TARGET_DURATION}}`
- Files: `shared/platform-specs.md`, `stages/01-script/CONTEXT.md`
- Type: free text
- Example: "YouTube, 5-8 minutes" or "TikTok/Reels, 30-60 seconds"

### Q8: Brand colors? (primary, secondary, accent, background, text as hex)
- Placeholders: `{{PRIMARY_COLOR}}`, `{{SECONDARY_COLOR}}`, `{{ACCENT_COLOR}}`, `{{BACKGROUND_COLOR}}`, `{{TEXT_COLOR}}`
- Files: `stages/02-spec/references/design-system.md`, `stages/02-spec/references/component-registry.md`, `stages/03-build/references/build-conventions.md`
- Type: free text (hex codes)
- If the user only gives 1-2 colors, fill sensible defaults for the rest.

### Q9: Heading font and body font?
- Placeholders: `{{HEADING_FONT}}`, `{{BODY_FONT}}`
- Files: `stages/02-spec/references/design-system.md`, `stages/02-spec/references/component-registry.md`, `stages/03-build/references/build-conventions.md`
- Type: free text
- Default: Inter for body, bold sans-serif for headings.

### Q10: Do you want the pipeline to generate animation code with Remotion?
- Type: yes/no
- If YES: Keep `stages/03-build/` and `{{?BUILD_STAGE}}` section. Point user to `stages/03-build/references/remotion-setup.md`.
- If NO: Remove `stages/03-build/` folder entirely. Remove `{{?BUILD_STAGE}}...{{/BUILD_STAGE}}` from `CONTEXT.md`.

---

## After Onboarding

After replacing all direct placeholders, derive and fill:
1. Voice tone rule, personality markers, and anti-patterns (from Q2)
2. Brand positioning and content mission (from Q1, Q3, Q4)
3. Per-pillar details: angle, topics, audience fit, template (from Q5 + Q3)

Then scan every `.md` file for remaining `{{` patterns. If any remain, resolve them. Tell the user:

"You are set up. Your production system is configured with [brand name]'s voice, [palette], and [platform]. To make a video, just give me a topic."
