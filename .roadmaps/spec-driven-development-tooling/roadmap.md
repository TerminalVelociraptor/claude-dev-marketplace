# spec-driven-development tooling Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #1_
_Updated: 2026-09-26 - U7 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Record the follow-up research | done | - |
| U2 | Apply the approved sdd.md edits | done | - |
| U3 | `bin/sdd-check` and its tests | done | U2 |
| U4 | Generators and the menu setting | done | U2 |
| U5 | Derive skill | done | U2 |
| U6 | Update skill | done | U3 |
| U7 | Skill lint test | done | U4, U5, U6 |
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
- U4: generators add unsettled questions to Open decisions after approval, link each to the item it came from, gate on open questions needed before the document being generated, and place a missing section where `sdd.md` puts it (G1–G5) - overrides `plan.md:374`, `plan.md:377`, `plan.md:387`, `plan.md:399-401`. reason: unsettled questions had no defined path into Open decisions; user approved, 2026-09-26.
- U4: `plan.md:13` read narrowly: no generator produces Open decisions, but generators may add lines to it - narrows `plan.md:13`. reason: user approved G1–G5, 2026-09-26.
- U4: `sdd.md` Open decisions gains an optional "needed before" document, named in plain text (S6–S7); U4 also carries the user's own System Components edit at `sdd.md:60` - overrides `plan.md:331` (must not touch `sdd.md`). reason: S6–S7 support the G2 gate, user approved 2026-09-26; the `sdd.md:60` edit was the user's, found uncommitted at close, reason not recorded.
- U5: globs taken from an existing rule file are re-checked with Glob; if one matches nothing, propose new globs from the repo layout and confirm with the developer - extends `plan.md:467`. reason: a moved component leaves a glob that matches nothing, so its rule silently stops loading (`sdd.md:204`); user approved, 2026-09-26.
- U5: `argument-hint` is quoted - overrides `plan.md:452`. reason: unquoted, YAML reads `[...]` as a list; all six U4 skills quote theirs; user approved (D2), 2026-09-26.
- U5: the live run used a repo with one of its two component specs, not none - overrides the setup at `plan.md:474`. reason: the user's test repo already had one spec; this exercised both skip reasons.
- between U5 and U6: `docs/01-overview.md` is renamed `docs/overview.md` in `sdd.md` (lines 15, 34, 57, 80, 189) and in the real-`sdd.md` test in `tests/test_sdd_check.py`; U8 names `docs/overview.md` - overrides `plan.md:60`, `plan.md:197`. reason: it was the only numbered document and the number did no work; user approved, 2026-09-26.
- U6: the Contradictions bullet adds the example "an Open decisions question with no answer link while an ADR or document already settles it" - overrides `plan.md:510`. reason: generators now append to Open decisions (U4 G1–G5); user approved, 2026-09-26.
- U6: `argument-hint` is quoted - overrides `plan.md:486`. reason: unquoted, YAML reads `[...]` as a list (as U5); user approved (E2), 2026-09-26.
- U6: judgment checks fetch a GitHub issue with `gh issue view <n>` - extends `plan.md:509`. reason: the issue is piped only into `sdd-check`, so there was no file for the model to Read; user approved (Q1=A), 2026-09-26.
- U6: with nothing named, step 1 runs `sdd-check` with no `--doc` and does not ask for a target - extends `plan.md:500`. reason: a bare live run asked which file to check instead of checking `docs/`; user approved (F1), 2026-09-26.
- U7: the lint test loads `parse_entries` from `bin/sdd-check` - overrides `plan.md:528` (`parse_sdd`). reason: `bin/sdd-check` has no `parse_sdd`; its entry parser is `parse_entries`; user approved, 2026-09-26.

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

**Status:** done

**Effort:** 2h 0m

**Key findings:**
- Outcome: Six generator skills, a shared generate procedure, challenge methods and the `challenge_menu` setting (default on) are built; generators now add unsettled questions to Open decisions and warn on open questions that block the document. Acceptance passed: `claude plugin validate` printed `✔ Validation passed`; the user reported all live checks passed (one question per message, menu after each item, "I don't know" under Open questions and appended to Open decisions, link-bearing runs). See U4 Amendments.
- Files: Added `plugins/spec-driven-development/shared/generate.md`, `shared/challenge-methods.md`, `skills/{vision,system,adr,component,slice,task}/SKILL.md`; modified `.claude-plugin/plugin.json` and `sdd.md` (Open decisions "needed before", System Components wording). U6 must read `generate.md` §4 and the U6 Amendment: generators write Open decisions lines, so update's Contradictions check gains an example. U7 should read the six skills and `generate.md`; U8 the manifest setting and the Open decisions flow, since `plan.md:568` says that section is kept by hand.
- Gotchas: An unset boolean showed false in `/config` while the protocol treated it as menu-on; a saved false persists after adding a true default. The first menu-off run skipped draft review. A live run claimed the update skill would link Open decisions to System; update as planned has no such check, and nothing then wrote Open decisions lines.
- Decisions made and why: Match the ADR heading exactly; make draft review independent of the menu; default the menu on so `/config` shows the real behavior. Generators append Open decisions lines after approval rather than leaving it manual, because the manual path lost questions. "Needed before" is optional and plain text: `sdd.md:130` lets a component spec leave questions open, and a link to a not-yet-written document would be a broken link. The gate warns rather than blocks, so the developer decides. Update gets only one Contradictions example, not a status check, since status tracking is out of scope (`plan.md:15`).

