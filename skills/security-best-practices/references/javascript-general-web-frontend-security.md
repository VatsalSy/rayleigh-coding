# Frontend JavaScript/TypeScript Web Security Spec (Vanilla Browser JS/TS, Modern Browsers)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new frontend JavaScript/TypeScript (no specific framework assumed).
2. **Security review / vulnerability hunting** in existing frontend code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, hard-code, or commit secrets (API keys intended to be secret, private keys, passwords, OAuth refresh tokens, session tokens, cookies).
  Notes:

  * Frontend code is inherently observable by end users. If a value must remain secret, it must not be in browser-delivered code.
  * If the project uses “public” keys (e.g., publishable analytics keys), they MUST be treated as non-secret and scoped accordingly.

* MUST NOT “fix” security by disabling protections (e.g., weakening CSP with `unsafe-inline`/`unsafe-eval` without justification, removing origin checks for `postMessage`, switching to `innerHTML` for convenience, accepting arbitrary redirects/URLs, or turning off sanitization).

* MUST provide **evidence-based findings** during audits: cite file paths, code snippets, and relevant HTML/CSP/config values that justify the claim.

* MUST treat uncertainty honestly:

  * Security headers (CSP, frame-ancestors, etc.) might be set by server/edge/CDN rather than in repo code. If not visible, report as “not visible here; verify at runtime/edge config.” (Also note that `<meta http-equiv=...>` only simulates a subset of headers; don’t assume other security headers exist just because a meta tag exists.) ([MDN Web Docs][1])

---

## 1) Operating modes

### 1.1 Generation mode (default)

When asked to write new frontend JS/TS code or modify existing code:

* MUST follow every **MUST** requirement in this spec.
* SHOULD follow every **SHOULD** requirement unless the user explicitly says otherwise.
* MUST prefer safe-by-default browser APIs and proven libraries over custom security code (especially for HTML sanitization).
* MUST avoid introducing new risky sinks (DOM XSS injection sinks like `innerHTML`, navigation to `javascript:` URLs, dynamic code execution via `eval`/`Function`, unsafe `postMessage`, unsafe third-party script loading, etc.). ([OWASP Cheat Sheet Series][2])

### 1.2 Passive review mode (always on while editing)

While working anywhere in a frontend repo (even if the user did not ask for a security scan):

* MUST “notice” violations of this spec in touched/nearby code.
* SHOULD mention issues as they come up, with a brief explanation + safe fix.

### 1.3 Active audit mode (explicit scan request)

When the user asks to “scan”, “audit”, or “hunt for vulns”:

* MUST systematically search the codebase for violations of this spec.
* MUST output findings in a structured format (see §2.3).

Recommended audit order:

1. HTML entrypoints (`index.html`, server-rendered templates), script/style includes, and any CSP delivery (header vs meta). ([W3C][3])
2. DOM XSS sinks (`innerHTML`, `document.write`, `insertAdjacentHTML`, event-handler attributes) and their data sources (URL params/hash, storage, postMessage, API responses). ([OWASP Cheat Sheet Series][2])
3. Navigation/redirect handling (`window.location*`, link targets, URL allowlists) including `javascript:` URL hazards. ([MDN Web Docs][4])
4. Cross-origin communication (`postMessage`, iframe embed patterns, sandboxing). ([MDN Web Docs][5])
5. Storage of sensitive data (localStorage/sessionStorage) and assumptions about trust. ([OWASP Cheat Sheet Series][6])
6. Third-party scripts / tag managers / CDNs, and integrity controls (SRI) and policy controls (CSP). ([OWASP Cheat Sheet Series][7])
7. DOM clobbering gadgets and unsafe reliance on `window`/`document` named properties. ([OWASP Cheat Sheet Series][8])

---

## 2) Definitions and review guidance

### 2.1 Untrusted input (treat as attacker-controlled unless proven otherwise)

Examples include:

* URL-derived data: `location.href`, `location.search`, `location.hash`, `document.baseURI`, `new URLSearchParams(location.search)`, routing fragments. ([OWASP Cheat Sheet Series][2])
* DOM content that may include user-controlled markup (comments, profiles, CMS content, markdown-to-HTML output, etc.), especially if inserted dynamically. ([OWASP Cheat Sheet Series][2])
* `postMessage` event data (`event.data`) and metadata (`event.origin`) from other windows/frames. ([MDN Web Docs][5])
* Browser storage: `localStorage`, `sessionStorage`, IndexedDB (contents can be attacker-influenced via XSS or local machine access; never treat as “trusted”). ([OWASP Cheat Sheet Series][6])
* Any data returned from network calls (even if from “your API”), because it may contain stored attacker content that becomes dangerous only when inserted into the DOM. ([OWASP Cheat Sheet Series][2])

### 2.2 Dangerous sink (DOM XSS / code execution sink)

A sink is any API/operation that can execute script or interpret attacker-controlled strings as HTML/JS/URL in a security-sensitive way. High-signal sinks include:

* HTML parsing / insertion: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `document.writeln`. ([OWASP Cheat Sheet Series][2])
* Dynamic code execution: `eval`, `new Function`, `setTimeout("...")`, `setInterval("...")`. ([MDN Web Docs][10])
* Navigation to script-bearing URLs (e.g., `javascript:`) via setters like `Location.href`/`window.location` (and via link `href` if attacker-controlled). ([MDN Web Docs][4])
* Setting event handler attributes from strings, e.g. `setAttribute("onclick", "...")`. ([OWASP Cheat Sheet Series][2])

### 2.3 Required audit finding format

For each issue found, output:

* Rule ID:
* Severity: Critical / High / Medium / Low
* Location: file path + function/class/module + line(s)
* Evidence: the exact code/config snippet
* Impact: what could go wrong, who can exploit it
* Fix: safe change (prefer minimal diff)
* Mitigation: defense-in-depth if immediate fix is hard
* False positive notes: what to verify if uncertain

---

## 3) Secure baseline: minimum production configuration (MUST in production)

This is the smallest baseline that prevents common frontend JS/TS security misconfigurations. Some items are “in repo” (HTML/JS) and some may live at the server/edge.

### 3.1 Content Security Policy (CSP) baseline (SHOULD; MUST for high-risk apps)

* SHOULD deliver CSP via HTTP response headers when possible.
* MAY deliver CSP via an HTML `<meta http-equiv="Content-Security-Policy" ...>` tag when you cannot set headers (e.g., purely static hosting constraints). ([MDN Web Docs][1])
* If using CSP via `<meta http-equiv>`, MUST understand the limitations:

  * The policy only applies to content that follows the meta element (so it must appear very early, before any scripts/resources you want governed). ([W3C][3])
  * The following directives are **not supported** in a meta-delivered policy and will be ignored: `report-uri`, `frame-ancestors`, and `sandbox`. ([W3C][3])
  * “Report-only” CSP cannot be set via a meta element. ([W3C][3])

Practical baseline goals:

* Avoid script sources `unsafe-inline` and `unsafe-eval` (they significantly weaken CSP’s value against XSS). ([MDN Web Docs][10])
* Prefer nonce- or hash-based script policies if you need inline scripts. ([MDN Web Docs][10])
* Consider enabling Trusted Types enforcement where