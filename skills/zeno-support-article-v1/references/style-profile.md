# Zeno Support Centre Style Profile

Use this profile whenever current Zeno support articles are unavailable or do not settle a style question. Current verified public content takes precedence for product terminology and regional spelling.

## Reader and Purpose

- Write for legal professionals who understand their work but may be new to the feature.
- Help the reader accomplish one clear task quickly.
- Assume competence. Explain the product without explaining basic legal practice.
- State what the feature or workflow enables before expanding on detail.

## Voice

- Address the reader as **you**.
- Use present tense and active voice.
- Keep sentences and paragraphs short.
- Use plain, warm, professional language.
- Make Zeno or the user the subject of a sentence when that improves clarity.
- Avoid hype, marketing language, condescension, emojis, exclamation marks, and unsupported promises.
- Match the spelling convention used in current Zeno support content. Do not mix regional spellings within one article.

## Product Terminology

Preserve verified Zeno vocabulary and capitalisation. Established examples include:

- **Legal Research mode**
- **Assistant**
- **Table Review**
- workspace

Bold visible UI elements exactly as they appear in the product. Do not promote a descriptive phrase to a product name or alter capitalisation without evidence.

## Title and Heading Rules

- Use one H1 title in Title Case.
- Start most procedural titles with **How to**.
- Use a noun phrase or **What is [feature]?** for a concept article.
- Use the customer's literal question for an FAQ title.
- Add an optional one-sentence subtitle only when it clarifies the outcome.
- Use H2 headings for main sections.

Conventional headings include:

- `## What is [feature]?`
- `## How to [complete the task]`
- `## Important Points to Note`
- `## Frequently asked questions`
- `## Additional Resources`

Use conventional headings only when they help. Do not add empty or repetitive sections.

## Archetype Skeletons

### How-to Guide

```markdown
# How to [Complete the Task]

[Optional one-sentence subtitle describing the outcome.]

[One short paragraph explaining when to use this workflow.]

## How to [Complete the Task]

1. [Imperative action using **exact UI labels**.]

   [Screenshot: the exact view and state to capture]

2. [Next single action.]

   [Screenshot: the exact view and state to capture]

## Important Points to Note

- [Supported caveat, permission, or limitation.]

## Additional Resources

- [Verified related public article](URL)
```

### Feature Walkthrough or Concept Article

```markdown
# What is [Feature]?

[Optional one-sentence summary.]

## What is [Feature]?

[Direct explanation of the feature and where it appears.]

[Feature] helps you:

- [Supported benefit or capability]
- [Supported benefit or capability]

## How to [Use or Find the Feature]

1. [Imperative action using **exact UI labels**.]

   [Screenshot: the exact view and state to capture]

## Important Points to Note

- [Supported caveat or limitation.]
```

### Short FAQ

```markdown
# [Customer's Literal Question]?

[Direct answer in the first paragraph.]

[Add a short explanation or numbered procedure only when needed.]
```

Add Frequently asked questions or Additional Resources only when they improve the answer.

## Steps and Screenshots

- Use a numbered list for a sequence.
- Begin each step with an imperative verb.
- Keep one main action in each step.
- Bold every exact button, menu, tab, field, mode, and setting label.
- Put examples in parentheses when they improve understanding.
- For a how-to guide, add a screenshot placeholder after almost every step.
- Describe the screen, relevant control, and useful UI state in each placeholder.
- Never imply that a placeholder is a completed screenshot.

## Article Boundaries

Include only the customer-facing article. Do not add:

- an author or publication date;
- breadcrumbs;
- an Intercom Related Articles widget;
- internal Notion or Slack links;
- drafting notes or citations;
- unsupported product behaviour;
- a claim that the article was published.

Keep the staging handoff compatible with the local HTML converter. Use exactly one H1 followed only by H2 headings, plain paragraphs, flat numbered or bullet lists, bold, italics, inline code, verified absolute HTTPS links, and screenshot placeholders. Do not use raw HTML, Markdown images, tables, blockquotes, H3-or-deeper headings, or nested lists.
