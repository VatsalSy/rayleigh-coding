---
name: cloudflare
description: >
  Use when the user asks to update DNS, deploy or modify a Cloudflare Worker,
  purge cache, check traffic, or run wrangler against their Cloudflare account.
---

# Cloudflare

Discover account and zone IDs at runtime. Never hard-code them in skills or commits.

## Credentials

Required env vars (fail loudly if missing):

| Env var | Used for |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Preferred. Scoped token for wrangler and Bearer REST calls |
| `CLOUDFLARE_ACCOUNT_ID` | Account scoped API paths |
| `CLOUDFLARE_EMAIL` + `CLOUDFLARE_GLOBAL_API_KEY` | Legacy Global Key auth only when a token is unavailable |

```bash
: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is not set.}"
: "${CLOUDFLARE_ACCOUNT_ID:?CLOUDFLARE_ACCOUNT_ID is not set. Discover via wrangler whoami or the dashboard.}"
CF_ACCOUNT="$CLOUDFLARE_ACCOUNT_ID"
```

## Discover zones and account

```bash
wrangler whoami
curl -s "https://api.cloudflare.com/client/v4/zones?per_page=50" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "
import json,sys
for z in json.load(sys.stdin).get('result', []):
    print(z['name'], z['id'])
"
```

Resolve `<ZONE_ID>` from that list. Do not invent IDs.

## wrangler

```bash
wrangler --version
wrangler whoami
wrangler tail <worker-name> --format pretty
cd <worker-dir> && wrangler deploy
```

Prefer `CLOUDFLARE_API_TOKEN` for wrangler. Use the REST API for DNS, cache, and firewall when wrangler does not cover the action.

## REST patterns

Base: `https://api.cloudflare.com/client/v4`  
Auth: `-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"`  
(Legacy Global Key uses `X-Auth-Email` + `X-Auth-Key` instead.)

### List Workers

```bash
curl -s "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT/workers/scripts" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### DNS list / create / update

```bash
curl -s "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### Purge cache

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## Gotchas

1. Global API Key and API Token use different header schemes. Do not mix them.
2. `"proxied": true` is orange-cloud; `false` is DNS-only.
3. Worker routes attach to a zone, not the account.
4. Cache purge is fast; CDN edges can take ~30s to reflect it.
5. Never commit account IDs, zone IDs, or tokens into a public skill or repo.
