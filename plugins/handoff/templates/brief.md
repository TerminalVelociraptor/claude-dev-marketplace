<!-- check: max-lines=150 -->
# Handoff: <short title>

Written <timestamp> from <working directory>.

## Terms
<!-- check: optional -->
Words this session gave a local meaning, one line each. Include any that clash with the project's
own docs, such as "step" in a plan vs. "stage" in a process doc. Leave this section out if there
are none.

## Goal
What the user is ultimately trying to achieve, and what "done" looks like. If there is a Plan,
keep this short and point to it.

## Current state
What is done, what is in progress, and what is untouched. Include branch and uncommitted changes.
Mark each claim verified or unverified.

## Decisions
Each decision the user confirmed this session and why, including options rejected and the reason.
If there is a Plan, list here only decisions that apply to several steps; the rest go in their
step. Anything assumed but never confirmed belongs under Undecided or Open questions, not here.

## Plan
<!-- check: optional, steps -->
Only when the session produced a multi-step plan that isn't finished. One `### Step N: <name>`
per step, each with all four labels:

**Deliverables:** The exact files or outputs.
**Agreed:** Behavior the user confirmed, with reasons.
**Undecided:** Details nobody confirmed, including ones you would have to decide while building
the step even if nobody raised them. The next agent proposes these before building.
**Done when:** How the step's result is checked.

## Dead ends
Approaches tried that failed or were abandoned, and why, so they are not retried.

## Constraints and preferences
Requirements, gotchas, and user preferences stated this session that are not already in
CLAUDE.md or memory.

## Key files
<!-- check: paths-exist -->
One list item per file, starting with its path in backticks (`path` or `path:line`), then one line
on its role. Every path must already exist; files still to be built belong in the Plan.

## Open questions
Unresolved questions, and who or what can answer them.

## Next steps
An ordered list the next agent can start on immediately, with exact commands where relevant.
