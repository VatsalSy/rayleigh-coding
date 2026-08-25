# Evidence routing

Choose lanes from the anchor and its leads. Do not query every connected
surface merely because it exists.

## Source control and workshop history

Always inspect local Git. Follow renames, pickaxe exact strings/thresholds,
read introducing and reshaping patches, related tests/comments, and linked
issues. Use `gh` only for GitHub workshop records. Use Origin records for an
Origin change when available. Never invent parity between the two review
systems.

Best for implementation-time rationale and alternatives discussed during
review. Pitfalls include squash history, misleading messages, copied patterns,
and bot commits.

## Repo docs

Inspect in-tree README, ADRs, `AGENTS.md`, design notes, and comments that
state motivation. A public README may omit private operational rationale by
design; treat silence as a gap, not proof of absence.

## Issues and long-form documents

Follow linked GitHub Issues, Origin changes, or tickets when the anchor points
there. Read the complete relevant record, including comments and parent/child
links. Distinguish a proposal/draft from the decision that actually shipped.

## Scoped Slack (lead required)

Use Slack tools only when the user provides a concrete lead: a message URL,
channel plus tight date window, or named thread. Fetch the full thread. Do not
search DMs, unrelated private channels, or the whole workspace for colour.
Retention/auth failures are coverage gaps.

## Optional runtime evidence (lead required)

When the question concerns an operational threshold and the user (or a commit
message) names a concrete service artefact, add the owning authority:

- exception/release telemetry (e.g. Sentry) for first/last-seen and stack data;
- deploy or request logs for timing and failure modes.

Use time-bounded queries around the decision window. A graph moving after a
commit is correlation until a PR, incident, or decision record connects them.
Do not start jobs or services merely to reconstruct history.

## Coverage report

For every lane, report one of:

- searched, with query/window and relevant evidence;
- searched, no relevant result within the stated scope;
- unavailable, with the access/tool/retention reason;
- skipped, with a concrete irrelevance reason.

`Probably empty` is not a valid reason. `No lead and outside the bounded
question` is.
