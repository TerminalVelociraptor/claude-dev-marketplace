// Tests for hooks/format.ts: one test per row of the U4 test table
// (plan.md:480-497), plus the edges of each threshold.

import { expect, test } from 'claude-code/testing'
import type { TurnCost } from '../types'
import { countdown, modelName, percentColor, row, usd } from '../hooks/format'

const MIN = 60_000

// A TurnCost with only the fields a row test cares about.
function turn(t: Partial<TurnCost> & { total: number }): TurnCost {
  return {
    main: { usd: 0, models: {} },
    sub: { usd: 0, models: {} },
    correction: 0,
    unpriced: [],
    ...t,
  }
}

test('modelName strips claude- and a date, and joins the version with a dot', () => {
  expect(modelName('claude-opus-5-5')).toBe('Opus 5.5')
  expect(modelName('claude-haiku-4-5-20251001')).toBe('Haiku 4.5')
  expect(modelName('terra')).toBe('Terra')
})

test('usd uses 2 decimals from a cent up and 4 below it', () => {
  expect(usd(0.28)).toBe('$0.28')
  expect(usd(0.004)).toBe('$0.0040')
  expect(usd(-0.03)).toBe('-$0.03')
  expect(usd(0.01)).toBe('$0.01')
  expect(usd(0.0099)).toBe('$0.0099')
})

test('countdown is <1m below a minute and for negatives', () => {
  expect(countdown(-5)).toBe('<1m')
  expect(countdown(30_000)).toBe('<1m')
  expect(countdown(59_999)).toBe('<1m')
  expect(countdown(60_000)).toBe('1m')
})

test('countdown drops units that are not needed', () => {
  expect(countdown(23 * MIN)).toBe('23m')
  expect(countdown(65 * MIN)).toBe('1h05m')
  expect(countdown(((24 + 12) * 60 + 13) * MIN)).toBe('1d12h13m')
  expect(countdown(((2 * 24 + 3) * 60 + 4) * MIN)).toBe('2d03h04m')
  expect(countdown(86_400_000)).toBe('1d00h00m')
})

test('row groups by thread, sorts by cost and shows untracked spend (D3)', () => {
  const t = turn({
    total: 0.28,
    main: { usd: 0.2, models: { 'claude-opus-5-5': { usd: 0.2, requests: 4, agents: [] } } },
    sub: {
      usd: 0.05,
      models: {
        'claude-haiku-5-5': { usd: 0.02, requests: 4, agents: ['a1', 'a2'] },
        terra: { usd: 0.03, requests: 3, agents: ['a3'] },
      },
    },
    untracked: 0.03,
  })
  expect(row(t)).toBe(
    '~$0.28 this turn · main $0.20 (Opus 5.5: 4 requests) · subagents $0.05 (Terra: 1 agent, 3 requests; Haiku 5.5: 2 agents, 4 requests) · untracked $0.03',
  )
})

test('row hides untracked spend too small to print and says "1 request"', () => {
  const t = turn({
    total: 0.05,
    main: { usd: 0.05, models: { 'claude-opus-5-5': { usd: 0.05, requests: 1, agents: [] } } },
    untracked: 0.00004,
  })
  expect(row(t)).toBe('~$0.05 this turn · main $0.05 (Opus 5.5: 1 request)')
})

test('row lists unpriced models when untracked is unknown', () => {
  const t = turn({ total: 0, untracked: undefined, unpriced: ['claude-x-1'] })
  expect(row(t).endsWith(' · unpriced: X 1')).toBe(true)
})

test('row shows untracked from $0.00005 up (prints as $0.0001), not below', () => {
  expect(row(turn({ total: 0.00005, untracked: 0.00005 }))).toContain('untracked $0.0001')
  expect(row(turn({ total: 0.0000499, untracked: 0.0000499 }))).not.toContain('untracked')
  expect(row(turn({ total: -0.00005, untracked: -0.00005 }))).toContain('untracked -$0.0001')
})

test('percentColor switches at 50 and 80', () => {
  expect(percentColor(49.9)).toBe('success')
  expect(percentColor(50)).toBe('warning')
  expect(percentColor(79.9)).toBe('warning')
  expect(percentColor(80)).toBe('error')
})
