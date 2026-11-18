---
name: sol-loop
disable-model-invocation: true
description: >-
  Use on explicit invocation or from an authorised full-send or full-stop run for a bounded review and repair loop on the same intended change.
---


# Sol loop

Independently adapted from [tstack](https://github.com/t3dotgg/tstack)
(`NOTICE.txt`).

1. Identify and record the comparison base, intended change, and current candidate.
   Run covering checks and freeze the scoped diff for `code-review`. Respect any
   required independent reviewer and screen outgoing evidence for sensitive material.
2. Verify each significant finding against the source. Fix the demonstrated case
   with the smallest change and a focused check when practical. Record why any
   disputed or out-of-scope finding was declined.
3. Rerun the relevant checks. Review each material revision against the same intent
   and base, carrying unresolved findings and their evidence forward. A score or
   approval attaches to its own candidate. No new round is needed for purely
   editorial changes that leave the reviewed behaviour and decision unchanged.
4. Stop when the current revision clears review, when the same objection recurs
   without new evidence, or after three substantive rounds. Report the final
   revision, checks, and unresolved items. Honour any required review gate before
   delivery.

The loop leaves GitHub actions to the workflow that authorised them.
