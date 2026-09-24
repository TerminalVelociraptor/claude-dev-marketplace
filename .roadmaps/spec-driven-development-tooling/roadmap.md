# spec-driven-development tooling Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #1_
_Updated: 2026-09-24 - U1 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Record the follow-up research | done | - |
| U2 | Apply the approved sdd.md edits | not started | - |
| U3 | `bin/sdd-check` and its tests | not started | U2 |
| U4 | Generators and the menu setting | not started | U2 |
| U5 | Derive skill | not started | U2 |
| U6 | Update skill | not started | U3 |
| U7 | Skill lint test | not started | U4, U5, U6 |
| U8 | README | not started | U4, U5, U6 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged from the frozen plan. `none.` until one occurs._
- all: user approved the Assumed rows and asked for them to be moved into Agreed; plan.md was edited once after start to do this - overrides `plan.md:24-41`. reason: user decision, 2026-09-24.
- U1: the plan says to check both Agent OS rows, but only one existed in the interaction table; marked that existing row per user direction - overrides `plan.md:118`. reason: no second row was present.

---

### U1 - Record the follow-up research

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Follow-up research was added; the plan's acceptance checks passed.
- Files: `plugins/spec-driven-development/research.md` updated with the checked Agent OS row, follow-up findings and verified-source entries.
- Gotchas: The interaction table had one Agent OS row, not two; the existing row was marked checked per user direction. See Amendments.
- Decisions made and why: Kept the plan's recommended Q1=A and O6=A choices for question style and menu opt-out.

---

### U2 - Apply the approved sdd.md edits

**Status:** not started

**Effort:** -

**Executes:** `plan.md:151-153 § U2: Apply the approved sdd.md edits`

**Acceptance:** `plan.md:154 § U2: Apply the approved sdd.md edits ➔ Done when`

**Edits:** `plan.md:57-77 § sdd.md edits (all approved)`; `plan.md:55 § Resolved labels ➔ S1–S5`

**Governed by:** `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U3 - `bin/sdd-check` and its tests

**Status:** not started

**Effort:** -

**Executes:** `` plan.md:156-319 § U3: `bin/sdd-check` and its tests ``

**Acceptance:** `` plan.md:321-323 § U3: `bin/sdd-check` and its tests ➔ Done when ``

**Decisions:** `plan.md:29-31 § Agreed (this session)`; `plan.md:46 § Resolved labels ➔ O1`; `plan.md:49-51 § Resolved labels ➔ O4, O5, O5b`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U4 - Generators and the menu setting

**Status:** not started

**Effort:** -

**Executes:** `plan.md:325-436 § U4: Generators (six thin skills, a shared protocol and methods), plus the menu setting`

**Acceptance:** `plan.md:438-443 § U4 ➔ Done when`; live run `plan.md:599-601 § Verification`

**Decisions:** `plan.md:28 § Agreed (this session) ➔ challenge menu`; `plan.md:33-34 § Agreed (this session) ➔ skill name, live run`; `plan.md:46 § Resolved labels ➔ O1`; `plan.md:49 § Resolved labels ➔ O4`; `plan.md:52 § Resolved labels ➔ O6`; `plan.md:54 § Resolved labels ➔ Q1`; `plan.md:37-39 § Agreed (this session)`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:94-96 § Cross-cutting gotchas`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U5 - Derive skill

**Status:** not started

**Effort:** -

**Executes:** `plan.md:445-473 § U5: Derive skill`

**Acceptance:** `plan.md:474-477 § U5: Derive skill ➔ Done when`; live run `plan.md:599-601 § Verification`

**Decisions:** `plan.md:34 § Agreed (this session) ➔ live run`; `plan.md:47-49 § Resolved labels ➔ O2, O3, O4`; `plan.md:37 § Agreed (this session)`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:94-96 § Cross-cutting gotchas`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U6 - Update skill

**Status:** not started

**Effort:** -

**Executes:** `plan.md:479-520 § U6: Update skill`

**Acceptance:** `plan.md:521-523 § U6: Update skill ➔ Done when`; live run `plan.md:599-601 § Verification`

**Decisions:** `plan.md:30 § Agreed (this session) ➔ files and GitHub issues`; `plan.md:34 § Agreed (this session) ➔ live run`; `plan.md:49 § Resolved labels ➔ O4`; `plan.md:35 § Agreed (this session) ➔ main session`; `plan.md:37-38 § Agreed (this session)`; `plan.md:40 § Agreed (this session) ➔ one issue per run`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:94-96 § Cross-cutting gotchas`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U7 - Skill lint test

**Status:** not started

**Effort:** -

**Executes:** `plan.md:525-538 § U7: Skill lint test`

**Acceptance:** `plan.md:540-542 § U7: Skill lint test ➔ Done when`

**Decisions:** `plan.md:33 § Agreed (this session) ➔ skill name`; `plan.md:36-37 § Agreed (this session)`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U8 - README

**Status:** not started

**Effort:** -

**Executes:** `plan.md:544-589 § U8: README`

**Acceptance:** `plan.md:590-592 § U8: README ➔ Done when`; plan-wide `plan.md:596-606 § Verification (end to end, after U8)`

**Decisions:** `plan.md:33 § Agreed (this session) ➔ skill name`; `plan.md:52 § Resolved labels ➔ O6`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U1, done
- Why stopped: U1 closed
- Mid-edit when stopped: nothing
- Open question awaiting an answer: none
- Working agreements: none stated yet
- Next action: `/roadmap begin U2`
- Environment: branch `spec-driven-development_stage-1`
