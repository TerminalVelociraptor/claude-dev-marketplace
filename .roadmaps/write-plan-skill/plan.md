# write-plan skill (issue #10)

## Context

The plan-writing rules live in the global CLAUDE.md (`~/dotfiles/claude/.claude/CLAUDE.md`, section
`# Plans (plan mode only)`), so they load in every session although they only matter in plan mode. Issue #10
moves them into a `workflow-preferences` skill that loads when a plan is written. The issue body was a quick
outline; this plan replaces it. A review of the current rules found defects that the skill text fixes (agreed
with the user): the executor has four names, plan-level sections are scattered with no order, the dependency
statement is optional, stop-and-ask triggers have no home, code references by line number go stale when an
earlier unit edits the file, and nothing checks the plan before ExitPlanMode.

## Goal

A `write-plan` skill that is the single source of the plan-writing rules, fixes the defects above, gives
plans a fixed section template, and runs `over-engineering-check` before ExitPlanMode. CLAUDE.md's Plans
section shrinks to one line telling Claude to invoke the skill in plan mode.

## Not doing

- Describing how to enter or exit plan mode, or where the plan file lives (built-in plan mode owns that).
- Triggering on planning talk outside plan mode.
- Naming any other skill or tool in write-plan except `over-engineering-check` (user: not coupled to a specific skill).
- A plan section recording the over-engineering check: outcomes go to Not doing or Decisions › Agreed.
- A deterministic plan checker script or ExitPlanMode hook. Deferred; no issue is created unless needed later.
- A UserPromptSubmit hook, unless U3 fails its threshold (then stop and ask).
- "Stop for review after each unit" in plans (user: the execution tool covers checkpoints).
- The CLAUDE.md line "Outside plan mode, don't write a plan unless I ask…": deleted, not moved. Its cause
  was the always-loaded plan rules, which leave CLAUDE.md in U2.
- A committed eval case: `claude plugin eval` cases have no permission-mode key, so they cannot run in plan mode.

## Decisions

### Agreed
- The skill is the only copy of the rules. CLAUDE.md's Plans section becomes one invoke line. (U1, U2)
- Order: edit CLAUDE.md first, then test on fresh agents without the always-on rules; fewer than 4 of 5
  triggered → stop and ask. (U2, U3)
- Over-engineering findings → AskUserQuestion; revise only as the user chooses. A rework that removes
  something worth keeping out is recorded under Not doing; a declined finding under Decisions › Agreed with
  the user's reason. No findings → ExitPlanMode. (U1)
- Skill text fixes: one term "the executor"; template with fixed section order; Dependencies always present;
  Execution rules section; approving the plan approves Assumed entries; Context section; "before
  ExitPlanMode" stated; how wording deliverables are checked; "the user" instead of I/me; one merged
  verification rule; assumed conventions listed only under Decisions; code referenced by path and stable
  anchor, not line number. (U1)
- No over-engineering section in the template. (U1)

### Undecided
- Update issue #10's body to match this plan (outward-facing; not done without approval). (none)
- Also test the trigger on Sonnet (`--model sonnet`), one run. Default: not done. (U3)

### Assumed
- Skill name `write-plan`, consistent with `propose-changes`. (U1)
- Template at `skills/write-plan/resources/template.md`. (U1)
- No version bump in `.claude-plugin/plugin.json`; the previous two skill additions did not bump it
  (commits 169b4b2, e595964). (U1)
- "Clean agent without the always-on rules" = fresh `claude -p` sessions after U2, with the old Plans rules
  gone and the one-line invoke pointer present (it is part of the real setup). (U3)
- U2 edits the dotfiles file but does not commit it: dotfiles has unrelated uncommitted changes
  (`claude/.claude/settings.json`, `zsh/.zshrc`). (U2)
- Test runs use the default model. (U3)

## Conventions

- Skill files: Markdown, YAML frontmatter with `name` and a folded `description: >-` wrapped near 100
  columns, as in `plugins/workflow-preferences/skills/over-engineering-check/SKILL.md` (frontmatter block).
