# Stage 01: Script Writing

Take a topic or content idea and produce a finished script ready for animation spec work.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | Topic or content idea | The starting point |
| Brand vault | `../../brand-vault/voice-rules.md` | "Voice Rules" through "What the Voice Is NOT" | Tone guidance for writing |
| Brand vault | `../../brand-vault/identity.md` | "One-Sentence Brand" and "Audience" | Know who you are writing for |
| Reference | `references/hook-system.md` | Full file | Hook patterns and examples |
| Reference | `references/script-templates.md` | Full file | Structural templates for content types |
| Reference | `references/content-pillars.md` | Relevant pillar section only | Topic context and angle |
| Shared | `../../shared/platform-specs.md` | Platform matching {{PRIMARY_PLATFORM}} | Duration and format constraints |

## Process

1. Identify which content pillar this topic falls under
2. Select a hook pattern from the hook system
3. Choose a script template based on content type
4. Write the script following voice rules
5. Check against platform specs for length and format
6. Add the metadata header (pillar, hook type, template, duration, platform)
7. Save to output/

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Finished script | `output/[topic-slug]-script.md` | Markdown with metadata header and script body |

The finished script in `output/` is the human edit surface. Open it, rewrite lines, adjust the hook, change timing notes. Stage 02 reads whatever is in that file.
