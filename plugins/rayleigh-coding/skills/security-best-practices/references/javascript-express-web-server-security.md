# Express (Node.js) Web Security Spec (Express 5.x / 4.19.2+, Node.js LTS)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new Express apps and routes.
2. **Security review / vulnerability hunting** in existing Express code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, or commit secrets (API keys, passwords, private keys, session secrets, cookies, tokens).
* MUST NOT “fix” security by disabling protections (e.g., weakening cookie flags, disabling CSRF defenses for cookie-authenticated apps, enabling permissive CORS, trusting proxy headers from the open internet, turning on debugging/stack traces in production, disabling TLS without a replacement).
* MUST provide **evidence-based findings** during audits: cite file paths, code snippets, middleware/config values, and runtime assumptions that justify the claim.
* MUST treat uncertainty honestly: if a protection might exist in infrastructure (reverse proxy, gateway, WAF, CDN), report it as “not visible in app code; verify at runtime/config.”
* MUST prefer vetted libraries and platform controls over “roll your own” crypto/auth/session/CSRF. Express explicitly expects the application to validate/handle user input correctly; it does not do this automatically. ([Express][1])

---

## 1) Operating modes

### 1.1 Generation mode (default)

When asked to write new Express code or modify existing code:

* MUST follow every **MUST** requirement in this spec.
* SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
* MUST prefer safe-by-default APIs and proven libraries over custom security code.
* MUST avoid introducing new risky sinks (shell execution, dynamic code evaluation, unsafe redirects, serving user files as HTML, template rendering from untrusted strings, unsafe filesystem paths, SSRF URL fetch endpoints, etc.).

### 1.2 Passive review mode (always on while editing)

While working anywhere in an Express repo (even if the user did not ask for a security scan):

* MUST “notice” violations of this spec in touched/nearby code.
* SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)

When the user asks to “scan”, “audit”, or “hunt for vulns”:

* MUST systematically search the codebase for violations of this spec.
* MUST output findings in a structured format (see §2.3).

Recommended audit order:

1. Entrypoints (server/app bootstrap), deployment manifests, Dockerfiles, process manager config, CI/CD.
2. Express settings + middleware stack order (helmet, parsers, auth, sessions, CSRF, CORS).
3. Proxy trust (`trust proxy`) and IP/protocol/host handling. ([Express][2])
4. Auth flows, sessions, cookies, password reset links, redirect handling. ([Express][1])
5. State-changing routes + CSRF protections (cookie-authenticated apps). ([OWASP Cheat Sheet Series][3])
6. Template rendering and XSS defenses (HTML generation, CSP, `res.locals`). ([OWASP Cheat Sheet Series][4])
7. File handling (uploads + downloads + static files) and path traversal. ([Express][5])
8. Injection classes (SQL, NoSQL, command execution, unsafe deserialization). ([OWASP Cheat Sheet Series][6])
9. Outbound requests (SSRF) and webhook/callback delivery. ([OWASP Cheat Sheet Series][7])
10. Rate limiting / brute-force defenses / abuse controls. ([Express][1])
11. Dependency hygiene / lockfiles / npm audit / vulnerable Express versions. ([Express][1])

---

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)

In Express, common untrusted inputs include:

* `req.params` (route parameters)
* `req.query` (query string parameters; can be strings/arrays/objects depending on parsing) ([OWASP Cheat Sheet Series][8])
* `req.body` from `express.json()`, `express.urlencoded()`, `express.text()`, `express.raw()` ([Express][5])
* `req.headers` / `req.get(...)`
* `req.cookies` / `req.signedCookies` (if cookie parsing middleware is used)
* Upload metadata and filenames (e.g., multer `file.originalname`, `file.mimetype`)
* Any data from external systems (webhooks, third-party APIs, message queues)
* Any persisted user content (DB rows) that originated from users

Special proxy note:

* If `trust proxy` is enabled, values like `req.ip`, `req.hostname`, and `req.protocol` may be derived from `X-Forwarded-*` headers which **can be attacker-controlled** if your proxy chain is not correctly overwriting/removing them. ([Express][2])

### 2.2 State-changing request

A request is state-changing if it can create/update/delete data, change auth/session state, trigger side effects (purchase, email send, webhook send), or initiate privileged actions.

### 2.3 Required audit finding format

For each issue found, output:

* Rule ID:
* Severity: Critical / High / Medium / Low
* Location: file path + function/route/middleware name + line(s)
* Evidence: the exact code/config snippet
* Impact: what could go wrong, who can exploit it
* Fix: safe change (prefer minimal diff)
* Mitigation: defense-in-depth if immediate fix is hard
* False positive notes: what to verify if uncertain

---

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest “production baseline” that prevents common Express misconfigurations.

Minimum baseline targets:

* `helmet()` is used and configured (especially CSP where applicable), and fingerprinting is reduced (disable `x-powered-by`). ([Express][1])
* A custom 404 handler and a custom error handler exist, and production does not leak internal stack traces. ([Express][1])
* Cookie/session usage is deliberate:

  * Not using default session cookie names
  * Cookies use secure attributes (`Secure`, `HttpOnly`, `SameSite`) as appropriate
  * Cookie-backed sessions never store secrets (they are readable by the client)
  * Server-side sessions never use MemoryStore in production. ([Express][1])
