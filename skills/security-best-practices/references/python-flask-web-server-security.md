# Flask security checklist

Use alongside `security-best-practices`. Focus on:

- CSRF protection (Flask-WTF or equivalent) on cookie sessions
- Jinja autoescape on; never `|safe` on untrusted input
- Parameterized SQL / ORM only
- `SECRET_KEY` from environment
- Debug toolbar off in production

Expand from Flask security docs when a deeper checklist is needed.