---

### U5 - Derive skill

**Status:** done

**Effort:** 2h 0m

**Key findings:**
- Outcome: Built the derive skill from `plan.md:448-472`, with the glob re-check and quoted `argument-hint` (see U5 Amendments). Acceptance passed in the user's live run: a CLAUDE.md block between the `sdd` markers and a Mermaid context diagram were proposed; no rule file was written, with "no code" and "no spec and no code" as the reasons; `git status` was clean after declining. `claude plugin validate` printed `✔ Validation passed`. After the user added `src/` for one component, a second run proposed globs and wrote its rule file.
- Files: Added `plugins/spec-driven-development/skills/derive/SKILL.md`. U7 lints it; U8 documents it.
- Gotchas: Unquoted `argument-hint: [...]` parses as a YAML list, not a string. The re-check of an existing rule file's glob that matches nothing was not exercised in the live run.
- Decisions made and why: Left the "no code yet" wording at `plan.md:476` unamended until the live run showed the real reason (Q1=A); the skill gave the code-based reason for each component, so no change was needed. Re-check existing globs because a moved component otherwise leaves a rule that silently stops loading (`sdd.md:204`).

---

### U6 - Update skill

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Built the update skill from `plan.md:482-519`, with the Contradictions example, quoted `argument-hint`, issue fetch for judgment checks and a no-target run (see U6 Amendments). Acceptance passed per the user's report that all live tests worked as expected (planted contradiction and broken link, `git status` clean until approval, bare run); `claude plugin validate` printed `✔ Validation passed`.
- Files: Added `plugins/spec-driven-development/skills/update/SKILL.md`. U7 lints it; U8 documents it, including that a bare `/update` checks `docs/` while slices and tasks must be named. Also committed here: the `docs/overview.md` rename in `sdd.md` and `tests/test_sdd_check.py` (see Amendments); U8 must use the new path.
- Gotchas: With no target and the first wording, the model asked for a file and mentioned a clean working tree, reading `/update` as "check what changed". Slices and tasks have no location in `sdd.md`, so no run finds them unnamed.
- Decisions made and why: Fetch issues with `gh issue view` rather than rely on the model to think of it; the permission was already allowed. Kept slices and tasks name-only rather than having the skill search for them, because a search rule would be a location `sdd.md` doesn't state (`plan.md:10`).

---

### U7 - Skill lint test

**Status:** done

**Effort:** 1h 0m

**Key findings:**
- Outcome: Built `tests/test_skill_lint.py` with six checks, one per row of `plan.md:531-538`. Acceptance passed: the suite printed `OK`, and the paste check failed naming `shared/generate.md`; each of the other five tests also failed on a bad input. One deviation: it loads `parse_entries` (see U7 Amendment).
- Files: Added `plugins/spec-driven-development/tests/test_skill_lint.py`. U8 must read it: the two "not restated" checks scan `README.md` once it exists, so the README can't copy an `sdd.md` location or Why word for word.
- Gotchas: `parse_entries` turns `<name>` into `*` and drops `(...)` from entry names, so the location check reads the original wording from `sdd.md` itself, and the `Document:` check drops the `(...)` the same way. `assertIn`/`assertNotIn` print the whole file or entry list on failure, so the tests use `assertTrue`/`assertFalse` with a one-line message.
- Decisions made and why: Each check first asserts there is something to check, so a regex that matched nothing can't pass without testing anything. `README.md` is scanned only if it exists, since U8 hasn't written it yet. The restatement checks only catch exact copies, as the plan specifies.

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
- Written against: U7, done
- Why stopped: U7 closed at the user's command.
- Mid-edit when stopped: none.
- Open question awaiting an answer: none.
- Working agreements: “I want to see only the text that changed.” (wording-proposal format; prompted by the U2 `sdd.md` proposal.)
- Next action: wait for the user's `/roadmap begin U8`.
- Environment: branch `spec-driven-development_stage-1`
