---
name: brave-search
description: Use when a task needs browserless web search or page-content extraction — documentation lookups, facts, current information, or fetching a URL as markdown. NOT for arXiv topic search (arxiv-search) or citation data (semantic-scholar).
---

# Brave Search

Headless web search and content extraction using Brave Search. No browser required.

## Setup

No API key is required for the bundled `search.js` and `content.js` scripts. They fetch Brave search result pages and extract content directly, so do not require `BRAVE_API_KEY` to be exported.

If you prefer, the built-in `web_search` tool is also available and is the simpler path for most searches.

## Search

```bash
./search.js "query"                    # Basic search (5 results)
./search.js "query" -n 10              # More results
./search.js "query" --content          # Include page content as markdown
./search.js "query" -n 3 --content     # Combined
```

## Extract Page Content

```bash
./content.js https://example.com/article
```

Fetches a URL and extracts readable content as markdown.

## Output Format

```
--- Result 1 ---
Title: Page Title
Link: https://example.com/page
Snippet: Description from search results
Content: (if --content flag used)
  Markdown content extracted from the page...

--- Result 2 ---
...
```

## When to Use

- Searching for documentation or API references
- Looking up facts or current information
- Fetching content from specific URLs
- Any task requiring web search without interactive browsing

## When NOT to Use (prefer dedicated skills)

- **Academic paper search by topic** → use `arxiv-search` skill (arXiv API, structured results)
- **DOI / citation count / forward citations** → use `semantic-scholar` skill (S2 API)
- **Author h-index or "who's citing paper X"** → use `semantic-scholar` skill