* Request body parsing has explicit limits (`express.json({ limit })`, `express.urlencoded({ limit, parameterLimit, depth })`). ([Express][5])
* `trust proxy` is configured explicitly to match your proxy topology; not blindly `true`. ([Express][2])
* Login/auth endpoints have brute-force protection and rate limiting. ([Express][1])
* Dependencies are regularly audited/updated (`npm audit` + advisory response). ([Express][1])

---

## 4) Rules (generation + audit)

Each rule contains: required practice, insecure patterns, detection hints, and remediation.

### EXPRESS-INPUT-001: Treat all user input as untrusted and validate it

Severity: High

Required:

* MUST validate and normalize untrusted inputs before using them in security-sensitive logic or dangerous sinks (DB queries, redirects, filesystem, HTML output, shell commands). Ensure the untrusted inputs are type checked and structure checked before using or passing forward.
* SHOULD apply allowlists (known-good) rather than blocklists when feasible.
* MUST reject or safely handle unexpected types/shapes in `req.query`, `req.params`, and `req.body`.

Insecure patterns:

* Passing `req.query`, `req.params`, `req.body` directly into database/query builders, redirects, filesystem paths, or templates.
* Assuming `req.query.foo` is always a string (it can be an array/object depending on parsing). ([OWASP Cheat Sheet Series][8])

Detection hints:

* Identify “untrusted-to-sink” flows: request → sink (`res.redirect`, SQL execution, `sendFile`, `child_process`, template render, outbound fetch).
* Search for direct usage of `req.query.*`, `req.body.*`, `req.params.*` in sensitive calls.

Fix:

* Add schema validation (e.g., zod/joi/express-validator) at route boundaries.
* Normalize types (e.g., force IDs to integers; reject arrays when scalar expected).

Notes:

* Express production security guidance explicitly says input validation/handling is the application’s responsibility. ([Express][1])

---

### EXPRESS-REDIRECT-001: Prevent open redirects; validate redirect targets

Severity: Medium

Required:

* MUST validate redirect destinations derived from untrusted input (`next`, `return_to`, `url`).
* SHOULD allowlist only same-site relative paths (preferred) or a strict allowlist of domains.
* MUST fall back to a safe default when validation fails.

Insecure patterns:

* `res.redirect(req.query.next)` with no validation.
* `res.redirect(req.body.url)` or `res.location(...)` using untrusted URLs.

Detection hints:

* Search for `res.redirect(` and `res.location(` and trace the source of the target.
* Look for query params named `next`, `redirect`, `return`, `url`.

Fix:

* Only allow relative paths (starting with `/`) and disallow `//`, backslashes, and encoded variants.
* If cross-domain redirects are required, allowlist exact hosts and enforce `https`.

Notes:

* Express documentation calls out open redirects as dangerous user input and shows validating the host before redirecting. ([Express][1])
* Keep Express updated: Express has had an open-redirect-related CVE affecting some versions, and upgrades are part of the mitigation posture. ([NVD][9])

---

### EXPRESS-HEADERS-001: Use Helmet (or equivalent) to set essential security headers

Severity: Medium

Required:

* SHOULD use `helmet()` to set common security headers.
* SHOULD configure CSP realistically (avoid `unsafe-inline` where possible) for pages that render user-influenced content.
* SHOULD set `X-Content-Type-Options: nosniff`, clickjacking defenses (`X-Frame-Options` or CSP `frame-ancestors`), and appropriate referrer policy.

NOTE: It is most important to set the CSP's script-src. All other directives are not as important and can generally be excluded for the ease of development.

Insecure patterns:

* No security headers set in app code and no evidence they are set at the edge.
* CSP missing on apps that display user content.
* Misconfigured framing headers that unintentionally allow clickjacking.

Detection hints:

* Search for `helmet(` usage; check if CSP is configured or disabled.
* Search for `res.setHeader(` / `res.set(` for security header setting.
* If not visible in app code, check nginx/CDN config; otherwise flag “verify at edge.”

Fix:

* Add `helmet()` early in middleware order and configure:

  * CSP (`contentSecurityPolicy`)
  * Frame protections (`frameguard` or CSP `frame-ancestors`)
  * `X-Content-Type-Options` (`noSniff`)

Notes:

* Express production security best practices recommend Helmet and list headers Helmet sets by default. ([Express][1])
* OWASP HTTP Headers guidance is a useful reference when tuning policies. ([OWASP Cheat Sheet Series][10])

---

### EXPRESS-FINGERPRINT-001: Reduce fingerprinting by disabling `x-powered-by` and customizing error/404 responses

Severity: Low (defense-in-depth)

Required:

* SHOULD disable `X-Powered-By` using `app.disable('x-powered-by')`.
* SHOULD provide a custom 404 handler and a custom error handler to avoid distinct default responses and to control information leakage.

Insecure patterns:

* Default `X-Powered-By: Express` header left enabled.
* Default Express 404/error responses in production with identifiable formatting and/or stack traces.

Detection hints:

* Search for `app.disable('x-powered-by')`.
* Check middleware tail for a custom 404 (`app.use((req,res)=>...)`) and a custom error handler (`app.use((err,req,res,next)=>...)`).
* Check if `NODE_ENV` is correctly set for production behavior (see EXPRESS-ERROR-001). ([Express][11])

Fix:

* Add:

  * `app