# jQuery / legacy frontend security checklist

Use alongside `security-best-practices`. Focus on:

- Prefer `.text()` over `.html()` for untrusted data
- Avoid `$(userInput)` as a selector when input may contain HTML
- Escape URLs before putting them in `href` / `src`
- Do not pass unsanitized strings to `eval`, `setTimeout(string)`, or `new Function`
- Keep jQuery patched; prefer modern framework patterns for new UI

Expand from a trusted AppSec source when a deeper checklist is needed.
