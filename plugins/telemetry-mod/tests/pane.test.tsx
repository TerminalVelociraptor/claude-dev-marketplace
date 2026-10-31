// Tests for the pane (hooks/pane.tsx, drawn by register.tsx's ui.render hook
// for the pane) and for the /telemetry command that opens and closes it: the
// three rows of the U7 test table (plan.md:674-678), the section order, the
// edges of the table's length, the context card, and the toggle.
//
// `$.ui.mount` draws the pane as Claude Code would; `find` and `findAll` look
// for Text in the drawing. The state is seeded through a `state.get` stand-in
// that answers each key in its saved form, `{ shape, value }` (see
// hooks/session.ts).

import type { RenderPropsOf } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import type { TestBody } from 'claude-code/testing'
import type { ContextView, Snapshot, Turn } from '../types'
import { INITIAL } from '../hooks/cache'
import { PANE_COLUMNS, TABLE_TURNS } from '../hooks/pane'

const NOW = 1_000_000_000_000

type Dollar = Parameters<TestBody>[0]
type On = Parameters<TestBody>[1]

const BASE: Snapshot = {
  model: 'Opus 5.5', gitDirty: false, correction: 0, limits: [], cache: INITIAL, turnCount: 0, byModel: {},
}

// The props Claude Code hands the pane hook; only bodyColumns matters here.
const PROPS: RenderPropsOf['Pane'] = {
  title: 'Telemetry',
  isFocused: false,
  bodyColumns: 60,
  placement: 'dock',
  scroll: { offset: 0, bodyRows: 60 },
  view: {},
}

// A finished turn costing `main` on Opus, `sub` in subagents and `untracked`.
function turn(index: number, main: number, sub = 0, untracked?: number): Turn {
  const group = (usd: number): Turn['main'] => ({
    usd,
    models: usd ? { 'claude-opus-5-5': { usd, requests: 1, agents: [] } } : {},
  })
  return {
    total: main + sub + (untracked ?? 0),
    main: group(main),
    sub: group(sub),
    untracked,
    correction: 0,
    unpriced: [],
    index,
    doneAt: NOW,
  }
}

// `count` turns numbered 1..count, $0.10 each.
const turnsOf = (count: number) => Array.from({ length: count }, (_, i) => turn(i + 1, 0.1))

// A table row: the turn's number, then four figures.
const ROW = /^ *\d+( +[\d.—]+){4}$/

// Seeds the snapshot, the turns and the clock, then draws the pane.
async function pane($: Dollar, on: On, change: Partial<Snapshot>, turns: Turn[] = []) {
  mock.clock(on, { now: NOW })
  const snap: Snapshot = { ...BASE, ...change }
  on('state.get', (_$, e) => {
    const value = e.key === 'turns' ? { shape: 'turns-v1', value: turns } : { shape: 'snap-v3', value: snap }
    return { value: { value, version: 1 } }
  })
  return $.ui.mount({
    plugin: 'telemetry-mod', surface: 'terminal', component: 'Pane', requestId: 'telemetry', props: PROPS,
  })
}

test('the session line shows the total, the turn count, and one row per turn', async ($, on) => {
  const turns = [turn(1, 0.45), turn(2, 1.74), turn(3, 1.02)]
  const ui = await pane($, on, { ccTotal: 3.21, turnCount: 3 }, turns)
  expect(await ui.find({ type: 'Text', text: /Session \$3\.21 · 3 turns/ })).toBeDefined()
  expect(await ui.findAll({ type: 'Text', text: ROW })).toHaveLength(3)
  await ui.unmount()
})

test('the session line adds the correction to Claude Code\'s total', async ($, on) => {
  const ui = await pane($, on, { ccTotal: 3, correction: 0.21, turnCount: 3 })
  expect(await ui.find({ type: 'Text', text: /Session \$3\.21/ })).toBeDefined()
  await ui.unmount()
})

test('By model lists the models biggest first', async ($, on) => {
  const byModel = { 'claude-haiku-5-5': 0.21, 'claude-opus-5-5': 2.71, terra: 0.29 }
  const ui = await pane($, on, { byModel })
  const rows = await ui.findAll({ type: 'Text', text: /^(Opus 5\.5|Terra|Haiku 5\.5) +\$/ })
  expect(rows.map((r) => r.text?.split(' ')[0])).toEqual(['Opus', 'Terra', 'Haiku'])
  await ui.unmount()
})

// usd() prints exactly 0 with 4 decimals, like every amount under a cent.
test('with no turns the session line reads 0 turns and there is no table', async ($, on) => {
  const ui = await pane($, on, {})
  expect(await ui.find({ type: 'Text', text: 'Session $0.0000 · 0 turns' })).toBeDefined()
  expect(await ui.findAll({ type: 'Text', text: ROW })).toHaveLength(0)
  expect(await ui.find({ type: 'Text', text: /Turn/ })).toBeUndefined()
  await ui.unmount()
})

test('one turn reads "1 turn"', async ($, on) => {
  const ui = await pane($, on, { turnCount: 1 })
  expect(await ui.find({ type: 'Text', text: 'Session $0.0000 · 1 turn' })).toBeDefined()
  await ui.unmount()
})

