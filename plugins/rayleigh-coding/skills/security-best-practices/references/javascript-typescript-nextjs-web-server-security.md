# Next.js (TypeScript/JavaScript) Web Security Spec (Next.js 16.1.x, Node.js 20.9+)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new Next.js backend code (Route Handlers, API Routes, Server Actions, Proxy/Middleware).
2. **Security review / vulnerability hunting** in existing Next.js repos (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

Target scope: Next.js **16.1.x** (latest line shown in the App Router docs) ([Next.js][1]), running on Node.js **20.9+** (per Next.js system requirements). ([Next.js][2])

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, or commit secrets (API keys, passwords, private keys, session cookies, OAuth tokens, `process.env` dumps, database URLs with credentials).
* MUST NOT “fix” security by disabling protections (e.g., disabling origin checks, relaxing CORS to `*`, skipping authz checks, turning off cookie security flags, turning off CSP because it’s “hard”).
* MUST provide **evidence-based findings** during audits: cite file paths, code snippets, and configuration values that justify each claim.
* MUST treat uncertainty honestly: if a protection might exist in infrastructure (reverse proxy, CDN, WAF, platform headers), report it as “not visible in app code; verify at runtime/config”.
* MUST assume all request-facing server code is reachable by attackers unless there is a clearly enforced auth boundary (not just “the UI doesn’t link to it”).
* MUST treat TypeScript types as **non-security boundaries**: types do not validate runtime input; runtime checks are required. ([Next.js][3])

---

## 1) Operating modes

### 1.1 Generation mode (default)

When asked to write new Next.js code or modify existing code:

* MUST follow every **MUST** requirement in this spec.
* SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
* MUST prefer safe-by-default APIs and proven libraries over custom security code.
* MUST avoid introducing new risky sinks (dynamic code execution, unsafe redirects, serving user files as HTML, SSRF URL fetchers, building SQL strings, etc.).

### 1.2 Passive review mode (always on while editing)

While working anywhere in a Next.js repo (even if the user did not ask for a security scan):

* MUST “notice” violations of this spec in touched/nearby code.
* SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)

When the user asks to “scan”, “audit”, or “hunt for vulns”:

* MUST systematically search the codebase for violations of this spec.
* MUST output findings in a structured format (see §2.3).

Recommended audit order:

1. Deployment entrypoints and environment (Dockerfiles, `package.json` scripts, hosting config).
2. Next.js config (`next.config.*`), Proxy/Middleware, routing patterns.
3. Authentication, sessions, cookies.
4. CSRF protections and state-changing endpoints (Server Actions, Route Handlers, API Routes).
5. XSS (React + CSP) and unsafe HTML rendering.
6. Cache/data-leak hazards (static rendering + caching + “use cache”).
7. File handling (uploads/downloads) and path traversal.
8. Injection classes (SQL/ORM misuse, command execution, unsafe deserialization).
9. Outbound requests (SSRF).
10. Redirect handling (open redirects).
11. CORS and security headers.

---

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)

In Next.js backends, untrusted input includes:

App Router:

* Route Handler params and request data:

  * `context.params` (dynamic segments), search params (`request.url`, `new URL(request.url).searchParams`)
  * `request.headers`, `request.cookies`
  * `await request.json()`, `await request.formData()`, `await request.text()`
* Dynamic APIs used in Server Components/Server Functions:

  * `headers()` and `cookies()` values ([Next.js][4])

Pages Router:

* `req.query`, `req.cookies`, `req.body` in `pages/api/*` handlers ([Next.js][3])

Plus:

* Anything from external systems (webhooks, third-party APIs, message queues)
* Any persisted user content (DB rows) that originated from users

### 2.2 State-changing request

A request is state-changing if it can create/update/delete data, change auth/session state, trigger side effects (purchase, email send, webhook send), or initiate privileged actions.

Special note for Next.js:

* **Server Actions** are invoked via network requests and can mutate state; treat them as state-changing endpoints. ([Next.js][5])

### 2.3 Required audit finding format

For each issue found, output:

* Rule ID:
* Severity: Critical / High / Medium / Low
* Location: file path + function/route name + line(s)
* Evidence: the exact code/config snippet
* Impact: what could go wrong, who can exploit it
* Fix: safe change (prefer minimal diff)
* Mitigation: defense-in-depth if immediate fix is hard
* False positive notes: what to verify if uncertain

---

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest “production baseline” that prevents common Next.js backend misconfigurations.

### 3.1 Run Next.js in production mode (MUST)

* MUST run `next build` + `next start` (or the managed platform equivalent), not `next dev`. Dev mode has different error/reporting behavior and is not designed for production exposure. ([Next.js][6])
* MUST ensure `NODE_ENV=production` in production (Next.js defaults `NODE_ENV` based on command; verify the runtime environment). ([Next.js][7])

