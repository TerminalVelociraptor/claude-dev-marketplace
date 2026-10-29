# Plan: `telemetry-mod`, a fresh Claude Code mod for cost and session telemetry

## Context

`plugins/telemetry` (Python hooks + a `statusLine` command) exists mainly to work around two limits: plugins can't set the status line, and Claude Code's cost total only reached the status line. That produced `/telemetry:setup`, the `plugin_root` file, the startup reminder, the status-line → `cc_snapshot.json` → `Stop` hand-off with a 1.5 s wait, and the `resync` baseline.

Claude Code's mod API (in-process TypeScript hooks) removes both limits: `$.session.usage()` / `session.measure` give the cost total, context and rate limits directly. Also, `turn.step` reports each model request's usage, including subagents (`agentId`) and clodex GPT calls (model id `terra`). A throwaway mod (`telemetry-preview`, 2026-10-29) proved this on screen: a bordered band above the prompt, and a per-turn row showing main/subagent requests and agent counts.

**Goal:** a new plugin `plugins/telemetry-mod`, built fresh as a mod (not a port of telemetry's code or workarounds):
- **A.** An always-on status band: model, effort, git / context, cost, 5h and 7d limits, cache. Under the prompt if the spike in U6 finds a workable way; otherwise above it.
- **B.** A per-turn cost row after every answer, grouped by thread, with untracked spend.
- **C.** A `/telemetry` command that toggles a docked details pane.

**Not building or doing:**
- No changes to or removal of `plugins/telemetry`. It stays installed and running beside the mod; removing it is a later decision.
- No transcript parsing, no files under `~/.claude/telemetry-state`, no `statusLine` entry, no setup skill.
- No fast-mode pricing: the mod API doesn't expose `speed`. See Gotchas.
- No sharing or publishing of the mod.

## Conventions

- **Language:** TypeScript as the engine's types require (TS 5.4+). ES modules; JSX compiles against global `h` (`jsx: react`, `jsxFactory: h`). No DOM, no Node; everything external goes through `$`. *Taken from the API types header.*
- **Style:** 2-space indent, single quotes, no semicolons, camelCase, `async` hooks shaped `($, e, next)`. Match the throwaway mod and the API examples.
- **Files:** lowercase single-word module names in `hooks/` (`pricing.ts`, `ledger.ts`, `cache.ts`, `format.ts`, `band.tsx`, `pane.tsx`, `register.tsx`). State contract in `types/index.d.ts`.
- **Tests:** `plugins/telemetry-mod/tests/<module>.test.ts`, importing `test`, `expect` (and `mock` if needed) from `claude-code/testing`.
- **Commands:**
  - Test: `claude plugin test plugins/telemetry-mod`
  - Validate: `claude plugin validate plugins/telemetry-mod`
  - Type-check: `tsc -p plugins/telemetry-mod` (`/usr/local/bin/tsc`, version 7.0.2, verified installed)
  - If tsc 7 rejects the config or the engine's types (it's the new native compiler, and the types only promise TS 5.4+), use `npx -y -p typescript@5.6.3 tsc -p plugins/telemetry-mod` instead (verified working this session) and note which one was used.
- **Type files:** the engine writes `plugins/telemetry-mod/.claude-plugin/types/` the first time a session loads the mod. Type-checking needs that folder, so load the mod once first (U1). The folder is gitignored.
- **Repo rules are warnings in this plan.** The `CLAUDE.md` rules (stdlib Python scripts in `bin/` with no extension, unittest tests) were written before mods existed. Where they don't fit a mod, follow this plan and list the departure in the unit's review note. U9 rewrites the rules.
- **Comments are a deliverable (the user is new to mods and TypeScript).** Every file opens with a plain-English header saying:
  - what the file does;
  - where it sits in the flow;
  - which other files use it.

  Every hook gets a comment saying when Claude Code calls it and what the hook does with the data. The first use of each mod or TypeScript idea gets a one-line explanation where it's used: `next(e)`, async generator hooks (`function*` / `yield*`), `$.state` atoms, `Shaped<…>`, JSX trees, `as const`, union types. Comments explain *why* and *what*, never restate a line. `register.tsx` opens with a short "how to read this mod" map. Review checks this like code.

## Decisions

**Agreed (with the user, 2026-10-29)**
- **D1. New plugin beside the old one.** It's `plugins/telemetry-mod` with its own marketplace entry, and `plugins/telemetry` is untouched. *Affects U1, U8.*
- **D2. Built fresh, not ported.** Old code is not reference for the pricing formula or the rates: U2 validates both against Anthropic's and OpenAI's published pricing, and U5 checks the formula against Claude Code's own total. *Affects all units.*
- **D9. Web research goes through the Brave MCP tools first** (`mcp__brave-search__brave_web_search`, or `brave_llm_context` to read a page). If Brave fails or can't return a page, stop and tell the user before using WebFetch or WebSearch. *Affects U2.*
- **D10. A model switch triggers a full refresh**, not just the new name: model, effort, context, limits and git. *Affects U5.*
- **D11. Comments for a reader new to mods and TypeScript** (see Conventions). *Affects all code units.*
- **D12. Repo rules are warnings, rewritten at the end.** *Affects U1, U9.*
- **D3. Row format: grouped by thread.** `~$0.28 this turn · main $0.20 (Opus 5.5: 4 requests) · subagents $0.05 (Haiku 5.5: 2 agents, 4 requests; Terra: 1 agent, 3 requests) · untracked $0.03`. *Affects U4, U5.*
- **D4. B is the plain `turn.complete` row.** It can't have a border. The duration-line placement was tested and is unreliable: short turns have no line, and background agents turn it into a waiting line. A probe on every render component never saw the row. *Affects U5.*
- **D5. Include the `/telemetry` pane.** *Affects U7.*
- **D6. Band under the prompt if possible.** *Affects U6.*
- **D7. 7d (and every) countdown formatted like `1d12h13m`.** *Affects U4.*
- **D8. Better cache estimate.** *Affects U3.*

**Undecided (for the user)**
- **X1. Haiku 5.5 cache-read rate.** It isn't in the cached API reference. U2 looks it up with the rest of the rates (D9). If no published source gives it, stop and ask. *Affects U2.*
- **X2. Band placement.** The U6 spike shows the options on screen and the user picks. *Affects U6.*
- **X3. Plugin name.** `telemetry-mod` is assumed; renaming later is cheap. *Affects U1.*

**Assumed (my call, not confirmed)**
- **A1. Default cache lifetime 1 hour** until learned (U3). Cache writes are priced at the lifetime the estimator currently believes, for main and subagent requests alike. A wrong guess moves cost between main/sub and untracked; the turn total doesn't change. *Affects U2, U3.*
- **A2. Session figure.** Claude Code's own session total plus a running correction for re-priced non-Claude models. *Affects U2, U5.*
- **A3. Keep the last 200 turns** in state for the pane. *Affects U5, U7.*
- **A4. Refresh git, model and usage every 30 s**, and also right away after a model switch (D10) and after each turn. *Affects U5.*
- **A5. Spend between turns lands in the next turn.** Background subagents, titles and summaries spent between turns are counted in the next turn, as tested in the throwaway. *Affects U2, U5.*

