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

- **Tool prerequisites**: If stages need external tools, create a prerequisites/ folder with a CONTEXT.md listing all tools and setup guides for each. See "Pattern 7: Tool Prerequisites" in `/_core/CONVENTIONS.md`.

- **Placeholder syntax**: `{{SCREAMING_SNAKE_CASE}}` for variables. `{{?SECTION}}...{{/SECTION}}` for conditional blocks (whole sections only). See `/_core/placeholder-syntax.md`.

- **Quality rules**: CONTEXT.md under 80 lines, reference files under 200 lines, no em dashes, lowercase-with-hyphens naming.
