# HTML Explainer Patterns

Choose one primary pattern from the relationship the reader must understand.
These are structural recipes, not visual templates. Derive typography, colour,
spacing and illustration style from the subject and any existing project
language.

## Selection guide

| Pattern | Use when | Essential elements | Avoid |
|---|---|---|---|
| Aligned comparison | Several alternatives share evaluation axes | Same fields in the same order, decisive differences, recommendation and trade-offs | Unequal detail that quietly favours one option |
| System or mechanism map | Components, variables or actors affect one another | Boundaries, labelled links, direction, legend, critical path and failure/recovery paths | Decorative arrows with no defined relationship |
| Timeline or settled plan | Order, dependency and acceptance gates matter | Milestones, prerequisites, owner, evidence gate, rollback and completion test | Inventing dates or re-planning unsettled work |
| Evidence ledger | Claims have mixed support or competing explanations | Observation/inference/proposal/unknown labels, provenance, discriminating test and confidence limits | Colour that implies certainty unsupported by evidence |
| Annotated review | A diff, module or document needs focused explanation | Real source excerpts, line/file anchors, margin annotations, severity or decision status and reading order | Fabricated findings or screenshots standing in for coverage |
| Decision editor | the user must sort, tune, filter or select structured choices | Reversible controls, constraints, dependency warnings, reset and explicit export | Hidden persistence, uploads, or state with no export |
| Status or incident narrative | Change over time and current truth matter | Current state, chronological evidence, impact, recovery, receipts and unresolved follow-up | Conflating timestamps, observations and causes |

## Aligned comparison

Use a shared schema across every option. Good axes include mechanism, evidence,
compatibility, reversibility, cost, failure mode, validation and next action.
Keep option order stable between desktop and mobile; on narrow screens, stack
each axis with all options together rather than turning each option into an
isolated essay.

Make the recommendation visible but not visually overwhelming. State what
would cause it to change. If one option lacks evidence, show the gap rather
than filling the space with speculation.

## System or mechanism map

Start from the relationship type:

- **flow:** material, data, authority or work moves through stages;
- **dependency:** one component or decision enables another;
- **causal mechanism:** a control parameter changes an intermediate process
  that changes an observable;
- **state machine:** events move the system between named states;
- **ownership map:** people, services or controllers own distinct decisions.

Use HTML/CSS for structured regions and inline SVG for explicit connections.
Every arrow needs a direction and meaning. Use a small legend, highlight one
critical path, and show failure/recovery paths when they are part of the
decision. Provide a linear text fallback for screen readers and printing.

For research, organise the map as mechanism -> scaling or limiting argument ->
observable -> discriminating evidence. Label numerical and experimental
evidence by its actual owner; CoMPhy contributes theory, scaling, asymptotics
and DNS, not collaborator-owned experiments.

## Timeline or settled plan

This pattern renders an already grounded plan. Preserve the plan's exact
commitments and open decisions; do not invent estimates merely to fill a
timeline.

Show:

1. milestone and intended outcome;
2. prerequisite or evidence gate;
3. owner or owning workflow;
4. validation receipt;
5. failure/rollback path;
6. acceptance test.

Use dependency lines only where dependency is real. A sequence is not
automatically a dependency. If the plan is still underspecified, return to
`grill-me` or `create-plan` rather than masking uncertainty with a polished
roadmap.

## Evidence ledger

Use this for research explainers, technical investigations and decision briefs
where source status matters as much as the conclusion.

Give each item an explicit class:

- **Observed:** directly read, measured, rendered, or live-verified.
- **Inferred:** the best interpretation of observations, with the reasoning.
- **Proposed:** an intervention, model, design, or next action.
- **Unknown:** missing evidence, unresolved mechanism, or conflicting result.

For competing explanations, align them against the same predicted signature
and discriminating test. In simulation work, compare matched physical
resolution and detector definitions rather than visually privileging raw grid
level. Use `publication-plots` for actual plots; HTML may arrange and annotate
the verified figures but does not replace the plotting workflow.

## Annotated review

Anchor commentary to real evidence: file and line, diff hunk, rendered element,
or document passage. Keep the untouched source visually distinct from the
annotation. Use severity only when the owning review has established it;
otherwise label comments as question, explanation, risk, or suggestion.

Useful structure:

- orientation: what changed and why;
- reading order: entry point, hot path, seam and failure path;
- source excerpt or diff with tight annotations;
- implications and compatibility;
- validation already run and gaps still open.

Do not paste entire copyrighted documents or large source files merely to make
the page feel complete.

## Decision editor

Use this when manipulating the choice is easier than describing it: triage,
ordering, parameter tuning, prompt comparison, approval/rejection, dependency
selection, or structured annotation.

Requirements:

- start from a sensible, visibly labelled proposed state;
- make every change reversible and include reset;
- show constraints and dependency violations immediately;
- work with pointer and keyboard input;
- keep the state in memory unless local persistence is explicitly useful and
  contains no sensitive data;
- end with a deterministic export: Markdown, JSON, prompt, CSV, or minimal
  diff, depending on the owning workflow.

Build dynamic nodes with DOM APIs and write user-controlled text with
`textContent`. Never compose pasted/source data into `innerHTML` or inline
event-handler strings. Treat imported JSON as untrusted, validate its shape,
and reject unexpected keys or types.

## Status or incident narrative

Lead with current truth and impact, then show the chronology that supports it.
Distinguish event time, observation time and report time. Separate symptom,
diagnosis, action and completed verification. Give recovery and rollback equal
visual weight to the happy path for infrastructure work.

End with exact receipts and unresolved follow-up. A green status is justified
only by current evidence; absence of an error is not a health check.

## Visual language

Prefer information hierarchy over decoration:

- one clear title and purpose;
- a short orientation region, not a marketing hero;
- a restrained palette whose colours have defined meaning;
- typography and spacing that support the reading path;
- consistent alignment across comparable elements;
- inline SVG only when it communicates a relationship;
- no gradients, glass effects, oversized numerals, arbitrary metric cards,
  fake dashboards, or emoji decoration by default.

Reuse a real project design system when one exists. Otherwise choose a modest,
subject-specific direction and explain colour semantics in a legend. Do not
use CoMPhy logos or publication branding unless the named target is approved
for that identity.

## Accessibility and resilience

- Use semantic landmarks, one `h1`, logical heading levels and descriptive
  control labels.
- Preserve DOM reading order when CSS changes layout.
- Provide visible focus and a complete keyboard path.
- Do not encode status or evidence class by colour alone.
- Respect `prefers-reduced-motion`; avoid essential information in animation.
- Ensure useful reflow at narrow widths without horizontal page scrolling.
- Add print styles that retain labels, provenance and conclusions.
- Give SVG a descriptive accessible name and a textual fallback.
- Make controls fail safely and keep the core explanation readable without
  JavaScript where practical.

## Provenance and export

Keep provenance close to the claim it supports. Local project sources may be
shown as repository-relative paths and line anchors; public-candidate pages
use publishable citations or a compact source list. Never expose private
absolute paths simply because they are convenient during generation.

An interactive artefact is not the system of record. Export decisions in the
smallest format the owning workflow can consume, and show exactly what will be
copied or downloaded before the user triggers it.
