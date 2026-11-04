# over-engineering-check skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #9_
_Updated: 2026-11-04 - U3 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the skill file | done | - |
| U2 | Rewrite the always-on rules and update the notes | done | U1 |
| U3 | Behaviour tests | done | U1 |

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

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: no deviations. The over-engineering rule (D12) and narrow-reading rule (D18) are rewritten in dotfiles `CLAUDE.md` and committed (`89bf0f3`, only that file). The D14 bullet and D16 section are in `~/notes/working-with-ai.md`. All five Done-when checks passed.
- Files: modified `/home/david/dotfiles/claude/.claude/CLAUDE.md` (lines 8 and 23) and `/home/david/notes/working-with-ai.md` (bullet at line 48, section at line 76). Neither is in this repo. `settings.json` in dotfiles stays modified and uncommitted, untouched.
- Gotchas: the plan's D16 markdown block is `plan.md:252-288`; my first attempt used the wrong range and was redone. `Edit` needs a prior `Read` of each file.
- Decisions made and why: the dotfiles commit was made during the unit, not by `close`, because the roadmap commit covers only this repo. The notes file is not in git, so it has no commit.

---

### U3 - Behaviour tests

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: no deviations. T5 (Sonnet 1.00, Opus 1.00, 3/3 fired each) and T6 (Sonnet 1.00, 0/3 fired) passed against `plan.md:369-370`. T1-T4 were run by the user, who confirmed every expected result held; no per-case output was recorded.
- Files: added `plugins/workflow-preferences/evals/{trigger-patching-a-patch,no-trigger-bug-review}/prompt.md` and one grader each under `graders/`, copied from `plan.md:374-426`. Modified `.gitignore` (`plugins/*/evals/results/`) and root `CLAUDE.md` (evals bullet under `## Commands`). `evals/results/` is ignored and untracked.
- Gotchas: the plan's U3 heading and the roadmap's earlier wording say T1-T5, but the plan defines T1-T6. Exit codes of the eval commands were not captured (`${PIPESTATUS[0]}` is empty in zsh), so the pass rests on the printed scores and ✓ lines. The `plugins:` fallback at `plan.md:445-447` was not needed.
- Decisions made and why: ran the three eval commands exactly as in `plan.md:430-432`. Accepted the user's word for T1-T4 rather than re-running them, at the user's instruction.

---

## Handoff
_Replaced each session, never appended to._
- Written against: U3, done
- Why stopped: U3 closed, the last unit; waiting for the user's OK to push and open the PR.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: may I push the branch and open a PR with `Closes #9` (`plan.md:452-453`)?
- Working agreements: "During execution, stop for my review after each unit." (user's global `CLAUDE.md`, Plans section). "Defer commits and such to roadmap." (user, when asked to propose U1's changes; commits go through `roadmap close`.)
- Next action: none - plan complete
- Environment: branch `9-add-over-engineering-check-skill-to-workflow-preferences`; dotfiles has an unrelated uncommitted change to `claude/.claude/settings.json`.
