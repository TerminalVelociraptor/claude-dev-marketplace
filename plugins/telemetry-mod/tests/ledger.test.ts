// Tests for hooks/ledger.ts: one test per Ledger row of the U2 test table
// (plan.md:372-375), plus one row for the plan.md:354 amendment.

import type { ModelUsage } from 'claude-code'
import { expect, test } from 'claude-code/testing'
import { Ledger } from '../hooks/ledger'
import { chargedByClaudeCode } from '../hooks/pricing'

// The kit has no toBeCloseTo, so floats are compared to within 1e-9.
function near(actual: number | undefined, expected: number) {
  expect(actual).toBeDefined()
  // `actual!` tells TypeScript it isn't undefined, which the line above checked.
  expect(Math.abs(actual! - expected)).toBeLessThan(1e-9)
}

const USAGE: ModelUsage = {
  input_tokens: 1000, output_tokens: 500, cache_read_input_tokens: 20000, cache_creation_input_tokens: 2000,
}

test('a mixed turn splits by thread and puts the rest in untracked', () => {
  const ledger = new Ledger()
  const requests = [
    ...Array.from({ length: 4 }, () => ({ model: 'claude-opus-5-5', usage: USAGE })),
    ...Array.from({ length: 2 }, () => ({ model: 'claude-haiku-5-5', agentId: 'a1', usage: USAGE })),
    { model: 'terra', agentId: 'b2', usage: USAGE },
  ]
  for (const r of requests) ledger.add(r, '1h')
  const tracked = requests.reduce((sum, r) => sum + chargedByClaudeCode(r.model, r.usage, '1h')!, 0)

  const turn = ledger.close(tracked + 0.03)

  near(turn.untracked, 0.03)
  expect(turn.sub.models['claude-haiku-5-5']?.agents).toEqual(['a1'])
  expect(turn.sub.models['terra']?.requests).toBe(1)
  expect(turn.sub.models['terra']?.agents).toEqual(['b2'])
  expect(turn.main.models['claude-opus-5-5']?.requests).toBe(4)
  near(turn.total, turn.main.usd + turn.sub.usd + 0.03)
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

// Added with the plan.md:354 amendment: Claude Code charges an unpriced
// non-claude model at the fallback rates; that charge must land in untracked.
test('an unpriced non-claude request is listed, counted, and its cost is untracked', () => {
  const ledger = new Ledger()
  ledger.add({ model: 'nova', agentId: 'c3', usage: USAGE }, '5m')
  const turn = ledger.close(0.10)
  expect(turn.unpriced).toEqual(['nova'])
  near(turn.untracked, 0.10)
  near(turn.total, 0.10)
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
