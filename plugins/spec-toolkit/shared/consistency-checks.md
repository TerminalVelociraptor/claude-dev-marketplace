# Consistency Check Procedure

Shared procedure for checking a spec's internal coherence. Used standalone by the
`spec-consistency` skill and as the first pass of `spec-evaluator`. This check is purely
internal to the document — it does not use the web and does not score completeness.

## What to check

Read the whole spec first, then check for these, in roughly this priority:

1. **Direct contradictions.** Two statements that cannot both be true (e.g. "the API is
   stateless" in one section, "the API caches session state per connection" in another;
   or a latency target of 200 ms in the quality section and 500 ms in an SLA table).

2. **Terminology drift.** The same concept named differently across sections (e.g.
   "user" vs "account" vs "principal" for the same entity), or the same term used for two
   different concepts. Flag each cluster and propose one canonical term.

3. **Diagram / text disagreement.** A component, arrow, or data flow shown in a diagram
   that the prose contradicts or omits, or vice versa. Names in diagrams that don't match
   the names used in text.

4. **Numeric / threshold mismatches.** The same quantity stated with different values in
   different places (limits, timeouts, capacities, versions, ports, sizes).

5. **Reference integrity.** Cross-references that point to sections, decisions, or
   components that don't exist or have been renamed. ADRs referenced by number that are
   missing or superseded without the reference updating.

6. **Decision vs implementation mismatch.** A decision recorded one way (e.g. "we will use
   Postgres") but described differently elsewhere in the spec (e.g. a data section assuming
   a document store).

## How to report

For each finding, give:

- **Location(s):** the sections or line ranges where the conflicting statements appear.
- **The conflict:** quote or closely point to both sides so it is auditable.
- **Severity:** *blocking* (a genuine contradiction that makes the spec unimplementable as
  written) vs *drift* (naming/reference inconsistency that should be tidied but isn't fatal).
- **Suggested resolution:** which version is likely correct if inferable, or a note that the
  author must decide. Do not silently pick a side on a substantive contradiction — surface it.

## Rules

- Report only genuine inconsistencies. Two sections covering related topics at different
  levels of detail is not a contradiction.
- Do not rewrite the spec. Identify the conflicts and propose resolutions; the author decides.
- If the spec is internally consistent, say so plainly rather than inventing minor nits.
