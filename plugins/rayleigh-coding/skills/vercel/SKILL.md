---
name: vercel
description: >
  Use when the user asks to deploy to Vercel, check a build status, view
  deployment logs, update env vars, manage domains, or roll back a
  Vercel-hosted project. Requires VERCEL_TOKEN.
---

# Vercel

Discover project IDs via the CLI or API. Never hard-code personal project inventories in skills.

## Credentials

```bash
: "${VERCEL_TOKEN:?VERCEL_TOKEN is not set. Create a token at https://vercel.com/account/tokens and export it.}"
```

## Discover projects

```bash
vercel ls --token "$VERCEL_TOKEN"
curl -s "https://api.vercel.com/v9/projects?limit=20" \
  -H "Authorization: Bearer $VERCEL_TOKEN" | python3 -c "
import json,sys
for p in json.load(sys.stdin).get('projects', []):
    print(p['name'], '|', p['id'])
"
```

Use the printed `id` as `<PROJECT_ID>`.

## CLI

```bash
vercel --version
cd <repo-root>
vercel --token "$VERCEL_TOKEN" --prod --yes
vercel ls --token "$VERCEL_TOKEN" <project-name>
vercel logs --token "$VERCEL_TOKEN" <deployment-url>
vercel rollback --token "$VERCEL_TOKEN" <project-name>
```

`--prod` targets production. Omitting it creates a preview deployment.

## REST patterns

Base: `https://api.vercel.com`  
Header: `-H "Authorization: Bearer $VERCEL_TOKEN"`

### Latest deployments

```bash
curl -s "https://api.vercel.com/v6/deployments?projectId=<PROJECT_ID>&limit=5" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Env vars

```bash
curl -s "https://api.vercel.com/v9/projects/<PROJECT_ID>/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

Env changes do not always redeploy automatically. Trigger a new deployment when the change must take effect.

## Gotchas

1. Token scope may be personal-only. Org/team projects need a token with that scope.
2. SSO protection on a project can block unauthenticated proxies or workers.
3. Older build logs may be truncated. Inspect recent failures promptly.
4. Never commit `VERCEL_TOKEN` or project ID tables into a public skill.
