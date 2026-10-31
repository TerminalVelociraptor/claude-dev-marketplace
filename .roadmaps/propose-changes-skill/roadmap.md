# propose-changes skill Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #8_
_Updated: 2026-10-31 - U2 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Create the skill file | done | - |
| U2 | Rewrite issue #8's body | done | - |
| U3 | Remove the CLAUDE.md section and run the clean subagent test | done | U1 |
| U4 | User live tests, then restore the section | not started | U3 |
| U5 | Commit | not started | U4 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U5: work happens on the existing branch `8-add-propose-changes-skill-to-workflow-preferences` (already checked out at start), not a new `8-add-propose-changes-skill` from `main` - overrides `plan.md:33` and `plan.md:262`. reason: the user created this branch before `/roadmap start`.
- U5: also write `plugins/workflow-preferences/README.md` (short: plugin purpose, the one skill `propose-changes`, how to invoke it as `/workflow-preferences:propose-changes`; at least 40 words) and commit it with the skill - overrides `plan.md:262` (commit `SKILL.md` only) and `plan.md:264` (Done when: `git log -1 --stat` shows only `SKILL.md`); U5 now expects `SKILL.md` plus `README.md`, plus the `.roadmaps/` files. reason: user decision after U1; `plugin validate` reported `README_MISSING`. LICENSE and icon findings stay out of scope.
- U3: the subagent test was not clean: the subagent still saw the removed `# Presenting proposed changes` rules (likely inherited from this session's startup CLAUDE.md; mechanism unverified). User accepted the run as-is (option a) - overrides `plan.md:26` (D10, "run only after the section is removed so the test is clean"). U4's live tests in fresh sessions serve as the clean test. reason: the subagent followed the skill over CLAUDE.md and reported every conflict.
- U3/U4: the CLAUDE.md backup is at `/tmp/claude-1000/-home-david-agent-tools-plugin-marketplace/5defd3f7-3531-4841-ac91-d9f8096ece7b/scratchpad/presenting-proposed-changes.md` (plus a whole-file copy `presenting-proposed-changes.full-backup.md` in the same directory), not the path in `plan.md:160`; U4 restores from it. reason: the plan's path is in an earlier session's scratchpad; user approved ("go").

---

### U1 - Create the skill file

**Status:** done

**Effort:** 0h 15m

**Key findings:**
- Outcome: Created `plugins/workflow-preferences/skills/propose-changes/SKILL.md` verbatim from `plan.md:50-122`; no deviations. Acceptance passed: `claude plugin validate` reports "Validation passed"; `grep -c '~~'` → `0`.
- Files: added `plugins/workflow-preferences/skills/propose-changes/SKILL.md` (65 lines). U3 and U4 test this file; U5 commits it. `SKILL.md:16` is 101 columns, one over the ~100 target (A3), kept verbatim.
- Gotchas: `plugin validate` also reports `README_MISSING` and `LICENSE_MISSING` (directory-submission errors) and `ICON_MISSING` (warning); none fail the run. README is handled in U5 (see Amendments). The plan's outer four-backtick fence must be stripped when extracting the file.
- Decisions made and why: kept the plan's text verbatim, including the 101-column line, rather than re-wrap, so the file matches what the user approved. LICENSE and icon left out of scope by the user.

---

### U2 - Rewrite issue #8's body

**Status:** done

**Effort:** 0h 15m

**Key findings:**
- Outcome: Issue #8's body replaced with the text from `plan.md:128-155`; no deviations. Acceptance passed: the body read back starts with `## Goal`, contains "diff block", and contains neither "Blocked by #7" nor "Repeat 3 times".
- Files: no repo files changed. The body was sent from a scratchpad file, not kept in the repo.
- Gotchas: the plan's command names a scratchpad path from an earlier session; a path in the current session's scratchpad was used instead. GitHub adds one trailing blank line to the stored body, so a byte-for-byte diff against the sent file shows that one line.
- Decisions made and why: held the edit for the user's explicit approval ("approve C1") before running `gh issue edit`, since the issue is visible outside this machine. Title, labels and comments left unchanged.

---

### U3 - Remove the CLAUDE.md section and run the clean subagent test

**Status:** done

**Effort:** 0h 15m

**Key findings:**
- Outcome: Removed `# Presenting proposed changes` (lines 47-56) from `~/dotfiles/claude/.claude/CLAUDE.md`, ran the subagent clarity test, applied user-approved fixes C1, C2, C3 and C5 to `SKILL.md`. Acceptance passed: Part B 9/10, with the #8 mismatch accepted by the user as addressed by C1; Part C defects fixed or waived; `claude plugin validate` passes and `grep -c '~~'` → `0`. Deviations: see Amendments (test not clean; backup path).
- Files: modified `plugins/workflow-preferences/skills/propose-changes/SKILL.md` - description also triggers when asked which format/structure/process to use (`SKILL.md:8-9`); unknown Why still shows the change and asks after it (`SKILL.md:26-27`); review fixes diff against current code (`SKILL.md:37-39`); example context line `return out.sort()` (`SKILL.md:67`). Modified `~/dotfiles/claude/.claude/CLAUDE.md` outside the repo (section removed, not committed). U4 must restore it from the backup named in the Amendments.
- Gotchas: a subagent launched from a session started before the removal still sees the removed CLAUDE.md rules (it quoted them as conflicts while `grep -c` on disk returned `0`); mechanism unverified. A clean test needs a session started after the removal. The S5 review showed stacked diffs (a later fix written against earlier fixes), which the skill did not forbid until C3. Part B #8 was not re-tested after C1.
- Decisions made and why: accepted the unclean run (option a) because the subagent followed the skill over CLAUDE.md and reported every conflict; U4's fresh-session live tests serve as the clean test. Waived C4 (caveat placement), C6 (extra example) and the rest of Part C as already covered or out of scope. Kept the folded description's short line `asked which one to use; and` rather than exceed 100 columns.

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
- Written against: U1, U2, U3 done; no unit in progress
- Why stopped: U3 closed, awaiting the user's review
- Mid-edit when stopped: the `# Presenting proposed changes` section is still removed from `~/dotfiles/claude/.claude/CLAUDE.md` (intended until U4); backup in this session's scratchpad (see Amendments) - `/tmp` may not survive a reboot
- Open question awaiting an answer: none
- Working agreements: "During execution, stop for my review after each unit." (user CLAUDE.md, Plans section); before any subagent, post a pre-flight check and wait for OK (user CLAUDE.md hard rule).
- Next action: `/roadmap begin U4` (depends on U3, satisfied); live tests in a session started after the removal, then restore the section from the backup
- Environment: branch `8-add-propose-changes-skill-to-workflow-preferences`; `claude` is aliased to `clodex claude`, use `command claude`
