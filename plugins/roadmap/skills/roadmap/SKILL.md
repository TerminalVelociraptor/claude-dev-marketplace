---
name: roadmap
description: >
  Track execution of an approved plan for one unit of work. Maintains a checkpoint overlay that
  points into a frozen plan and commits at each stage boundary, so progress can be reported or
  handed off mid-ticket. Invoke with /roadmap and a verb.
disable-model-invocation: true
---

# Roadmap

Input is a finished plan for **one unit of work** - normally what plan mode just wrote. Output is
`.roadmaps/<slug>/`, holding a frozen copy of that plan and a `roadmap.md` tracking execution
against it.

**The roadmap holds execution state only. It never restates a plan context.** Scope, contracts,
terminology, invariants, rationale and acceptance stay in one plan and are refrenced by a pointer.
There is no transcription step, so nothing can be lost in one.

The user drives every transition. An agent may do most of a unit's work with little promtping; this
skill never decides *whether* to.

## What this is not

- Not a planner, spec tool, or project manager. The plan arrives already approved.
- Not an execution engine. It records; it does not implement.
- Not for multi-plan programmes of work. One plan, one roadmap.

## Commands

Every action is an explicit verb. No mode inference, no conversational triggers - nothing changes
state and nothing commits off a chat phrase. On an unrecognised or missing verb, list the verbs and
stop. Never infer one.

| Command | Effect |
|---|---|
| `/roadmap` | Print the verbs and the state table. Read-only |
| `/roadmap start [plan-path]` | Create the roadmap. Commits. |
| `/roadmap resume` | Report where things stand. Read-only. |
| `/roadmap begin <unit>` | That unit ➔ `in progress`. | 
| `/roadmap close <unit>` | Acceptance, findings, collapse, handoff. No commit. |
| `/roadmap checkpoint` | Sync findings, amendments, handoff. No commit. |

`<unit>` is the plan's own label (`U3`). Where no roadmap exists, every verb but `start` says so and
stops.

## The files

`.roadmaps/<slug>/` at the **project root** - the directory the session was inoked in, not the git
top-level, not the nearest package marker. `<slug>` is 2-4 kebab-case words from the plan's title.

```
.roadmaps/<slug>/
  plan.md       frozen copy of the approved plan; never edited after start
  roadmap.md    execution state
```

If `.roadmaps/<slug>/` already exists, stop and report it. Never write over one.

`.roadmaps/` must not be ignored - the commits are the point. Check `git check-ignore -v .roadmaps`
at `start` and stop if it matches.

## Pointers

A pointer is `plan.md:<start>-<end> § <heading>`, optionally narrowed with `➔ <subject>`:

```
plan.md:101-110 § Target contracts ➔ Cache
plan.md:203:218 § Verification
```

Carry both the lines and the heading. Point at the tightest range that answers the question - two
lines where two lines will do, not the enclosing section. A range must not start of end mid-item:
begin it at the first line of the list entry, paragraph or code block it names.

## start

`/roadmap start [plan-path]`

1. **Resolve the plan.** With a path argument, use it. Wihtout one, use the plan-mode path already
   known from this session. If neither is available, prompt the user for a path argument.
2. **Readiness check.** The plan must name discrete units of work, must have a dependency statement,
   and must state something usable as verification. If any are missing, stop and say which. Nothing 
   else is checked.
3. **Copy** the plan to `.roadmaps/<slug>/plan.md`. Leave the original where it is.
4. **Ask for the work item** - ticket, issue id, whatever the project uses - and record it in the
   header. Do not infer it from the branch name or commit history: one found there may belong to
   different work. If the project tracks none, the line reads `none`.
5. **Write `roadmap.md`** from `resources/template.md`. Every unit is created `not started`,
   including the first. Fill `Depends on` from the plan's own dependency statement. Compute every
   pointer against the copied `plan.md`. Point each unit at any plan preamble or caveat that governs
   it, not only at its own section - a constraint stated once for all units still needs a pointer
   from each unit it binds.
6. **Commit** (see Committing).

## resume

`/roadmap resume`

Read `roadmap.md`, then only the plan lines the current unit poitns at - not the whole plan. Report
the current unit and its state, anything the handoff records as mid-edit, the working agreements, and
the next action. Ask before doing anything else.

## begin

`/roadmap begin <unit>`

Check the unit's `Depends on` is satisfied; if not, say so and stop. Otherwise set its status to
`in progress` and refresh the `_Updated:_` line.

A unit enters `in progress` only through this command. That is what makes "never start work the user
has not asked for" mechanical rather than a rule to remember.

## checkpoint

`/roadmap checkpoint`

Sync findings, `Amendments`, the handoff and the `_Updated:_` line. Does not commit. Use before
walking away mid-unit.