## Cross-cutting gotchas

- **G1 (verified).** `$.state` atoms need literal references: `atom({ plugin: 'telemetry-mod', key: 'snap' } as const, …)`. A constant for the plugin name fails validation.
- **G2 (verified).** `classic.*` hooks gate the engine. Every one needs `.catch(($, e, next) => next(e))`, or a failure can block, for example, `/model`.
- **G3 (verified).** `turn.step` hooks must be async generators: `async function* ($, e, next) { const r = yield* next(e); …; return r }`. Keep the work after `yield*` short; it spends the hook's budget.
- **G4 (verified).** A hot reload resets module variables; `$.state` survives. Keep only the in-flight turn ledger in module variables, and document that a reload mid-turn drops that turn's split.
- **G5 (verified).** `ModelUsage` has only `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` (+ `model` on `TurnUsage`). There is no write-TTL split, no `speed` and no web-search count. Fast mode, the 1h/5m write mix and web-search fees therefore end up in **untracked**; the totals stay right.
- **G6 (verified).** Claude Code prices model ids it doesn't know (the clodex GPT models) at Sonnet rates. Hence the correction in A2.
- **G7 (unverified).** It isn't confirmed that `claude plugin test` can import plugin files such as `../hooks/pricing.ts`. U2 checks this first.
- **G8 (unverified).** Installed from the directory marketplace (`dev-toolkits` has source `directory`, path `/home/david/agent-tools/plugin-marketplace`, verified), the plugin should be read from the repo folder, so `/reload-plugins` picks up edits. U1 checks this.

## Reference: patterns proven in the throwaway

The throwaway is at `/home/david/.claude/dev-mods/b494e4d3-f092-4319-a6e5-921df7fbf4bf/telemetry-preview/hooks/register.tsx`, if still present. The essentials are pasted here as untested drafts of the pattern; write new code from them.

```tsx
// usage from each request (G3)
on('turn.step', async function* ($, e, next) {
  const response = yield* next(e)
  const usage = response.usage            // TurnUsage | null
  if (!usage) return response
  const model = usage.model || e.model
  // e.agentId === undefined -> main thread; else a subagent's id
  return response
})

// model switch (G2): to_model, cache_ttl ('5m' | '1h'), prompt_cache_warm
on('classic.PostModelSwitch', async ($, e, next) => { /* update state */ return next(e) })
  .catch(($, e, next) => next(e))

// the per-turn row: text returned from turn.complete is drawn under the answer
on('turn.complete', async ($, e, next) => {
  const answer = await next(e)
  if (e.agentId !== undefined) return answer
  return { ...answer, text: '…row…' }
})

// session figures pushed after each main turn
on('session.measure', async ($, e, next) => { /* e.context, e.rateLimits, e.cost?.usd */ return next(e) })

// band above the prompt (known-good fallback for U6)
on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
  if (e.props.hasSurvey) return next(e)
  const { Box, Text } = $.ui.resolve(e)
  return <Box flexDirection="column" borderStyle="round" borderColor="subtle" paddingX={1}>…</Box>
})
```

Test-kit shape, from the API's example test (paste-safe; the original lives in a per-process temp folder):

```tsx
import { expect, test } from 'claude-code/testing'

test('the band shows the model', async ($, on) => {
  // Nothing sits beneath the plugin: hooks registered here stand for the engine.
  on('state.get', () => ({ value: { value: { /* a Snapshot */ }, version: 1 } }))
  const ui = await $.ui.mount({ plugin: 'telemetry-mod', component: 'AbovePrompt', surface: 'terminal',
    props: { hasSurvey: false, isWorking: false, /* + the remaining AbovePrompt props the types require */ } })
  expect((await ui.find({ type: 'Text', text: /Opus 5.5/ }))?.text).toContain('Opus 5.5')
  await ui.unmount()
})
```

## Dependencies

- U1 comes first.
- U2, U3 and U4 depend only on U1 and can run in any order.
- U5 needs U2–U4.
- U6 needs U5.
- U7 needs U5 and U4.
- U8 needs U5–U7.
- U9 comes last.

Stop for the user's review after each unit.

## Stop-and-ask triggers (all units)

- A spec ambiguity, or a needed file outside the unit's **Files** list.
- A failing test that tempts changing the assertion rather than the code.
- `claude plugin validate` reports an error you can't fix within the unit's contract.
- Any API name in this plan doesn't exist in `.claude-plugin/types/claude-code/index.d.ts` (grep for it before using it).
- Anything that would edit `plugins/telemetry/`, `~/.claude/settings.json`, or push or commit.
- Anything that would edit `CLAUDE.md` before U9.

Default: stop and ask; never work around.

---

## U1: Scaffold the plugin and the repo rules

**Deliverables:** an empty-but-loadable mod, its marketplace entry, and `.gitignore`. `CLAUDE.md` is not changed here (D12; see U9).

**Files**
- **Create:**
  - `plugins/telemetry-mod/.claude-plugin/plugin.json`
  - `plugins/telemetry-mod/hooks/hooks.json`
  - `plugins/telemetry-mod/hooks/register.tsx`
  - `plugins/telemetry-mod/types/index.d.ts`
  - `plugins/telemetry-mod/tsconfig.json`
  - `.gitignore`
- **Modify:** `.claude-plugin/marketplace.json`
- **Must not touch:** `plugins/telemetry/**`, `CLAUDE.md`

**Content**

`plugin.json`:
```json
{
  "name": "telemetry-mod",
  "version": "0.1.0",
  "description": "Cost and session telemetry as a Claude Code mod: a status band, a per-turn cost row, and a /telemetry details pane.",
  "author": { "name": "David Engel", "email": "drengel88@gmail.com" },
  "types": "./types/index.d.ts"
}
```

`hooks/hooks.json`: `{ "modules": ["./register.tsx"] }`

`hooks/register.tsx` (stub, replaced in U5):
```tsx
// Entry point of the telemetry-mod plugin. Claude Code loads this file
// (hooks/hooks.json names it) and calls `register` once, handing it `on`,
// which adds hooks. This stub adds none yet; U5 fills it in.
import type { Register } from 'claude-code'

export const register: Register = () => {}
```

`types/index.d.ts` (stub, filled in U5):
```ts
declare module 'claude-code' {
  interface PluginState {
    'telemetry-mod': {}
  }
}
export {}
```

