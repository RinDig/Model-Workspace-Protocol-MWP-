# Dataset Template

Structure for structured data output.

---

## JSON Schema

```json
{
  "metadata": {
    "title": "string",
    "generated": "ISO date",
    "methodology": "string",
    "source_count": "number"
  },
  "findings": [
    {
      "id": "string",
      "theme": "string",
      "claim": "string",
      "evidence": ["source_id_1", "source_id_2"],
      "confidence": "high|medium|low|inconclusive"
    }
  ],
  "sources": [
    {
      "id": "string",
      "citation": "string",
      "credibility": "high|medium|low",
      "url": "string (optional)"
    }
  ]
}
```

---

## Usage

- Suitable for programmatic access
- Can be imported to databases or spreadsheets
- Supports filtering and analysis