- First body line is the load marker, as in that file: ``Say `over-engineering-check loaded`.``
- No scripts or tests: this plan adds no deterministic code.
- Commit message: `[#10] workflow-preferences: <message>` (see `git log --oneline -5`).

## Gotchas

- The installed `workflow-preferences@dev-toolkits` reads from this repo directory (`claude plugin list`:
  "Read from: …/plugins/workflow-preferences"), so a new skill should appear in new sessions without
  reinstalling (unverified). Do not pass `--plugin-dir`: it would load the plugin twice.
- `UserPromptSubmit` hook input includes `permission_mode` (verified in code.claude.com/docs/en/hooks only,
  not by running). The issue's "confirm with a claude-code-guide agent" step is not needed.
- In `-p` mode, ExitPlanMode is not offered without a permission host (docs; unverified by running). `-p`
  runs test triggering and plan structure, not the pre-exit step; U3's interactive run covers that.

## Dependencies

U2 depends on U1 (the pointer names the skill). U3 depends on U2 (it tests the post-edit setup).

## U1 — Create the write-plan skill and plan template

**Deliverables:** `write-plan` skill with the rewritten rules and a plan template.

**Files:** create `plugins/workflow-preferences/skills/write-plan/SKILL.md`,
`plugins/workflow-preferences/skills/write-plan/resources/template.md`; must not touch the other skills,
`.claude-plugin/plugin.json`, `README.md`, `~/dotfiles/claude/.claude/CLAUDE.md`.

**Content** — `SKILL.md`, exactly:

````markdown
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
````

**Content** — `resources/template.md`, exactly:

````markdown
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
````

**Gotchas:**
- `over-engineering-check` ends with "Then stop and wait for the user."; write-plan's No-findings branch says
  to call ExitPlanMode instead. Whether Claude follows write-plan there is checked in U3's interactive run
  (unverified).
- Angle brackets in `description` display as `&lt;`/`&gt;` (skills docs); the description uses none.

**Done when:**
- `claude plugin validate plugins/workflow-preferences` reports no errors; fails on a frontmatter parse error.
- Description length: `python3 -c "t=open('plugins/workflow-preferences/skills/write-plan/SKILL.md').read();d=t.split('---')[1].split('description:')[1].replace('>-','');print(len(' '.join(d.split())))"` prints a number under 1024.
- Rule coverage: a reviewer checks each rule of the current `# Plans (plan mode only)` section (identified by
  its opening words) lands as below; any unmapped rule fails:

  | Rule opening words | Lands in |
  |---|---|
  | "These rules apply to plan-mode plan files…" | intro (plan-mode half); outside-plan-mode half deleted (U2) |
  | "Investigate cheaply first…" | Before writing 1 |
  | "Point at existing code to reuse…" | Before writing 2 (now anchor, not line number) |
  | "State the goal…" | Structure › Context/Goal/Not doing |
  | "Break the work into small…", "Write each unit so…", "Label units U1…" | Structure bullets 2-4 |
  | "For each unit give **Deliverables**…" | Unit fields; Done when › Verification; Structure › Decisions |
  | "**Content** means…", "Length is never a reason…" | Unit fields › Content, Length |
  | "\"Done when\" must be checkable…", "For units that write tests…" | Unit fields › Done when, test tables |
  | "If units depend on each other…" | Structure › Dependencies (now always) |
  | "Include a **Conventions** section…" | Structure › Conventions |
  | "Record every key decision and gotcha…" | Structure › Gotchas and Decisions; "say whether verified" merged into Before ExitPlanMode 1 |
  | "Give the executing agent stop-and-ask triggers…" | Structure › Execution rules + template |
  | "Before emitting the plan, verify…" | Before ExitPlanMode 1 |
  | "During execution, stop for my review…" | dropped (user decision) |

- Stop for the user's review, then commit `[#10] workflow-preferences: add write-plan skill` on branch
  `10-write-plan-skill`. No push.

