# write-plan skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #10_
_Updated: 2026-11-11 - U3 closed; plan complete_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the write-plan skill and plan template | done | - |
| U2 | Replace the Plans section in CLAUDE.md with an invoke line | done | U1 |
| U3 | Measure triggering and plan structure in plan mode | done | U2 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U3: `resources/template.md` gains a blank line before `### Undecided` and `### Assumed` and between unit field lines, after the interactive run showed subheadings running into the list above; user approved ("Apply both"). Overrides `plan.md:185-235 § U1 — Create the write-plan skill and plan template ➔ template.md Content`.

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

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Acceptance passed. Fresh `claude -p --permission-mode plan` runs invoked `write-plan` in 5/5 and produced the full structure (U1 heading, Deliverables, Files, Done when, Dependencies) in 5/5; the user's interactive run showed write-plan, then over-engineering-check, then the plan-approval view. One deviation: the template's spacing was changed (see Amendments); one confirming run on the changed template also triggered and kept the structure.
- Files: modified `plugins/workflow-preferences/skills/write-plan/resources/template.md` (+8 blank lines). Test logs, the classifier `classify.py` and a negative control are in the session scratchpad only; six test plans `plan-this-change-add-*.md` were left in `~/.claude/plans/`.
- Gotchas: in `-p`, ExitPlanMode is absent from the session's tool list (confirmed in the run logs), so agents end by asking for approval in text; only an interactive run exercises the exit step. `-p` plan mode does write a plan file to `~/.claude/plans/`. Agents copy the template's blank-line layout exactly, so missing blank lines show up as subheadings running into lists in the approval view. In zsh, `${PIPESTATUS[0]}` is empty; use `$pipestatus`.
- Decisions made and why: matched each plan file to its run by the run's own Write call rather than by timestamp, because the five runs were parallel. Ran a negative control so the classifier was shown able to fail. Skipped the optional Sonnet run (plan default) and a second interactive run (user: "I'm happy not to do another interactive test").

---

## Handoff
_Replaced each session, never appended to._
- Written against: U3, done; all units done
- Why stopped: plan complete
- Mid-edit when stopped: none
- Open question awaiting an answer: none
- Working agreements: none recorded
- Next action: none - plan complete
- Environment: branch `10-write-plan-skill`; `plugins/sdd/sdd.md` has an uncommitted change unrelated to this work; dotfiles has the U2 edit to `claude/.claude/CLAUDE.md` uncommitted, by plan
