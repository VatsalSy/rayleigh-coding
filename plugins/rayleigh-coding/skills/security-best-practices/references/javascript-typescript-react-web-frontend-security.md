# React (JavaScript/TypeScript) Web Security Spec (React 19.x, TypeScript 5.x)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new React code.
2. **Security review / vulnerability hunting** in existing React code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, or commit secrets (API keys, OAuth client secrets, private keys, session cookies, JWTs, signing keys).

  * Frontend note: anything shipped to the browser is observable by end users and attackers (view-source, devtools, proxies); never treat client code or “env vars in the bundle” as secret. ([create-react-app.dev][1])
* MUST NOT “fix” security by disabling protections (e.g., turning off CSP to “make it work”, adding `unsafe-inline`/`unsafe-eval` without a documented, constrained plan, disabling CSRF protections when using cookies, widening CORS, skipping sanitization, or “temporary” bypasses that ship). ([OWASP Cheat Sheet Series][2])
* MUST provide **evidence-based findings** during audits: cite file paths, code snippets, and configuration values that justify the claim.
* MUST treat uncertainty honestly: if a protection might exist in infra (CDN/WAF/reverse proxy), report it as “not visible in app code; verify via runtime headers / edge config”.
* MUST assume any data that crosses a trust boundary (URL, storage, network, postMessage, third-party scripts) can be attacker-influenced unless proven otherwise (see §2.1).

---

## 1) Operating modes

### 1.1 Generation mode (default)

When asked to write new React code or modify existing code:

* MUST follow every **MUST** requirement in this spec.
* SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
* MUST prefer safe-by-default APIs and proven libraries over custom security code.
* MUST avoid introducing new risky sinks (raw HTML insertion, direct DOM sinks like `innerHTML`, dynamic code execution, untrusted redirects/navigation, third‑party script injection, unsafe token storage, etc.). ([MDN Web Docs][3])

### 1.2 Passive review mode (always on while editing)

While working anywhere in a React repo (even if the user did not ask for a security scan):

* MUST “notice” violations of this spec in touched/nearby code.
* SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)

When the user asks to “scan”, “audit”, or “hunt for vulns”:

* MUST systematically search the codebase for violations of this spec.
* MUST output findings in a structured format (see §2.3).

Recommended audit order:

1. App entrypoints, build tooling (Vite/Webpack/CRA/Next), deployment configs, CDN/static hosting config.
2. Secrets & configuration exposure (env vars, runtime config injection, source maps).
3. Rendering of untrusted data (XSS/DOM XSS), especially `dangerouslySetInnerHTML`, markdown/HTML renderers, URL attributes.
4. Direct DOM usage and dangerous JS execution (`innerHTML`, `eval`, `new Function`, `document.write`, etc.).
5. Auth & session patterns (token storage, cookies, CSRF interactions, OAuth flows).
6. Network layer (axios/fetch wrappers, dynamic base URLs, credentialed requests, data exfil risks).
7. Navigation & redirect handling (open redirects, `window.location`, `target=_blank`, `window.open`).
8. Third-party scripts/tags/analytics and integrity controls (CSP, SRI).
9. Service worker/PWA behavior (HTTPS, caching rules, update strategy).
10. Security headers posture (CSP, clickjacking, nosniff, referrer policy) in app or at the edge. ([OWASP Cheat Sheet Series][2])

---

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)

Examples include:

* URL-derived data: `window.location`, query params, hash fragments, route params.
* Any data from browser storage: `localStorage`, `sessionStorage`, `IndexedDB` (including data previously written by the app—because XSS or extensions can tamper with it). ([OWASP Cheat Sheet Series][4])
* Any data from cross-window messaging: `window.postMessage` payloads. ([OWASP Cheat Sheet Series][4])
* Any data from remote APIs, webhooks proxied to the client, GraphQL responses, CMS content, feature flag services.
* Any persisted user content (profiles, comments, rich text, markdown) rendered in the UI.
* Any data produced by third-party scripts or tag managers (treat as untrusted unless strongly controlled). ([OWASP Cheat Sheet Series][5])

### 2.2 State-changing request (frontend perspective)

A request is state-changing if it can create/update/delete data, change auth/session state, trigger side effects (purchase, email send, webhook), or initiate privileged actions.

Frontend-specific note:

* State changes are often triggered by `fetch/axios` calls or form submissions. If authentication is cookie-based, these calls can be CSRF-relevant (§4 REACT-CSRF-001). ([OWASP Cheat Sheet Series][6])

### 2.3 Required audit finding format

For each issue found, output:

