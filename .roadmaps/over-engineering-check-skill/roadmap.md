# over-engineering-check skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #9_
_Updated: 2026-11-04 - U1 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the skill file | done | - |
| U2 | Rewrite the always-on rules and update the notes | not started | U1 |
| U3 | Behaviour tests | not started | U1 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U3: the stop-and-ask trigger reads "`~/.local/bin/claude -p` (manual cases) or `~/.local/bin/claude plugin eval` (eval cases) can't run the cases" - overrides `plan.md:459`. reason: U3 runs cases with the real binary (`plan.md:330-338`), not the clodex alias; the trigger was not updated when U3 changed.
- U2: the stop-and-ask trigger reads "The current text of `CLAUDE.md` lines 8-9 or line 24 no longer matches U2's `-` lines" - overrides `plan.md:461`. reason: U2 also rewrites the narrow-reading rule at line 24 (`plan.md:296-299`); the trigger was not updated when that edit was added.
- U1: no separate commit; the file is committed by `/roadmap close U1` - overrides `plan.md:205` ("Commit on the branch. Don't push yet."). reason: user decision, commits go through roadmap close. Not pushed either way.

---

### U1 - Create the skill file

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: `SKILL.md` created verbatim from `plan.md:114-188`; `claude plugin validate plugins/workflow-preferences` passed; user ran the skill in a fresh session and reported the marker fired and the behaviour looked good. Only deviation: the commit is made by `close`, see Amendments.
- Files: added `plugins/workflow-preferences/skills/over-engineering-check/SKILL.md` (75 lines). U2 and U3 should read it: U2 points the always-on rule at it, U3 tests its behaviour.
- Gotchas: `validate` also prints a LICENSE_MISSING "problem", an ICON_MISSING warning and the README advice. None changes the verdict (they apply only under `--profile directory`), so the plan's mention of only the README warning is incomplete. Out of scope, not fixed. Don't take that output for a failure.
- Decisions made and why: wrote the file by copying `plan.md` lines 114-188 with `sed` rather than retyping, so it can't drift from the plan; a `diff` against those lines showed no difference. Fresh-session check done by the user in a plain session (not `--plugin-dir`), since the plan says the local plugin needs no reinstall.

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
- Written against: U1, done
- Why stopped: U1 closed; waiting for the user's review before the next unit.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: "During execution, stop for my review after each unit." (user's global `CLAUDE.md`, Plans section). "Defer commits and such to roadmap." (user, when asked to propose U1's changes; commits go through `roadmap close`.)
- Next action: `/roadmap begin U2` (rule edit in dotfiles and notes bullet) or `/roadmap begin U3` (T1-T5 behaviour test results); this close unblocked both, and the plan advises doing U2 after U1.
- Environment: branch `9-add-over-engineering-check-skill-to-workflow-preferences`; dotfiles has an unrelated uncommitted change to `claude/.claude/settings.json`.
