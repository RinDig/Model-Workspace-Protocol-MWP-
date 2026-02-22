# Onboarding Questionnaire: Course Deck Production

Read this file when the user types "setup". Ask ALL questions below in a single conversational pass. These configure the production system -- not a specific course. Individual course details are collected at the start of each pipeline run.

---

Ask these questions all at once. The user should be able to answer everything in one message.

### Q1: What name or organization should appear on the decks?
- Placeholder: `{{PRODUCER_NAME}}`
- Files: `shared/producer-identity.md`
- Type: free text
- Example: "Dr. Smith", "Acme Training Co.", "Stanford CS Department"

### Q2: Pick a color palette (or bring your own).
- Placeholders: `{{PRIMARY_COLOR}}`, `{{SECONDARY_COLOR}}`, `{{ACCENT_COLOR}}`, `{{BG_COLOR}}`, `{{TEXT_COLOR}}`
- Files: `design-system/palette.md`
- Type: selection or free text
- Options:
  - **Classic Blue:** Primary 1C2833, Secondary 2E4053, Accent 3498DB, BG F4F6F6, Text 2C3E50
  - **Teal & Coral:** Primary 277884, Secondary 5EA8A7, Accent FE4447, BG FFFFFF, Text 2C3E50
  - **Burgundy Luxury:** Primary 5D1D2E, Secondary 951233, Accent 997929, BG FAF7F2, Text 2C3E50
  - **Forest Green:** Primary 1E5128, Secondary 4E9F3D, Accent D4A843, BG FFFFFF, Text 191A19
  - **Custom:** provide five hex values (primary, secondary, accent, background, text)

### Q3: Heading font and body font?
- Placeholders: `{{HEADING_FONT}}`, `{{BODY_FONT}}`
- Files: `design-system/typography.md`
- Type: multiple choice
- Web-safe only: Arial, Georgia, Verdana, Trebuchet MS, Impact, Tahoma, Times New Roman
- Default: Arial / Arial

### Q4: What kind of source material do you typically work from?
- Placeholder: `{{TYPICAL_SOURCES}}`
- Files: `shared/producer-identity.md`
- Type: free text
- Examples: "academic papers and PDFs", "my own lecture notes", "textbook chapters", "mixed -- varies per course"
- Purpose: Helps the agent know which extraction strategies to default to. Does NOT lock you in -- you can provide anything per course.

### Q5: Where do you usually start in the pipeline?
- Placeholder: `{{DEFAULT_START_STAGE}}`
- Files: `shared/producer-identity.md`
- Type: selection
- Options:
  - **From scratch** -- I bring raw material and need everything (Stage 01)
  - **From notes** -- I have organized content, skip extraction (Stage 02)
  - **From a syllabus** -- I already have a curriculum, just need decks (Stage 03)
- Purpose: Sets the default starting point. You can always override per course.

---

## After Onboarding

Tell the user:

"You are set up. Here is your production config:

- **Identity:** [producer name]
- **Design:** [palette name], [heading font] / [body font]
- **Default start:** Stage [01|02|03]

To start a new course, just say what you want to build and provide your source material. I will collect the course details (name, audience, session count) at the start of each run."

Then scan the workspace for any remaining `{{` patterns. If any remain, ask for the missing info.
