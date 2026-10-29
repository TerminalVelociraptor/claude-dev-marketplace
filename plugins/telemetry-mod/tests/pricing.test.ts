// Tests for hooks/pricing.ts: one test per row of the U2 test table
// (plan.md:361-371), with Terra's expected values updated to GPT-6.1 Terra's
// published rates, plus two rows for rules the table didn't cover.

import type { ModelUsage } from 'claude-code'
import { expect, test } from 'claude-code/testing'
import { chargedByClaudeCode, priceUsage } from '../hooks/pricing'

// The kit has no toBeCloseTo, so floats are compared to within 1e-9.
function near(actual: number | undefined, expected: number) {
  expect(actual).toBeDefined()
  // `actual!` tells TypeScript it isn't undefined, which the line above checked.
  expect(Math.abs(actual! - expected)).toBeLessThan(1e-9)
}

// Token counts in the test table's shorthand; omitted counts are 0.
function u(t: { input?: number; output?: number; read?: number; creation?: number }): ModelUsage {
  return {
    input_tokens: t.input ?? 0,
    output_tokens: t.output ?? 0,
    cache_read_input_tokens: t.read ?? 0,
    cache_creation_input_tokens: t.creation ?? 0,
  }
}

test('opus 5.5: 1M input costs $4', () => {
  near(priceUsage('claude-opus-5-5', u({ input: 1e6 }), '5m'), 4)
})

test('opus 5.5: 1M cache reads cost $0.20', () => {
  near(priceUsage('claude-opus-5-5', u({ read: 1e6 }), '5m'), 0.2)
})

test('opus 5.5: 1M cache writes cost $5 at 5m and $8 at 1h', () => {
  near(priceUsage('claude-opus-5-5', u({ creation: 1e6 }), '5m'), 5)
  near(priceUsage('claude-opus-5-5', u({ creation: 1e6 }), '1h'), 8)
})

test('opus 5.5: 1M output costs $20', () => {
  near(priceUsage('claude-opus-5-5', u({ output: 1e6 }), '5m'), 20)
})

test('terra: the long-prompt tier applies above 272K', () => {
  // 0.3M input at $1 x2, plus 1M output at $5 x1.5
  near(priceUsage('terra', u({ input: 300000, output: 1e6 }), '5m'), 8.1)
})

test('terra: the long-prompt tier does not apply at exactly 272K', () => {
  near(priceUsage('terra', u({ input: 272000 }), '5m'), 0.272)
})

test('an unknown claude model has no price', () => {
  expect(priceUsage('claude-unknown-9', u({ input: 1e6 }), '5m')).toBeUndefined()
})

test('Claude Code charges a non-claude model at the fallback (Sonnet 5) rates', () => {
  near(chargedByClaudeCode('terra', u({ input: 1e6 }), '5m'), 2)
})

test('Claude Code charges nothing we can know for an unknown claude model', () => {
  expect(chargedByClaudeCode('claude-unknown-9', u({ input: 1e6 }), '5m')).toBeUndefined()
})

// Added: GPT cache writes use OpenAI's fixed 1.25x, whatever Claude's lifetime.
test('terra: cache writes cost 1.25x input even when the lifetime is 1h', () => {
  // 100K tokens, under the 272K tier: 0.1M at $1 x1.25
  near(priceUsage('terra', u({ creation: 100000 }), '1h'), 0.125)
})

// Added: Haiku 5.5's 100K tier counts cache reads and raises the cache-read rate.
test('haiku 5.5: cache reads count toward 100K and are priced 5x above it', () => {
  // prompt = 50K input + 60K reads = 110K > 100K: 0.05M at $0.50 + 0.06M at $0.05
  near(priceUsage('claude-haiku-5-5', u({ input: 50000, read: 60000 }), '5m'), 0.028)
})
