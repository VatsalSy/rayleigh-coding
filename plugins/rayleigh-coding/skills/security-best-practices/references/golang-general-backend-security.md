# Go (Golang) Security Spec (Go 1.25.x, Standard Library, net/http)

This document is designed as a **security spec** that supports:
1) **Secure-by-default code generation** for new Go code.
2) **Security review / vulnerability hunting** in existing Go code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

--------------------------------------------------------------------

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

- MUST NOT request, output, log, or commit secrets (API keys, passwords, private keys, session cookies, JWTs, database URLs with credentials, signing keys, client secrets).
- MUST NOT “fix” security by disabling protections (e.g., `InsecureSkipVerify`, `GOSUMDB=off` for public modules, wildcard CORS + credentials, removing auth checks, disabling CSRF defenses on cookie-auth apps).
- MUST provide **evidence-based findings** during audits: cite file paths, code snippets, build/deploy configs, and concrete values that justify the claim.
- MUST treat uncertainty honestly: if a control might exist in infrastructure (reverse proxy, WAF, service mesh, platform config), report it as “not visible in app code; verify at runtime/config.”
- MUST keep fixes minimal, correct, and production-safe; avoid introducing breaking changes without warning (especially around auth/session flows, and proxies).

--------------------------------------------------------------------

## 1) Operating modes

### 1.1 Generation mode (default)
When asked to write new Go code or modify existing code:
- MUST follow every **MUST** requirement in this spec.
- SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
- MUST prefer safe-by-default APIs and proven libraries over custom security code.
- MUST avoid introducing new risky sinks (shell execution, dynamic template execution, serving user files as HTML, unsafe redirects, weak crypto, unbounded parsing, etc.).

### 1.2 Passive review mode (always on while editing)
While working anywhere in a Go repo (even if the user did not ask for a security scan):
- MUST “notice” violations of this spec in touched/nearby code.
- SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)
When the user asks to “scan”, “audit”, or “hunt for vulns”:
- MUST systematically search the codebase for violations of this spec.
- MUST output findings in a structured format (see §2.3).

Recommended audit order:
1) Build/deploy entrypoints: `main.go`, `cmd/*`, Dockerfiles, Kubernetes manifests, systemd units, CI workflows.
2) Go toolchain & dependency policy: Go version, modules, `go.mod/go.sum`, proxy/sumdb settings, govulncheck usage.
3) Secret management and config loading (env, files, secret stores) + logging patterns.
4) HTTP server configuration (timeouts, body limits, proxy trust, security headers).
5) AuthN/AuthZ boundaries, session/cookie settings, token validation.
6) CSRF protections for cookie-authenticated state-changing endpoints.
7) Template usage and output encoding (XSS), and any “render template from string” behavior (SSTI).
8) File handling (uploads/downloads/path traversal/temp files), static file serving.
9) Injection sinks: SQL, OS command execution, SSRF/outbound fetch, open redirects.
10) Concurrency/resource exhaustion (unbounded goroutines/queues, missing timeouts/contexts).
11) Use of `unsafe` / `cgo` / `reflect` in security-sensitive paths.
12) Debug/diagnostic endpoints (pprof/expvar/metrics) exposure.
13) Cryptography usage (randomness, password hashing).

--------------------------------------------------------------------

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)
Examples include:
- `*http.Request` fields: `r.URL.Path`, `r.URL.RawQuery`, `r.Form`, `r.PostForm`, headers, cookies, `r.Body`
- Path parameters from routers (including values extracted from URL paths)
- JSON/XML/YAML bodies, multipart form parts, uploaded files
- Any data from external systems (webhooks, third-party APIs, message queues)
- Any persisted user content (DB rows) that originated from users
- Configuration values that might be attacker-influenced in some deployments (headers set by upstream proxies, environment variables in multi-tenant systems)

### 2.2 State-changing request
A request is state-changing if it can create/update/delete data, change auth/session state, trigger side effects (purchase, email send, webhook send), or initiate privileged actions.

### 2.3 Required audit finding format
For each issue found, output:

- Rule ID:
- Severity: Critical / High / Medium / Low
- Location: file path + function/handler name + line(s)
- Evidence: the exact code/config snippet
- Impact: what could go wrong, who can exploit it
- Fix: safe change (prefer minimal diff)
- Mitigation: defense-in-depth if immediate fix is hard
- False positive notes: what to verify if uncertain (edge configs, proxy behavior, auth assumptions)

