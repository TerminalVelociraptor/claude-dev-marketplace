---
name: spec-factcheck
description: Validate the technical claims and assumptions in a design or architecture spec against the current state of the world using web search, flagging any that are wrong, outdated, or unsupported. Use this when the user wants to verify or validate the technical assertions, assumptions, or facts in a spec ("are these assumptions still valid?", "fact-check my design doc", "verify the technical claims here", "is any of this out of date?"). For a full graded review use spec-evaluator; for internal contradictions only use spec-consistency.
---

# Spec Technical Fact-Check

Validate the checkable technical claims in a spec using web search, and be honest about
which claims cannot be checked this way. This is the standalone version of the fact-check
pass.

## Load the procedure

Read the shared fact-check procedure and follow it exactly, including its abstention rules:

```
${CLAUDE_PLUGIN_ROOT}/shared/factcheck-procedure.md
```

## Get the spec

- Fact-check the spec the user provided or pasted.
- If they referred to a spec without providing it, ask for the file or path. Do not invent one.
- If they name specific claims or sections to check, prioritize those, but still scan the
  whole spec for other checkable assertions unless told to limit scope.

## Behavior

- Extract the web-checkable claims, verify each against current authoritative sources, and
  report Confirmed / Wrong / Outdated / Unsupported per the procedure, with sources for any
  Wrong or Outdated finding.
- List the non-web-verifiable claims (internal facts, design opinions, future predictions)
  separately, labeled as deliberately not judged — do not fake a verdict on these.
- Do not rewrite the spec; report findings and correct facts, and let the user revise.
