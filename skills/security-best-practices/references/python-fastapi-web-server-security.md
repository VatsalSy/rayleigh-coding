# FastAPI security checklist

Use alongside `security-best-practices`. Focus on:

- Validate bodies with Pydantic models; reject unknown fields when appropriate
- Dependency-injected auth on protected routes
- No shell=True / unsanitized subprocess from request data
- CORS allowlists explicit; no `*` with credentials
- Secrets and DB URLs from environment only

Expand from FastAPI security docs when a deeper checklist is needed.
