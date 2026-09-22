# Stage 1 Vision Tooling Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: none_
_Updated: 2026-09-21 - U2 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | `bin/check-vision` and its tests | done | - |
| U2 | the `/vision` skill | done | U1 |
| U3 | README and a real run | not started | U1, U2 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged from the frozen plan. `none.` until one occurs._
- U2: verified the `plan.md:791` "new session" review requirement with a fresh subagent (no memory of the interview) instead of an actual new Claude Code session, since this session couldn't spawn one — the subagent read only `SKILL.md`'s Review section and the overview file, same isolation the plan is testing for.

---

### U1 - `bin/check-vision` and its tests

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Built as `plan.md:175-601` specifies, code copied verbatim. Acceptance (`plan.md:603-608`) passed: `python3 -m unittest discover -s plugins/spec-driven-development/tests` ran 14 tests, `OK`; `cd /tmp && check-vision --root .` printed `check-vision: /tmp/docs/01-overview.md does not exist` and exited 2. Confirmed the check can fail: hardcoding the 8 heading names in a scratch copy made `test_headings_come_from_the_template` fail with `'missing-heading' not found in []`. Also exercised on a real document outside the test suite (one heading answered, rest still template prompts, plus a leftover draft): exit 1, 7 `empty-heading` findings, `--status` reported `filled`.
- Files: Created `plugins/spec-driven-development/bin/check-vision` (chmod +x, mode 775 pre-commit), `plugins/spec-driven-development/tests/test_check_vision.py`, `plugins/spec-driven-development/.gitignore` (`__pycache__/`). Modified `plugins/spec-driven-development/config.json` (removed the `vision` block) and `.claude/rules/spec-driven-development.md` (replaced the word-limit ownership row with `| Deterministic checks and their finding IDs | bin/check-vision |`). U2 and U3 read `bin/check-vision` and `config.json` as they now stand.
- Gotchas: `git ls-files -s` shows nothing for an untracked file, so the mode check from `plan.md:879` can only be confirmed right after staging/commit, not before.
- Decisions made and why: `.gitignore` placed at the plugin root (`plugins/spec-driven-development/.gitignore`) rather than the repo root — the plan named the file but not its location, and plugin-scoped build artifacts (`__pycache__/`) belong with the plugin that creates them.

---

### U2 - the `/vision` skill

**Status:** done

**Effort:** 0h 30m

**Key findings:**
- Outcome: Built as `plan.md:626-768` specifies, content copied verbatim. Acceptance (`plan.md:786-796`) passed on all five points: Setup on an empty temp project filled the title and left prompts intact (`missing`→`empty`); a real interview (toy idea: a tea-steeping timer) produced a draft `check-vision --draft` reported `OK` on; a fresh subagent with no memory of the interview ran Review and printed **Structure** `OK` / **Judgment** `No findings.`; a hand-written flawed overview produced 3 findings including both required ones ("probably on Postgres", "should feel fast"), and a clean one produced exactly `No findings.`; `grep -c '^### ' skills/vision/SKILL.md` → 2, the skill's own subheadings, not the template's eight.
- Files: Created `plugins/spec-driven-development/skills/vision/SKILL.md` only. `bin/check-vision`, `config.json` and `templates/01-overview.md` untouched, as required. U3 documents and exercises this file.
- Gotchas: none.
- Decisions made and why: The "existing vision" behaviour (`plan.md:892` open decision) was confirmed with the user as "ask, as drafted" — already the plan's Content wording, so no file change resulted, just confirmation. See also the Amendments entry on how the fresh-session requirement was tested.

---

### U3 - README and a real run

**Status:** not started

**Effort:** -

**Executes:** `plan.md:802-859 § U3 — README and a real run`

**Acceptance:** `plan.md:861-865 § U3 — README and a real run ➔ Done when`

**Scope:** `plan.md:25-31 § What we are NOT building`

**Terms:** `plan.md:39-40 § Terms ➔ Plugin root`

**Conventions:** `plan.md:134-146 § Conventions`

**Cross-cutting gotchas:** `plan.md:150-161 § Cross-cutting gotchas`

**Stop-and-ask:** `plan.md:165-169 § Stop-and-ask triggers`

**Verification:** `plan.md:871-887 § Verification`

**Open decisions:** `plan.md:891 § Decisions left for you ➔ U3's real project`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U2, closed this session.
- Why stopped: U2 complete and committed; next unit not yet begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: Commit at `start`, and approval to commit when closing units as well - stated by the user in reply to whether `start` should commit ("Commit at the start, and you have approval to commit when closing stages as well.").
- Next action: `/roadmap begin U3`
- Environment: project root `/home/david/agent-tools/plugin-marketplace`; branch `spec-driven-development_stage-1`; HEAD `be559e6` before this session's commit.
