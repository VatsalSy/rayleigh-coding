---
name: html-explainer
description: >-
  Use when the user says "make an HTML explainer", "show this as an interactive
  explainer/decision page", "visualise this report/comparison", or asks for a
  self-contained `.html` decision aid. NOT for production frontends; use
  dev-frontend-design.
user-invocable: true
---

# HTML Explainer

## Purpose

Create a self-contained browser artefact when spatial structure, visual
comparison, progressive disclosure, or small interactions will make serious
work materially easier to understand or decide. Treat HTML as a presentation
and decision layer over grounded evidence, not as a prettier substitute for
thinking or a default replacement for Markdown.

This is a adaptation of the working pattern described in
<https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html>
and illustrated at <https://thariqs.github.io/html-effectiveness/>. It is
independently written, uses no upstream template or runtime dependency, and
keeps CoMPhy's evidence, publication, custody and security boundaries.

## Entry contract

- **Explicit invocation:** `$html-explainer`, "make an HTML explainer",
  "interactive explainer/decision page", or an explicit request for a
  self-contained HTML comparison, report, map, or decision aid authorises
  creation of the local artefact. A site, production page, application or
  reusable UI routes to `dev-frontend-design` first, even if the request says
  "interactive". This skill does not authorise publishing or deployment.
- **Implicit fit:** if an ongoing task would benefit substantially from this
  medium but the user did not request a file, offer it in one sentence and wait
  for acceptance. Do not silently turn an ordinary answer into a file-writing
  project.
- Prefer chat, a small table, Markdown, or Mermaid when the content is short,
  linear, non-interactive, or already clear. HTML that adds decoration but not
  comprehension is a failure.

## Workflow

### 1. Ground the content

Inspect the smallest relevant set of real sources before designing: the
repository and diff, `project.yaml`, nearest `AGENTS.md`, existing plan or
report, tests, data, live state, and task-relevant project context. Never ask
the user for a discoverable fact.

Separate the content into:

- **observed:** directly supported by source or live evidence;
- **inferred:** a reasoned interpretation of that evidence;
- **proposed:** a design, decision, plan, or recommendation;
- **unknown:** an open question or evidence gap.

The visual treatment must preserve those labels. Polished presentation never
upgrades an inference into a result or an unknown into a decision.

### 2. Pass the medium test

Use HTML when at least one of these is central to the task:

- several alternatives need aligned, side-by-side comparison;
- relationships, dependencies, sequence, state, or failure paths are easier
  to grasp spatially;
- dense evidence needs navigation, filtering, tabs, or progressive disclosure;
- a small interaction lets the user test a parameter or organise choices;
- a decision interface needs to export the resulting selection back into the
  owning workflow.

If none applies, stop and answer in the simpler medium. Do not create a
dashboard hero, decorative metric cards, or a slide deck merely because HTML
can.

### 3. Respect the owning workflow

This skill presents work; it does not silently take ownership of it.

- `create-plan` forms implementation plans. Render only a settled plan or an
  explicitly requested visual exploration; never bypass its read-only
  planning contract.
- `deep-research` gathers and synthesises research evidence. HTML may explain
  the completed synthesis, not replace its evidence workflow or canonical
  record.
- `code-review` owns repository review findings. HTML may present an existing
  review or explain a diff, but must not manufacture severity or coverage.
- `publication-plots` remains mandatory for every scientific figure,
  including figures embedded in HTML.
- `comphy-scientific-slides` owns talks and staged scientific decks;
  `jupyter-notebook` owns executable analysis and tutorials;
  `dev-frontend-design` owns production pages, applications and reusable UI.

### 4. Set the content and custody boundary

Before writing, classify the artefact as **internal** or **public-candidate**.

- Internal artefacts may contain relevant operational detail, but never
  credentials, tokens, private keys, passwords, personal identifiers, or
  irrelevant private material.
- Public-candidate artefacts must exclude private hostnames, absolute private
  paths, internal operations, collaborator confidences and personal data.
  Unpublished simulation-derived findings additionally require the owning
  tracker receipt `promotion approved — <finding> -> <target>` before inclusion;
  general approval to make an HTML page is not promotion approval.
- Creating an HTML file grants no authority to upload, host, publish, email,
  message, or deploy it.