test('the turn count is the session\'s, not the number of saved turns', async ($, on) => {
  const ui = await pane($, on, { turnCount: 250 }, turnsOf(3))
  expect(await ui.find({ type: 'Text', text: /· 250 turns/ })).toBeDefined()
  await ui.unmount()
})

test('exactly TABLE_TURNS turns are all listed, including the first', async ($, on) => {
  const ui = await pane($, on, { turnCount: TABLE_TURNS }, turnsOf(TABLE_TURNS))
  expect(await ui.findAll({ type: 'Text', text: ROW })).toHaveLength(TABLE_TURNS)
  expect(await ui.find({ type: 'Text', text: /^ *1 / })).toBeDefined()
  await ui.unmount()
})

test('one more than TABLE_TURNS lists the latest TABLE_TURNS, dropping the first', async ($, on) => {
  const ui = await pane($, on, { turnCount: TABLE_TURNS + 1 }, turnsOf(TABLE_TURNS + 1))
  expect(await ui.findAll({ type: 'Text', text: ROW })).toHaveLength(TABLE_TURNS)
  expect(await ui.find({ type: 'Text', text: /^ *1 / })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: new RegExp(`^ *${TABLE_TURNS + 1} `) })).toBeDefined()
  await ui.unmount()
})

test('a zero or missing part reads —', async ($, on) => {
  // Turn 1: main only. The Sub and Untr. cells are both —.
  const ui = await pane($, on, { turnCount: 1 }, [turn(1, 0.45)])
  expect(await ui.find({ type: 'Text', text: /^ *1 +0\.45 +— +— +0\.45$/ })).toBeDefined()
  await ui.unmount()
})

// An untracked part, and how its cell reads: anything that prints as zero
// (float noise left by subtracting two totals) reads —, as the row hides it.
const UNTRACKED_CELLS: [number, string][] = [
  [-1e-17, '—'], [0.00004, '—'], [-0.00004, '—'], [0.0001, '0.0001'], [-0.0001, '-0.0001'],
]
for (const [untracked, shown] of UNTRACKED_CELLS) {
  test(`an untracked part of ${untracked} reads ${shown}`, async ($, on) => {
    const ui = await pane($, on, { turnCount: 1 }, [turn(1, 0.45, 0, untracked)])
    const escaped = shown.replace(/[.\-]/g, '\\$&')
    expect(await ui.find({ type: 'Text', text: new RegExp(`^ *1 +0\\.45 +— +${escaped} +0\\.45$`) })).toBeDefined()
    await ui.unmount()
  })
}

test('the session duration shows when Claude Code gave a start time', async ($, on) => {
  const ui = await pane($, on, { startedAt: NOW - 90 * 60_000 })
  expect(await ui.find({ type: 'Text', text: /· 1h30m$/ })).toBeDefined()
  await ui.unmount()
})

test('context shows the percent, the tokens and the window', async ($, on) => {
  on('session.usage', () => ({ value: { startedAt: 0, context: { window: 200_000 }, rateLimits: [] } }))
  const ui = await pane($, on, { ctxPercent: 64, ctxTokens: 128_400 })
  expect(await ui.find({ type: 'Text', text: '64%' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: / · 128K \/ 200K/ })).toBeDefined()
  await ui.unmount()
})

test('a 7-day limit shows its label, percent and countdown', async ($, on) => {
  const resetsAt = new Date(NOW + ((24 + 12) * 60 + 13) * 60_000).toISOString()
  const ui = await pane($, on, { limits: [{ kind: 'seven_day', percent: 18, resetsAt }] })
  expect(await ui.find({ type: 'Text', text: /7d/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: '18%' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /↻ 1d12h13m/ })).toBeDefined()
  await ui.unmount()
})

test('the cache line uses the band\'s words', async ($, on) => {
  // Last request 37 minutes ago on the assumed 1h lifetime: 23 minutes left.
  const cache = { ...INITIAL, model: 'claude-opus-5-5', lastAt: NOW - 37 * 60_000, hitRatio: 0.91 }
  const warm = await pane($, on, { cache })
  expect(await warm.find({ type: 'Text', text: /cache 91% 23m left/ })).toBeDefined()
  await warm.unmount()
})

test('with no request on record the cache line reads cold', async ($, on) => {
  const ui = await pane($, on, {})
  expect(await ui.find({ type: 'Text', text: 'cache cold' })).toBeDefined()
  await ui.unmount()
})

test('a rate-limit bar is filled to its percent of 16 cells, the rest a dim track', async ($, on) => {
  const ui = await pane($, on, { limits: [{ kind: 'five_hour', percent: 19 }] })
  // 19% of 16 cells is 3 cells (3.04, rounded).
  expect(await ui.find({ type: 'Text', text: '███' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: '░'.repeat(13) })).toBeDefined()
  await ui.unmount()
})

