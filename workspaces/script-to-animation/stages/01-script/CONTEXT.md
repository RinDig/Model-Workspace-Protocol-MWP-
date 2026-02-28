# Stage 01: Script Writing

Take a topic or content idea and produce a finished script ready for animation spec work.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | Topic or content idea | The starting point |
| Brand vault | `../../brand-vault/voice-rules.md` | "Hard Constraints" through "What the Voice Is NOT" | Tone guidance for writing |
| Brand vault | `../../brand-vault/identity.md` | "One-Sentence Brand" and "Audience" | Know who you are writing for |
| Reference | `references/hook-system.md` | Full file | Hook patterns and examples |
| Reference | `references/script-templates.md` | Full file | Structural templates for content types |
| Reference | `references/content-pillars.md` | Relevant pillar section only | Topic context and angle |
| Reference | `references/value-framework.md` | Full file | Value types for content validation |
| Shared | `../../shared/platform-specs.md` | Platform matching {{PRIMARY_PLATFORM}} | Duration and format constraints |

## Process

1. Identify which content pillar this topic falls under
2. Propose 3-5 concept angles, each as a single sentence a viewer could repeat to a friend. For each angle, tag which value types it naturally hits and which format it leans toward
3. **[Checkpoint 1]** -- Present angles to the human for selection
4. Take the selected angle and propose a value brief: the concept, which value slots this piece will fill (minimum 2) with specifics for each, the format, the hook in one sentence, and the close in one sentence
5. **[Checkpoint 2]** -- Present value brief to the human for confirmation
6. Write the full script in one pass following voice rules, audience constraints, and the value brief
7. Run the audit checks below. If any fail, revise before saving
8. Add the metadata header (pillar, hook type, template, value slots, duration, platform)
9. Save to output/

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | 3-5 concept angles, each as one sentence with value slot tags and format | Which angle to pursue, modify, combine, or redirect |
| 4 | Value brief: concept + value slots filled with specifics + format + hook + close | Confirm value direction before drafting begins |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Voice constraints | Zero violations of hard constraints from voice-rules.md |
| Value delivery | Script delivers on the value slots locked in the value brief |
| Hook timing | The belief gap or tension lands within 2-3 seconds |
| Close quality | Last line is something someone could say to a friend |
| Retention beats | No gap longer than 5 seconds without a tagged beat (Recognition, Surprise, Stack, Reversal, New Voice, Reframe, Implication) |
| Share test | Someone who learned this 5 minutes ago would feel confident sharing it |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Finished script | `output/[topic-slug]-script.md` | Markdown with metadata header and script body |

The finished script in `output/` is the human edit surface. Open it, rewrite lines, adjust the hook, change timing notes. Stage 02 reads whatever is in that file.
