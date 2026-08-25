# jQuery Frontend Security Spec (jQuery 4.0.x, modern browsers)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new jQuery-based frontend code.
2. **Security review / vulnerability hunting** in existing jQuery-based code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, or commit secrets (API keys, passwords, private keys, session tokens, refresh tokens, CSRF tokens, session cookies).
* MUST treat the browser as an attacker-controlled environment:

  * Frontend checks (UI gating, “disable button”, hidden fields, client-side validation) MUST NOT be treated as authorization or a security boundary.
  * Server-side authorization and validation MUST exist even if frontend is “correct”.
* MUST NOT “fix” security by disabling protections (e.g., relaxing CSP to allow `unsafe-inline`, enabling JSONP “because it works”, adding broad CORS, disabling sanitization, suppressing security checks).
* MUST provide evidence-based findings during audits: cite file paths, code snippets, and relevant configuration values.
* MUST treat uncertainty honestly: if a protection might exist at the edge (CDN/WAF/reverse proxy headers like CSP), report it as “not visible in repo; verify at runtime/config”.

---

## 1) Operating modes

### 1.1 Generation mode (default)

When asked to write new jQuery code or modify existing jQuery code:

* MUST follow every **MUST** requirement in this spec.
* SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
* MUST prefer safe-by-default patterns: text insertion, DOM node construction, allowlists, and proven sanitization libraries over custom escaping.
* MUST avoid introducing new risky sinks (HTML string building, dynamic script loading, JSONP, inline script/event-handler attributes, unsafe URL assignment, unsafe object merging).

### 1.2 Passive review mode (always on while editing)

While working anywhere in a repo that uses jQuery (even if the user did not ask for a security scan):

* MUST “notice” violations of this spec in touched/nearby code.
* SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)

When the user asks to “scan”, “audit”, or “hunt for vulns”:

* MUST systematically search the codebase for violations of this spec.
* MUST output findings in the structured format (see §2.3).

Recommended audit order:

1. jQuery sourcing, versions, and dependency hygiene (script tags, lockfiles, CDN usage, SRI).
2. CSP / Trusted Types / security headers posture (in repo and at runtime if observable).
3. DOM XSS: untrusted sources → jQuery sinks (`.html`, `.append`, `$("<…>")`, `.load`, etc.).
4. Script execution sinks: JSONP, `dataType:"script"`, `$.getScript`, dynamic `<script>` insertion.
5. URL/attribute assignment (`href`, `src`, `style`, `on*` attributes).
6. Prototype pollution / unsafe object merging (`$.extend` patterns).
7. AJAX auth patterns + CSRF for cookie-based sessions.
8. Third-party plugins and untrusted content rendering paths (comments, WYSIWYG, markdown-to-HTML).

---

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)

Examples include:

* Any data from the server that originates from users (user profiles, comments, “display name”, rich text, filenames).
* Data from third-party APIs or services.
* Browser-controlled sources:

  * `location.href`, `location.search`, `location.hash`
  * `document.URL`, `document.baseURI`, `document.referrer`
  * `window.name`
  * `localStorage` / `sessionStorage`
  * `postMessage` event data (unless strict origin and schema validation exists)
  * Any DOM content that could have been injected previously (stored XSS)

### 2.2 High-risk “sinks” in jQuery contexts

A sink is a code path where untrusted input can become interpreted as executable code or HTML.

Key jQuery sink categories:

* HTML insertion / parsing:

  * DOM manipulation methods that accept HTML strings such as `.html()`, `.append()`, and related methods (see CVE notes below). ([NVD][1])
  * `$(htmlString)` (when the argument can be interpreted as HTML markup).
  * `jQuery.parseHTML(html, …, keepScripts)` especially with `keepScripts=true`. ([jQuery API][2])
  * `.load(url)` (loads HTML into DOM; has special script execution behavior). ([jQuery API][3])
* Script execution / dynamic code loading:

  * `$.getScript()` / `$.ajax({ dataType: "script" })` (executes fetched JavaScript). ([jQuery API][4])
  * JSONP (`dataType: "jsonp"` or implicit JSONP behavior) (executes remote JavaScript as a response). ([jQuery API][5])
  * `eval`, `new Function`, `setTimeout("…")`, `setInterval("…")`, `$.globalEval` (if present)
* Dangerous attribute assignment:

  * Assigning untrusted strings to `href`, `src`, `srcdoc`, `style`, or event-handler attributes (`onload`, `onclick`, etc.)
  * `javascript:` URLs are particularly dangerous and discouraged. ([MDN Web Docs][6])

### 2.3 Required audit finding format

For each issue found, output:

* Rule ID:
* Severity: Critical / High / Medium / Low
* Location: file path + function/component + line(s)
* Evidence: the exact code/config snippet
* Impact: what could go wrong, who can exploit it
* Fix: safe change (prefer minimal diff)
* Mitigation: defense-in-depth if immediate fix is hard
* False positive notes: what to verify if uncertain

---

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest “production baseline” that prevents common jQuery-related security failures.

### 3.1 Use a supported, patched jQuery version (MUST)

* MUST use a supported jQuery major version and keep it updated.
* As of 2026-01-27, the jQuery project ships jQuery 4.0.0 as the latest major release. ([blog.jquery.com][7])
* If you must support very old browsers (notably IE < 11), jQuery 4 does not support them and you may need to stay on jQuery 3.x; treat this as a higher risk posture and patch aggressively. ([blog.jquery.com][7])

### 3.2 Load jQuery safely (MUST)

* MUST load jQuery only from:

  * Your own build pipeline (bundled via npm/yarn + lockfile), or
  * The official jQuery CDN / a trusted CDN with Subresource Integrity (SRI) enabled.
* If loading from a CDN, SHOULD use SRI (`integrity`) and correct `crossorigin` settings; the jQuery project explicitly supports and recommends SRI on its CDN. (Retrieved from [jquery.com][8])

### 3.3 CSP + Trusted Types (SHOULD, and MUST where available/required by policy)

* SHOULD deploy a Content Security Policy (CSP) that reduces XSS impact (especially `script-src` restrictions and avoiding `unsafe-inline`). If not done through HTTP server, this can be done through the `<meta http-equiv="Content-Security-Policy" content="...">` tag. ([OWASP Cheat Sheet Series][9]) NOTE: It is most important to set the CSP's script-src. All other directives are not as important and can generally be excluded for the ease of development.
* SHOULD consider Trusted Types as a strong defense-in-depth against DOM XSS. ([W3C][10])
* If you deploy the CSP directive `require-trusted-types-for`, then code MUST route DOM-injection through Trusted Types policies. ([MDN Web Docs][11])
* Note: jQuery 4.0 explicitly added Trusted Types support so that TrustedHTML can be used with jQuery manipulation methods without violating `require-trusted-types-for`. ([blog.jquery.com][7])

### 3.4 Security headers and cookie posture (defense in depth; SHOULD)

Even though these are typically set server-side, they materially reduce the blast radius of jQuery-related mistakes. However if the context is only the frontend web application, these cannot be acted on.

* SHOULD set common security headers (CSP, `X-Content-Type-Options: nosniff`, clickjacking protection via `frame-ancestors` / `X-Frame-Options`, `Referrer-Policy`). ([OWASP Cheat Sheet Series][12])
* SHOULD avoid storing long-lived secrets/tokens in places accessible to JavaScript (like `localStorage`