// Tests for hooks/ledger.ts: the Ledger rows of the U2 test table
// (plan.md:372-375), as changed by the U5 non-Claude amendment (C10): a turn
// with a non-Claude model is priced at our rates alone.

import type { ModelUsage } from 'claude-code'
import { expect, test } from 'claude-code/testing'
import { Ledger } from '../hooks/ledger'

// The kit has no toBeCloseTo, so floats are compared to within 1e-9.
function near(actual: number | undefined, expected: number) {
  expect(actual).toBeDefined()
  // `actual!` tells TypeScript it isn't undefined, which the line above checked.
  expect(Math.abs(actual! - expected)).toBeLessThan(1e-9)
}

const USAGE: ModelUsage = {
  input_tokens: 1000, output_tokens: 500, cache_read_input_tokens: 20000, cache_creation_input_tokens: 2000,
}

// $0.10 on Opus 5.5 and $0.03 on Terra ($4 and $1 per million input tokens).
const OPUS_10C: ModelUsage = { input_tokens: 25_000, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const TERRA_3C: ModelUsage = { input_tokens: 30_000, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }

test('a Claude-only turn puts the rest of Claude Code\'s total in untracked', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'claude-opus-5-5', usage: OPUS_10C }, '1h')
  const turn = ledger.close(0.13)
  near(turn.total, 0.13)
  near(turn.untracked, 0.03)
  expect(turn.correction).toBe(0)
})

test('a mixed turn splits by thread; with a non-Claude model it is our prices alone', () => {
  const ledger = new Ledger()
  const requests = [
    ...Array.from({ length: 4 }, () => ({ model: 'claude-opus-5-5', usage: USAGE })),
    ...Array.from({ length: 2 }, () => ({ model: 'claude-haiku-5-5', agentId: 'a1', usage: USAGE })),
    { model: 'terra', agentId: 'b2', usage: USAGE },
  ]
  for (const r of requests) ledger.add(r, '1h')
  const turn = ledger.close(1)

  expect(turn.untracked).toBeUndefined()
  near(turn.total, turn.main.usd + turn.sub.usd)
  near(turn.correction, turn.total - 1)
  expect(turn.sub.models['claude-haiku-5-5']?.agents).toEqual(['a1'])
  expect(turn.sub.models['terra']?.requests).toBe(1)
  expect(turn.sub.models['terra']?.agents).toEqual(['b2'])
  expect(turn.main.models['claude-opus-5-5']?.requests).toBe(4)
})

test('Opus $0.10 with a Terra subagent $0.03: total $0.13, correction -$0.12 against a $0.25 delta', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'claude-opus-5-5', usage: OPUS_10C }, '1h')
  ledger.add({ model: 'terra', agentId: 'b2', usage: TERRA_3C }, '5m')
  const turn = ledger.close(0.25)
  near(turn.total, 0.13)
  expect(turn.untracked).toBeUndefined()
  near(turn.correction, -0.12)
})

test('Terra $0.03 on the main thread: total $0.03, correction +$0.02 against a $0.01 delta', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'terra', usage: TERRA_3C }, '1h')
  const turn = ledger.close(0.01)
  near(turn.total, 0.03)
  expect(turn.untracked).toBeUndefined()
  near(turn.correction, 0.02)
})

test('Terra without Claude Code\'s total: no correction', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'terra', usage: TERRA_3C }, '1h')
  const turn = ledger.close(undefined)
  near(turn.total, 0.03)
  expect(turn.untracked).toBeUndefined()
  expect(turn.correction).toBe(0)
})

test('without Claude Code\'s total, untracked is undefined', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'claude-opus-5-5', usage: USAGE }, '5m')
  const turn = ledger.close(undefined)
  expect(turn.untracked).toBeUndefined()
  near(turn.total, turn.main.usd + turn.sub.usd)
})

test('an unpriced claude request is listed, counted, and its cost is untracked', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'claude-unknown-9', usage: USAGE }, '5m')
  const turn = ledger.close(0.10)
  expect(turn.unpriced).toEqual(['claude-unknown-9'])
  near(turn.untracked, 0.10)
  expect(turn.main.models['claude-unknown-9']?.requests).toBe(1)
})

test('an unpriced non-claude request is listed and counted, and Claude Code\'s charge for it is dropped', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'nova', agentId: 'c3', usage: USAGE }, '5m')
  const turn = ledger.close(0.10)
  expect(turn.unpriced).toEqual(['nova'])
  expect(turn.untracked).toBeUndefined()
  expect(turn.total).toBe(0)
  near(turn.correction, -0.10)
  expect(turn.sub.models['nova']?.requests).toBe(1)
})

test('a second close right after the first returns an empty turn', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'claude-opus-5-5', usage: USAGE }, '5m')
  ledger.close(1)
  expect(ledger.isEmpty()).toBe(true)
  const turn = ledger.close(undefined)
  expect(turn.total).toBe(0)
  expect(turn.main.models).toEqual({})
  expect(turn.sub.models).toEqual({})
})
