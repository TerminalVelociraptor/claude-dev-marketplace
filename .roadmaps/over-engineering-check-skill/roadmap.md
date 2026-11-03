# over-engineering-check skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #9_
_Updated: 2026-11-03 - roadmap started_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the skill file | not started | - |
| U2 | Rewrite the always-on rules and update the notes | not started | U1 |
| U3 | Behaviour tests | not started | U1 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U3: the stop-and-ask trigger reads "`~/.local/bin/claude -p` (manual cases) or `~/.local/bin/claude plugin eval` (eval cases) can't run the cases" - overrides `plan.md:459`. reason: U3 runs cases with the real binary (`plan.md:330-338`), not the clodex alias; the trigger was not updated when U3 changed.
- U2: the stop-and-ask trigger reads "The current text of `CLAUDE.md` lines 8-9 or line 24 no longer matches U2's `-` lines" - overrides `plan.md:461`. reason: U2 also rewrites the narrow-reading rule at line 24 (`plan.md:296-299`); the trigger was not updated when that edit was added.

---

### U1 - Create the skill file

**Status:** not started

**Effort:** -

**Executes:** `plan.md:98-197 § U1 — Create the skill file`

**Acceptance:** `plan.md:199-205 § U1 — Create the skill file ➔ Done when`

**Decisions:** `plan.md:27-79 § Decisions`

**Conventions:** `plan.md:81-90 § Conventions`

**Stop-and-ask:** `plan.md:457-462 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U2 - Rewrite the always-on rules and update the notes

**Status:** not started

**Effort:** -

**Executes:** `plan.md:209-299 § U2 — Rewrite the always-on rules and update the notes`

**Acceptance:** `plan.md:301-310 § U2 — Rewrite the always-on rules and update the notes ➔ Done when`

**Decisions:** `plan.md:27-79 § Decisions`

**Dependencies:** `plan.md:92-94 § Dependencies`

**Stop-and-ask:** `plan.md:457-462 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U3 - Behaviour tests

**Status:** not started

**Effort:** -

**Executes:** `plan.md:314-450 § U3 — Behaviour tests`

**Acceptance:** `plan.md:452-453 § U3 — Behaviour tests ➔ Done when`

**Cases:** `plan.md:361-370 § U3 — Behaviour tests ➔ Cases`

**Decisions:** `plan.md:27-79 § Decisions`

**Conventions:** `plan.md:81-90 § Conventions`

**Stop-and-ask:** `plan.md:457-462 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U1, not started
- Why stopped: roadmap just started; no unit begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: "During execution, stop for my review after each unit." (user's global `CLAUDE.md`, Plans section).
- Next action: `/roadmap begin U1` (Create the skill file).
- Environment: branch `9-add-over-engineering-check-skill-to-workflow-preferences`; dotfiles has an unrelated uncommitted change to `claude/.claude/settings.json`.
