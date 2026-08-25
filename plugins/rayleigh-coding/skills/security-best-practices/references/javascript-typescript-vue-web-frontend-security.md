# Vue / frontend security checklist

Use alongside `security-best-practices`. Focus on:

- Prefer textContent / safe binding over `v-html` with untrusted input
- Escape user content in templates; sanitize if HTML is required
- Pin dependencies; audit XSS sinks in custom directives
- CSRF tokens on cookie-auth mutating requests
- Avoid eval / new Function on user data

For deeper language guidance, expand this file from a trusted AppSec source rather than shipping a personal long-form dump.
