# Django security checklist

Use alongside `security-best-practices`. Focus on:

- `django.middleware.csrf.CsrfViewMiddleware` enabled
- ORM parameterized queries; never format SQL by hand
- `DEBUG=False` in production; secret key from env
- Authz checks on every mutating view
- File uploads validated and stored outside web root when possible

Expand from Django's official security docs when a deeper checklist is needed.
