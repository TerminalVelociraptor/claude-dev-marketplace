# telemetry-mod Roadmap

_Plan: `plan.md`_ - frozen. Read it for scope, contracts, terminology and acceptance.
_Ticket: #4_
_Updated: 2026-10-30 - U6 closed (done)_

## State
| Unit | Name | State | Depends on |
|---|---|---|---|
| U1 | Scaffold the plugin and the repo rules | done | - |
| U2 | Pricing and the per-turn ledger (pure) | done | U1 |
| U3 | Cache estimator (pure) | done | U1 |
| U4 | Formatting (pure) | done | U1 |
| U5 | Wiring, state and the per-turn row | done | U2, U3, U4 |
| U6 | The band, and the under-the-prompt spike | done | U5 |
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
- U5: besides the plan's three Opus turns, check the formula and `row` on a turn with a non-claude (clodex GPT) request: its `untracked` must stay under $0.005, which also confirms `FALLBACK_MODEL` (`plan.md:289`, unverified in U2); and read one real clodex log line to find its field names before any log replay. - extends `plan.md:577-590`. reason: U5's done-when covers only plain Opus turns, so nothing checks `FALLBACK_MODEL` or runs `row` on a real turn, which U2 and U4 both left to U5. Requested by the user 2026-10-29.
- U5: `CacheState`, `Group` and `TurnCost` move into `types/index.d.ts`, deleted from `hooks/cache.ts` and `hooks/ledger.ts`; those two plus `hooks/format.ts` and `tests/format.test.ts` import them from `../types`, with no re-export. - overrides `plan.md:511-513`, `plan.md:515-518`. reason: `claude plugin validate` refuses any import in the contract (`import reaches outside the file; the contract must be self-contained`), so the contract must own the stored-state types; this is the fallback `plan.md:537` names, with its extra files. Approved by the user 2026-10-29 (revised C1, option A).
- U5: `turn.step` prices a subagent request's cache writes at the 5-minute rate; only main-thread requests use `writeTtl(cache)`. - overrides `plan.md:553`. reason: in the live session (clodex log `20261029-223333541Z-…-pid353507`) Claude Code charged a Haiku subagent's 31,642-token write at 1.25x; at the main thread's 1h the row's parts came to $0.0070 against a $0.0052 total. One subagent request observed. Approved by the user 2026-10-29 (C9).
- U5: the row shows `untracked` whenever `|untracked| ≥ 0.00005` (prints as at least $0.0001), not from $0.005; `format.ts` and `tests/format.test.ts` changed. - overrides `plan.md:478`. reason: Claude Code makes a request after each turn that the hooks never see (506 input tokens, reading the main cache; likely its prompt suggestion, unverified), which lands in the next turn as `untracked`; hidden under $0.005 it made cheap-model rows not add up ($0.0011 total, $0.0005 main). Approved by the user 2026-10-29 (decision 1, option A).
- U5: the formula check runs 3 plain Opus turns and passes if each row's `untracked` matches, within $0.0005, the price of the post-turn side request in the clodex proxy log, instead of requiring no `untracked`. - overrides `plan.md:589-590`. reason: that side request costs about $0.01 on Opus, so a correct formula still shows `untracked` on every turn. Approved by the user 2026-10-29 (decision 2, option A).
- U5: `FALLBACK_MODEL` is `claude-opus-5-5`, not `claude-sonnet-5`; `hooks/pricing.ts` and `tests/pricing.test.ts` changed (fallback test now expects $4/M, plus a test from the live Terra turn). - overrides `plan.md:275`, `plan.md:289`, and G6 (`plan.md:75`). reason: a live Terra turn (30,674 input tokens, clodex log `20261029-223333541Z-…-pid353507`) showed `untracked $0.06`, which only Claude Code charging $4/M input (Opus 5.5) reproduces; Sonnet 5's $2/M predicts $0.0006. Unverified whether it is the built-in or the user's saved default (both Opus 5.5). Approved by the user 2026-10-29 (C8).
- U5: in a turn with any non-Claude model, `Ledger.close` returns our prices alone: `untracked` undefined, `total` = main + sub, `correction` = our total - Claude Code's delta (0 without one); Claude-only turns are unchanged with `correction` 0. `FALLBACK_MODEL` and `chargedByClaudeCode` are removed; `pricing.ts`, `ledger.ts`, the `TurnCost` comments in `types/index.d.ts`, `tests/pricing.test.ts` and `tests/ledger.test.ts` changed. Supersedes the C8 amendment and the U2 `tracked` amendment. - overrides `plan.md:63` (A2: correction per turn, not per request), `plan.md:275`, `plan.md:289`, `plan.md:354`, G6 (`plan.md:75`). reason: Claude Code's charge for an unknown model isn't a fixed rate: a Terra turn was charged at Opus 5.5 rates in one live session and about $0 in the next (after `/model terra` saved Terra as the default), giving a -$0.08 row. Spend the hooks can't see in such a turn goes uncounted. Approved by the user 2026-10-29 (C10).
- U5: the formula check (as amended, decision 2A) was verified to the row's printed precision (±$0.005), not ±$0.0005, and the live checks were confirmed from rows pasted as text rather than screenshots. - overrides `plan.md:585`, `plan.md:589-590`. reason: the row prints whole cents above $0.01 and the mod's state is kept only in memory, so no exact `untracked` figure can be read outside the session; each row total also matched the old telemetry and the proxy log at that precision.
- U6: the cache view has no `none` state: with no `lastAt` it is `cold`, so the band shows `cache cold` before the first reply and after a model switch; `hooks/cache.ts` and `tests/cache.test.ts` changed. - overrides `plan.md:404`, `plan.md:422`, `plan.md:430`, and the `none` case at `plan.md:611`. reason: `switched()` clears `lastAt` and `hitRatio`, so U3's `none` rule hid the segment after `/model`, and U6's live check (`plan.md:638`) needs `cache cold`; deleting the state was chosen over adding a rule to rescue it. Approved by the user 2026-10-30 (C1b).
- U6: the user confirms each placement and the live checks in words instead of by screenshot. - overrides `plan.md:619`, `plan.md:641`. reason: the user said of the `'above'` band "I don't need to bother with the screenshot" (2026-10-30).
- U6: `/model` changes the band's model name immediately only mid-conversation; switched before the first turn, the name changes on the next 30 s refresh (the cache already reads `cache cold`). U8's README lists this under Known limits. - overrides `plan.md:638`; extends `plan.md:751` (Known limits). reason: in a live fresh session the name took up to 30 s, while mid-conversation (after confirming the context reload) the name and `cache cold` changed at once; likely Claude Code raises `PostModelSwitch` only when there is a conversation, unverified (the typings don't say). Approved by the user 2026-10-30 (option 1).

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

**Status:** done

**Effort:** 0h 30m

**Model:** Claude: Sonnet 5.5 (medium) · GPT: Sol (medium) - small algorithm, fully specified with a test table.

**Key findings:**
- Outcome: built `hooks/cache.ts` (`CacheState`, `INITIAL`, `observe`, `switched`, `resumed`, `view`, `writeTtl`) and `tests/cache.test.ts` (15 tests: one per row of `plan.md:426-437`, plus 4 boundary rows) per `plan.md:385-442`; no deviations. `claude plugin test plugins/telemetry-mod`: 31 pass, 0 fail, exit 0 (16 from U2 plus 15 new); `tsc -p plugins/telemetry-mod` exit 0. With `FIVE_MIN` mutated to 600,000 in a scratch copy, 4 cache tests fail; with the two boundary comparisons loosened (`>` to `>=`, `<` to `<=`), the 2 gap-boundary tests fail; both runs exit 1. Replaying 3,676 real Claude requests (81 sessions in `~/.clodex/logs/sessions/`) through `cache.ts`: a `warm` prediction was followed by a cache read 3,559 of 3,578 times, 35 sessions learned 1h and none 5m.
- Files: created `plugins/telemetry-mod/hooks/cache.ts` and `plugins/telemetry-mod/tests/cache.test.ts`. U5 reads `cache.ts`: `observe`/`switched`/`resumed` take and return a `CacheState` (state it keeps), `view` returns a union on `kind` (`none`/`cold`/`warm`), and `writeTtl` gives pricing's `'5m' | '1h'`. U6 and U7 call `view`.
- Gotchas: the plan's new-model rule `s.ttlSource === 'switch' ? 'switch' : s.ttlSource` is a no-op, so the code uses `s.ttlSource`. The plan uses `promptTokens` without defining it; the code uses `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. An out-of-order time (`at` earlier than `lastAt`) gives a negative gap, so nothing is learned and no special case exists. `switched` drops `hitRatio` as well as `lastAt`, so right after a switch `view` is `none`, not `cold`. The replay's limits: no real data reaches the 5m learning branch (these logs have no 5-minute cache), main thread was approximated as each session's most frequent non-Haiku model, GPT routes were excluded, and the 19 warm-but-no-read requests were not investigated. The plan's `read`/`creation` shorthand maps to `cache_read_input_tokens`/`cache_creation_input_tokens`.
- Decisions made and why: learning the 1h lifetime has no `ttlSource` guard (a `learned` 5m can flip to 1h), because a read after more than 5 minutes proves 1h. Learning the 5m lifetime only runs from `assumed`, so evidence for 1h is never overwritten by a single rewrite. Tests build `ModelUsage` with a `u({read, creation})` helper like `pricing.test.ts`, so the table's shorthand reads the same in both files. Four boundary tests (gap of exactly 5 minutes and exactly 1 hour, two `resumed` edge cases) were added beyond the plan's table, at the user's request, after the first close, because real data never exercises the learning branches and the plan's table skipped the edges.

---

### U4 - Formatting (pure)

**Status:** done

**Effort:** 0h 30m

**Model:** Claude: Haiku 5.5 (high) · GPT: Sol (low) - pure functions with an exact spec and tests; step up to Sonnet 5.5 if tests fail twice.

**Key findings:**
- Outcome: built `hooks/format.ts` (`modelName`, `usd`, `countdown`, `row`, `percentColor`) and `tests/format.test.ts` (9 tests) per `plan.md:446-503`; no deviations. `claude plugin test plugins/telemetry-mod`: 40 pass, 0 fail, exit 0 (31 from U1-U3 plus 9 new); `tsc -p plugins/telemetry-mod` exit 0. With `p < 50` mutated to `p <= 50` in a scratch copy, the `percentColor` test fails and the run exits 1.
- Files: created `plugins/telemetry-mod/hooks/format.ts` and `plugins/telemetry-mod/tests/format.test.ts`. U5 calls `row(turn)` with the `TurnCost` from `Ledger.close`; U6 and U7 use `countdown`, `usd`, `modelName` and `percentColor`.
- Gotchas: the tsconfig makes an array destructure's first element possibly `undefined` (TS18048), so `modelName` writes `const [family = '', ...version]`. `row` was only run on usage numbers made up for the check, not on a real turn: the clodex logs under `~/.clodex/logs/sessions/` did not match the field names tried (not investigated), so the real-turn check is left to U5 (see Amendments).
- Decisions made and why: `row` sorts entries by usd descending, then by `modelName` with `localeCompare` (the plan says "by name" only). Edge tests were added beyond the plan's table: `usd` at 0.01 and 0.0099, `countdown` at 59,999 and 60,000, `untracked` at 0.005 and 0.0049, `percentColor` at 79.9. Both approved by the user 2026-10-29.

---

### U5 - Wiring, state and the per-turn row

**Status:** done

**Effort:** 2h 0m

**Model:** Claude: Opus 5.5 (high) · GPT: Astra (high) - hardest unit: unfamiliar mod API, live-session debugging, formula check.

**Key findings:**
- Outcome: built the state contract, the six hooks in `register.tsx`, the state accessors in `session.ts` and `tests/register.test.tsx` per `plan.md:507-590`, with the deviations in Amendments (U5 entries: contract ownership of the stored-state types, subagent 5m cache writes, `untracked` shown from $0.00005, the formula-check rule and its precision, and non-Claude turns priced at our rates alone, which replaced the `FALLBACK_MODEL` guess). Acceptance: `tsc` exit 0; `claude plugin test`: 48 pass, 0 fail; `claude plugin validate` exit 0, listing the six hooks and `gating hook with .catch` for both classic hooks. Live session (Opus 5.5): plain turn `~$0.37 · main $0.37 (Opus 5.5: 1 request)` matched the old telemetry; the Haiku subagent turn showed `subagents $0.0040 (Haiku 5.5: 1 agent, 1 request)`; three plain Opus turns' `untracked` matched the post-turn side requests in the clodex proxy log; a Terra turn showed `~$0.0018 · main $0.0018 (Terra: 1 request)`, matching the log.
- Files: modified `types/index.d.ts` (state contract; now also defines `CacheState`, `Group`, `TurnCost`), `hooks/register.tsx` (the hooks), `hooks/ledger.ts` (non-Claude turn rule; tracked/correction bookkeeping removed), `hooks/pricing.ts` (`FALLBACK_MODEL` and `chargedByClaudeCode` removed), `hooks/format.ts` (`untracked` threshold), `hooks/cache.ts` (imports `CacheState`), and `tests/{format,ledger,pricing}.test.ts`; created `hooks/session.ts` and `tests/register.test.tsx`. U6 and U7 must read and write state only through `session.ts` (`readSnap`, `updateSnap`, `updateTurns`, `sessionUsd`); U7 adds a `readTurns` there for the pane.
- Gotchas: `claude plugin validate` catches three things `tsc` accepts: an import in the contract (`the contract must be self-contained`), `read`/`update` on an atom defined in another file, and `$` passed into an imported arrow function (it follows `$` across an import only into a `function` declaration). In the test kit, the test's `$` has no `state` noun; a stand-in for a call the mod makes on `$` answers `{ value: … }` while one for a raised event answers its own result; `session.start` needs a stand-in; `Text` drops its `key` in the drawn tree, so find text by `{ type: 'Text', text }`. Claude Code makes requests the hooks never see: after each turn, one of about 506 input tokens reading the main cache (likely its prompt suggestion, unverified), sometimes a second; they land in the next turn's `untracked`, about $0.01 on Opus, and after a GPT turn that side request runs on the GPT model, so a following Claude-only turn carries Claude Code's unpredictable charge for it in `untracked`. Claude Code's charge for an unknown model varied between sessions (Opus 5.5 rates, then about $0 after `/model terra` saved Terra as the default; `/model` always saves the default for new sessions). Subagents write the cache with a 5-minute lifetime, the main thread with 1 hour (two live subagents, one main write). The clodex proxy log has two `response_usage` events per request (`message_start`, then final); take the last per `requestId`. The mod's state is only in memory, so exact figures can't be read from outside the session. A mutation must change what the assertion reads: `main` -> `mainx` slipped past the plan's prefix check.
- Decisions made and why: `session.ts` keeps the atoms private behind `function`-declaration accessors (C4b), not one atom copy per file, so the state names and shape tags live in one place; a kit test with a negative control showed `readSnap` inside `ui.render` still redraws on `updateSnap`. The contract owns the stored-state types and the hooks import them with no re-export (C1, option A), not duplicate definitions. Non-Claude turns use our prices alone (C10), chosen over a fixed fallback (wrong twice) and over trusting Claude Code's total (wrong for GPT either way); the cost is uncounted side spend in those turns. `untracked` shows from $0.00005 so rows add up (decision 1A). `session.start` doesn't await its first refresh, so git can't delay startup. `tests/register.test.tsx` uses an in-memory compare-and-set state stand-in instead of the plan's bare `state.get` stub, because a get-only stub never lets `update` land. Two edge tests beyond the plan's table (subagent turn end, missing Claude Code total) and one for the subagent lifetime, approved by the user. `Limit.percent` is mapped from the engine's `percentUsed`.
---

### U6 - The band, and the under-the-prompt spike

**Status:** done

**Effort:** 1h 0m

**Model:** Claude: Opus 5.5 (medium) · GPT: Astra (medium) - unfamiliar render API plus an exploratory placement spike.

**Key findings:**
- Outcome: built the two-line bordered band per `plan.md:602-614`, drawn above the prompt (`AbovePrompt`), the placement the user picked in the X2 spike ("Above is the winner"); the `hint` and `status` code paths were deleted. Acceptance: `tsc` exit 0; `claude plugin test`: 54 pass, 0 fail (three deliberate breakages of the band each failed one band test); `claude plugin validate` passes, listing `ui.render{component=AbovePrompt}`. Live, confirmed by the user in words: all segments show, mid-conversation `/model` changes the name and shows `cache cold` at once, 7d countdown reads `↻2d09h17m`. Deviations: see Amendments, U6 entries (no `none` cache state, confirmation in words, model name delayed up to 30 s before the first turn).
- Files: created `hooks/band.tsx` (`bandTree(ui, s, now)`: the band as JSX, given the drawing parts from `$.ui.resolve(e)` rather than `$`) and `tests/band.test.tsx`; modified `hooks/register.tsx` (the `AbovePrompt` hook), `hooks/cache.ts` (`view` has no `none`) and `tests/cache.test.ts`. U7's pane cache line (`plan.md:664`) uses `view`, which now returns only `cold` or `warm`.
- Gotchas: `PromptHint` places a custom drawing about 18 columns in, and `width="100%"` / `alignSelf` only stretch it right; Claude Code draws the mode pills separately, so taking over the hint doesn't kill them, and `e.props.hint` was just `·`. `$.ui.status` is plain text only. Claude Code raised no `PostModelSwitch` our hook saw for a switch before the first turn (likely not raised without a conversation, unverified). With nothing beneath the mod, `$.ui.mount` fails when the hook passes (`no implementation for ui.render`); a test of the pass needs an `on('ui.render', …)` stand-in for Claude Code's drawing. The old `telemetry` plugin's status line shows under the prompt alongside the band until it is removed.
- Decisions made and why: removed the cache view's `none` state (C1b) rather than adding a "no model on record" rule, which would have patched the rule that broke. Wrote the band as plain JSX plus a throwaway plain-text builder (C2b) rather than one shared data layer, since only the spike needed sharing. Both spike render hooks were registered unconditionally and chose at run time, because whether the validator accepts conditional registration was unverified. The chosen placement is recorded here rather than as an amendment, since `'above'` was the plan's own fallback. No draft-hiding: only `PromptHint` reports `isDraft`. Accepted the delayed name before the first turn over a shorter refresh or a per-draw `$.session.model()` call.
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
- Written against: U1-U6 done; U7 not started
- Why stopped: U6 closed and committed; no unit begun.
- Mid-edit when stopped: nothing.
- Open question awaiting an answer: none.
- Working agreements: D9 (Brave search first, `plan.md:45`) and D11 (comments for a reader new to mods and TypeScript, `plan.md:47`) were stated during plan review. Proposals use labelled changes C1, C2, … with a `What:` and a `Why:` line before the code (global `CLAUDE.md`, "Presenting proposed changes"; the user approved F3 on 2026-10-29 after saying "You didn't follow the rules for proposing changes … This keeps happening, how do we fix it"). On 2026-10-30, shown the `'above'` band, the user said "I don't need to bother with the screenshot": live checks are confirmed in words (U6 amendment). Everything else is in the user's CLAUDE.md.
- Next action: U7 is unblocked (U4, U5 done). Switch to the model on its **Model:** line (Sonnet 5.5 high), then `/roadmap begin U7`. Read U5's Files (state only through `hooks/session.ts`, add `readTurns` there) and U6's Gotchas (test stand-in for `ui.render`; `view` has no `none`).
- Environment: branch `4-create-telemetry-mod`; the old `telemetry` plugin is still installed and its status line shows under the prompt; the throwaway mod `telemetry-preview` is still on disk (U8 amendment); live checks run in a session started with `claude --plugin-dir plugins/telemetry-mod`; `/model sonnet` was run during U6 and saves the default for new sessions, so the default may now be Sonnet; F3 changed `/home/david/dotfiles/claude/.claude/CLAUDE.md`, uncommitted and outside this repo.
