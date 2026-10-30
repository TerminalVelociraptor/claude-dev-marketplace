// The band: two lines about the session (model, effort, git / context, cost,
// rate limits, cache), drawn from the saved snapshot.
//
// Where it sits: register.tsx's ui.render hooks read the snapshot through
// session.ts and hand it here with the drawing parts; this file only turns a
// snapshot into what the band shows. No hooks, no state, no `$`.
//
// The band sits above the prompt (AbovePrompt). Under the prompt was tried and
// dropped (U6): the hint line's slot is indented by Claude Code's layout, and
// the plugin status line is plain text only.

import type { ElementTable } from 'claude-code'
import type { Limit, Snapshot } from '../types'
import { view } from './cache'
import { countdown, percentColor, usd } from './format'
import { sessionUsd } from './session'

// The drawing parts a render hook gets from `$.ui.resolve(e)`. Taken as an
// argument rather than `$`, so nothing here needs the engine.
type Ui = { Box: ElementTable['Box']; Text: ElementTable['Text'] }

// '5h' and '7d' for the two windows Claude Code reports; any other kind as-is.
function limitLabel(kind: string): string {
  return kind === 'five_hour' ? '5h' : kind === 'seven_day' ? '7d' : kind
}

// ' ↻1d12h13m', or '' when the window has no reset time.
function resets(l: Limit, now: number): string {
  return l.resetsAt === undefined ? '' : ` ↻${countdown(Date.parse(l.resetsAt) - now)}`
}

// The band as a bordered box of two lines, segments joined by a dim ' · '.
export function bandTree(ui: Ui, s: Snapshot, now: number) {
  const { Box, Text } = ui
  const pct = (p: number) => <Text color={percentColor(p)}>{Math.round(p)}%</Text>

  const top = [<Text bold>{s.model}</Text>]
  if (s.effort) top.push(<Text>{s.effort}</Text>)
  if (s.git) {
    top.push(
      <Text>
        {s.git}
        {s.gitDirty && <Text color="warning">*</Text>}
      </Text>,
    )
  }

  const bottom = []
  if (s.ctxPercent !== undefined) {
    bottom.push(
      <Text>
        ctx {pct(s.ctxPercent)}
        {s.ctxTokens !== undefined ? ` (${Math.round(s.ctxTokens / 1000)}K)` : ''}
      </Text>,
    )
  }
  bottom.push(<Text color="warning">{`${usd(s.lastTurn ?? 0)} / ${usd(sessionUsd(s))}`}</Text>)
  for (const l of s.limits) {
    bottom.push(
      <Text>
        {limitLabel(l.kind)} {pct(l.percent)}
        {resets(l, now)}
      </Text>,
    )
  }
  const cache = view(s.cache, now)
  if (cache.kind === 'cold') bottom.push(<Text dimColor>cache cold</Text>)
  else {
    // The hit ratio is missing when a resumed session dated the cache before any request.
    const hit = cache.hitRatio === undefined ? '' : `${Math.round(cache.hitRatio * 100)}% `
    bottom.push(
      <Text>
        {`cache ${hit}${countdown(cache.leftMs)} left`}
        {cache.estimated && <Text dimColor> (est.)</Text>}
      </Text>,
    )
  }

  // `flatMap` puts a dim separator before every segment but the first.
  const line = (parts: typeof top) => (
    <Box>{parts.flatMap((part, i) => (i ? [<Text dimColor> · </Text>, part] : [part]))}</Box>
  )
  return (
    <Box flexDirection="column" borderStyle="round" borderColor="subtle" paddingX={1}>
      {line(top)}
      {line(bottom)}
    </Box>
  )
}
