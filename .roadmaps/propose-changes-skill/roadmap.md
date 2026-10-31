# propose-changes skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #8_
_Updated: 2026-10-31 - roadmap created_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the skill file | not started | - |
| U2 | Rewrite issue #8's body | not started | - |
| U3 | Remove the CLAUDE.md section and run the clean subagent test | not started | U1 |
| U4 | User live tests, then restore the section | not started | U3 |
| U5 | Commit | not started | U4 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U5: work happens on the existing branch `8-add-propose-changes-skill-to-workflow-preferences` (already checked out at start), not a new `8-add-propose-changes-skill` from `main` - overrides `plan.md:33` and `plan.md:262`. reason: the user created this branch before `/roadmap start`.

---

### U1 - Create the skill file

**Status:** not started

**Effort:** -

**Executes:** `plan.md:45-122 § U1 — Create the skill file`

**Acceptance:** `plan.md:124-126 § U1 — Create the skill file ➔ Done when`

**Decisions:** `plan.md:17-24 § Decisions ➔ D1-D8`; `plan.md:30-32 § Decisions ➔ A1-A3`

**Conventions:** `plan.md:38-39 § Conventions`

**Stop-and-ask:** `plan.md:266-271 § Stop-and-ask triggers`; review stop `plan.md:43 § Units`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U2 - Rewrite issue #8's body

**Status:** not started

**Effort:** -

**Executes:** `plan.md:128-155 § U2 — Rewrite issue #8's body`

**Acceptance:** `plan.md:157 § U2 — Rewrite issue #8's body ➔ Done when`

**Decisions:** `plan.md:27 § Decisions ➔ D11`

**Stop-and-ask:** `plan.md:266-271 § Stop-and-ask triggers`; review stop `plan.md:43 § Units`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U3 - Remove the CLAUDE.md section and run the clean subagent test

**Status:** not started

**Effort:** -

**Executes:** `plan.md:159-237 § U3 — Remove the CLAUDE.md section and run the clean subagent test`

**Acceptance:** `plan.md:239 § U3 ➔ Done when`

**Decisions:** `plan.md:25-26 § Decisions ➔ D9-D10`

**Conventions:** `plan.md:40 § Conventions ➔ subagent pre-flight`

**Stop-and-ask:** `plan.md:266-271 § Stop-and-ask triggers`; review stop `plan.md:43 § Units`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U4 - User live tests, then restore the section

**Status:** not started

**Effort:** -

**Executes:** `plan.md:241-257 § U4 — User live tests, then restore the section`

**Acceptance:** `plan.md:259 § U4 ➔ Done when`

**Decisions:** `plan.md:25 § Decisions ➔ D9`

**Conventions:** `plan.md:39 § Conventions ➔ clodex alias`

**Stop-and-ask:** `plan.md:266-271 § Stop-and-ask triggers`; review stop `plan.md:43 § Units`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U5 - Commit

**Status:** not started

**Effort:** -

**Executes:** `plan.md:261-262 § U5 — Commit`

**Acceptance:** `plan.md:264 § U5 — Commit ➔ Done when`

**Decisions:** `plan.md:33 § Decisions ➔ A4` (branch part amended, see Amendments)

**Stop-and-ask:** `plan.md:266-271 § Stop-and-ask triggers`; review stop `plan.md:43 § Units`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U1, not started
- Why stopped: roadmap just created
- Mid-edit when stopped: nothing
- Open question awaiting an answer: none
- Working agreements: "During execution, stop for my review after each unit." (user CLAUDE.md, Plans section); before any subagent, post a pre-flight check and wait for OK (user CLAUDE.md hard rule).
- Next action: `/roadmap begin U1` (or U2, which has no dependency)
- Environment: branch `8-add-propose-changes-skill-to-workflow-preferences`; `claude` is aliased to `clodex claude`
