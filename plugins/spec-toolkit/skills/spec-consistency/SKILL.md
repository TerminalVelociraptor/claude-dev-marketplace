---
name: spec-consistency
description: Check a design or architecture spec for internal consistency only — contradictions, terminology drift, diagram/text mismatches, and conflicting numbers — without a full evaluation. Use this when the user has edited or rewritten parts of a spec and wants to confirm it still holds together, or asks specifically about consistency, contradictions, or coherence ("is my spec still consistent?", "did I contradict myself?", "check this for conflicts"). For a full graded review use spec-evaluator instead; for validating technical claims use spec-factcheck.
---

# Spec Consistency Check

Run a fast internal-coherence check on a spec. This is the standalone version of the
consistency pass — no completeness scoring, no web search, no concision.

## Load the procedure

Read the shared consistency procedure and follow it exactly:

```
${CLAUDE_PLUGIN_ROOT}/shared/consistency-checks.md
```

## Get the spec

- Evaluate the spec the user provided or pasted.
- If they referred to a spec without providing it, ask for the file or path. Do not invent one.
- If they point to specific sections they just changed, pay special attention there, but still
  read the whole spec — a change in one section most often breaks consistency with another.

## Output

Follow the reporting format in the shared procedure: grouped findings with locations, the
conflict, severity (blocking vs drift), and a suggested resolution. Lead with blocking
contradictions, then drift. If the spec is consistent, say so plainly.
