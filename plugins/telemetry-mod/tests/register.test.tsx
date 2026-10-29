// Tests for hooks/register.tsx: the two rows of the U5 test table
// (plan.md:574-575), plus edge rows (subagent turn end, missing total,
// subagent cache-write lifetime).
//
// In a test, `$` is Claude Code itself and the hooks registered with `on` sit
// beneath the mod, standing in for the engine: they answer session.usage,
// $.state, the model requests and the turn ends. A stand-in for a call the mod
// makes on `$` answers `{ value: ... }`; one for an event Claude Code raises
// answers the event's own result. The mod's state lives in `store`, in its
// saved form `{ shape, value }`.

import type { ModelUsage, SessionUsage } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import type { TestBody } from 'claude-code/testing'
import type { Snapshot, Turn } from '../types'

// $0.10 on Opus 5.5 ($4 per million input tokens).
const OPUS_10C: ModelUsage = { input_tokens: 25_000, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
// $0.01 on Haiku 5.5 ($0.50 per million output tokens).
const HAIKU_1C: ModelUsage = { input_tokens: 0, output_tokens: 20_000, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
// A Haiku 5.5 cache write of 100K tokens: $0.0125 at the 5-minute rate (1.25x
// $0.10), $0.02 at the 1-hour rate (2x).
const HAIKU_WRITE: ModelUsage = { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 100_000 }

type Dollar = Parameters<TestBody>[0]
type On = Parameters<TestBody>[1]

// One saved value and its version, which goes up on every write.
type Stored = { value: unknown; version: number }

// What session.usage answers: Claude Code's session total, or none.
function usage(usd: number | undefined): SessionUsage {
  return { startedAt: 0, context: { window: 200_000 }, rateLimits: [], cost: usd === undefined ? undefined : { usd } }
}

// The hooks that stand in for the engine. `cost.usd` is what session.usage
// reports; a test changes it between turns. Opus requests report OPUS_10C,
// Haiku requests `haiku` (HAIKU_1C unless given). Returns the state store,
// keyed by state key.
function engine(on: On, cost: { usd: number | undefined }, haiku: ModelUsage = HAIKU_1C): Map<string, Stored> {
  const store = new Map<string, Stored>()
  mock.clock(on, { now: 1_000_000 })
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('session.usage', () => ({ value: usage(cost.usd) }))
  on('state.get', (_$, e) => ({ value: store.get(e.key) ?? { value: undefined, version: 0 } }))
  // Compare-and-set, as the engine does it: a write given an out-of-date
  // ifVersion misses, and `update` reads again and retries.
  on('state.set', (_$, e) => {
    const version = store.get(e.key)?.version ?? 0
    if (e.ifVersion !== undefined && e.ifVersion !== version) return { value: { isSet: false as const, version } }
    store.set(e.key, { value: e.value, version: version + 1 })
    return { value: { isSet: true as const, version: version + 1 } }
  })
  on('turn.step', async function* (_$, e) {
    const u = e.model === 'claude-haiku-5-5' ? haiku : OPUS_10C
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn' as const, usage: { ...u, model: e.model } }
  })
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  return store
}

// Raises one model request and reads its stream to the end, as the engine does.
async function step($: Dollar, model: string, agentId?: string) {
  const stream = $.turn.step({ turnId: 't', index: 0, model, messageCount: 1, agentId })
  for await (const _ of stream) { /* the response's chunks; not needed here */ }
  return stream.result
}

function complete($: Dollar, answer: string, agentId?: string) {
  return $.turn.complete({ turnId: 't', answer, durationMs: 1, isAborted: false, reason: 'answer', agentId })
}

// A value the mod saved, unwrapped from its `{ shape, value }` form.
function saved<T>(store: Map<string, Stored>, key: 'snap' | 'turns'): T {
  return (store.get(key)?.value as { value: T }).value
}

test('turns saved by an older version read as empty, so the first new turn is number 1', async ($, on) => {
  const cost = { usd: 0 as number | undefined }
  const store = engine(on, cost)
  // An old value with no shape tag, as an earlier version of the mod might
  // have left it. Read as-is it would make the new turn the second entry.
  store.set('turns', { value: [{ foo: 1 }], version: 1 })
  await $.session.start({ cwd: '/', surface: null, isInteractive: false })

  cost.usd = 0.1
  await step($, 'claude-opus-5-5')
  await complete($, 'done')

  const turns = saved<Turn[]>(store, 'turns')
  expect(turns).toHaveLength(1)
  expect(turns[0]?.index).toBe(1)
})

test('a main Opus turn costing $0.10 returns the row', async ($, on) => {
  const cost = { usd: 0 as number | undefined }
  engine(on, cost)
  await $.session.start({ cwd: '/', surface: null, isInteractive: false })

  cost.usd = 0.1
  await step($, 'claude-opus-5-5')
  const { text } = await complete($, 'done')

  expect(text.startsWith('~$0.10 this turn · main')).toBe(true)
})

test("a subagent's turn ending leaves the ledger open; the main turn's row counts it", async ($, on) => {
  const cost = { usd: 0 as number | undefined }
  engine(on, cost)
  await $.session.start({ cwd: '/', surface: null, isInteractive: false })

  cost.usd = 0.11
  await step($, 'claude-opus-5-5')
  await step($, 'claude-haiku-5-5', 'a1')
  // The subagent's answer comes back untouched: no row under it.
  expect((await complete($, 'sub answer', 'a1')).text).toBe('sub answer')
  const { text } = await complete($, 'done')

  expect(text).toBe('~$0.11 this turn · main $0.10 (Opus 5.5: 1 request) · subagents $0.01 (Haiku 5.5: 1 agent, 1 request)')
})

test("without Claude Code's total the turn has no untracked part and the last total is kept", async ($, on) => {
  const cost = { usd: 0 as number | undefined }
  const store = engine(on, cost)
  await $.session.start({ cwd: '/', surface: null, isInteractive: false })

  cost.usd = 0.1
  await step($, 'claude-opus-5-5')
  await complete($, 'first')

  cost.usd = undefined
  await step($, 'claude-opus-5-5')
  const { text } = await complete($, 'second')

  expect(text).toBe('~$0.10 this turn · main $0.10 (Opus 5.5: 1 request)')
  expect(saved<Turn[]>(store, 'turns').at(-1)?.untracked).toBeUndefined()
  expect(saved<Snapshot>(store, 'snap').ccTotal).toBe(0.1)
})

test("a subagent's cache writes are priced at the 5-minute rate, whatever the main thread's lifetime", async ($, on) => {
  const cost = { usd: 0 as number | undefined }
  engine(on, cost, HAIKU_WRITE)
  await $.session.start({ cwd: '/', surface: null, isInteractive: false })

  // The main thread's lifetime is the 1-hour default here; the subagent's
  // write costs $0.0125 at 5 minutes, and Claude Code's total agrees.
  cost.usd = 0.1125
  await step($, 'claude-opus-5-5')
  await step($, 'claude-haiku-5-5', 'a1')
  const { text } = await complete($, 'done')

  expect(text).toBe('~$0.11 this turn · main $0.10 (Opus 5.5: 1 request) · subagents $0.01 (Haiku 5.5: 1 agent, 1 request)')
})