## close

`/roadmap close <unit>`

1. **Check acceptance and report the real result.** Follow the unit's `Acceptance` pointer and run
   or observe what it names. If it fails, the unit stays `in progress`.

   **A passing command proves nothing until you know it can fail.** Before trusting a pass, confirm
   the command measures what its prose claims and that its exit status reflects that check rather
   than some later step in a pipeline. A command that cannot fail is not acceptance, and a wrong
   command is worse than an honest observable behavior because it launders a failure as a pass.
2. **Fill all four findings categories** from what actually happened - never from what the plan said
   would happen. A unit cannot close until they are filled.
3. **Record divergence.** Anything done differently from the plan becomes an `Amendments` entry
   naming the plan lines it overrides. `Outcome` either states "no deviations" or points at them.
4. **Ask for effort.** Ask the user how long the unit took, and write the answer to `Effort:` as
   `xh ym` rounded to the nearest 30 minutes - `3h 0m`, `0h 15m`, `3h 45m`. This is the figure to log
   in the work item. Never estimate it, and never infer it from timestamps or commit history.
5. **Collapse:** delete the unit's pointer lines. Status and Key findings survive.
6. Update the state table, rewrite the handoff, refresh `_Updated:_`.
7. **Commit** (see Committing).

When the last unit closes the work is finishedL say so, write `Next action: none - plan complete` in
the handoff, and leave the directory in place.

## Key Findings

| Category | Holds |
|---|---|
| Outcome | What was actually built, and the acceptance result. 1-3 lines. |
| Files | What was actually added/modified/deleted, flagging any a later unit must read and why. |
| Gotchas | What cost time, or would mislead someone repeating the work. |
| Decisions made and why | Choices where another option was viable, with the reason. |

`Outcome` must stand alone as a report of how the unit was resolved - it is what gets pasted into a
ticket. A pointer like "build per `plan.md:152-157`" is fine; it resolves in one hop.

Keep a finding if either limb holds: a later unit or a fresh session would act differently for
knowing it, or deleting it would lose the answer to "why was this done this way". A category with
geniunely nothing to record is written `none.` - never blank, never padded with invented detail.

**Findings are not a work log.** Do not narrate what was done in order.

## Amendments

Append-only, one line per divergence, naming the plan lines it overrides. The plan is never edited to
match reality; the roadmap records where they parted. Keeping them in one list rather than scattered
per unit is what makes a part-finished ticket readable.

## Handoff

Facts about the **session**, never facts about the work. Test: if a fact would still be true after a
week of nobody touching this, it belongs in the plan or in a finding, and the handoff points at it
rather than restating it.

Replaced each session, never appended to.

`Working agreements` records conventions established with the user - stop-and-wait agreements, output
formats, how they want to be communicated with. **Record only a convention the user actually stated,
in their words, with what prompted it. Never one inferred from observed behavior.**

## Committing

Only `start` and `close` commit.

1. Run `git status --porcelain`.
2. Stage `.roadmaps/<sluig>/` plus the paths that are project content - source, tests, config, project
   docs.
3. **Anything not clearly project content: stop, list it by path, and ask.** Sandboxes and other
   tooling leave artifacts in the working directory that are not yours to commit.
4. Never `git add -A` or `git add.`. Non-regulare files are never project content, and `git add`
   refuses them outright, so a blanket add hard-fails rather than failing quietly.
5. Message is `<ticket>: <message>`, using the work item from the header; with no ticket, the message
   alone. do not go looking for a house style in the commit history.
6. **Never push. Never rebase.**

Where the project has no version control, say so once and skip every commit step.

## Must not happen
- Never copy plan content into `roadmap.md`. Pointers only.
- Never edit `.roadmaps/<slug>/plan.md` after `start`.
- Never guess at a rotted pointer.
- Never infer a verb, or act on "checkpoint" said in conversation.
- Never move a unit to `in progress` outside `/roadmap begin`.
- Never mark a unit `done` before its acceptance has been checked and passed.
- Never write findings from memory of what was planned.
- Never invent a working agreement.
- Never `git add -A`, never push, never rebase.

## Authority

This skill is **not** the final authority over live repo conventions, `CLAUDE.md`, or `AGENTS.md` -
including a user-level `CLAUDE.md` outside the repo, which counts the same as one inside it. Where
one of those specifies something this skill also specifies - a commit format, an approval step -
follow it and carry on. That is deference, not a conflict, and needs no approval. Stop and ask only
where following both would undo each other or create a dead lock.

## Template

`resources/template.md` is the literal content of a new `roadmap.md`. Read it at `start` and whenever
you need a section's exact shape. Copy it; do not reproduce it from memory.
