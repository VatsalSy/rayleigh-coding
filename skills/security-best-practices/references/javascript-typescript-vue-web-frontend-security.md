# Vue.js Web Security Spec (Vue 3.x, TypeScript/JavaScript, common tooling: Vite)

This document is designed as a **security spec** that supports:

1. **Secure-by-default code generation** for new Vue code.
2. **Security review / vulnerability hunting** in existing Vue code (passive “notice issues while working” and active “scan the repo and report findings”).

It is intentionally written as a set of **normative requirements** (“MUST/SHOULD/MAY”) plus **audit rules** (what bad patterns look like, how to detect them, and how to fix/mitigate them).

---

## 0) Safety, boundaries, and anti-abuse constraints (MUST FOLLOW)

* MUST NOT request, output, log, or commit secrets (API keys, passwords, private keys, session cookies, auth tokens).
* MUST NOT “fix” security by disabling protections (e.g., weakening CSP, turning on unsafe template compilation, using `v-html` as a shortcut, bypassing backend auth, or “just store the token in localStorage”).
* MUST provide **evidence-based findings** during audits: cite file paths, code snippets, and configuration values that justify the claim.
* MUST treat uncertainty honestly: if a protection might exist at the edge (CDN, reverse proxy, WAF, server headers), report it as “not visible in repo; verify runtime/infra config”.
* MUST remember the frontend trust model: **any code shipped to browsers is attacker-readable and attacker-modifiable**. Secrets and “security enforcement” cannot rely on frontend-only logic.

## CONTINUE_SEE_FULL_FILE