--------------------------------------------------------------------

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest “production baseline” that prevents common Go misconfigurations.

### 3.1 Toolchain, patching, and dependency hygiene (MUST)
- MUST run a supported Go major version and keep to the latest patch releases.
- MUST treat Go standard library patch releases as security-relevant (many security fixes land in stdlib components like `net/http`, `crypto/*`, parsing packages).
- MUST use Go modules with committed `go.mod` and `go.sum`.
- MUST NOT disable module authenticity mechanisms for public modules (checksum DB) unless you have a controlled, documented replacement.
- MUST run `govulncheck` (source scan and/or binary scan) in CI and address findings.

### 3.2 HTTP server baseline (MUST for network-facing services)
If the program serves HTTP (directly or via a framework built on `net/http`):
- MUST configure an `http.Server` with explicit timeouts and header limits.
- MUST set request body size limits (global and per-route as needed).
- MUST avoid exposing diagnostic endpoints (pprof/expvar) publicly.
- SHOULD set a consistent set of security headers (or verify they are set at the edge).
- MUST set cookie security attributes for any cookies you issue.
- SHOULD implement rate limiting and abuse controls for auth and expensive endpoints.

Illustrative baseline skeleton (adjust to your project):
- Create a dedicated mux (avoid implicit global defaults unless intentionally managed).
- Wrap handlers with: panic-safe error handling, request ID, logging, auth, and limits.

--------------------------------------------------------------------

## 4) Rules (generation + audit)

Each rule contains: required practice, insecure patterns, detection hints, and remediation.

### GO-DEPLOY-001: Keep the Go toolchain and standard library updated (security releases)
Severity: Medium

NOTE: Upgrading dependencies and the core Go version can break projects in unexpected ways. Focus on only security-critical dependencies and if noticed, let the user know rather than upgrading automatically.

Required:
- MUST run a supported Go major release and apply patch releases promptly.
- SHOULD treat patch releases as security-relevant, even if your application code didn’t change.

Insecure patterns:
- Production builds pinned to old Go versions without a patching process.
- Docker images like `golang:1.xx` or custom base images that are not updated regularly.
- CI pipelines that intentionally suppress Go updates.

Detection hints:
- Inspect CI (`.github/workflows`, `gitlab-ci.yml`, etc.) for `go-version:` or toolchain setup.
- Inspect Dockerfiles for `FROM golang:` tags.
- Inspect `go.mod` `go` directive and any toolchain pinning.

Fix:
- Upgrade to the latest patch of a supported Go version.
- Add an automated check (CI) that fails when Go is below an approved minimum.

Notes:
- Go publishes regular minor releases that frequently include security fixes across standard library packages.

---

### GO-SUPPLY-001: Go module authenticity MUST NOT be disabled for public dependencies
Severity: High

Required:
- MUST keep module checksum verification enabled for public modules.
- SHOULD commit `go.sum` and treat changes as security-sensitive.
- MUST NOT use insecure module fetching settings for public modules.
- MAY configure private module behavior using `GOPRIVATE`/`GONOSUMDB` for private repos, but must do so narrowly and intentionally.

Insecure patterns:
- `GOSUMDB=off` in CI or production build environments for public modules.
- `GONOSUMDB=*` or overly broad patterns that effectively disable verification.
- `GOINSECURE=*` or broad `GOINSECURE` patterns for public modules.
- `GOPROXY=direct` everywhere without a clear policy.

Detection hints:
- Search build configs for `GOSUMDB`, `GONOSUMDB`, `GOINSECURE`, `GOPROXY`, `GOPRIVATE`.
- Look for documentation/scripts that recommend disabling checksum DB “to make builds work”.

Fix:
- Restore defaults for public module verification.
- For private modules:
  - Set `GOPRIVATE=your.private.domain/*`
  - Configure an internal proxy or direct fetching, and restrict `GONOSUMDB` to private patterns only.

Notes:
- Disabling checksum verification removes an important integrity layer against targeted or compromised upstream delivery.

---

### GO-CONFIG-001: Secrets must be externalized and never logged or committed
Severity: High (Critical if credentials are committed)

Required:
- MUST load secrets from environment variables, secret managers, or secure config files with restricted permissions.
- MUST NOT hard-code secrets in Go source, test fixtures that may reach production, or build args.
- MUST NOT log secrets or full credential-bearing connection strings.
- SHOULD fail closed in production if required secrets are missing.

