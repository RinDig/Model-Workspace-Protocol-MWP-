# Current-state snapshot contract

Build this metadata-only JSON object from a complete run of Intercom MCP `list_articles`:

```json
{
  "source": "intercom-mcp:list_articles",
  "fetched_at": "2026-07-22T12:00:00Z",
  "complete": true,
  "total_pages": 1,
  "pages_fetched": [1],
  "total_count": 1,
  "articles": [
    {
      "id": "123",
      "content_id": "456",
      "title": "How to use a feature",
      "description": "Complete one task.",
      "state": "published",
      "parent_id": 456,
      "parent_type": "collection",
      "author_id": 789,
      "created_at": 1750000000,
      "updated_at": 1750001000,
      "url": "https://support.example.com/en/articles/123-how-to-use-a-feature"
    }
  ]
}
```

## Requirements

- Set `source` exactly to `intercom-mcp:list_articles` and `complete` exactly to `true`.
- Use `per_page: 150`. Set `total_pages` from MCP and list every fetched page in ascending order without gaps. Use one fetched page for an empty Help Center.
- Set `total_count` to the exact number of unique articles supplied.
- Include every listed article exactly once. Accept only `published` and `draft` states.
- Copy `content_id` from `list_articles`; Intercom Knowledge editor links require it and cannot be built from the article ID.
- Use numeric IDs or `null` for author and parent IDs. Supply `parent_id` and `parent_type` together or set both to `null`.
- Use Unix integer timestamps or `null`. Use an absolute HTTPS public URL or `null`.
- Include only the documented fields. Never include `body`, `body_markdown`, conversation IDs, private links, transcripts, or arbitrary MCP response fields.

The helper validates completeness and uniqueness before atomically replacing `current-state.json` and `CURRENT_STATE.md`. Invalid imports leave the last successful overview untouched.
