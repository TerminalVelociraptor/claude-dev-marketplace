// The /telemetry pane: the session's details drawn from the saved state, one
// bordered card per section: session total, rate limits, prompt cache, spend
// per model, the latest turns, and where the context comes from.
//
// Where it sits: register.tsx's `/telemetry` command opens the pane, and its
// ui.render hook for the pane reads the state through session.ts and hands it
// here with the drawing parts; this file only turns state into what the pane
// shows. No hooks, no state, no `$`. It is the pane's twin of band.tsx, and
// borrows the band's cache words and limit labels from it.
//
// The numbers and colours you may want to change are the constants just below.

import type { ElementTable } from 'claude-code'
import type { ContextView, Snapshot, Turn } from '../types'
import { cacheText, limitLabel } from './band'
import { countdown, modelName, nonZero, percentColor, usd } from './format'
import { sessionUsd } from './session'

// How many of the latest turns the table lists. register.tsx keeps this many
// turns in state too, so raising it fills up over the next turns; turns
// already dropped don't come back.
export const TABLE_TURNS = 10
// How many of the biggest memory files, MCP tools, agents and skills the
// Context card lists. register.tsx cuts the saved list to this many.
export const BIGGEST_ITEMS = 5
// How wide the dock is asked to be, in columns. The terminal may give less
// (never more than 45% of its width), and a width you dragged it to wins.
export const PANE_COLUMNS = 48
// How many `█` a bar has when it is full: the biggest model's share is the whole bar.
const MODEL_BAR_CELLS = 20
// How many `█` a rate-limit bar has at 100%.
const LIMIT_BAR_CELLS = 16
// The colour of each model in By model, by the first word of its name. A model
// not listed here is drawn in the normal text colour. Any CSS-style colour works.
const MODEL_COLORS: Record<string, string> = {
  Opus: '#c586e6',
  Sonnet: '#e59a4a',
  Haiku: '#5fd0c0',
  Astra: '#f08fb0',
  Luna: '#f08fb0',
  Sol: '#f08fb0',
  Terra: '#f08fb0',
}

// The drawing parts a render hook gets from `$.ui.resolve(e)`. Taken as an
// argument rather than `$`, so nothing here needs the engine.
type Ui = { Box: ElementTable['Box']; Text: ElementTable['Text'] }

// What the hook hands over besides the saved state.
type Props = {
  bodyColumns: number      // cells across the pane's body
  rows: number             // rows the room gives the body; the footer sits at the last one
  windowTokens?: number    // the model's context window, from $.session.usage()
}

// A money figure for a table cell: '0.45', or '—' for nothing or an amount
// that prints as zero (float noise such as -0.00000000000001).
function cell(x: number | undefined): string {
  return x === undefined || !nonZero(x) ? '—' : usd(x).replace('$', '')
}

// Right-aligns text in a column `width` cells wide.
const right = (text: string, width: number) => text.padStart(width)

// '128K': tokens in thousands, for the context line.
const thousands = (n: number) => `${Math.round(n / 1000)}K`

// '2.4K': tokens in thousands to one decimal, for the breakdown.
const tenths = (n: number) => `${(n / 1000).toFixed(1)}K`

// Splits `cells` squares between the values in proportion, with no square lost
// to rounding: each value gets its whole share, and the squares left over go to
// the biggest fractions.
function shares(values: number[], cells: number): number[] {
  const total = values.reduce((t, v) => t + v, 0)
  if (total <= 0) return values.map(() => 0)
  const exact = values.map((v) => (v / total) * cells)
  const whole = exact.map(Math.floor)
  const fraction = (i: number) => (exact[i] ?? 0) - (whole[i] ?? 0)
  const byFraction = exact.map((_, i) => i).sort((a, b) => fraction(b) - fraction(a))
  for (const i of byFraction.slice(0, cells - whole.reduce((t, n) => t + n, 0))) whole[i] = (whole[i] ?? 0) + 1
  return whole
}

// The table's rows, oldest first, one line each. `slice(-n)` keeps the last n.
function tableLines(turns: Turn[]): { header: string; rows: string[] } {
  const line = (index: string, cells: string[]) => right(index, 4) + cells.map((c) => right(c, 8)).join('')
  return {
    header: line('Turn', ['Main', 'Sub', 'Untr.', 'Total']),
    rows: turns.slice(-TABLE_TURNS).map((t) =>
      line(String(t.index), [cell(t.main.usd), cell(t.sub.usd), cell(t.untracked), cell(t.total)]),
    ),
  }
}

// Session spend per model name, biggest first. Two ids that read the same
// ('claude-haiku-5-5' and a dated one) are one row.
function byModel(spend: Snapshot['byModel']): [string, number][] {
  const names = new Map<string, number>()
  for (const [id, spent] of Object.entries(spend)) {
    const name = modelName(id)
    names.set(name, (names.get(name) ?? 0) + spent)
  }
  return [...names].sort(([an, a], [bn, b]) => b - a || an.localeCompare(bn))
}

// The model's colour: its first word ('Opus' for 'Opus 5.5') looked up in MODEL_COLORS.
const modelColor = (name: string) => MODEL_COLORS[name.split(' ')[0] ?? '']