Insecure patterns:
- String constants containing tokens/keys/passwords.
- `.env` files or config files with secrets committed to repo.
- Logging `os.Environ()`, dumping full configs, or printing DSNs.

Detection hints:
- Search for suspicious literals (`API_KEY`, `SECRET`, `PASSWORD`, `Authorization:`).
- Inspect config loaders and logging statements.
- Inspect CI logs or debug print paths.

Fix:
- Move secrets to a secret store / environment variables.
- Redact sensitive fields in logs.
- Add secret scanning to CI and pre-commit.

---

### GO-HTTP-001: HTTP servers MUST set timeouts and MaxHeaderBytes
Severity: High (DoS risk)

Required:
- MUST set: `ReadHeaderTimeout`, and SHOULD set `ReadTimeout`, `WriteTimeout`, `IdleTimeout` as appropriate for the service.
- MUST set `MaxHeaderBytes` to a justified limit for your application.
- MUST NOT rely on default zero-values for timeouts in production for internet-facing servers.

Insecure patterns:
- `http.ListenAndServe(":8080", handler)` with a default `http.Server` (no explicit timeouts).
- `&http.Server{}` with timeouts left at zero.
- Missing `MaxHeaderBytes`.

Detection hints:
- Search for `http.ListenAndServe(`, `ListenAndServeTLS(`, `Server{` and inspect configured fields.
- Check for reverse proxies; even with a proxy, app-level timeouts still matter.

Fix:
- Use `http.Server{ReadHeaderTimeout: ..., ReadTimeout: ..., WriteTimeout: ..., IdleTimeout: ..., MaxHeaderBytes: ...}`.
- Calibrate timeouts per endpoint type (streaming vs JSON APIs).

Notes:
- Net/http documents that these timeouts exist and that zero/negative values mean “no timeout”; production services should choose explicit values.

---

### GO-HTTP-002: Request body and multipart parsing MUST be size-bounded
Severity: Medium (DoS risk; can be High for upload-heavy apps)

Required:
- MUST enforce a global maximum request body size for endpoints that accept bodies.
- MUST enforce strict multipart upload limits and avoid unbounded form parsing.
- SHOULD enforce per-route limits when some endpoints legitimately need larger bodies.
- SHOULD set upstream (proxy) limits as defense-in-depth.

Insecure patterns:
- Reading `r.Body` with `io.ReadAll(r.Body)` without a size cap.
- Calling `r.ParseMultipartForm(...)` with overly large limits (or forgetting size controls).
- Accepting file uploads with no limits on file size, number of parts, or total body size.

Detection hints:
- Search for `io.ReadAll(r.Body)`, `json.NewDecoder(r.Body)`, `ParseMultipartForm`, `FormFile`, `multipart`.
- Look for missing `http.MaxBytesReader` or equivalent per-handler limiting.
- Look for “upload” endpoints and check limits.

Fix:
- Wrap request bodies with `http.MaxBytesReader(w, r.Body, maxBytes)` before parsing.
- For multipart, set conservative limits and validate file sizes/part counts explicitly.
- Set proxy limits (e.g., at ingress) in addition to app limits.

Notes:
- There are known vulnerability classes and advisories related to excessive resource consumption in multipart/form parsing; treat unbounded parsing as a security issue.

---

### GO-DEPLOY-002: Diagnostic endpoints (pprof/expvar/metrics) MUST NOT be publicly exposed
Severity: High

NOTE: This only applies to production configurations. These endpoints are often used for debug or dev endpoints. If found, confirm that it would be reachable from the actual production deployment.

Required:
- MUST NOT expose `net/http/pprof` handlers on a public internet-facing listener without strong access controls.
- SHOULD run diagnostics on a separate, internal-only listener (loopback/VPC-only) and require auth.
- MUST review what diagnostic endpoints reveal (stack traces, memory, command lines, environment, internal URLs).

Insecure patterns:
- Side-effect import `import _ "net/http/pprof"` in a server binary with a public mux.
- `/debug/pprof/*` reachable without auth.
- `/debug/vars` (expvar) reachable without auth.

Detection hints:
- Search for `net/http/pprof` imports (including blank imports).
- Search for route prefixes `/debug/pprof`, `/debug/vars`.
- Check whether `http.DefaultServeMux` is used and whether any debug handlers register globally.

