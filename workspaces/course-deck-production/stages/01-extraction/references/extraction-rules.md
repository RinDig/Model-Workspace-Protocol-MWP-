# Extraction Rules

How to pull structured teaching content from unstructured source material.

## Chunk Types

| Type | Description | Example |
|------|-------------|---------|
| Concept | A key idea or principle | "Backpropagation is how neural networks learn from errors" |
| Definition | A formal term definition | "Gradient descent: an optimization algorithm that..." |
| Fact | A specific data point or claim | "GPT-3 has 175 billion parameters" |
| Example | A concrete illustration | "For instance, in a spam filter..." |
| Procedure | A step-by-step process | "To fine-tune a model: 1. Prepare data, 2. Set hyperparameters..." |
| Visual | Something that should become a chart, diagram, or image | "The accuracy curve shows improvement plateauing at epoch 50" |

## Tagging Format

Each chunk gets a tag block:

```markdown
### [Chunk title]

- **Type:** concept | definition | fact | example | procedure | visual
- **Topic:** [topic area, e.g., "neural networks", "data preprocessing"]
- **Complexity:** intro | intermediate | advanced
- **Source:** [where this came from -- page number, section, or "original"]

[Content of the chunk]
```

## Grouping

After extracting all chunks, group them by topic. Topics become candidate modules in Stage 02.

Order topics from foundational to advanced. If a chunk references another concept, the referenced concept's topic should come first.

## What to Skip

- Bibliographies and reference lists (unless a specific citation is needed)
- Administrative content (author bios, publication info)
- Duplicate content across sources (keep the clearest version)
- Content too specialized for the target audience

## Output Length

Target 3-8 chunks per expected session. If you extract 100 chunks for a 10-session course, that is roughly right. If you have 300, consolidate.