## U2 — Replace the Plans section in CLAUDE.md with an invoke line

**Deliverables:** CLAUDE.md no longer holds plan rules; one line tells Claude to invoke the skill.

**Files:** modify `~/dotfiles/claude/.claude/CLAUDE.md` (the target of `readlink -f ~/.claude/CLAUDE.md`;
write to the resolved path, never the symlink); must not touch anything else in dotfiles.

**Content:** replace the whole section from the heading `# Plans (plan mode only)` up to, not including, the
heading `# After finishing work` with exactly:

```markdown
# Plans
In plan mode, invoke the `workflow-preferences:write-plan` skill before writing the plan file.

```

Read the file first. If the section does not start with "These rules apply to plan-mode plan files" and end
with "During execution, stop for my review after each unit.", stop and ask.

**Done when:**
- `grep -c 'Label units U1' ~/dotfiles/claude/.claude/CLAUDE.md` prints `0` (prints `1` if the old section remains).
- `grep -c 'Outside plan mode' ~/dotfiles/claude/.claude/CLAUDE.md` prints `0`.
- `grep -c 'invoke the .workflow-preferences:write-plan. skill' ~/dotfiles/claude/.claude/CLAUDE.md` prints `1`.
- No commit in dotfiles (Assumed). Stop for the user's review.

## U3 — Measure triggering and plan structure in plan mode

**Deliverables:** a results table (run → Skill call, marker, U1 heading, Deliverables, Files, Done when,
Dependencies) reported to the user as ✔/✘ with the actual counts.

**Files:** create only under
`/tmp/claude-1000/-home-david-agent-tools-plugin-marketplace/4ed1cfe9-5c99-4ee5-b15e-21b04fcbb184/scratchpad/`;
must not touch any repo or dotfiles file.

**Content:**
1. Pre-check: `claude -p "Reply with only the names of available skills that contain write-plan."` → output
   contains `workflow-preferences:write-plan`. If not, stop and ask.
2. Five fresh runs from the repo root, each in the background with a 600 s timeout:
   `claude -p --permission-mode plan --output-format stream-json --verbose "Plan this change: add a Skills section to plugins/workflow-preferences/README.md listing each skill with a one-line purpose." > <scratchpad>/write-plan-run-<i>.jsonl`
   (unverified: `stream-json` needs `--verbose` with `-p`. If the flags error, drop `--verbose` and retry
   once; else stop and ask.)
3. Classify each run:
   - **Triggered:** the jsonl has a Skill tool call whose input matches
     `"skill"\s*:\s*"(?:workflow-preferences:)?write-plan"` (same shape as
     `plugins/workflow-preferences/evals/trigger-patching-a-patch/graders/skill-fired.md`).
   - **Marker:** `write-plan loaded` appears in assistant text.
   - **Structure:** the newest file in `~/.claude/plans/` written during the run (if none, the final
     message) has a `U1` heading and the words `Deliverables`, `Files`, `Done when`, `Dependencies`
     (unverified: whether `-p` writes the plan file).
4. Interactive run, by the user: start `claude` in the repo, press Shift+Tab into plan mode, send the same
   prompt. Observe: the marker; `over-engineering-check` invoked before ExitPlanMode; ExitPlanMode reached,
   or AskUserQuestion if there are findings.

**Done when:** triggered in ≥ 4 of 5, structure in ≥ 4 of 5, and the interactive run shows the pre-exit
check. Triggered in ≤ 3 of 5 → stop and ask (candidate: a UserPromptSubmit hook on
`permission_mode == "plan"`, planned separately). Stop for the user's review.

## Verification

End to end: U3's five runs and the interactive run, on a real prompt against this repo, after U2 has
removed the always-on rules.

## Execution rules

Stop and ask, never work around, when:
- the spec is ambiguous or contradicts itself
- a run's output cannot be classified by the U3 step 3 rules
- U3 falls below its thresholds
- a unit needs a file outside its Files list
- `claude plugin validate` fails for a reason not in the new files
