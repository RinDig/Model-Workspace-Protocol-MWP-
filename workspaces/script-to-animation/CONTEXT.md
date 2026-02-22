# Script-to-Animation Workspace

Take a content idea through script writing, animation specification, and build.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Write a new script | `stages/01-script/CONTEXT.md` | Takes a topic and produces a finished script |
| Create animation spec | `stages/02-spec/CONTEXT.md` | Takes a script and produces beat-by-beat visual spec |
| Build animation code | `stages/03-build/CONTEXT.md` | Takes a spec and produces Remotion components |

{{?BUILD_STAGE}}

### Build Stage

The build stage (03-build) converts specs into Remotion component code. If your workflow does not include code generation, this stage can be removed during onboarding.

{{/BUILD_STAGE}}

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Brand context | `brand-vault/CONTEXT.md` | Routes to voice rules and brand identity |
| Platform specs | `shared/platform-specs.md` | Resolution, duration, format per platform |
| Remotion skill | `skills/remotion-best-practices/SKILL.md` | Full Remotion API reference, 35 rule files with code examples |
| Frontend design skill | `skills/frontend-design/SKILL.md` | Design philosophy, aesthetics, avoiding generic AI look |