`tsconfig.json`, from the API types header:
```json
{
  "compilerOptions": {
    "target": "es2023", "lib": ["es2023"], "types": [],
    "module": "esnext", "moduleResolution": "bundler",
    "strict": true, "noUncheckedIndexedAccess": true,
    "noEmit": true, "skipLibCheck": true,
    "jsx": "react", "jsxFactory": "h", "jsxFragmentFactory": "Fragment"
  },
  "include": [".claude-plugin/types", "hooks", "types", "tests"]
}
```

`.gitignore` (the repo has none; verified):
```
# Written by Claude Code when it loads a mod
plugins/*/.claude-plugin/types/
```

`marketplace.json`: append to `plugins`, after `sdd`:
```json
{
  "name": "telemetry-mod",
  "source": "./plugins/telemetry-mod",
  "description": "Cost and session telemetry as a Claude Code mod: an always-on status band (model, effort, git, context, cost, rate limits, cache), a per-turn cost row split by main thread, subagents and untracked spend, and a /telemetry details pane.",
  "category": "productivity",
  "tags": ["cost", "mod", "tokens", "pricing", "rate-limits"]
}
```

**Gotchas**
- **G8:** after adding the marketplace entry, the user runs `/plugin install telemetry-mod@dev-toolkits` and `/reload-plugins`. That's an outward action: ask the user to run it, don't run it yourself. Then check that `plugins/telemetry-mod/.claude-plugin/types/claude-code/index.d.ts` exists. If it doesn't (Claude Code loaded a cached copy instead of the folder), stop and ask.
- If loading creates other files in the plugin folder (e.g. a generated `tsconfig.json` beside ours, or other type folders), stop and ask before ignoring or committing them.

**Done when**
- ✔ `claude plugin validate plugins/telemetry-mod` prints no `✘ Found … error` in the manifest or hooks sections. The directory-submission README/LICENSE problems are expected until U8.
- ✔ `python3 -c "import json; print([p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']])"` prints a list ending in `'telemetry-mod'`.
- ✔ After the user's install and reload, `test -f plugins/telemetry-mod/.claude-plugin/types/claude-code/index.d.ts && echo ok` prints `ok`.
- ✔ The type-check command exits 0.
- ✔ `git status --short` shows no files under `.claude-plugin/types/`.

---

## U2: Pricing and the per-turn ledger (pure)

**Deliverables:** `hooks/pricing.ts`, `hooks/ledger.ts`, and their tests.

**Files**
- **Create:**
  - `plugins/telemetry-mod/hooks/pricing.ts`
  - `plugins/telemetry-mod/hooks/ledger.ts`
  - `plugins/telemetry-mod/tests/pricing.test.ts`
  - `plugins/telemetry-mod/tests/ledger.test.ts`
- **Must not touch:** `plugins/telemetry/**`

**Step 1, test import (G7):** write `tests/pricing.test.ts` with one trivial test that imports `../hooks/pricing.ts` and run `claude plugin test plugins/telemetry-mod`. If the import isn't supported, stop and ask.

**Step 2, validate rates and formula before coding them (D2, D9).** The `RATES` table below is a *starting point to check*, not a source.

Using the Brave MCP tools (`brave_web_search` to find, `brave_llm_context` to read), find the official pricing pages:
- Anthropic: the API pricing page on `platform.claude.com` or `docs.claude.com`;
- OpenAI: the API pricing page for GPT-5.6 Luna/Terra/Sol and GPT-6 Astra.

For every row of the `RATES` table, check input, cache read and output, plus any long-prompt tier with its threshold and multipliers. Also check these formula facts:
1. A 5-minute cache write costs 1.25× input, and a 1-hour write 2× input.
2. Cache reads have their own per-model rate (not always 0.1× input).
3. Haiku 5.5's >100K-prompt rates ($0.50/$2.50): whether they apply to the whole request, and how its cache-read rate scales above 100K.
4. The GPT >272K tier (input ×2, output ×1.5): whether it applies to the whole request, and whether cached input is scaled too.
5. Which Claude model id Claude Code prices unknown models at. Old notes say Sonnet; check Claude Code docs or changelog. If nothing is published, keep `claude-sonnet-5` and mark it unverified.

Record the results in the review note as a table (fact → value → source URL → date read). Write the source URLs and the date into the header comment of `pricing.ts`.
- Where a published value differs from the table, use the published one and say so in the review note.
- Where Brave can't find or read a page, stop and tell the user before using any other web tool.
- If a value can't be found at all (X1 is the likely case), stop and ask.

**Contract: `pricing.ts`**
```ts
export type Rates = {
  input: number; cacheRead: number; output: number    // USD per 1M tokens
  tier?: { aboveInputTokens: number; multiplier: { input: number; output: number } }
}
export const RATES: Readonly<Record<string, Rates>>    // keyed by model id exactly as usage.model reports it
export const FALLBACK_MODEL = 'claude-sonnet-5'        // rates Claude Code applies to ids it doesn't know (G6)
export const CACHE_WRITE_MULTIPLIER = { '5m': 1.25, '1h': 2 } as const
export type WriteTtl = keyof typeof CACHE_WRITE_MULTIPLIER

// Our price for one request; undefined when the model has no rates.
export function priceUsage(model: string, usage: ModelUsage, ttl: WriteTtl): number | undefined
// What Claude Code's own total charged for the same request: our price for
// claude-* ids we know, the fallback model's price for non-claude ids, and
// undefined for an unknown claude-* id (Claude Code's charge then shows as untracked).
export function chargedByClaudeCode(model: string, usage: ModelUsage, ttl: WriteTtl): number | undefined
```

**Pricing rule (exact):**
- `promptTokens = input + cacheRead + cacheCreation`.
- If `rates.tier` and `promptTokens > tier.aboveInputTokens`:
  - multiply the input rate and the cache-read rate by `tier.multiplier.input`;
  - multiply the output rate by `tier.multiplier.output`.
- `usd = (input·in + cacheRead·read + cacheCreation·in·CACHE_WRITE_MULTIPLIER[ttl] + output·out) / 1e6`.

**Content: `RATES`** (USD/MTok). These are starting values, each one checked in Step 2:

| Id | input | cacheRead | output | tier | Source |
|---|---|---|---|---|---|
| `claude-opus-5-5` | 4.00 | 0.20 | 20.00 | — | claude-api skill, cached 2026-10-06 |
| `claude-opus-5` | 5.00 | 0.50 | 25.00 | — | pricing.json |
| `claude-sonnet-5-5` | 2.00 | 0.20 | 10.00 | — | claude-api skill |
| `claude-sonnet-5` | 2.00 | 0.20 | 10.00 | — | pricing.json |
| `claude-haiku-5-5` | 0.10 | **X1** | 0.50 | above 100000: input ×5, output ×5 | claude-api skill ($0.50/$2.50 beyond 100K) |
| `claude-haiku-4-5` | 1.00 | 0.10 | 5.00 | — | pricing.json |
| `claude-haiku-4-5-20251001` | 1.00 | 0.10 | 5.00 | — | pricing.json |
| `claude-fable-5-1` | 10.00 | 0.25 | 50.00 | — | claude-api skill |
| `luna` | 0.10 | 0.01 | 0.50 | above 272000: input ×2, output ×1.5 | pricing.json |
| `terra` | 2.00 | 0.20 | 12.00 | above 272000: input ×2, output ×1.5 | pricing.json |
| `sol` | 2.00 | 0.20 | 10.00 | above 272000: input ×2, output ×1.5 | pricing.json |
| `astra` | 10.00 | 1.00 | 50.00 | above 272000: input ×2, output ×1.5 | pricing.json |

