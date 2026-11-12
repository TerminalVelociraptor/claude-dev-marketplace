---
name: write-plan
description: >-
  Rules for writing the plan file in plan mode: a fixed section template, units U1, U2… each with
  Deliverables, Files, Contract, Content, Gotchas and Done when, Agreed/Undecided/Assumed decisions,
  and a pre-exit checklist that runs over-engineering-check before ExitPlanMode. Use whenever plan
  mode is active and a plan is being written or revised. Not for planning talk outside plan mode.
---

Say `write-plan loaded`.

# Writing a plan

These rules govern the plan file while plan mode is active.

**The executor** is the agent that implements the plan: a fresh, possibly less capable agent with no
conversation context. It sees only the plan and the files the plan names, and never sees this skill.

## Before writing

- Investigate cheaply first (existing conventions, git state) so the plan fits what is actually there.
  If scouting the codebase would help, propose it to the user (haiku is usually enough).
- Point at existing code to reuse by path and a stable anchor (a function, class or heading name, or a
  short quote), not by line number: an earlier unit may change the file before a later unit reads it.
  Where the code is not in the working tree (deleted, only in git history, in another repo), paste it
  into the plan. Never cite a path the executor cannot open.

## Structure

Read [resources/template.md](resources/template.md) and write the plan in its section order. Keep every
plan-level section, writing `None.` where it has nothing; leave out a unit field with nothing to say.

- **Context** says why the change is being made: the problem, what prompted it, the intended outcome.
  **Goal** and **Not doing** say what we are building and what we are not.
- Break the work into small, actionable units the executor can implement and the user can review. Don't
  split logically grouped work just to make units small. If a unit is larger or more complex than the
  others, say so and why.
- Write each unit so the executor could implement it without guessing. It may open the files the unit
  names; anything else it would have to look up, infer or decide goes in the unit or under Undecided.
- Label units U1, U2, …, each with its own heading, so each unit can be referenced by its label.
- **Decisions** has three lists, each entry naming the units it affects: **Agreed** (confirmed by the
  user), **Undecided** (still open for the user) and **Assumed** (decided without the user's
  confirmation). Approving the plan approves its Assumed entries, so list every unconfirmed choice there.
- **Conventions** states once: language/runtime version, style, naming, test runner and test-file
  naming, taken from the repo. In an empty repo, write `See Decisions › Assumed` and list each
  convention there instead.
- **Gotchas:** record every gotcha found so far. Put each in the Gotchas field of the unit it affects;
  only cross-cutting ones go in the plan-level section.
- **Dependencies** is always present, so the executor knows the order: which units depend on which, or
  `None: units are independent.`
- **Execution rules** gives the executor its stop-and-ask triggers: the defaults in the template plus
  any this plan needs. The default is to stop and ask, never to work around.

## Unit fields

- **Files:** create / modify / must not touch.
- **Contract:** inputs, outputs, errors, invariants.
- **Content:** where the file's wording is the deliverable (a prompt, skill, agent, template, config,
  doc), the full drafted text. For code: the contract, the test cases, and the exact rules for anything
  the executor would otherwise invent (a parsing rule, a regex, an algorithm). Write code out only where
  prose would be ambiguous, mark it as an untested draft, and leave glue to the executor.
- Length is never a reason to sketch wording. The test is whether the executor could produce the file
  without inventing wording, algorithms or names.
- **Done when** must be checkable: a command that passes or a behavior the user can observe. Name the
  expected output, not just a zero exit, and say how the check would fail. A check that cannot fail is
  not a check. For code, the test cases are the check; for a wording deliverable, name what a reviewer
  compares it against, such as each rule in the source. If Done when is the same for every unit, give it
  once under Verification.
- For units that write tests, list the cases as a table (input → expected) so the executor doesn't
  invent coverage. Include a row for each edge of every threshold or comparison (exactly at it, and one
  either side) and for each optional input left undefined.

## Before ExitPlanMode

Run these steps before calling ExitPlanMode, and again after any change to the plan:

1. Verify every path, command, commit, file state and gotcha the plan asserts. Mark each one you could
   not verify `(unverified)`.
2. Check the plan against the template: every plan-level section present, every unit under its own
   heading with the fields it needs.
3. Run `workflow-preferences:over-engineering-check` on the plan, with its Goal and Not doing as the
   goal and non-goals.
   - **Findings:** post the report, then ask with AskUserQuestion which proposed reworks to apply.
     Revise the plan only as the user chooses, and record each outcome where the executor will see it:
     a rework that removed something worth keeping out goes under **Not doing**; a declined finding goes
     under **Decisions › Agreed** with the user's reason. Then start these steps again.
   - **No findings:** call ExitPlanMode.
