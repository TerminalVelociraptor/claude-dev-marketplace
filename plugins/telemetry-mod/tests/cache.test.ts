// Tests for hooks/cache.ts: one test per row of the U3 test table
// (plan.md:426-437). Each pins one rule of the cache estimate.

import type { ModelUsage } from 'claude-code'
import { expect, test } from 'claude-code/testing'
import { INITIAL, observe, resumed, switched, view, writeTtl } from '../hooks/cache'

const T0 = 1_000_000_000_000
const OPUS = 'claude-opus-5-5'

// Token counts in the test table's shorthand; omitted counts are 0.
function u(t: { input?: number; read?: number; creation?: number }): ModelUsage {
  return {
    input_tokens: t.input ?? 0,
    output_tokens: 0,
    cache_read_input_tokens: t.read ?? 0,
    cache_creation_input_tokens: t.creation ?? 0,
  }
}

test('a fresh state is cold', () => {
  expect(view(INITIAL, T0)).toEqual({ kind: 'cold' })
})

test('a model switch is cold until the next request', () => {
  expect(view(switched(INITIAL, 'claude-sonnet-5-5', '1h'), T0)).toEqual({ kind: 'cold' })
})

test('one request with cache activity is warm, with an assumed 1h lifetime', () => {
  const s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  expect(view(s, T0)).toEqual({ kind: 'warm', hitRatio: 0.9, leftMs: 3_600_000, estimated: true })
})

test('the same state is cold once the lifetime has passed', () => {
  const s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  expect(view(s, T0 + 3_600_000)).toEqual({ kind: 'cold' })
})

test('a read after a 10 minute gap learns the 1h lifetime', () => {
  let s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  s = observe(s, OPUS, u({ read: 500 }), T0 + 600_000)
  expect(s.ttlSource).toBe('learned')
  expect(s.ttlMs).toBe(3_600_000)
})

test('a full rewrite after a 10 minute gap learns the 5m lifetime', () => {
  let s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  s = observe(s, OPUS, u({ creation: 1000 }), T0 + 600_000)
  expect(s.ttlSource).toBe('learned')
  expect(s.ttlMs).toBe(300_000)
})

test('a lifetime set by a model switch is never overridden by learning', () => {
  let s = switched(INITIAL, 'claude-haiku-5-5', '5m')
  s = observe(s, 'claude-haiku-5-5', u({ read: 900, creation: 100 }), T0)
  s = observe(s, 'claude-haiku-5-5', u({ input: 100 }), T0 + 600_000)   // no cache activity: ignored
  s = observe(s, 'claude-haiku-5-5', u({ creation: 1000 }), T0 + 600_001)
  expect(s.ttlSource).toBe('switch')
  expect(s.ttlMs).toBe(300_000)
})

test('a request with no cache activity leaves the state unchanged', () => {
  const s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  expect(observe(s, OPUS, u({ input: 5000 }), T0 + 1000)).toEqual(s)
})

test('a new model starts its own timing and learns nothing from the old one', () => {
  let s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  s = observe(s, 'terra', u({ creation: 50 }), T0 + 1)
  expect(s.model).toBe('terra')
  expect(s.hitRatio).toBe(0)
  expect(s.lastAt).toBe(T0 + 1)
  expect(s.ttlSource).toBe('assumed')
})

test('resuming with a known response age backdates the last request', () => {
  const s = resumed(INITIAL, 120, false, T0)
  expect(s.lastAt).toBe(T0 - 120_000)
})

test('resuming a likely-expired session shows cold', () => {
  const warm = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  const s = resumed(warm, 5000, true, T0 + 5000)
  expect(view(s, T0 + 5000)).toEqual({ kind: 'cold' })
})

test('writeTtl maps the lifetime to the pricing label', () => {
  expect(writeTtl({ ttlMs: 300_000, ttlSource: 'learned' })).toBe('5m')
  expect(writeTtl({ ttlMs: 3_600_000, ttlSource: 'assumed' })).toBe('1h')
})

// Boundary rows beyond the plan's table (plan.md:426-437): they pin the exact edges
// of the learning rules, so changing `>` to `>=` in cache.ts fails a test.

test('a gap of exactly 5 minutes with a read learns nothing', () => {
  let s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  s = observe(s, OPUS, u({ read: 500 }), T0 + 300_000)
  expect(s.ttlSource).toBe('assumed')
})

test('a gap of exactly 1 hour with a full rewrite learns nothing', () => {
  let s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  s = observe(s, OPUS, u({ creation: 1000 }), T0 + 3_600_000)
  expect(s.ttlSource).toBe('assumed')
})

test('resuming with nothing known leaves the state unchanged', () => {
  const s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  expect(resumed(s, undefined, undefined, T0 + 1000)).toEqual(s)
})

test('a likely-expired resume with no response age is still cold', () => {
  const s = observe(INITIAL, OPUS, u({ read: 900, creation: 100 }), T0)
  expect(view(resumed(s, undefined, true, T0 + 1000), T0 + 1000)).toEqual({ kind: 'cold' })
})