* Rule ID:
* Severity: Critical / High / Medium / Low
* Location: file path + component/function + line(s)
* Evidence: the exact code/config snippet
* Impact: what could go wrong, who can exploit it
* Fix: safe change (prefer minimal diff)
* Mitigation: defense-in-depth if immediate fix is hard
* False positive notes: what to verify if uncertain

---

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest “production baseline” that prevents common React frontend misconfigurations.

### 3.1 Production build and configuration hygiene (MUST)

* MUST ship a production build (minified, no dev-only overlays/tools, correct mode flags).
* MUST ensure build-time configuration does not embed secrets into the shipped JS/HTML/CSS. Build-time “environment variables” are not secret; treat them as public. ([create-react-app.dev][1])
* SHOULD treat source maps as sensitive operational artifacts:

  * Either don’t publish them publicly, or publish them only where intended (e.g., behind auth or to an error-reporting provider), because they can reveal code structure and internal URLs.

### 3.2 Browser-enforced protections (SHOULD, but baseline expectation for modern apps)

* SHOULD deploy a CSP as defense-in-depth against XSS, and keep it compatible with your React build (avoid `unsafe-inline` and `unsafe-eval` unless strictly necessary and documented). ([OWASP Cheat Sheet Series][2])
* SHOULD use Subresource Integrity (SRI) for any third-party script/style loaded from a CDN (or self-host instead). ([MDN Web Docs][7])
* SHOULD enable clickjacking defenses via `frame-ancestors` (CSP) and/or `X-Frame-Options`, unless embedding is an explicit product requirement. ([MDN Web Docs][8])

### 3.3 High-risk features baseline (MUST if used)

* If rendering any user-provided HTML/markdown/rich text:

  * MUST sanitize before insertion and avoid raw DOM sinks. ([OWASP Cheat Sheet Series][9])
* If using service workers / PWA:

  * MUST serve over HTTPS and implement a safe caching/update strategy (service workers are powerful request/response proxies). ([MDN Web Docs][10])

---

## 4) Rules (generation + audit)

Each rule contains: required practice, insecure patterns, detection hints, and remediation.

### REACT-CONFIG-001: Never embed secrets in the client bundle (env vars are public)

Severity: Critical (if secrets exposed)

Required:

* MUST NOT place secrets in React code, in `public/` assets, or in build-time environment variables intended for client consumption.
* MUST assume any value available to the React app at runtime can be extracted by an attacker.

Insecure patterns:

* Using build-time env vars for secrets:

  * `process.env.REACT_APP_*` containing private keys or credentials.
  * `import.meta.env.VITE_*` containing secrets.
* Hard-coded secrets in JS/TS, `.env` committed, or secrets in `public/config.json` served to all users.

Detection hints:

* Search for:

  * `REACT_APP_`, `VITE_`, `NEXT_PUBLIC_`, `process.env.`, `import.meta.env.`
  * `apiKey`, `secret`, `token`, `private`, `password`, `client_secret`
* Inspect `public/` for runtime config JSON.

Fix:

* Move secrets server-side (API, BFF, serverless function).
* Use a backend to mint short-lived, scoped tokens if the browser needs to call third-party APIs.

Notes:

* CRA explicitly warns not to store secrets and notes env vars are embedded into the build and visible to anyone inspecting files. ([create-react-app.dev][1])
* Vite explicitly notes that variables exposed to client code end up in the client bundle and should not contain sensitive info. ([vitejs][11])

---

### REACT-XSS-001: Do not use `dangerouslySetInnerHTML` with untrusted content (sanitize or avoid)

Severity: High (Only if you can prove attacker-controlled HTML reaches it)

Required:

* MUST avoid `dangerouslySetInnerHTML` unless absolutely necessary.
* If it must be used:

  * MUST sanitize untrusted HTML with a proven sanitizer (e.g., DOMPurify) and an allowlist-oriented configuration.
  * MUST keep the sanitization logic centralized and heavily reviewed.
  * SHOULD add a CSP and consider Trusted Types (see REACT-TT-001).

Insecure patterns:

* `<div dangerouslySetInnerHTML={{ __html: userHtml }} />` where `userHtml` is from API/URL/storage.
* “Sanitization” done with regexes, ad-hoc stripping, or incomplete allowlists.

Detection hints:

* Grep: `dangerouslySetInnerHTML`, `__html:`
* Trace the origin of the HTML string (API/CMS/URL/localStorage).

Fix:

* Replace with safe rendering:

  * Render structured data as React elements/components instead of HTML strings.
  * If rich text is required, sanitize with DOMPurify (or equivalent) and render the sanitized output.
* Add CSP; remove dangerous sinks where possible.

Notes:

* React explicitly warns that `dangerouslySetInnerHTML` is dangerous and can introduce XSS if misused. ([React][12])
* OWASP explicitly calls out React’s `dangerouslySetInnerHTML` witho