Put a header comment above `RATES` naming the two sources and their dates. This file becomes the mod's single source for prices; `plugins/telemetry/pricing.json` stays the old plugin's.

**Contract: `ledger.ts`**
```ts
export type Request = { model: string; agentId?: string; usage: ModelUsage }
export type Group = { usd: number; models: Record<string, { usd: number; requests: number; agents: string[] }> }
export type TurnCost = {
  total: number                  // main.usd + sub.usd + (untracked ?? 0)
  main: Group
  sub: Group
  untracked?: number             // undefined when Claude Code's total was unavailable
  correction: number             // sum of (our price - Claude Code's charge) for priced non-claude requests
  unpriced: string[]             // model ids with no rates, sorted, unique
}
export class Ledger {
  add(request: Request, ttl: WriteTtl): void
  close(claudeCodeDelta: number | undefined): TurnCost  // returns the turn and starts a fresh one
  isEmpty(): boolean
}
```

**Rules:**
- **`add`:**
  - Main when `agentId === undefined`, otherwise sub.
  - Priced: add `priceUsage` to the group's and the model's `usd`.
  - Every request: `requests += 1`.
  - For sub requests, add the `agentId` to `agents` if absent.
  - Unpriced: record the model in `unpriced`; the request still counts in `requests`.
- **`close`:**
  - `tracked = Σ chargedByClaudeCode over requests where it is defined`.
  - If the delta is defined, `untracked = delta − tracked`.
  - `correction = Σ (priceUsage − chargedByClaudeCode)`, over requests whose model doesn't start with `claude-` and has rates.
  - Then reset.

**Test cases**

