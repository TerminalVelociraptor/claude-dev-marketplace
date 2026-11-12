# write-plan skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #10_
_Updated: 2026-11-11 - U2 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the write-plan skill and plan template | done | - |
| U2 | Replace the Plans section in CLAUDE.md with an invoke line | done | U1 |
| U3 | Measure triggering and plan structure in plan mode | not started | U2 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
none.

---

### U1 - Create the write-plan skill and plan template

**Status:** done

**Effort:** 0h 15m

**Key findings:**
- Outcome: Skill and template created exactly per `plan.md:85-241`; no deviations. Acceptance passed: both files byte-match the plan's blocks, `claude plugin validate` exit 0, description length 387 (< 1024), all 17 current Plans rules map to a row of the coverage table.
- Files: added `plugins/workflow-preferences/skills/write-plan/SKILL.md` and `resources/template.md`. U2 must read `SKILL.md` (it is the invoke target) and the global CLAUDE.md `# Plans (plan mode only)` section it replaces.
- Gotchas: `claude plugin validate` also prints a directory-profile error (`LICENSE_MISSING`) and an icon warning for the plugin; they are pre-existing, outside U1's files, and do not affect the exit code. Rule coverage was checked by reading, not by script.
- Decisions made and why: Kept Structure and Unit fields inside `SKILL.md` rather than a reference file, because every rule applies to every plan and a separate file adds a skippable read. Accepted that the section order is stated in both `SKILL.md` and the template.

---

### U2 - Replace the Plans section in CLAUDE.md with an invoke line

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: The `# Plans (plan mode only)` section of `~/dotfiles/claude/.claude/CLAUDE.md` is replaced by `# Plans` plus one line telling Claude to invoke `workflow-preferences:write-plan` in plan mode; no deviations. Acceptance passed: the `Label units U1` and `Outside plan mode` greps print `0`, the invoke-line grep prints `1`, and nothing was committed in dotfiles.
- Files: modified only `/home/david/dotfiles/claude/.claude/CLAUDE.md` (-19/+2 lines), left uncommitted. U3 tests against this edited file, so it must stay in place.
- Gotchas: the section spans lines 26-44, not 26-45 (line 45 is the blank line before `# After finishing work`); the first scripted edit hit an assertion on this and wrote nothing. The dotfiles repo also has unrelated uncommitted changes (`claude/.claude/settings.json`, `zsh/.zshrc`).
- Decisions made and why: edited with a script that asserts the section's first line, last line and the following heading before writing, so a wrong range cannot delete other rules.

---

### U3 - Measure triggering and plan structure in plan mode

**Status:** not started

**Effort:** -

**Executes:** `plan.md:294-320 § U3 — Measure triggering and plan structure in plan mode`

**Acceptance:** `plan.md:322-324 § U3 — Measure triggering and plan structure in plan mode ➔ Done when`; `plan.md:326-329 § Verification`

**Scope:** `plan.md:26 § Not doing ➔ UserPromptSubmit hook`; `plan.md:30 § Not doing ➔ committed eval`

**Decisions:** `plan.md:36-37 § Decisions ➔ Agreed`; `plan.md:50 § Decisions ➔ Undecided`; `plan.md:57-58 § Decisions ➔ Assumed`; `plan.md:61 § Decisions ➔ Assumed`

**Gotchas:** `plan.md:73-79 § Gotchas`

**Stop-and-ask:** `plan.md:331-338 § Execution rules`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U2, done
- Why stopped: U2 closed; U3 not begun
- Mid-edit when stopped: none
- Open question awaiting an answer: none
- Working agreements: none recorded
- Next action: `/roadmap begin U3` (Measure triggering and plan structure in plan mode)
- Environment: branch `10-write-plan-skill`; `plugins/sdd/sdd.md` has an uncommitted change unrelated to this work; dotfiles has the U2 edit to `claude/.claude/CLAUDE.md` uncommitted, by plan
