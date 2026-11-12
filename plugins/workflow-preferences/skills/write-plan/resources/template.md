# <Plan title>

## Context
<Why the change is being made: the problem, what prompted it, the intended outcome.>

## Goal
<What we are building, in one or two sentences.>

## Not doing
- <Out-of-scope item>

## Decisions
### Agreed
- <Decision confirmed by the user> (U1, U2)
### Undecided
- <Question still open for the user> (U3)
### Assumed
- <Choice made without the user's confirmation> (U1)

## Conventions
- Runtime: <language and version>
- Style and naming: <rules>
- Tests: <runner>; files named <pattern>

## Gotchas
- <Gotcha affecting more than one unit> (verified | unverified)

## Dependencies
<U2 depends on U1. | None: units are independent.>

## U1 — <short name>
**Deliverables:** <what exists when the unit is done>
**Files:** create `<path>`; modify `<path>`; must not touch `<path>`
**Contract:** <inputs, outputs, errors, invariants>
**Content:** <full drafted text, or contract + test table + exact rules>
**Gotchas:** <gotchas for this unit only> (verified | unverified)
**Done when:** `<command>` → <expected output>; fails if <condition>

## Verification
<Done when shared by every unit, and an end-to-end check on a real input.>

## Execution rules
Stop and ask, never work around, when:
- the spec is ambiguous or contradicts itself
- a failing test tempts changing the assertion
- the unit needs a file outside its Files list
- <triggers specific to this plan>
