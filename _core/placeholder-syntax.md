# Placeholder Syntax

How the onboarding system works. Workspaces ship with placeholder variables in their markdown files. The onboarding agent replaces these with real content when a user runs `setup`.

---

## Basic Syntax

Placeholders use double braces and SCREAMING_SNAKE_CASE:

```
{{BRAND_NAME}}
{{TARGET_AUDIENCE}}
{{PRIMARY_COLOR}}
```

These are literal strings in markdown files. They are not code variables. The onboarding agent finds them and replaces them with the user's answers through string substitution.

---

## Replacement Rules

1. The onboarding agent reads `setup/questionnaire.md` for the list of questions
2. Each question maps to one or more placeholders
3. Each question specifies which files contain its placeholder
4. The agent asks the questions conversationally, collecting answers
5. The agent replaces every instance of each placeholder with the corresponding answer
6. After all replacements, the agent scans the entire workspace for any remaining `{{` patterns
7. If any remain, the agent flags them and asks the user for the missing information
8. Onboarding is complete only when zero placeholders remain

---

## Where Placeholders Can Appear

Placeholders can appear in any markdown file within a workspace:
- Brand vault files (voice-rules.md, identity.md)
- Reference files (hook-system.md, design-system.md, etc.)
- Shared files (platform-specs.md)
- Stage CONTEXT.md files (only in Inputs table values, not in routing structure)

Placeholders should NOT appear in:
- CLAUDE.md files (these need to work before onboarding runs)
- Top-level CONTEXT.md routing tables (these need to work before onboarding runs)
- The questionnaire.md itself (the questions are the source, not the target)

---

## Conditional Sections

Conditional sections wrap content that gets removed if the user indicates it is not needed.

Syntax:

```markdown
{{?SECTION_NAME}}

## Section Heading

Content that may or may not be relevant...

{{/SECTION_NAME}}
```

**Rule: Conditional blocks can only wrap entire sections.** A section means a heading and all content below it, up to the next heading of the same or higher level.

Valid:

```markdown
{{?VIDEO_PRODUCTION}}

## Video Production Settings

Resolution, frame rate, and export format for your video pipeline.

- Resolution: 1920x1080
- Frame rate: 30fps
- Export format: MP4

{{/VIDEO_PRODUCTION}}
```

Invalid (do not do this):

```markdown
- Item one
{{?OPTIONAL_ITEM}}
- Item two (optional)
{{/OPTIONAL_ITEM}}
- Item three
```

Invalid (do not do this):

```markdown
The brand voice is {{?FORMAL}}formal and authoritative{{/FORMAL}}
{{?CASUAL}}casual and conversational{{/CASUAL}}.
```

Why this rule exists: removing inline content leaves orphaned list markers, broken sentences, or malformed markdown. Wrapping complete sections means removal always produces clean markdown.

---

## Naming Conventions

Use descriptive names: `{{BRAND_NAME}}` not `{{BN}}`.

Group related placeholders with common prefixes:
- `{{VOICE_DESCRIPTION}}`, `{{VOICE_ADJECTIVES}}`
- `{{PRIMARY_COLOR}}`, `{{SECONDARY_COLOR}}`, `{{ACCENT_COLOR}}`
- `{{CONTENT_PILLAR_1}}`, `{{CONTENT_PILLAR_2}}`

Conditional section names should describe what they wrap:
- `{{?BUILD_STAGE}}` for the build stage section
- `{{?PILLAR_4}}` for the fourth content pillar

---

## Questionnaire Mapping

The `setup/questionnaire.md` file is the bridge between questions and placeholders. Each question entry specifies:

- The question text (what the agent asks the user)
- The placeholder(s) it populates
- The file(s) where those placeholders appear
- The input type (free text, multiple choice, yes/no)
- Optional: follow-up questions for vague answers
- Optional: conditional logic (if answer is X, remove section Y)

See `_core/templates/questionnaire-template.md` for the format.
