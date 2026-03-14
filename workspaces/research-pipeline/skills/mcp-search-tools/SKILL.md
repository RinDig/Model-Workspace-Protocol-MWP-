---
name: mcp-search-tools
description: Use when searching for information online, finding documentation, looking up APIs, researching topics, or when current knowledge is insufficient to answer a question. Triggers on: search, find, look up, research, documentation, how do I, what is, latest, news about, compare, vs, best practices
---

# MCP Search Tools

Structured web research using 4 MCP search tools with automatic mode selection.

## When to Use

Invoke this skill when:
- User asks to "search", "find", "look up", or "research" something
- User asks "how do I", "what is", "latest", "news about"
- User needs documentation, APIs, or code examples
- Your current knowledge is insufficient to answer
- User compares things ("X vs Y", "best practices for Z")

**Use MCP search tools for better results than built-in WebSearch.**

## Mode Selection

```
┌─────────────────────────────────────────────────────────────┐
│ ASK: How complex is this query?                             │
│                                                             │
│ SIMPLE factual lookup?                                      │
│   └─► QUICK MODE (single tool)                              │
│                                                             │
│ COMPLEX topic, learning, or building knowledge?             │
│   └─► DEEP MODE (parallel tools)                            │
│                                                             │
│ BUILDING knowledge base / comprehensive report?             │
│   └─► COMPREHENSIVE MODE (all tools + scrape)               │
└─────────────────────────────────────────────────────────────┘
```

## Tool Selection (4-Question Filter)

```
Q1: "Do I need NEWS or current events?"
    └─► Use Exa (has dates, breaking news)
        Backup: Firecrawl

Q2: "Do I need FULL CONTENT to read immediately?"
    └─► Use Exa (15K tokens, code included)
        Backup: Scrape top URL from Brave/Firecrawl

Q3: "Do I need the OFFICIAL/CANONICAL source?"
    └─► Use Brave (authority ranking)
        OR Ref (developer docs with deep links)
        Backup: Check domains manually

Q4: "Do I need a GITHUB repo or specific doc section?"
    └─► Use Ref (purpose-built for this)
        Backup: Brave with "site:github.com"

DEFAULT: If none match → Use Exa
```

## Quick Mode

**When:** Simple factual query, single answer needed

**Workflow:**
1. Identify query type from matrix below
2. Call ONE tool
3. Return answer with citation

**Query Type → Tool:**

| Query Type | Tool | MCP Name |
|------------|------|----------|
| News/current events | Exa | `mcp__exa__web_search_exa` |
| Learn concept | Exa | `mcp__exa__web_search_exa` |
| Official docs | Brave | `mcp__brave-search__brave_web_search` |
| Developer docs | Ref | `mcp__ref__ref_search_documentation` |
| GitHub repo | Ref | `mcp__ref__ref_search_documentation` |
| Code examples | Exa Code | `mcp__exa__get_code_context_exa` |
| Local business | Brave Local | `mcp__brave-search__brave_local_search` |

## Deep Mode

**When:** Complex topic, learning, pros/cons, comparisons

**Workflow:**
1. Call ALL 4 tools in parallel
2. Merge unique URLs, de-duplicate by domain
3. Synthesize findings into coherent answer
4. Include citations with source links

## Comprehensive Mode

**When:** Building knowledge base, detailed report needed

**Workflow:**
1. Run Deep Mode (all 4 tools parallel)
2. Identify top 3-5 most relevant URLs
3. Scrape each with `mcp__firecrawl__firecrawl_scrape`
4. Organize into structured report with sections
5. Include full source list with descriptions

## Rate Limit Handling

**Detection:** Empty results, timeout errors, 429 status

**Fallback Chains:**

| Query Type | Primary | Fallback Chain |
|------------|---------|----------------|
| Learning | Exa | Brave → Firecrawl |
| Official Docs | Brave | Ref → Firecrawl |
| GitHub | Ref | Brave site:github.com |
| Code Examples | Exa Code | Ref → Brave |
| News | Exa | Firecrawl → Brave |

## Tool Capabilities Quick Reference

| Capability | Exa | Brave | Firecrawl | Ref |
|------------|-----|-------|-----------|-----|
| Full content (15K tokens) | ✅ | ❌ | ❌ | ❌ |
| Code snippets | ✅ | ❌ | ❌ | Via GitHub |
| Dates/recency | ✅ | ❌ | ❌ | ❌ |
| Official docs ranking | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| GitHub repos | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| Deep doc links | ❌ | ❌ | ❌ | ✅ |
| Breaking news | ⭐⭐⭐ | ⭐ | ⭐⭐ | ❌ |

## The 80/20 Rule

```
80% of searches → Use Exa
  - Returns usable content immediately
  - Includes code snippets
  - Has dates for recency

20% of searches → Use Brave or Ref
  - Official/canonical sources
  - GitHub repos
  - Specific doc sections
```
