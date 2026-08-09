# Technical Fact-Check Procedure

Shared procedure for validating the technical claims in a spec against the current state of
the world, using web search. Used standalone by the `spec-factcheck` skill and as a pass of
`spec-evaluator`.

The goal is to catch technical assertions that are wrong, outdated, or unsupported — before
they get built on. The discipline that makes this useful rather than noisy is knowing which
claims are checkable and abstaining on the rest.

## Step 1: Extract the checkable claims

Read the spec and pull out the concrete technical assertions. A claim is **web-checkable**
when it is about the external, current-world state of a technology, standard, or service —
something a reliable source could confirm or refute. Examples:

- "Library/framework X supports feature Y" / "X requires runtime version Z".
- "Service X has a rate limit of N" / "X's free tier includes Y".
- "Protocol/standard X mandates Y" / "Algorithm X is considered broken/deprecated".
- "X is compatible with Y" / "X and Y cannot be used together".
- "The current stable version of X is N" / "X reached end-of-life".

## Step 2: Do NOT verdict on non-checkable claims

Explicitly set these aside and label them as *not web-verifiable* rather than validating them.
Pretending to confirm these is the main failure mode to avoid:

- **Claims internal to this system** — "our peak load is 5,000 rps", "the team has three
  backend engineers", "our budget is $X". These are the author's own facts; the web cannot
  confirm them. You may note if an internal claim is *self-inconsistent* with another part of
  the spec, but that is a consistency finding, not a fact-check verdict.
- **Design opinions / judgment calls** — "a microservices approach is best here",
  "this is the simplest design". These are arguable positions, not checkable facts. You may
  note if a claim contradicts a strong industry consensus, but frame it as "consensus differs",
  not "false".
- **Predictions about the author's future system** — "this will scale to 10x". You can check
  whether the chosen technology is *capable* of that in general, but not whether this specific
  system will achieve it.

## Step 3: Verify each checkable claim

- Search for each checkable claim. Prefer primary/authoritative sources (official docs,
  the project's own release notes, standards bodies, vendor pricing pages) over aggregators
  and forums.
- Because technology facts change, search for the current state rather than relying on prior
  knowledge — versions, limits, deprecations, and pricing go stale.
- Search each distinct claim separately; do not batch unrelated claims into one query.

## Step 4: Report

For each checkable claim, report one of:

- **Confirmed** — with the source. Keep it brief.
- **Wrong** — the claim contradicts current reliable sources. State the correct fact and cite it.
- **Outdated** — was true, no longer is (e.g. a version or limit has changed). State the current fact.
- **Unsupported** — no reliable source found either way. Flag it as unverified, do not guess.

Then list the **not web-verifiable** claims separately, so the author knows what was
deliberately not judged and can confirm those themselves.

## Rules

- Never render a true/false verdict on a claim you could not actually check. "Unverified"
  and "not web-verifiable" are the honest outputs; a confident verdict on an uncheckable
  claim is worse than saying nothing.
- Cite sources for every Wrong/Outdated finding so the author can confirm.
- Do not rewrite the spec; report findings and correct facts, and let the author revise.
- Respect standard sourcing quality: authoritative over SEO'd, primary over secondary.