test('the cards come in the order Rate limits, Prompt cache, By model, the table, Context', async ($, on) => {
  const limits = [{ kind: 'five_hour', percent: 19 }]
  const ui = await pane($, on, { limits, byModel: { 'claude-opus-5-5': 1 }, ctxPercent: 5, turnCount: 1 }, turnsOf(1))
  const titles = await ui.findAll({ type: 'Text', text: /^(Session|Rate limits|Prompt cache|By model|Last \d+ turns|Context)/ })
  expect(titles.map((t) => t.text?.split(' ').slice(0, 2).join(' '))).toEqual([
    'Session $0.0000', 'Rate limits', 'Prompt cache', 'By model', `Last ${TABLE_TURNS}`, 'Context',
  ])
  await ui.unmount()
})

// Where the used context comes from: three categories, two items.
const CONTEXT: ContextView = {
  categories: [
    { name: 'Messages', tokens: 82_300, color: 'permission' },
    { name: 'System tools', tokens: 14_100, color: 'promptBorder' },
    { name: 'Skills', tokens: 5_900, color: 'success' },
  ],
  items: [
    { kind: 'Memory', name: '~/.claude/CLAUDE.md', tokens: 2_400 },
    { kind: 'MCP', name: 'claude-in-chrome: computer', tokens: 2_100 },
  ],
}

test('the context card lists each category with its tokens and share of the used context', async ($, on) => {
  const ui = await pane($, on, { ctxPercent: 10, context: CONTEXT })
  // 102.3K used: Messages is 80%, System tools 14%, Skills 6%.
  expect(await ui.find({ type: 'Text', text: /Messages +82\.3K +80%/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /System tools +14\.1K +14%/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Skills +5\.9K +6%/ })).toBeDefined()
  await ui.unmount()
})

test('the context bar fills the card exactly, whatever the rounding', async ($, on) => {
  const ui = await pane($, on, { ctxPercent: 10, context: CONTEXT })
  // The body is 60 columns wide; the border and padding take 4.
  expect(await ui.find({ type: 'Text', text: '█'.repeat(PROPS.bodyColumns - 4) })).toBeDefined()
  await ui.unmount()
})

test('the context card lists the biggest items under their own heading', async ($, on) => {
  const ui = await pane($, on, { ctxPercent: 10, context: CONTEXT })
  expect(await ui.find({ type: 'Text', text: 'Biggest items' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Memory +~\/\.claude\/CLAUDE\.md +2\.4K/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /MCP +claude-in-chrome: computer +2\.1K/ })).toBeDefined()
  await ui.unmount()
})

test('with no breakdown saved the context card is just the ctx line', async ($, on) => {
  const ui = await pane($, on, { ctxPercent: 10 })
  expect(await ui.find({ type: 'Text', text: '10%' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: 'Biggest items' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: /Messages/ })).toBeUndefined()
  await ui.unmount()
})

test('a long item name is cut to the card with an ellipsis', async ($, on) => {
  const name = 'plugin-dev:a-skill-with-a-very-very-very-long-name-indeed'
  const context = { ...CONTEXT, items: [{ kind: 'Skill', name, tokens: 900 }] }
  const ui = await pane($, on, { ctxPercent: 10, context })
  // 56 columns inside the card: 7 for the kind, 5 for the size, 43 for the name
  // and its padding, so a name over 42 characters is cut to 41 and an ellipsis.
  expect(await ui.find({ type: 'Text', text: new RegExp(`Skill +${name.slice(0, 41)}… +0\\.9K`) })).toBeDefined()
  await ui.unmount()
})

test('the footer says how to close the pane', async ($, on) => {
  const ui = await pane($, on, {})
  expect(await ui.find({ type: 'Text', text: '× or /telemetry closes' })).toBeDefined()
  await ui.unmount()
})

// Stands in for the engine's pane calls. `isUp` says whether `telemetry` is
// listed as open; the calls the mod makes are recorded.
function panes(on: On, isUp: boolean) {
  const calls: string[] = []
  mock.clock(on, { now: NOW })
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('ui.panes', () => ({ value: isUp ? [{ id: 'telemetry', title: 'Telemetry', isShown: true, isFocused: false, isPlaced: true }] : [] }))
  on('ui.open', (_$, e) => {
    calls.push(`open ${e.id} ${e.title} focus=${e.focus} columns=${e.columns}`)
    return { value: { isPlaced: true as const } }
  })
  on('ui.close', (_$, e) => {
    calls.push(`close ${e.id}`)
    return { value: undefined }
  })
  return calls
}

// What the engine raises when the person types `/telemetry` at the prompt in
// the fullscreen layout.
const TYPED = {
  command: 'telemetry',
  args: '',
  origin: { kind: 'composer' as const },
  presentation: { isFullscreen: true, columns: 120 },
}

test('/telemetry opens the pane when it is closed, without focus', async ($, on) => {
  const calls = panes(on, false)
  const { text } = await $.command.run(TYPED)
  expect(text).toBe('Telemetry pane opened.')
  expect(calls).toEqual([`open telemetry Telemetry focus=undefined columns=${PANE_COLUMNS}`])
})

test('/telemetry closes the pane when it is open', async ($, on) => {
  const calls = panes(on, true)
  const { text } = await $.command.run(TYPED)
  expect(text).toBe('Telemetry pane closed.')
  expect(calls).toEqual(['close telemetry'])
})
