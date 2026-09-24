# spec-driven-development tooling Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #1_
_Updated: 2026-09-24 - U4 checkpointed; live acceptance pending_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Record the follow-up research | done | - |
| U2 | Apply the approved sdd.md edits | done | - |
| U3 | `bin/sdd-check` and its tests | done | U2 |
| U4 | Generators and the menu setting | in progress | U2 |
| U5 | Derive skill | not started | U2 |
| U6 | Update skill | not started | U3 |
| U7 | Skill lint test | not started | U4, U5, U6 |
| U8 | README | not started | U4, U5, U6 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged from the frozen plan. `none.` until one occurs._
- all: user approved the Assumed rows and asked for them to be moved into Agreed; plan.md was edited once after start to do this - overrides `plan.md:24-41`. reason: user decision, 2026-09-24.
- U1: the plan says to check both Agent OS rows, but only one existed in the interaction table; marked that existing row per user direction - overrides `plan.md:118`. reason: no second row was present.
- U2: user approved including the required `.roadmaps` state change in addition to `sdd.md` in the diff-stat acceptance result - overrides `plan.md:154`. reason: roadmap state tracking is required during execution.
- U3: each of the 22 tests adds a paired input control; verification also used a temporary always-clean checker to demonstrate that all 22 can fail - extends `plan.md:237-313`. reason: user requested evidence that tests measure their claimed behavior.
- U4: the ADR skill passes `ADR (decision record)` rather than `ADR` - overrides `plan.md:355`. reason: this matches the heading in `sdd.md`; user approved the correction.
- U4: every drafted item pauses for keep/revise review even with challenges off - overrides `plan.md:388-395`. reason: the live run skipped review when the menu was disabled; user approved R1.
- U4: `challenge_menu` declares `default: true` - extends `plan.md:423-435`. reason: user requested an on-by-default setting that can be explicitly switched off.

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

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: The approved S1–S5 edits were applied verbatim to `sdd.md`; acceptance passed with the user's allowance for the roadmap state change in the diff.
- Files: `plugins/spec-driven-development/sdd.md` updated with the approved heading/link, component-spec, ADR path, CLAUDE.md marker and path-rule wording.
- Gotchas: The diff also includes the required U2 roadmap status update; the user approved this in the acceptance result. See Amendments.
- Decisions made and why: Included the roadmap state update alongside `sdd.md` per user direction; see Amendments.

---

### U3 - `bin/sdd-check` and its tests

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Built the document checker and 22 subprocess tests. Acceptance passed: `Ran 22 tests`, `OK`; removing casefold in a temporary checker copy made case 11 fail for the intended `not-in-target` finding. See Amendments for the added paired controls.
- Files: Added executable `plugins/spec-driven-development/bin/sdd-check` (U6 calls its CLI) and `plugins/spec-driven-development/tests/test_sdd_check.py` (isolated roots, including one run against real `sdd.md`).
- Gotchas: An always-clean checker made all 22 tests fail by assertion, but this is not a targeted implementation mutation for each case. Each test uses a new temporary root; reverse and shuffled orders also passed.
- Decisions made and why: Added paired controls to every test to check input sensitivity without adding a mutation framework; kept the casefold implementation mutation in a temporary copy so the project file stayed untouched.

---

### U4 - Generators and the menu setting

**Status:** in progress

**Effort:** -

**Executes:** `plan.md:325-436 § U4: Generators (six thin skills, a shared protocol and methods), plus the menu setting`

**Acceptance:** `plan.md:438-443 § U4 ➔ Done when`; live run `plan.md:599-601 § Verification`

**Decisions:** `plan.md:28 § Agreed (this session) ➔ challenge menu`; `plan.md:33-34 § Agreed (this session) ➔ skill name, live run`; `plan.md:46 § Resolved labels ➔ O1`; `plan.md:49 § Resolved labels ➔ O4`; `plan.md:52 § Resolved labels ➔ O6`; `plan.md:54 § Resolved labels ➔ Q1`; `plan.md:37-39 § Agreed (this session)`

**Governed by:** `plan.md:10 § Context ➔ hard rule`; `plan.md:81-92 § Conventions`; `plan.md:94-96 § Cross-cutting gotchas`; `plan.md:98-103 § Stop-and-ask triggers`

**Key findings:**
- Outcome: Six generators, shared interview/challenge methods, and the menu setting are built. Plugin validation passed; the user's live Vision run produced `docs/01-overview.md` in `test-sdd`. Menu-after-each-item and "I don't know" acceptance details, plus further link-bearing document runs, remain unchecked.
- Files: Added `plugins/spec-driven-development/shared/generate.md`, `shared/challenge-methods.md`, and `skills/{vision,system,adr,component,slice,task}/SKILL.md`; modified `.claude-plugin/plugin.json`. U7 should read the six skills and shared procedure; U8 should read the manifest setting.
- Gotchas: An unset boolean showed false in `/config` without a saved value, while the protocol treated anything but explicit false as menu-on; a saved false persists after adding a true default. The first menu-off run skipped draft review, prompting R1.
- Decisions made and why: Match the ADR heading exactly; make draft review independent of the challenge menu; default the setting to true so its displayed initial value matches the intended behavior. See U4 Amendments.

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
- Written against: U4, in progress
- Why stopped: user requested a checkpoint before completing the remaining live acceptance checks.
- Mid-edit when stopped: none; U4 files remain uncommitted.
- Open question awaiting an answer: whether menu-after-each-item and "I don't know" in `plan.md:440-443 § U4 ➔ Done when` pass, and whether link-bearing document runs work; user reported 1 hour at the attempted close, so ask for the final total after the remaining work.
- Working agreements: “I want to see only the text that changed.” (wording-proposal format; prompted by the U2 `sdd.md` proposal.) “don't close U4 yet” (stop-and-wait; prompted by the missing "I don't know" test and planned link-bearing generator runs.)
- Next action: wait for the user's live tests and explicit `/roadmap close U4`; do not begin U5.
- Environment: branch `spec-driven-development_stage-1`
