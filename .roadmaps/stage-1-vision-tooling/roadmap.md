# Stage 1 Vision Tooling Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: none_
_Updated: 2026-09-21 - U1 closed_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | `bin/check-vision` and its tests | done | - |
| U2 | the `/vision` skill | not started | U1 |
| U3 | README and a real run | not started | U1, U2 |

States: `not started` / `in progress` / `done`

## Amendments
_Append-only. Where execution diverged from the frozen plan. `none.` until one occurs._
none.

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

**Status:** not started

**Effort:** -

**Executes:** `plan.md:614-784 § U2 — the /vision skill`

**Acceptance:** `plan.md:786-796 § U2 — the /vision skill ➔ Done when`

**Scope:** `plan.md:25-31 § What we are NOT building`

**Terms:** `plan.md:39-40 § Terms ➔ Plugin root`

**Conventions:** `plan.md:134-146 § Conventions`

**Cross-cutting gotchas:** `plan.md:150-161 § Cross-cutting gotchas`

**Stop-and-ask:** `plan.md:165-169 § Stop-and-ask triggers`

**Verification:** `plan.md:871-887 § Verification`

**Open decisions:** `plan.md:892-894 § Decisions left for you ➔ Existing-vision behaviour and Assumed items`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

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
- Written against: U1, closed this session.
- Why stopped: U1 complete and committed; next unit not yet begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: Commit at `start`, and approval to commit when closing units as well - stated by the user in reply to whether `start` should commit ("Commit at the start, and you have approval to commit when closing stages as well.").
- Next action: `/roadmap begin U2`
- Environment: project root `/home/david/agent-tools/plugin-marketplace`; branch `spec-driven-development_stage-1`; HEAD `5706e1c` before this session's commit.