// The pane as a column of cards, with the footer at the bottom.
export function paneTree(ui: Ui, s: Snapshot, turns: Turn[], now: number, props: Props) {
  const { Box, Text } = ui
  const pct = (p: number) => <Text color={percentColor(p)}>{Math.round(p)}%</Text>
  // One round-bordered card; its title (if any) is the first line inside it.
  // Same border as the band's. The border and padding take 4 of the columns.
  const inner = props.bodyColumns - 4
  const card = (title: string | undefined, ...rows: JSX.Element[]) => (
    <Box flexDirection="column" borderStyle="round" borderColor="subtle" paddingX={1}>
      {title !== undefined && <Text bold>{title}</Text>}
      {rows}
    </Box>
  )

  // 1. Session. The duration is left out when Claude Code gave no start time.
  const duration = s.startedAt === undefined ? '' : ` · ${countdown(now - s.startedAt)}`
  const cards = [
    card(
      undefined,
      <Text bold>{`Session ${usd(sessionUsd(s))} · ${s.turnCount} ${s.turnCount === 1 ? 'turn' : 'turns'}${duration}`}</Text>,
    ),
  ]

  // 2. Rate limits: a bar, a dim track to its full length, and the time to the
  // reset, so the resets line up.
  if (s.limits.length) {
    cards.push(
      card(
        'Rate limits',
        ...s.limits.map((l) => {
          const filled = Math.round((l.percent / 100) * LIMIT_BAR_CELLS)
          return (
            <Text>
              {limitLabel(l.kind).padEnd(4)}
              <Text color={percentColor(l.percent)}>{right(`${Math.round(l.percent)}%`, 4)}</Text>{' '}
              <Text color={percentColor(l.percent)}>{'█'.repeat(filled)}</Text>
              <Text dimColor>{'░'.repeat(LIMIT_BAR_CELLS - filled)}</Text>
              {l.resetsAt === undefined ? '' : ` ↻ ${countdown(Date.parse(l.resetsAt) - now)}`}
            </Text>
          )
        }),
      ),
    )
  }

  // 3. Prompt cache: the band's words.
  const cache = cacheText(s.cache, now)
  cards.push(
    card(
      'Prompt cache',
      cache.cold ? (
        <Text dimColor>{cache.text}</Text>
      ) : (
        <Text>
          {cache.text}
          {cache.estimated && <Text dimColor> (est.)</Text>}
        </Text>
      ),
    ),
  )

  // 4. By model: each model's share of the total is its bar.
  const models = byModel(s.byModel)
  if (models.length) {
    const sum = models.reduce((t, [, v]) => t + v, 0)
    const nameWidth = Math.max(...models.map(([n]) => n.length))
    cards.push(
      card(
        'By model',
        ...models.map(([name, v]) => (
          <Text>
            <Text color={modelColor(name)}>{name.padEnd(nameWidth)}</Text>
            {` ${right(usd(v), 8)} `}
            <Text color={modelColor(name)}>{'█'.repeat(sum > 0 ? Math.round((v / sum) * MODEL_BAR_CELLS) : 0)}</Text>
          </Text>
        )),
      ),
    )
  }

  // 5. The latest turns. No turns, no table.
  if (turns.length) {
    const table = tableLines(turns)
    cards.push(
      card(`Last ${TABLE_TURNS} turns`, <Text dimColor>{table.header}</Text>, ...table.rows.map((r) => <Text>{r}</Text>)),
    )
  }

  // 6. Context: the line from Claude Code, then (while the breakdown is
  // there) what the used context is made of and the biggest items in it.
  if (s.ctxPercent !== undefined || s.context) {
    const rows: JSX.Element[] = []
    if (s.ctxPercent !== undefined) {
      const used =
        s.ctxTokens === undefined
          ? ''
          : ` · ${thousands(s.ctxTokens)}${props.windowTokens === undefined ? '' : ` / ${thousands(props.windowTokens)}`}`
      rows.push(
        <Text>
          ctx {pct(s.ctxPercent)}
          {used}
        </Text>,
      )
    }
    if (s.context) rows.push(...contextRows(Text, s.context, inner))
    cards.push(card('Context', ...rows))
  }

  // The spacer takes the room left over, which pushes the footer to the
  // bottom; a pane shorter than its cards just clips (and scrolls when focused).
  return (
    <Box flexDirection="column" width={props.bodyColumns} minHeight={props.rows}>
      {cards}
      <Box flexGrow={1} />
      <Text dimColor>× or /telemetry closes</Text>
    </Box>
  )
}

// The Context card's breakdown: one bar split by category, a legend, then the
// biggest items under a dim rule.
function contextRows(Text: Ui['Text'], context: ContextView, inner: number): JSX.Element[] {
  const { categories, items } = context
  const used = categories.reduce((t, c) => t + c.tokens, 0)
  const cells = shares(categories.map((c) => c.tokens), inner)
  const nameWidth = Math.max(0, ...categories.map((c) => c.name.length))
  const rows: JSX.Element[] = []

  if (used > 0) {
    rows.push(
      <Text>
        {categories.map((c, i) => (
          <Text color={c.color}>{'█'.repeat(cells[i] ?? 0)}</Text>
        ))}
      </Text>,
    )
  }
  for (const c of categories) {
    rows.push(
      <Text>
        <Text color={c.color}>■ </Text>
        {`${c.name.padEnd(nameWidth)} ${right(tenths(c.tokens), 6)}${right(`${Math.round((c.tokens / used) * 100)}%`, 5)}`}
      </Text>,
    )
  }

  if (items.length) {
    rows.push(<Text> </Text>, <Text dimColor>{'─'.repeat(inner)}</Text>, <Text bold>Biggest items</Text>)
    const nameCells = inner - 13
    for (const item of items) {
      const name = item.name.length > nameCells - 1 ? `${item.name.slice(0, nameCells - 2)}…` : item.name
      rows.push(
        <Text>
          <Text dimColor>{item.kind.padEnd(7)}</Text>
          {`${name.padEnd(nameCells)}${right(tenths(item.tokens), 5)}`}
        </Text>,
      )
    }
  }
  return rows
}
