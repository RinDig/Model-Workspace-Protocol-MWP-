# Course Metadata

This file is a template. The agent fills it in at the start of each new course run by asking the user conversationally. Do NOT put placeholders here -- this is per-course data, not system config.

## How to Use

At the start of Stage 01 (or whichever stage the user enters), collect this info from the user and write a copy to the current stage's output folder as `[course-slug]-meta.md`:

```markdown
# [Course Name]

- **Description:** [one sentence]
- **Target audience:** [who and what level]
- **Session count:** [number, default 8]
- **Session duration:** [minutes, default 45]
- **Slides per session:** 15-25
- **Aspect ratio:** 16:9 (720pt x 405pt)
- **Source material:** [what the user provided for this run]
```

This metadata file travels forward through the pipeline. Each stage reads it from the previous stage's output.