### 3.2 Put a reverse proxy / edge layer in front when self-hosting (MUST for public internet)

* If self-hosting, MUST place a reverse proxy (e.g., nginx) or equivalent edge layer in front of the Next.js server to handle malformed requests, slow attacks, payload size limits, rate limiting, and similar concerns. ([Next.js][8])

### 3.3 Baseline header/cookie posture (SHOULD)

* SHOULD set a baseline of security headers globally (CSP, `X-Content-Type-Options`, clickjacking defense via CSP `frame-ancestors` and/or `X-Frame-Options`, etc.). Next.js provides guidance for implementing CSP via Proxy/headers. ([Next.js][7])
* MUST ensure auth/session cookies use secure attributes (`Secure`, `HttpOnly`, `SameSite`) as appropriate. ([Next.js][9])
IMPORTANT NOTE: Only set `Secure` in production environment. When running in a local dev environment over HTTP, do not set `Secure` property on cookies. You should do this conditionally based on if the app is running in production mode. You should also include a property like `SESSION_COOKIE_SECURE` which can be used to disable `Secure` cookies when testing over HTTP.

### 3.4 Clear separation between server-only and client code (MUST)

* MUST prevent secrets and privileged logic from being bundled into client code.
* MUST treat `NEXT_PUBLIC_*` environment variables as public (browser-exposed and inlined at build time). ([Next.js][7])

---

## 4) Rules (generation + audit)

Each rule contains: required practice, insecure patterns, detection hints, and remediation.

### NEXT-DEPLOY-001: Do not run `next dev` in production; ensure production mode behavior

Severity: High (if production)

NOTE: If they are deploying to a specific Next.js hosting provider, they do not need to worry about this.

Required:

* MUST NOT deploy `next dev` or any development server mode to production.
* MUST ensure production builds and production runtime are used for any public deployment. ([Next.js][6])

Insecure patterns:

* `next dev` in Docker `CMD`, Procfile, platform start command.
* `NODE_ENV=development` in production environment config.
* Debug/dev-only endpoints or flags exposed publicly.

Detection hints:

* Search `package.json` scripts and deployment manifests for `next dev`.
* Search infra for `NODE_ENV=development` or missing `NODE_ENV`.
* Check Kubernetes/PM2/systemd entrypoints for `next dev`.

Fix:

* Use `next build` during CI/build and `next start` at runtime (or platform-native build/run).
* Ensure environment sets `NODE_ENV=production`.

Note:

* Dev mode is fine for local development. Only flag if it is being used as a production entrypoint.

---

### NEXT-SUPPLY-001: Stay on supported Next.js releases; patch quickly for security advisories

Severity: High (Critical if known-vulnerable version)

Required:

* MUST run a supported Next.js version line and apply security updates promptly. Next.js documents an LTS/support policy. ([Next.js][10])
* MUST treat published advisories as urgent upgrade signals (e.g., update to a patched release). ([GitHub][11])

Insecure patterns:

* Running EOL Next.js major/minor without backported security fixes.
* Ignoring advisories, or pinning `next` to a vulnerable range.

Detection hints:

* Check `package.json` and lockfiles for `next` version.
* Compare against Next.js support policy and advisories.

IMPORTANT: Any versions older than these minor versions are vulnerable to "react2shell" vulnerability (https://nextjs.org/blog/CVE-2025-66478):
15.0.5
15.1.9
15.2.6
15.3.6
15.4.8
15.5.7
16.0.7

Fix:

* Upgrade `next` to a supported and patched version.
* Add a dependency update process + CI checks.


---

### NEXT-SECRETS-001: Secrets MUST NOT be committed or exposed to the browser

Severity: High (Critical if secret is client-exposed)

Required:

* MUST store secrets in environment variables or a secret manager; MUST NOT commit `.env*` files.
* MUST treat `.env*` as sensitive; Next.js warns you “almost never want to commit these files.” ([Next.js][7])
* MUST treat any `NEXT_PUBLIC_*` environment variable as public and browser-visible (inlined into the client bundle at build time). ([Next.js][7])

Insecure patterns:

* `.env`, `.env.local`, `.env.production` committed to git.
* `NEXT_PUBLIC_API_KEY`, `NEXT_PUBLIC_SECRET`, `NEXT_PUBLIC_DATABASE_URL`, etc.
* Rendering `process.env` values into HTML or returning them from API routes.

Detection hints:

* Scan git history and repo files for `.env` content, `DB_PASS=`, `API_KEY=`, `SECRET=`.
* Grep for `NEXT_PUBLIC_` and review any sensitive-looking names.
* Search for `process.env` usage in Client Components (`"use client"`) and shared modules.

Fix:

* Move secrets to server-only env vars (no `NEXT_PUBLIC_` prefix).
* Ensure `.env*` is ignored and secrets are injected at deploy time.
* Rotate leaked keys.

---

### NEXT-SECRETS-0