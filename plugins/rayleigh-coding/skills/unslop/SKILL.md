---
name: unslop
description: >-
  Use when the user asks to "de-slop this", "remove AI tells", "make this read
  human", "fix this README/blog/release-note prose", or hands over
  machine-flavoured writing (docs, READMEs, PR descriptions, changelogs,
  blog drafts) for repair. NOT for drafting new documents from scratch
  (use dev-readme-writer or dev-docstring) or commit messages
  (use dev-commit-message).
---

# Unslop

Repair existing text so it stops reading as machine-generated. Removing
patterns is half the job; the other half is putting specificity back in.
Sterile, voiceless prose is just as obvious as puffery.

## 1. Bound the edit

Record before touching anything:

- the file or selection, its audience, and its genre (reference doc,
  announcement, changelog);
- the intended tone, so repair does not flatten it;
- what must survive untouched: numbers, code identifiers, commands, paths,
  citations, caveats, headings other tools parse.

Never optimise for an AI-detector score. A flagged pattern is evidence to
inspect, not proof that a sentence must go. Blanket word or punctuation bans
produce worse text than the tell did.

## 2. Repair pass

1. Scan for the patterns below and list what you found.
2. Rewrite. Preserve meaning, match the intended tone.
3. Add voice (section 4).
4. Self-audit (section 5).

## 3. Patterns to detect and fix

### Content

1. **Puffery.** "game-changer", "revolutionary", "seamless experience",
   "cutting-edge". Cut it and state what actually happened or works.
2. **Vague attribution.** "developers report", "the community agrees". Name
   the source (issue, benchmark, RFC) or delete the claim.
3. **Promotional framing.** "blazingly fast", "effortlessly", "powerful"
   without a number. Replace with the measurement or delete the adjective.
4. **Formulaic symmetry.** "Despite these challenges, X continues to thrive."
   Replace with specific facts.
5. **Superficial trailing clauses.** "...ensuring a smooth workflow",
   "...highlighting the importance of X". Delete, or expand into a real
   statement with evidence.

### Vocabulary

6. **AI-favourite words.** delve, leverage, utilize, robust (unmeasured),
   seamless, landscape (abstract), tapestry, testament, underscore, pivotal,
    intricate, holistic. Swap for the plain word.
7. **Fancy verbs for "is" and "has".** "serves as", "stands as", "boasts",
   "features". Say "is" or "has".
8. **Synonym cycling.** Three names for one component in one paragraph. Pick
   the canonical identifier and repeat it; in code docs repetition aids
   search.
9. **"Not just X, but Y."** State the point directly.
10. **Forced groups of three.** Use the natural number of items.

### Style and formatting

11. **Em dash overuse.** Prefer periods and commas for separation. If a
    sentence needs a dash to parse, split it.
12. **Boldface sprawl.** Do not bold every proper noun, flag, or acronym.
13. **Inline-header lists that restate themselves.** "**Performance:**
    Performance improved..." becomes prose. A bold lead-in followed by
    genuinely new detail is fine.
14. **Title case headings.** Use sentence case.
15. **Decorative emoji** in headings and bullets. Remove unless the genre
    genuinely calls for them.
16. **Curly quotes** in docs and code fences. Straight quotes.

### Chatbot artifacts

17. **Assistant pleasantries.** "I hope this helps!", "Let me know if you
    have questions!", "Great catch!". Delete from anything meant to ship.
18. **Hedge-stacks.** "could potentially possibly". One honest qualifier
    maximum.
19. **Filler openers.** "It is important to note that", "In order to",
    "Due to the fact that". Delete or shorten.

### Jargon

20. **Metaphor nouns posing as architecture.** substrate, bedrock,
    scaffolding, flywheel, north star, paradigm, primitive (as noun) used
    loosely. Substitute the concrete word: base, helper library, loop,
    goal, model, function.
21. **Feelings instead of mechanisms.** "stays out of your way", "SQL you
    can read", "types that follow your schema". Name the behaviour: which
    call returns what, which check fails when, what number changed. If you
    cannot restate a sentence as an instruction, fact, or measurement, cut
    it. Test: could the sentence drop unchanged into another project's
    README? Then it says nothing about this one.

### Sentence mechanics

22. **Passive voice hiding the actor.** "errors are logged" becomes
    "the runner logs errors". Passive stays only when the actor is unknown
    or irrelevant.
23. **Adverbs propping up weak verbs.** "runs quickly" becomes the timing
    number or "is fast".
24. **Dense sentences that force backtracking.** One idea per sentence;
    split or drop clauses until parsing is linear.
25. **Generic conclusions.** "The future looks bright." End with the next
    concrete step or stop earlier.

## 4. Put voice back in

- **Be specific.** Concrete nouns, real numbers, named files. Specificity is
  the strongest anti-slop signal available.
- **Let sentence length follow the argument.** A short sentence can land a
  result; a longer one can carry a causal chain. Vary naturally, never on
  quota.
- **Have a position where the author has one.** Trade-offs acknowledged
  honestly read more human than neutral listing. Do not invent opinions the
  source does not hold.
- **Keep useful structure.** Roadmaps, tables, caveats, and section labels
  are functional, not tells. Do not destroy document architecture to seem
  casual.
- **Do not manufacture personality.** Forced fragments, fake enthusiasm, and
  staged messiness are their own detectable pattern.

## 5. Self-audit before handing back

1. Does the opening state the actual problem or change, not its mood?
2. Is every claim now tied to a mechanism, number, or named source?
3. Did the claim ledger survive: versions, flags, commands, caveats?
4. Would any paragraph still fit a different project after swapping two
   nouns? If yes, make it concrete or remove it.
5. Does it read like someone competent wrote it for a reason, rather than
   like a "humanised" rewrite?

Report the pattern classes you fixed and any sentences left intentionally
untouched because they were load-bearing.
