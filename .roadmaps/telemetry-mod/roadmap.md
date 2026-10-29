# telemetry-mod Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #4_
_Updated: 2026-10-29 - U2 closed (done)_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Scaffold the plugin and the repo rules | done | - |
| U2 | Pricing and the per-turn ledger (pure) | done | U1 |
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
- U1: `types/index.d.ts` stub exports `type Snapshot = {}` and declares `'telemetry-mod': { snap: Shaped<Snapshot> }`, with no `export {}`. - overrides `plan.md:196-204`. reason: the validator rejects `export {}` (a contract may export only types); a real `export type` also makes the file a module so the `declare module` block augments instead of redefining. U5 replaces `Snapshot`. Approved by the user 2026-10-29.
- U1: to generate `plugins/telemetry-mod/.claude-plugin/types/`, load the repo folder with `claude --plugin-dir plugins/telemetry-mod` instead of `/plugin install telemetry-mod@dev-toolkits` + `/reload-plugins`. - overrides `plan.md:238`. reason: the marketplace install loaded a cached copy under `~/.claude/plugins/cache/` and generated no types folder in the repo (G8's stop condition); the cached copy was uninstalled. Approved by the user 2026-10-29.
- U8: at the end, remove the throwaway mod folder `/home/david/.claude/dev-mods/b494e4d3-f092-4319-a6e5-921df7fbf4bf/telemetry-preview/` (ask before deleting; it is outside git). Kept until then as a reference. - extends `plan.md:687-773`. reason: the plan's final unit has no cleanup step.
- U2: the GPT rows price the models the user set on 2026-10-29: `astra` = GPT-6 Astra, `luna` = GPT-6 Luna, `sol` = GPT-6.1 Sol, `terra` = GPT-6.1 Terra. This supersedes the alias list in the first U2 amendment (`sol` was GPT-6 Sol, `terra` GPT-5.6 Terra). - overrides `plan.md:268`, `plan.md:320-323`. reason: the user updated their model config; this session's Agent tool list still shows the old mapping, so the user's statement is the source.
- U2: `Rates` gains an optional `cacheWrite?: number`, a fixed cache-write multiplier that replaces `CACHE_WRITE_MULTIPLIER[ttl]` when set. The GPT rows set it to 1.25 (OpenAI's default 30-minute write; 12-hour writes are 2.5×), and Claude rows leave it out. - overrides `plan.md:284-287`, `plan.md:306`. reason: OpenAI's cache-write multipliers don't match Claude's 5m/1h ones, so with A1's 1h default the plan's formula would price every GPT write at 2×. Approved by the user 2026-10-29 (Decision 1, option A).
- U2: `Ledger` counts a request's Claude Code charge in `tracked` only when we priced it too, and a test row covers an unpriced non-claude model. - overrides `plan.md:354`. reason: Claude Code charges an unpriced non-claude model at the fallback rates; under the plan's rule that charge was in `tracked` but in no group, so `total` came out short by it. Approved by the user 2026-10-29.

---

### U1 - Scaffold the plugin and the repo rules

**Status:** done

**Effort:** 0h 15m

**Model:** Claude: Sonnet 5.5 (medium) · GPT: Sol (medium) - small scaffolding with mechanical checks; no need for Opus.

**Key findings:**
- Outcome: empty-but-loadable mod scaffolded per `plan.md:158-235`, with two deviations (see Amendments, both U1). `claude plugin validate` passes, the marketplace list ends with `telemetry-mod`, `tsc -p plugins/telemetry-mod` (tsc 7.0.2) exits 0, the generated `claude-code/index.d.ts` exists, and nothing under `.claude-plugin/types/` shows in `git status -uall`. The only validate complaints are the README, LICENSE and icon items U8 fixes.
- Files: created `plugins/telemetry-mod/{.claude-plugin/plugin.json,hooks/hooks.json,hooks/register.tsx,types/index.d.ts,tsconfig.json}` and `.gitignore`; modified `.claude-plugin/marketplace.json`. Later units read `types/index.d.ts` (U5 replaces the `Snapshot` stub and fills `PluginState`) and `register.tsx` (U5 fills it in). The engine wrote `plugins/telemetry-mod/.claude-plugin/types/` (gitignored).
- Gotchas: a contract `.d.ts` may only export types, so `export {}` fails validation; it needs a real `export type` to be a module. `/plugin install` loads a cached copy under `~/.claude/plugins/cache/` and never writes the types folder into the repo; only `claude --plugin-dir plugins/telemetry-mod` does. Two `CLAUDE.md` rules don't fit a mod, a departure per `plan.md:32` that U9 rewrites: checks run through `tsc`, `claude plugin validate` and `claude plugin test` rather than Python scripts in `bin/`, and tests will be `tests/*.test.ts` rather than unittest.
- Decisions made and why: `export type Snapshot = {}` rather than `export {}` or a neutral name, to match the throwaway mod's `Shaped<Snapshot>` shape so U5 only fills it in. Types generated via `--plugin-dir` rather than the marketplace install, because the install generated nothing.

---

### U2 - Pricing and the per-turn ledger (pure)

**Status:** done

**Effort:** 0h 30m

**Model:** Claude: Opus 5.5 (high) · GPT: Sol (high) - pricing research plus exact arithmetic; mistakes here skew every cost row.

**Key findings:**
- Outcome: built `hooks/pricing.ts` (12-row `RATES`, `priceUsage`, `chargedByClaudeCode`) and `hooks/ledger.ts` (`Ledger`) per `plan.md:282-357`, with three deviations (Amendments: U2 alias mapping, `cacheWrite`, `tracked` rule). Every rate row and formula facts 1-5 were checked against Anthropic's and OpenAI's pricing pages on 2026-10-29 (sources in `pricing.ts`'s header); fact 5, the fallback model, is unverified. `claude plugin test plugins/telemetry-mod`: 16 pass, 0 fail, exit 0 (exits 1 with a rate or the tier rule mutated); `tsc -p plugins/telemetry-mod` exit 0.
- Files: created `plugins/telemetry-mod/hooks/{pricing.ts,ledger.ts}` and `plugins/telemetry-mod/tests/{pricing.test.ts,ledger.test.ts}` (11 and 5 tests). U4 reads `ledger.ts` for the `TurnCost` shape. U5 reads `ledger.ts` (`add` takes the cache lifetime per request, because `close` has none) and `pricing.ts` (`FALLBACK_MODEL` is what its check against Claude Code's total must confirm).
- Gotchas: `tsc` rejects `.ts` in import paths (TS5097); import without the extension, which both `tsc` and `claude plugin test` accept. The test kit has no `toBeCloseTo`; each test file has a `near()` helper. GPT prompt length counts cache-write tokens, so a 1M-token write trips the 272K tier. clodex 2.21.4 on the `openai-oauth` route never reports GPT cache writes (0 of 1,556 GPT requests across 278 logs in `~/.clodex/logs/sessions/`; reads on 1,341): written tokens arrive inside `input_tokens`, so GPT cost reads low by 0.25x input rate on them, and `cacheWrite` is inert there. The log fields are camelCase (`cacheCreationInputTokens`); a snake_case grep finds nothing. `openai-oauth` is a ChatGPT sign-in, so GPT figures are API-equivalent, not billed. Fallback evidence conflicts with G6: `github.com/abundant-ai/harbor/pull/139` (Claude Code 2.1.285) says unknown ids are priced at "the default model's rate" ($5/M in its example), and the engine types say only "the default tier was assumed" (`.claude-plugin/types/claude-code/index.d.ts:8069`).
- Decisions made and why: published rates replace the plan's starting values where they differ: `claude-sonnet-5-5` cache read 0.20 -> 0.10, `claude-haiku-5-5` cache read (X1) = 0.01, `terra` (GPT-6.1 Terra) 2/0.20/12 -> 1/0.05/5, `sol` (GPT-6.1 Sol) cache read 0.20 -> 0.10; Terra's two test expectations changed to 8.1 and 0.272 (`plan.md:381` allows it). `FALLBACK_MODEL` stays `claude-sonnet-5`, marked unverified, per `plan.md:275`, so U5's check against real totals settles it rather than third-party evidence. `cacheWrite` is kept although inert on `openai-oauth`, so GPT writes price correctly if clodex starts receiving write counts. Two test rows were added beyond the plan's table (Terra's fixed write multiplier; Haiku 5.5's tier counting cache reads), plus one for the `tracked` amendment, to cover rules the table didn't. The validation table itself was reported in the session, not saved to a file.

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
- Written against: U1, U2 done; U3, U4 not started
- Why stopped: U2 closed and committed; no unit begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: D9 (Brave search first, `plan.md:45`) and D11 (comments for a reader new to mods and TypeScript, `plan.md:47`) were stated during plan review; everything else is in the user's CLAUDE.md.
- Next action: U3 and U4 are unblocked (U5 needs both). Switch to the model on the chosen unit's **Model:** line (U3: Sonnet 5.5 medium; U4: Haiku 5.5 high), then `/roadmap begin <unit>`.
- Environment: branch `4-create-telemetry-mod`; the old `telemetry` plugin is still installed and running; the throwaway mod `telemetry-preview` is still on disk (U8 amendment); the scratch copies used for mutation checks were deleted.
