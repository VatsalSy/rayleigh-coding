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
