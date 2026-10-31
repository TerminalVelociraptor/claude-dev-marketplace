// Tests for the band (hooks/band.tsx, drawn by register.tsx's ui.render
// hook): one test per row of the U6 test table (plan.md:625-631).
//
// `$.ui.mount` draws the band as Claude Code would, and `find` looks for a
// Text in the drawing. The snapshot is seeded through a `state.get` stand-in
// in its saved form, `{ shape, value }` (see hooks/session.ts).

import type { RenderPropsOf } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import type { TestBody } from 'claude-code/testing'
import type { Snapshot } from '../types'
import { INITIAL } from '../hooks/cache'

const NOW = 1_000_000_000_000

type Dollar = Parameters<TestBody>[0]
type On = Parameters<TestBody>[1]

const BASE: Snapshot = {
  model: 'Opus 5.5', gitDirty: false, correction: 0, limits: [], cache: INITIAL, turnCount: 0, byModel: {},
}

// The props Claude Code hands the AbovePrompt hook; only hasSurvey matters here.
const PROPS: RenderPropsOf['AbovePrompt'] = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 20,
  bodyColumns: 100,
  scroll: { offset: 0, bodyRows: 20 },
  view: {},
}

// Seeds the snapshot and the clock, then draws the band.
async function band($: Dollar, on: On, change: Partial<Snapshot>) {
  mock.clock(on, { now: NOW })
  const snap: Snapshot = { ...BASE, ...change }
  on('state.get', () => ({ value: { value: { shape: 'snap-v3', value: snap }, version: 1 } }))
  return $.ui.mount({ plugin: 'telemetry-mod', surface: 'terminal', component: 'AbovePrompt', props: PROPS })
}

test('line 1 shows the model, and a * when the branch is dirty', async ($, on) => {
  const ui = await band($, on, { effort: 'high', git: 'main', gitDirty: true })
  expect(await ui.find({ type: 'Text', text: /Opus 5\.5/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: '*' })).toBeDefined()
  await ui.unmount()
})

test('line 1 shows the repo as its own segment', async ($, on) => {
  const ui = await band($, on, { repo: 'claude-dev-marketplace', git: 'main' })
  expect(await ui.find({ type: 'Text', text: 'claude-dev-marketplace' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /^main/ })).toBeDefined()
  await ui.unmount()
})

test('with no repo, line 1 has no repo segment', async ($, on) => {
  const ui = await band($, on, { git: 'main' })
  expect(await ui.find({ type: 'Text', text: 'claude-dev-marketplace' })).toBeUndefined()
  await ui.unmount()
})

test('the context segment shows the percent and the tokens in thousands', async ($, on) => {
  const ui = await band($, on, { ctxPercent: 64, ctxTokens: 128_400 })
  expect(await ui.find({ type: 'Text', text: /ctx/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: '64%' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /\(128K\)/ })).toBeDefined()
  await ui.unmount()
})

test('a 7-day limit shows its label, percent and countdown', async ($, on) => {
  const resetsAt = new Date(NOW + ((24 + 12) * 60 + 13) * 60_000).toISOString()
  const ui = await band($, on, { limits: [{ kind: 'seven_day', percent: 18, resetsAt }] })
  expect(await ui.find({ type: 'Text', text: /7d/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: '18%' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /↻1d12h13m/ })).toBeDefined()
  await ui.unmount()
})

test('a warm cache on the assumed lifetime shows its hit ratio, time left and (est.)', async ($, on) => {
  // Last request 37 minutes ago on the assumed 1h lifetime: 23 minutes left.
  const cache = { ...INITIAL, model: 'claude-opus-5-5', lastAt: NOW - 37 * 60_000, hitRatio: 0.91 }
  const ui = await band($, on, { cache })
  expect(await ui.find({ type: 'Text', text: /cache 91% 23m left/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: / \(est\.\)/ })).toBeDefined()
  await ui.unmount()
})

test('before the first refresh (no model yet) the hook passes, so Claude Code draws its own', async ($, on) => {
  // Stands for Claude Code's own drawing of the band, beneath the mod.
  on('ui.render', (_$, e) => {
    const { Text } = _$.ui.resolve(e)
    return <Text>engine band</Text>
  })
  const ui = await band($, on, { model: '' })
  expect(await ui.find({ type: 'Text', text: 'engine band' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /ctx|cache/ })).toBeUndefined()
  await ui.unmount()
})
