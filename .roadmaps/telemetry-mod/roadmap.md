# telemetry-mod Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #4_
_Updated: 2026-10-29 - added a model pick (Claude + GPT) to each unit; U2 amendment on clodex aliases; U8 amendment to remove the throwaway mod; handoff environment corrected_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Scaffold the plugin and the repo rules | not started | - |
| U2 | Pricing and the per-turn ledger (pure) | not started | U1 |
| U3 | Cache estimator (pure) | not started | U1 |
| U4 | Formatting (pure) | not started | U1 |
| U5 | Wiring, state and the per-turn row | not started | U2, U3, U4 |
| U6 | The band, and the under-the-prompt spike | not started | U5 |
| U7 | `/telemetry` pane | not started | U4, U5 |
| U8 | README, final validation, comparison with the old telemetry | not started | U5, U6, U7 |
| U9 | Rewrite the repo rules for scripts and mods | not started | U1, U2, U3, U4, U5, U6, U7, U8 |

States: `not started` / `in progress` / `done`

Model picks (2026-10-29): each unit's **Model:** line gives one Claude and one GPT model (effort in brackets); switch to it before `/roadmap begin`. Picked from current release benchmarks and prices: Opus 5.5 leads coding (SWE-bench Pro 89.9%, first on Artificial Analysis's Coding Agent Index v2.0); Sonnet 5.5 is close on terminal work at half Opus's rates; GPT-6 Astra is the strongest GPT for coding, but costs 2.5× Opus per token; GPT-6 Sol is the cheap GPT default. Model-picker's reference (snapshot 2026-09-13) predates Opus/Sonnet/Haiku 5.5 and lists GPT-5.6 Sol/Luna rather than the GPT-6 models the `sol`/`luna` aliases now run, so its picks weren't used as-is.

## Amendments
_Append-only. Where execution diverged or will diverge from the frozen plan. `none.` until one occurs._
- U2: before validating the GPT rates, confirm which OpenAI model each clodex alias runs, and price that model. Claude Code's model list names `luna` = GPT-6 Luna, `sol` = GPT-6 Sol, `terra` = GPT-5.6 Terra, `astra` = GPT-6 Astra. The `luna`/`sol` starting values ($0.10/$0.01/$0.50 and $2/$0.20/$10, taken from telemetry's `pricing.json`) match GPT-6 rates, not the GPT-5.6 models `pricing.json`'s comment names: GPT-5.6 Luna is $0.20/$0.02/$1.20 and GPT-5.6 Sol $4/$0.40/$20 (OpenAI pricing, read 2026-10-29). GPT-6.1 Sol reportedly has a $0.10 cache-read rate. - overrides `plan.md:320-323`. reason: found while checking model picks; the plan's rows name aliases without saying which model they price.
- U8: at the end, remove the throwaway mod folder `/home/david/.claude/dev-mods/b494e4d3-f092-4319-a6e5-921df7fbf4bf/telemetry-preview/` (ask before deleting; it is outside git). Kept until then as a reference. - extends `plan.md:687-773`. reason: the plan's final unit has no cleanup step.

---

### U1 - Scaffold the plugin and the repo rules

**Status:** not started

**Effort:** -

**Model:** Claude: Sonnet 5.5 (medium) · GPT: Sol (medium) - small scaffolding with mechanical checks; no need for Opus.

**Executes:** `plan.md:156-246 § U1: Scaffold the plugin and the repo rules`

**Acceptance:** `plan.md:241-246 § U1 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:43 § Decisions ➔ D1`, `plan.md:48 § Decisions ➔ D12`, `plan.md:59 § Decisions ➔ X3`

**Gotchas:** `plan.md:77 § Cross-cutting gotchas ➔ G8`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U2 - Pricing and the per-turn ledger (pure)

**Status:** not started

**Effort:** -

**Model:** Claude: Opus 5.5 (high) · GPT: Sol (high) - pricing research plus exact arithmetic; mistakes here skew every cost row.

**Executes:** `plan.md:250-381 § U2: Pricing and the per-turn ledger (pure)`

**Acceptance:** `plan.md:379-381 § U2 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:44-45 § Decisions ➔ D2, D9`, `plan.md:57 § Decisions ➔ X1`, `plan.md:62-63 § Decisions ➔ A1, A2`, `plan.md:66 § Decisions ➔ A5`

**Gotchas:** `plan.md:74-76 § Cross-cutting gotchas ➔ G5, G6, G7`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U3 - Cache estimator (pure)

**Status:** not started

**Effort:** -

**Model:** Claude: Sonnet 5.5 (medium) · GPT: Sol (medium) - small algorithm, fully specified with a test table.

**Executes:** `plan.md:385-442 § U3: Cache estimator (pure)`

**Acceptance:** `plan.md:442 § U3 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:54 § Decisions ➔ D8`, `plan.md:62 § Decisions ➔ A1`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U4 - Formatting (pure)