| Input | Expected |
|---|---|
| `priceUsage('claude-opus-5-5', {input:1e6, output:0, read:0, creation:0}, '5m')` | `4` |
| same, `{read:1e6}` | `0.2` |
| same, `{creation:1e6}`, `'5m'` / `'1h'` | `5` / `8` |
| same, `{output:1e6}` | `20` |
| `priceUsage('terra', {input:300000, output:1e6}, '5m')` | `0.3·2·2 + 12·1.5 = 19.2` (tier applies: 300000 > 272000) |
| `priceUsage('terra', {input:272000}, '5m')` | `0.544` (tier doesn't apply at equality) |
| `priceUsage('claude-unknown-9', …)` | `undefined` |
| `chargedByClaudeCode('terra', {input:1e6}, '5m')` | `2` (Sonnet 5 input rate) |
| `chargedByClaudeCode('claude-unknown-9', …)` | `undefined` |
| Ledger: 4 main opus requests, 2 sub haiku from agent `a1`, 1 sub terra from `b2`; `close(delta)` where delta = tracked + 0.03 | `untracked ≈ 0.03`; `sub.models['claude-haiku-5-5'].agents = ['a1']`; terra `requests = 1`, `agents = ['b2']`; `total = main.usd + sub.usd + 0.03` |
| Ledger: `close(undefined)` | `untracked === undefined`, `total = main.usd + sub.usd` |
| Ledger: one unpriced claude request + `close(0.10)` | `unpriced = ['claude-unknown-9']`; `untracked = 0.10`; `requests` counted |
| Ledger: second `close` right after the first | an empty TurnCost (`total 0`, no models) |

Compare floats with `toBeCloseTo` (or the kit's equivalent; check the testing types).

**Done when**
- ✔ The review note's validation table covers every `RATES` row and formula facts 1–5, each with a source URL and the date read, or is marked unverified with the reason.
- ✔ `claude plugin test plugins/telemetry-mod` reports every case above passing (the runner's own summary line shows the count, 0 failed). It fails if a rate or rule is mis-typed: each table row is its own assertion. If Step 2 changed a rate, update the expected values in the test table to match and say so in the review note.

---

## U3: Cache estimator (pure)

**Deliverables:** `hooks/cache.ts` + `tests/cache.test.ts`. A better estimate than the throwaway (D8): per-model, the lifetime learned from evidence, and resume-aware.

**Files:** **Create** `plugins/telemetry-mod/hooks/cache.ts`, `plugins/telemetry-mod/tests/cache.test.ts`.

**Contract**
```ts
export type CacheState = {
  model?: string                          // session model the estimate is for
  ttlMs: number                           // 3_600_000 or 300_000
  ttlSource: 'assumed' | 'learned' | 'switch'
  lastAt?: number                         // ms epoch of the last main-thread request that read or wrote the cache
  hitRatio?: number                       // that request's cacheRead / promptTokens, 0..1
}
export const INITIAL: CacheState          // { ttlMs: 3_600_000, ttlSource: 'assumed' } (A1)
export function observe(s: CacheState, model: string, usage: ModelUsage, at: number): CacheState
export function switched(s: CacheState, toModel: string, ttl: '5m' | '1h'): CacheState
export function resumed(s: CacheState, secondsSinceLastResponse: number | undefined, likelyExpired: boolean | undefined, now: number): CacheState
export function view(s: CacheState, now: number): { kind: 'none' } | { kind: 'cold' } | { kind: 'warm'; hitRatio?: number; leftMs: number; estimated: boolean }
export function writeTtl(s: CacheState): '5m' | '1h'
```

**Rules (exact)**
- **`observe`**
  - Skip a request with no cache activity: if `cacheRead + cacheCreation === 0`, return `s` unchanged.
  - **New model:** if `s.model` is set and differs from `model`, start from `{ ...INITIAL, ttlMs: s.ttlMs, ttlSource: s.ttlSource === 'switch' ? 'switch' : s.ttlSource, model }`. This keeps the lifetime knowledge but drops `lastAt` and `hitRatio`.
  - **Learning,** when `gap = at − lastAt` is defined and `ttlSource !== 'switch'`:
    - `gap > 300_000` and `cacheRead > 0` → `ttlMs = 3_600_000`, `ttlSource = 'learned'`;
    - `300_000 < gap < 3_600_000`, `cacheRead === 0` and `cacheCreation > 0`, and `ttlSource === 'assumed'` → `ttlMs = 300_000`, `ttlSource = 'learned'`.
  - Then set `lastAt = at`, `hitRatio = cacheRead / promptTokens`, `model = model`.
- **`switched`:** `{ model: toModel, ttlMs: ttl === '5m' ? 300_000 : 3_600_000, ttlSource: 'switch' }`. No `lastAt`: the new model's cache is cold.
- **`resumed`:**
  - `likelyExpired === true` → drop `lastAt` (cold).
  - Otherwise, if `secondsSinceLastResponse` is defined, set `lastAt = now − seconds·1000`.
  - Otherwise unchanged.
- **`view`:**
  - No `lastAt` and no `hitRatio` → `none`.
  - `lastAt + ttlMs ≤ now` or no `lastAt` → `cold`.
  - Otherwise `warm`, with `leftMs = lastAt + ttlMs − now` and `estimated = ttlSource === 'assumed'`.

**Test cases**

| Steps | Expected `view` / state |
|---|---|
| `INITIAL` | `none` |
| observe opus `{read:900, creation:100, input:0}` at t0 | warm, hitRatio 0.9, leftMs 3_600_000 at t0, `estimated: true` |
| …then view at t0 + 3_600_000 | `cold` |
| observe at t0, then again at t0 + 600_000 with `read > 0` | `ttlSource: 'learned'`, ttlMs 3_600_000 |
| observe at t0, then at t0 + 600_000 with `read = 0, creation > 0` | `ttlSource: 'learned'`, ttlMs 300_000 |
| `switched(s, 'claude-haiku-5-5', '5m')`, then observe at t0 + 600_000 with `read = 0` | stays `ttlSource: 'switch'`, 300_000 |
| observe with `read = 0, creation = 0` | state unchanged |
| observe opus at t0, then observe terra (`read 0, creation 50`) at t0+1 | model `terra`, hitRatio 0, `lastAt = t0+1`; no learning (no gap for the new model) |
| `resumed(s, 120, false, now)` | `lastAt = now − 120_000` |
| `resumed(s, 5000, true, now)` | view `cold` |
| `writeTtl` with ttlMs 300_000 / 3_600_000 | `'5m'` / `'1h'` |

**Done when:** ✔ `claude plugin test plugins/telemetry-mod` reports all cache cases passing.

---

## U4: Formatting (pure)

**Deliverables:** `hooks/format.ts` + `tests/format.test.ts`.

**Files:** **Create** `plugins/telemetry-mod/hooks/format.ts`, `plugins/telemetry-mod/tests/format.test.ts`.

**Contract**
```ts
export function modelName(id: string): string          // display name
export function usd(x: number): string                 // money
export function countdown(ms: number): string          // D7
export function row(turn: TurnCost): string            // D3
export function percentColor(p: number): 'success' | 'warning' | 'error'
```

**Rules**
- **`modelName`:**
  - Strip a leading `claude-` and a trailing `-YYYYMMDD` (8 digits).
  - Split the rest on `-`. The first part, capitalised, is the family; the remaining parts joined with `.` are the version.
  - Examples: `claude-opus-5-5` → `Opus 5.5`; `claude-haiku-4-5-20251001` → `Haiku 4.5`; `terra` → `Terra`.
- **`usd`:** `|x| < 0.01` → `$` + 4 decimals, otherwise 2 decimals; negative values get a leading `-` before `$`. Examples: `0.28` → `$0.28`, `0.004` → `$0.0040`, `-0.03` → `-$0.03`.
- **`countdown`:**
  - `ms < 60_000` → `<1m`.
  - Otherwise split into d/h/m (floor):
    - with days → `${d}d${hh}h${mm}m`, hours and minutes 2-digit;
    - else with hours → `${h}h${mm}m`;
    - else `${m}m`.
- **`row`:**
  - Parts joined with ` · `, in this order:
    1. `~${usd(total)} this turn`
    2. `main ${usd(main.usd)} (${entries})`, if main has models
    3. `subagents ${usd(sub.usd)} (${entries})`, if sub has models
    4. `untracked ${usd(untracked)}`, if defined and `|untracked| ≥ 0.005`
    5. `unpriced: ${names}`, if any
  - Entries are joined with `; ` and sorted by `usd` descending, then by name.
  - A main entry is `${modelName}: ${n} request(s)`; a sub entry is `${modelName}: ${a} agent(s), ${n} request(s)`, singular for 1.
  - Unpriced names are `modelName`s joined with `, `.
- **`percentColor`:** `< 50` success, `< 80` warning, else error.

**Test cases**

| Input | Expected |
|---|---|
| `countdown(30_000)` | `<1m` |
| `countdown(23·60_000)` | `23m` |
| `countdown((60+5)·60_000)` | `1h05m` |
| `countdown(((24+12)·60+13)·60_000)` | `1d12h13m` |
| `countdown(((2·24+3)·60+4)·60_000)` | `2d03h04m` |
| `countdown(86_400_000)` | `1d00h00m` |
| `countdown(-5)` | `<1m` |
| `modelName` cases above | as listed |
| `usd` cases above | as listed |
| `row` for the D3 turn (main opus 0.20/4 requests; sub haiku 0.02/2 agents/4 requests, terra 0.03/1 agent/3 requests; untracked 0.03; total 0.28) | `~$0.28 this turn · main $0.20 (Opus 5.5: 4 requests) · subagents $0.05 (Terra: 1 agent, 3 requests; Haiku 5.5: 2 agents, 4 requests) · untracked $0.03` (sorted by usd: Terra 0.03 before Haiku 0.02) |
| `row`: main only, one request, untracked 0.001 | `~$0.05 this turn · main $0.05 (Opus 5.5: 1 request)` (untracked hidden) |
| `row`: untracked undefined, unpriced `['claude-x-1']` | ends with ` · unpriced: X 1` |
| `percentColor(49.9 / 50 / 80)` | success / warning / error |

**Done when:** ✔ `claude plugin test plugins/telemetry-mod` reports all format cases passing.

---

## U5: Wiring, state and the per-turn row

**Deliverables:** the real `register.tsx` hooks and the state contract. After this unit the per-turn row shows in a live session; the band is still the U6 work.

**Files**
- **Modify:** `plugins/telemetry-mod/hooks/register.tsx`, `plugins/telemetry-mod/types/index.d.ts`
- **Create:** `plugins/telemetry-mod/tests/register.test.tsx`

**Contract: state (`types/index.d.ts`)**
```ts
import type { CacheState } from '../hooks/cache'
import type { TurnCost } from '../hooks/ledger'
export type Limit = { kind: string; percent: number; resetsAt?: string }
export type Snapshot = {
  model: string; effort?: string; git?: string; gitDirty: boolean
  ctxPercent?: number; ctxTokens?: number
  ccTotal?: number                 // Claude Code's session total (session.usage / session.measure)
  correction: number               // sum of TurnCost.correction this session (A2)
  lastTurn?: number                // last TurnCost.total
  limits: Limit[]
  cache: CacheState
  startedAt?: number
}
export type Turn = TurnCost & { index: number; doneAt: number }
declare module 'claude-code' {
  interface PluginState {
    'telemetry-mod': { snap: Shaped<Snapshot>; turns: Shaped<Turn[]> }
  }
}
```
If a contract file can't import from `../hooks/*`, inline the types in the contract and have `hooks/*` import them from `../types` instead. Stop and ask if neither works.

**Hooks (exact behaviour)**
- **`session.start`:**
  - Cancel any previous timer; start `$.clock.every(30_000, refresh)` (A4).
  - `baseline = (await $.session.usage()).cost?.usd`.
  - `$.command.register({ name: 'telemetry', description: 'Toggle the telemetry details pane' })`. The handler is U7; register it now only if U7's hook exists, otherwise in U7.
  - Call `refresh` once, then `next(e)`.
  - `refresh` sets: `model = modelName($.session.model())`; git branch (fallback short sha) and dirty flag via `$.process.run(['git', …], { timeoutMs: 2000 })`; `ctxPercent`, `ctxTokens`, `limits`, `ccTotal` from `$.session.usage()`; `startedAt = usage.startedAt`.
  - Any failure is swallowed.
- **`classic.SessionStart`:** if `e.source` is `resume` or `fork`, `cache = resumed(cache, e.seconds_since_last_response, e.prompt_cache_likely_expired, now)`. `.catch(($, e, next) => next(e))` per G2.
- **`classic.PostModelSwitch`:**
  - Set `model = modelName(e.to_model)` and `cache = switched(cache, e.to_model, e.cache_ttl)` at once, so the band changes on the next redraw.
  - Then start `refresh` without awaiting it (D10), so effort, context and limits follow too.
  - `.catch` per G2.
- **`turn.step`** (G3):
  - After `yield*`, if `usage`: `ledger.add({ model, agentId: e.agentId, usage }, writeTtl(cache))`.
  - If main: `effort = String(e.effort)` when defined, and `cache = observe(cache, model, usage, now)`.
- **`turn.complete`:**
  - If `e.agentId !== undefined`, return `next(e)`.
  - Otherwise `answer = await next(e)`; `cc = (await $.session.usage()).cost?.usd`; `delta = cc !== undefined && baseline !== undefined ? cc − baseline : undefined`; `baseline = cc ?? baseline`; `turn = ledger.close(delta)`.
  - Append `{ ...turn, index: previous index + 1 (1 if none), doneAt: now }` to `turns`, keeping the last 200 (A3).
  - Update `snap`: `lastTurn = turn.total`, `correction += turn.correction`, `ccTotal = cc ?? ccTotal`.
  - Return `{ ...answer, text: row(turn) }`.
- **`session.measure`:** update `ctxPercent`, `ctxTokens`, `limits`, and `ccTotal` (when `e.cost`).
- **Session spend** (for U6/U7): `(ccTotal ?? 0) + correction`. Export a helper `sessionUsd(snap)` from `register.tsx` or a small `hooks/session.ts`.

**Gotchas**
- **G1, G2, G3, G4.**
- `turn.complete` fires for subagent turns too: never close the ledger there.
- `baseline` is a module variable: after a reload, `session.start` re-reads it, so a reload costs at most one turn's split (A5).
- **Before using them:** grep `$.command.register`, `classic.SessionStart` field names (`source`, `seconds_since_last_response`, `prompt_cache_likely_expired`) and `usage.startedAt` in the laid types. They were present in build 2.1.312.

**Test cases** (`register.test.tsx`; only what the kit can drive: check the testing types for raising `turn.step` / `turn.complete`; if it can't, test via the real session below)

| Input | Expected |
|---|---|
| Seeded `turns` from an older shape (`state.get` returns `{ value: [{ foo: 1 }], version: 1 }`) | the mod reads `turns` as `[]` (`shape` tag declined), and doesn't throw |
| If the kit can raise events: a main `turn.step` with opus usage, then `turn.complete` with `session.usage` answering cost +0.10 | returned `text` starts with `~$0.10 this turn · main` |

**Done when**
- ✔ `claude plugin test` passes.
- ✔ `claude plugin validate plugins/telemetry-mod` lists hooks `session.start, classic.SessionStart, classic.PostModelSwitch, turn.step, turn.complete, session.measure` and `gating hook with .catch` for both classic hooks.
- ✔ Type-check exits 0.
- ✔ **Real session**, after the user runs `/reload-plugins`:
  - a plain turn shows a row `~$… this turn · main $… (Opus 5.5: N requests)`;
  - a turn with one haiku subagent that finishes inside the turn adds `subagents $… (Haiku 5.5: 1 agent, N requests)`;
  - the row's total is within $0.01 of the old telemetry's `This request cost` line for the same turn.
  
  The user confirms by screenshot. The check fails if the row is missing, the split is absent, or the totals differ by more than $0.01.
- ✔ **Formula check against Claude Code's own total (D2).**
  - Run 3 plain Opus turns with no tools and no subagents.
  - Each one's row should show no `untracked` part: |untracked| < $0.005, so the row hides it.
  - If a turn shows untracked ≥ $0.005 consistently, the per-request price disagrees with what Claude Code charges. Likely causes: the cache-write lifetime (A1), or a wrong rate. Report the three rows and stop and ask; don't tune numbers to make it vanish.

---

## U6: The band, and the under-the-prompt spike

**Deliverables:** `hooks/band.tsx`, which renders A, and a spike that shows the placement options to the user, who picks one (X2). This unit is larger than the others because it includes a user checkpoint mid-way.

**Files**
- **Create:** `plugins/telemetry-mod/hooks/band.tsx`, `plugins/telemetry-mod/tests/band.test.tsx`
- **Modify:** `plugins/telemetry-mod/hooks/register.tsx`

**Content: the band** (both lines, segments joined by a dim ` · `):
- **Line 1:**
  - **bold** model;
  - effort, if known;
  - git branch, plus a `warning`-coloured `*` when dirty.
- **Line 2:**
  - `ctx ` + percent coloured by `percentColor` + ` (NK)`, where `NK` is `round(ctxTokens/1000)`;
  - `warning`-coloured `${usd(lastTurn ?? 0)} / ${usd(sessionUsd)}`;
  - for each limit, `5h`/`7d`/`kind`, then the coloured percent, then ` ↻${countdown(resetsAt − now)}`;
  - the cache segment from `view(cache, now)`: `none` → omitted; `cold` → dim `cache cold`; `warm` → `cache ${round(hitRatio·100)}% ${countdown(leftMs)} left`, plus a dim ` (est.)` when `estimated`.
- Return `next(e)` when there's nothing to show yet (`model === ''`) or, for `AbovePrompt`, when `e.props.hasSurvey`.
- Draw nothing when `isDraft` if the user asks for that at the checkpoint; default: always draw.

**Spike (X2):** implement `PLACEMENT` as a constant in `band.tsx`, with three values:
1. `'hint'`: a `ui.render { component: 'PromptHint' }` hook returning a column: the engine's hint text as dim `Text` (`e.props.hint`), then the bordered band. The hint line's live pills become plain text in this mode; say so at the checkpoint.
2. `'status'`: `$.ui.status(text)` with the two lines joined by `\n`, no colours, no border. Call it from `refresh`, `turn.complete` and `session.measure`, not from a render hook.
3. `'above'`: `ui.render { component: 'AbovePrompt' }`, bordered: the known-good fallback.

Load each one in turn (edit the constant, then the user runs `/reload-plugins`). Ask the user for one screenshot per placement and record which the user picks. Then delete the unused code paths and keep only the chosen placement; don't ship a setting.

**Test cases** (`band.test.tsx`, via `$.ui.mount` on the chosen component, state seeded with `on('state.get', …)` as in the Reference section)

| Seeded snapshot | Expected text found |
|---|---|
| model `Opus 5.5`, effort `high`, git `main`, dirty | a Text containing `Opus 5.5`; a Text `*` |
| ctxPercent 64, ctxTokens 128_400 | `ctx`, `64%`, `(128K)` |
| limits `[{kind:'seven_day', percent:18, resetsAt: now+((24+12)·60+13)·60_000}]` | `7d`, `18%`, `↻1d12h13m` |
| cache warm, assumed, hit 0.91, 23 min left | `cache 91% 23m left`, `(est.)` |
| `model === ''` | the hook passes (the engine's own element, per the example's third test) |

**Done when**
- ✔ The user has picked a placement (record it in the unit's review note).
- ✔ `claude plugin test` passes.
- ✔ Type-check exits 0.
- ✔ **Real session:**
  - the band shows in the chosen place with all segments;
  - `/model sonnet` changes the model name within one redraw (no 30 s wait), and the cache segment shows `cache cold` until the next reply;
  - the 7d countdown reads like `1d12h13m`.
  
  The user confirms by screenshot.

---

## U7: `/telemetry` pane

**Deliverables:** `hooks/pane.tsx`; the `/telemetry` command toggles a docked pane.

**Files**
- **Create:** `plugins/telemetry-mod/hooks/pane.tsx`, `plugins/telemetry-mod/tests/pane.test.tsx`
- **Modify:** `plugins/telemetry-mod/hooks/register.tsx`

**Behaviour**
- **`command.run { command: 'telemetry' }`:**
  - If `$.ui.panes()` lists id `telemetry`, `$.ui.close({ id: 'telemetry' })` and answer `{ text: 'Telemetry pane closed.' }`.
  - Otherwise `$.ui.open({ id: 'telemetry', title: 'Telemetry' })` and answer `{ text: 'Telemetry pane opened.' }`.
  - Don't pass `focus`: the prompt keeps the keyboard.
- **`ui.render { component: 'Pane', requestId: 'telemetry' }`:** a column sized to `e.props.bodyColumns`, with these sections:
  1. `Session ${usd(sessionUsd)} · ${turns.length} turns · ${countdown(now − startedAt)}`; omit the duration if `startedAt` is unknown.
  2. A table of the last `max(1, bodyRows − 14)` turns: `Turn  Main  Sub  Untr.  Total`, with numbers via `usd` without `$`, and `—` for 0 or undefined.
  3. **By model:** session sums per `modelName` over `turns` (main + sub `usd`), sorted descending, each with a bar of `█` sized `round(share · 20)`.
  4. **Context:** `ctx P% · NK / windowK` (window from `$.session.usage().context.window`).
  5. **Rate limits:** one row per limit, with a bar (`█` of 16 per percent) and `↻ countdown`.
  6. **Prompt cache:** the same words as the band's cache segment.

  End with a dim footer: `× or /telemetry closes`.

**Gotchas:**
- Before using `$.ui.panes`, `$.ui.close` and `command.run`, check their names and shapes in the laid types (present in 2.1.312).
- A render hook must not write state.

**Test cases** (`pane.test.tsx`, mounting `Pane` with `requestId: 'telemetry'` and seeded `turns`/`snap`)

| Seed | Expected |
|---|---|
| 3 turns totalling 0.45, 1.74 and 1.02 | a Text containing `$3.21` (if ccTotal + correction = 3.21) and three table rows |
| turns with opus 2.71, terra 0.29, haiku 0.21 | By-model order Opus 5.5, Terra, Haiku 5.5 |
| no turns | `Session $0.00 · 0 turns` and no table rows |

**Done when**
- ✔ `claude plugin test` passes.
- ✔ Type-check exits 0.
- ✔ **Real session:** `/telemetry` opens the pane docked beside the chat (fullscreen layout) while typing in the prompt still works; a second `/telemetry` closes it. The user confirms by screenshot.

---

## U8: README, final validation, comparison with the old telemetry

**Deliverables:** `plugins/telemetry-mod/README.md`; all checks green; a short comparison note in the review message.

**Files:** **Create** `plugins/telemetry-mod/README.md`. **Must not touch:** `plugins/telemetry/**`.

**Content: README.md** (fill in the `⟨…⟩` slots from U6's choice):
```markdown
# telemetry-mod

Cost and session telemetry for Claude Code, built as a mod (in-process hooks). Replaces what the `telemetry` plugin does with a status line and transcript parsing.

## What it shows

- **Status band** ⟨under / above⟩ the prompt, always on:
  `Opus 5.5 · high · main*`
  `ctx 64% (128K) · $0.28 / $3.21 · 5h 42% ↻1h12m · 7d 18% ↻1d12h13m · cache 91% 23m left`
- **A cost row after every turn:**
  `~$0.28 this turn · main $0.20 (Opus 5.5: 4 requests) · subagents $0.05 (Terra: 1 agent, 3 requests; Haiku 5.5: 2 agents, 4 requests) · untracked $0.03`
- **`/telemetry`** toggles a pane beside the chat: per-turn table, cost by model, context, rate limits, cache.

## How costs are worked out

- Each model request's token usage comes from Claude Code (`turn.step`), main thread and subagents alike, and is priced from `hooks/pricing.ts`.
- **untracked** is Claude Code's own cost total for the turn minus what Claude Code charged for the requests above: calls that never pass through a turn (web search helpers, compaction, titles), plus anything the mod can't price exactly (fast mode, the 1h/5m cache-write mix).
- Claude Code prices models it doesn't know (the clodex GPT models) at Sonnet rates; the mod re-prices them from `pricing.ts`, and the session total includes that correction.
- Spend between turns (a background subagent finishing late, titles) is counted in the next turn's row.

## Cache estimate

The cache lifetime is learned: a cache hit after more than 5 minutes means 1 hour; a model switch reports it directly. Until then it assumes 1 hour and marks the countdown `(est.)`. Switching model shows `cache cold`; resuming a session uses Claude Code's own "likely expired" flag.

## Install

`/plugin install telemetry-mod@dev-toolkits`, then `/reload-plugins`. No setup step and no settings changes.

## How the code fits together

A mod is TypeScript that Claude Code runs inside itself. `hooks/hooks.json` names the entry file; Claude Code calls its `register` function, which subscribes to events with `on(event, hook)`. Each hook receives `$` (everything the mod can ask Claude Code for) and `e` (the event's data), and calls `next(e)` to let Claude Code carry on.

| File | Role |
|---|---|
| `hooks/register.tsx` | Wiring: which events the mod listens to, and what it does on each (start here) |
| `hooks/ledger.ts` | Adds up each model request in a turn into main / subagents / untracked |
| `hooks/pricing.ts` | Price table and the formula for one request |
| `hooks/cache.ts` | Prompt-cache estimate: hit ratio, time left, learned lifetime |
| `hooks/format.ts` | Turns numbers into the text you see (`$0.28`, `1d12h13m`, the cost row) |
| `hooks/band.tsx` | Draws the status band |
| `hooks/pane.tsx` | Draws the `/telemetry` pane |
| `types/index.d.ts` | The values the mod keeps for the session (`$.state`), which survive a reload |
| `tests/` | One test file per module, run with `claude plugin test` |

Flow of one turn:
1. `turn.step` fires for every model request, main thread and subagents. The ledger records its tokens; the cache estimate updates.
2. `turn.complete` fires when the main turn ends. The ledger closes against Claude Code's cost total, and the row text is returned.
3. `session.measure` pushes context and rate-limit figures; the band redraws from the stored snapshot.

## Changing it

- Rates: `hooks/pricing.ts` (`RATES`, keyed by the model id Claude Code reports). An unknown model shows as `unpriced: …` in the row.
- Test: `claude plugin test plugins/telemetry-mod`
- Validate: `claude plugin validate plugins/telemetry-mod`
- Type-check: `tsc -p plugins/telemetry-mod`

## Known limits

- The cost row can't have a border: Claude Code draws it outside any component a mod can redraw.
- A hot reload in the middle of a turn loses that turn's main/subagent split (the total is still right next turn).
- Fast mode and the cache-write mix can't be priced per request; their difference shows as untracked.
```

**Done when**
- ✔ `claude plugin validate plugins/telemetry-mod` has no errors in the manifest or hooks sections. A remaining LICENSE-only directory warning is acceptable; note it.
- ✔ `claude plugin test plugins/telemetry-mod` passes all suites.
- ✔ Type-check exits 0.
- ✔ **Real session, one turn with two haiku subagents and one terra subagent, all inside the turn:**
  - the row reads `subagents $… (… Haiku 5.5: 2 agents, … ; Terra: 1 agent, …)`;
  - its total is within $0.02 of the old telemetry's line, the gap being terra's re-pricing.
  
  The user confirms by screenshot.
- `git status --short` lists only files under `plugins/telemetry-mod/`, plus `.claude-plugin/marketplace.json` and `.gitignore`.
- ✔ **Comment review (D11):**
  - every file under `hooks/` opens with a header comment;
  - every `on(…)` call has a comment saying when Claude Code calls it;
  - `grep -c '^//' plugins/telemetry-mod/hooks/*.ts*` shows a non-zero count for each file.
  
  The user skims `register.tsx` and says whether the flow is clear without reading the code.

---

## U9: Rewrite the repo rules for scripts and mods

**Deliverables:** a proposed rewrite of `CLAUDE.md`, reviewed with the user and then applied, plus a list of existing plugins that don't follow the new rules (findings only, no fixes).

**Files:**
- **Modify:** `CLAUDE.md`, only after the user approves the wording.
- **Must not touch:** anything under `plugins/`.

**Steps**
1. Re-read the current `CLAUDE.md`, plus the departures recorded in U1–U8 review notes.
2. Present the draft below as labelled before/after items (per the user's CLAUDE.md "Presenting proposed changes"), adjusted for what the build taught us. Wait for approval of each item.
3. Apply the approved items.
4. List the plugins that break the approved rules, as findings, with `path` references. Known now (verified): `plugins/telemetry/scripts/*.py` (has a `.py` extension, isn't in `bin/`, no tests); `plugins/learning/hooks/reinject.py` (has a `.py` extension, isn't in `bin/`). Don't fix them in this unit.

**Content: draft (a starting point for the review, not final)**
```markdown
# plugin-marketplace

Claude Code plugins, one per directory under `plugins/`, each listed in `.claude-plugin/marketplace.json`.

## Every plugin
- Keep one source of truth per fact. Other files read it or point to it.
- Deterministic work goes in code; agents and skills only judge prose.
- Each plugin has a README: what it does, how to install it, how to change it.
- Validate: `claude plugin validate plugins/<plugin>`

## Script plugins (command hooks, or skills that call scripts)
- Scripts are standard-library Python in `plugins/<plugin>/bin/`: no file extension, executable, `#!/usr/bin/env python3`.
- Tests use unittest in `plugins/<plugin>/tests/` and run scripts through `subprocess` with `sys.executable`.
- Test: `python3 -m unittest discover -s plugins/<plugin>/tests`

## Mods (`hooks/hooks.json` lists `modules`)
- Use a mod when the plugin needs Claude Code's own UI (bands, panes, per-turn rows) or in-process data (session cost, per-request usage); otherwise prefer a script plugin.
- Code is TypeScript in `plugins/<plugin>/hooks/`: `register.tsx` only wires hooks; logic that can be tested without Claude Code lives in plain modules beside it.
- Values the mod keeps are declared in `types/index.d.ts`.
- Tests: `plugins/<plugin>/tests/*.test.ts(x)` with `claude-code/testing`. Run: `claude plugin test plugins/<plugin>`
- Type-check: `tsc -p plugins/<plugin>` (needs `.claude-plugin/types/`, which Claude Code writes when it loads the mod; gitignored)
- Comment for a reader new to mods: a header on every file, and on every hook when Claude Code calls it.
```

**Gotchas:** keep the rules short. If a proposed rule only exists to patch a problem another rule creates, flag it as possible over-engineering, per the user's CLAUDE.md.

**Done when**
- ✔ The user approved each item.
- ✔ `git diff CLAUDE.md` shows exactly the approved items.
- ✔ The findings list names each non-conforming plugin path.

## Verification (end to end)

1. `claude plugin test plugins/telemetry-mod`: all suites pass, 0 failed.
2. `claude plugin validate plugins/telemetry-mod`: no errors in the hooks section; lists the hooks from U5–U7.
3. `tsc -p plugins/telemetry-mod` (or the npx fallback from Conventions): exit 0.
4. **Live session** (the user, by screenshots):
   - plain turn → row and band;
   - `/model` switch → immediate model change and `cache cold`;
   - three-subagent turn → agent counts and split;
   - `/telemetry` → pane toggles while typing still works;
   - totals within $0.01–$0.02 of the old telemetry's per-turn line.