Fix:
- Remove diagnostics from production builds, or bind them to an internal-only listener.
- Add strong authentication/authorization (and ideally network-level restrictions).

Notes:
- pprof is typically imported for its side effect of registering HTTP handlers under `/debug/pprof/`.

---

### GO-HTTP-003: Reverse proxy and forwarded header trust MUST be explicit
Severity: High (auth, URL generation, logging/auditing correctness)

Required:
- If behind a reverse proxy, MUST define which proxy is trusted and how client IP/scheme/host are derived.
- MUST NOT trust `X-Forwarded-For`, `X-Forwarded-Proto`, `Forwarded`, or similar headers from the open internet.
- MUST ensure “secure cookie” logic, redirects, and absolute URL generation do not rely on spoofable headers.

Insecure patterns:
- Using `r.Header.Get("X-Forwarded-For")` as the client IP without validating the proxy boundary.
- Deriving “is HTTPS” from `X-Forwarded-Proto` without confirming it came from a trusted proxy.
- Using forwarded `Host` values for password reset links without allowlisting.

Detection hints:
- Search for `X-Forwarded-For`, `X-Forwarded-Proto`, `Forwarded`, `Real-IP`, and any custom “client IP” helpers.
- Inspect ingress/proxy configs; if not visible, mark as “verify at edge”.

Fix:
- Enforce proxy trust at the edge and in app:
  - Accept forwarded headers only from known proxy IP ranges.
  - Prefer platform-provided mechanisms where available.
- If generating external links, use a configured allowlisted canonical origin (not the request’s Host header).

---

### GO-HTTP-004: Security headers SHOULD be set (in app or at the edge)
Severity: Medium

Required (typical web app serving browsers):
- SHOULD set:
  - `Content-Security-Policy` (CSP) appropriate to the app. NOTE: It is most important to set the CSP's script-src. All other directives are not as important and can generally be excluded for the ease of development.
  - `X-Content-Type-Options: nosniff`
  - Clickjacking protection (`X-Frame-Options` and/or CSP `frame-ancestors`)
  - `Referrer-Policy` and `Permissions-Policy` where appropriate
- MUST ensure cookies have secure attributes (see GO-HTTP-005).

NOTE:
- These headers may be set via reverse proxy/CDN; if not visible in app code, report as “verify at edge”.

Insecure patterns:
- No security headers anywhere (app or edge) for a browser-facing app.
- CSP missing for apps rendering untrusted content.

Detection hints:
- Search for middleware setting headers: `w.Header().Set("Content-Security-Policy", ...)`, etc.
- Search for reverse proxy config that sets headers.

Fix:
- Add centralized header middleware in Go, or configure at the edge.
- Keep CSP realistic; avoid `unsafe-inline` where possible.

---

### GO-HTTP-005: Cookies MUST use secure attributes in production
Severity: Medium

Required (production, HTTPS):
- MUST set `Secure` on cookies that carry auth/session state. IMPORTANT NOTE: Only set `Secure` in production environment when TLS is configured. When running in a local dev environment over HTTP, do not set `Secure` property on cookies. You should do this conditionally based on if the app is running in production mode. You should also include a property like `SESSION_COOKIE_SECURE` which can be used to disable `Secure` cookies when testing over HTTP.
- MUST set `HttpOnly` on auth/session cookies.
- SHOULD set `SameSite=Lax` by default (or `Strict` if compatible), and only use `None` when necessary (and only with `Secure`).
- SHOULD set bounded lifetimes (`Max-Age`/`Expires`) appropriate to the app.

Insecure patterns:
- Setting auth/session cookies without `Secure` in HTTPS deployments.
- Cookies without `HttpOnly` for session identifiers.
- `SameSite=None` for cookie-authenticated apps without a strong CSRF strategy.

Detection hints:
- Search for `http.SetCookie`, `&http.Cookie{`, `Set-Cookie`.
- Inspect cookie flags in auth/session code.

Fix:
- Set the correct fields on `http.Cookie` and centralize cookie creation.

Notes:
- SameSite is defense-in-depth and does not replace CSRF protections for cookie-auth apps.

---

### GO-HTTP-006: Cookie-authenticated state-changing endpoints MUST be CSRF-protected
Severity: High

- IMPORTANT NOTE: If cookies are not used for auth (e.g., pure bearer token in Authorization header with no ambient cookies), CSRF is not a risk for those endpoints.

Required:
- MUST protect all state-changing e