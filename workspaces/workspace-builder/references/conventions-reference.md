# MWP Conventions Reference

The canonical MWP conventions live at `/_core/CONVENTIONS.md`. Read that file for the full specification.

This file is a pointer, not a copy. Do not duplicate content from CONVENTIONS.md here.

## Quick Reference

The most important conventions for building a new workspace:

- **Four-layer routing**: CLAUDE.md (Layer 0) -> CONTEXT.md (Layer 1) -> Stage CONTEXT.md (Layer 2) -> Content files (Layer 3). See "Four-Layer Routing Architecture" in `/_core/CONVENTIONS.md`.

- **Stage contracts**: Every stage CONTEXT.md has Inputs, Process, Outputs sections. No exceptions. See "Pattern 1: Stage Contracts" in `/_core/CONVENTIONS.md`.

- **Stage handoffs**: Output folders connect stages. Stage N writes to output/, Stage N+1 reads from there. See "Pattern 2: Stage Handoffs" in `/_core/CONVENTIONS.md`.

- **One-way references**: If A references B, B must not reference A. See "Pattern 3: One-Way Cross-References" in `/_core/CONVENTIONS.md`.

- **Selective loading**: CONTEXT.md tables specify sections within files, not just filenames. See "Pattern 4: Selective Section Routing" in `/_core/CONVENTIONS.md`.

- **One canonical home**: Every piece of information lives in one place. Other files point there. See "Pattern 5: Canonical Sources" in `/_core/CONVENTIONS.md`.

- **CONTEXT.md = routing only**: No definitions, rules, or extended content in CONTEXT.md files. See "Pattern 6: CONTEXT.md = Routing, Not Content" in `/_core/CONVENTIONS.md`.

- **Tool prerequisites**: If stages need system-level tools (Node.js, Python, LibreOffice), write setup guides in the relevant stage's references/ folder. See "Pattern 7: Tool Prerequisites" in `/_core/CONVENTIONS.md`.

- **Bundled skills**: Copy relevant Claude Code skills into skills/ folder. Skills provide domain knowledge (APIs, best practices, code examples) and can replace custom reference docs. Discover local skills and search GitHub during Stage 01. See "Pattern 9: Bundled Skills" in `/_core/CONVENTIONS.md`.

- **Specs are contracts**: Specification stages define WHAT and WHEN, not HOW. No component names, frame numbers, or prop definitions in specs. The build stage has creative freedom within the quality floor. See "Pattern 10: Specs Are Contracts" in `/_core/CONVENTIONS.md`.

- **Checkpoints**: Creative stages should pause for human steering between process steps. Agent completes a unit of work, presents options, human redirects. See "Pattern 11: Checkpoints" in `/_core/CONVENTIONS.md`.

- **Stage audits**: Creative and build stages include a quality checklist the agent runs before writing to output/. Each check has an unambiguous pass condition. See "Pattern 12: Stage Audits" in `/_core/CONVENTIONS.md`.

- **Value validation**: Content-producing stages define value types and lock which ones each piece will deliver before drafting begins. See "Pattern 13: Value Validation" in `/_core/CONVENTIONS.md`.

- **Docs over outputs**: Reference docs are the authoritative source for how to build. Agents do not read other output/ files to learn patterns. See "Pattern 14: Docs Over Outputs" in `/_core/CONVENTIONS.md`.

- **Shared constants**: Code-producing workspaces define shared constant files (colors, fonts, timing) that all outputs import from. See "Pattern 15: Shared Constants" in `/_core/CONVENTIONS.md`.

- **Placeholder syntax**: `{{SCREAMING_SNAKE_CASE}}` for variables. `{{?SECTION}}...{{/SECTION}}` for conditional blocks (whole sections only). See `/_core/placeholder-syntax.md`.

- **Quality rules**: CONTEXT.md under 80 lines, reference files under 200 lines, no em dashes, lowercase-with-hyphens naming.