**Status:** not started

**Effort:** -

**Model:** Claude: Haiku 5.5 (high) · GPT: Sol (low) - pure functions with an exact spec and tests; step up to Sonnet 5.5 if tests fail twice.

**Executes:** `plan.md:446-503 § U4: Formatting (pure)`

**Acceptance:** `plan.md:503 § U4 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:49 § Decisions ➔ D3`, `plan.md:53 § Decisions ➔ D7`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U5 - Wiring, state and the per-turn row

**Status:** not started

**Effort:** -

**Model:** Claude: Opus 5.5 (high) · GPT: Astra (high) - hardest unit: unfamiliar mod API, live-session debugging, formula check.

**Executes:** `plan.md:507-590 § U5: Wiring, state and the per-turn row`

**Acceptance:** `plan.md:577-590 § U5 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:44 § Decisions ➔ D2`, `plan.md:46 § Decisions ➔ D10`, `plan.md:49-50 § Decisions ➔ D3, D4`, `plan.md:63-66 § Decisions ➔ A2-A5`

**Gotchas:** `plan.md:70-75 § Cross-cutting gotchas ➔ G1-G6`

**Reference:** `plan.md:79-129 § Reference: patterns proven in the throwaway`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U6 - The band, and the under-the-prompt spike

**Status:** not started

**Effort:** -

**Model:** Claude: Opus 5.5 (medium) · GPT: Astra (medium) - unfamiliar render API plus an exploratory placement spike.

**Executes:** `plan.md:594-641 § U6: The band, and the under-the-prompt spike`

**Acceptance:** `plan.md:632-641 § U6 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:52-53 § Decisions ➔ D6, D7`, `plan.md:58 § Decisions ➔ X2`

**Gotchas:** `plan.md:70-73 § Cross-cutting gotchas ➔ G1-G4`

**Reference:** `plan.md:79-129 § Reference: patterns proven in the throwaway`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U7 - `/telemetry` pane

**Status:** not started

**Effort:** -

**Model:** Claude: Sonnet 5.5 (high) · GPT: Sol (high) - follows the render patterns U6 establishes.

**Executes:** `plan.md:645-683 § U7: /telemetry pane`

**Acceptance:** `plan.md:680-683 § U7 ➔ Done when`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:51 § Decisions ➔ D5`, `plan.md:64 § Decisions ➔ A3`

**Reference:** `plan.md:79-129 § Reference: patterns proven in the throwaway`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U8 - README, final validation, comparison with the old telemetry

**Status:** not started

**Effort:** -

**Model:** Claude: Sonnet 5.5 (medium) · GPT: Sol (medium) - README writing plus running the checks.

**Executes:** `plan.md:687-773 § U8: README, final validation, comparison with the old telemetry`

**Acceptance:** `plan.md:758-773 § U8 ➔ Done when`, `plan.md:824-834 § Verification (end to end)`

**Scope limits:** `plan.md:14-18 § Context ➔ Not building or doing`

**Conventions:** `plan.md:20-38 § Conventions`

**Decisions:** `plan.md:43 § Decisions ➔ D1`, `plan.md:47 § Decisions ➔ D11`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

### U9 - Rewrite the repo rules for scripts and mods

**Status:** not started

**Effort:** -

**Model:** Claude: Opus 5.5 (medium) · GPT: Astra (medium) - judgment-heavy rules rewrite; few tokens, so the stronger model is cheap here.

**Executes:** `plan.md:777-821 § U9: Rewrite the repo rules for scripts and mods`

**Acceptance:** `plan.md:819-821 § U9 ➔ Done when`

**Conventions:** `plan.md:32 § Conventions ➔ Repo rules are warnings`

**Decisions:** `plan.md:48 § Decisions ➔ D12`

**Stop-and-ask:** `plan.md:143-152 § Stop-and-ask triggers (all units)`

**Key findings:** _(all four required before this unit may be close)_
- Outcome:
- Files:
- Gotchas:
- Decisions made and why:

---

## Handoff
_Replaced each session, never appended to._
- Written against: U1, not started
- Why stopped: roadmap just created; no unit begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: the two stated during plan review are recorded in the plan as D9 (Brave search first, `plan.md:45`) and D11 (comments for a reader new to mods and TypeScript, `plan.md:47`); everything else is in the user's CLAUDE.md.
- Next action: switch to Sonnet 5.5 (medium), or Sol (medium) if out of Claude tokens, then `/roadmap begin U1`.
- Environment: branch `4-create-telemetry-mod`; the throwaway mod `telemetry-preview` is on disk at `/home/david/.claude/dev-mods/b494e4d3-f092-4319-a6e5-921df7fbf4bf/telemetry-preview/` but not loaded in this session (it loaded only for the earlier one); the old `telemetry` plugin is installed and running.