Inspect the destination and its repository before writing. Never overwrite an
existing file or absorb unrelated dirty changes unless the user explicitly
requested that exact replacement. Choose a new descriptive filename or stop
when the target collides. Use the user-specified destination when it passes
those checks. Otherwise, in a profiled project, default to
`<project>/scratch/html/<descriptive-slug>.html` and follow `project-tracker`
plus `project-lock` for the tracked context mutation and checkpoint. If no safe
owning project or destination can be resolved, ask one short question rather
than polluting a component repository or private home directory.

Honour inline directives per `../CONVENTIONS.md`.

### 5. Choose one primary pattern

Read `references/patterns.md`, then select the smallest pattern that matches
the relationship being explained. Combine patterns only when the artefact has
one clear reading path; a kitchen-sink page is just another wall of text.

Write a compact internal brief before coding:

1. audience and decision or learning job;
2. source material and evidence status;
3. primary visual pattern;
4. information hierarchy and reading path;
5. useful interaction, if any;
6. export or handoff format;
7. internal/public-candidate boundary.

### 6. Build one self-contained file

Default to a single `.html` file that opens locally without a build step:

- semantic HTML, inline CSS and inline SVG;
- system fonts and local data;
- no CDN, analytics, remote fonts, external scripts, trackers, network fetches,
  or hidden uploads;
- responsive layout with a useful mobile reading order and print/static
  fallback;
- no emoji in filenames, headings, controls, diagrams, or free prose;
- subject-specific visual language derived from the material or an existing
  project design system, not a fixed CoMPhy skin or generic AI-card aesthetic.

JavaScript is optional. Add it only for filtering, toggling, parameter
exploration, navigation, or export that materially improves the task. Keep the
artefact useful when JavaScript is unavailable wherever practical.

For dynamic content:

- use `textContent`, `document.createElement`, DOM properties and
  `addEventListener`;
- do not use `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`,
  `eval`, `new Function`, string timers, inline event-handler attributes, or
  `javascript:` URLs;
- validate structured imported data and allowlist URL protocols and origins;
- treat URL parameters, storage, pasted text, imported JSON and source-derived
  strings as untrusted;
- store no secrets or authentication material in browser storage.

When an editor changes state, provide an explicit export such as copy as
Markdown, copy as prompt, download JSON, or copy minimal diff. The exported
text is the durable handoff; browser state is not project truth.

### 7. Verify the artefact

Use the DOM/XSS construction guidance in `security-best-practices` and use
`playwright` for real-browser validation. Generated or internal HTML does not
go to CodeRabbit merely because that sibling skill mentions corroborating
review. Run repository-aware CodeRabbit only when the artefact is shipping
component code, the owning repository permits external review, and the diff
contains no sensitive or unpublished content.

At minimum:

1. Open the exact local file in a real browser.
2. Capture desktop and narrow/mobile screenshots and inspect both visually.
3. Check the browser console for errors.
4. Exercise every control, keyboard path, and export action.
5. Confirm visible focus, logical heading order, labels, contrast, reduced
   motion behaviour, responsive reflow and print/static readability.
6. Confirm no unexpected network requests or external resource dependencies.
7. Re-read the rendered claims against their sources and the declared
   observation/inference/proposal/unknown labels.

Fix verified problems and repeat the affected checks. Do not call an artefact
verified from source inspection alone.

### 8. Hand off without publishing

Return:

- a clickable local file link;
- one sentence stating its purpose and content boundary;
- the validation performed;
- a screenshot when visual review materially helps;
- any remaining evidence gaps or browser limitations;
- the exported decision/brief when an interactive editor produced one.

If the file lives in tracked project context, checkpoint it before reporting
durability. Publication, hosting and external sharing remain separate explicit
requests routed to their owning skills.

## Gotchas

1. **Recognition is the core skill.** Do not emit HTML for a short explanation,
   a simple table, or because the source article is fashionable.
2. **Presentation cannot repair weak evidence.** Preserve uncertainty and
   provenance; never turn a provisional research reading into a polished
   public claim.
3. **A self-contained file has a strict supply-chain boundary.** Remote fonts,
   CDNs, analytics and convenience libraries violate the default contract.
4. **Interactivity must close the loop.** A decision editor without a clear
   export leaves important state trapped in the browser.
5. **Do not clone one aesthetic across domains.** A research mechanism map, an
   infrastructure recovery path and an administrative decision board should
   not look like the same indigo dashboard.
6. **Browser validation is part of creation.** Source that looks plausible can
   still overflow, hide focus, break on mobile, fail to print, or throw at the
   first click.
7. **Local creation is not publication.** Never deploy or share merely because
   a standalone file is easy to host.
