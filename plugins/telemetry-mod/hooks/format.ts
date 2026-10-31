// Turns numbers and model ids into the short strings the telemetry UI shows:
// model names, repo names, dollar amounts, countdowns, the per-turn row and a colour.
// Pure: no hooks, no state, no `$`.
// Where it sits: ledger.ts produces a TurnCost; this file formats it. Used by
// register.tsx (the per-turn row), band.tsx (U6) and pane.tsx (U7).

import type { TurnCost } from '../types'

// 'claude-haiku-4-5-20251001' -> 'Haiku 4.5'; 'terra' -> 'Terra'.
export function modelName(id: string): string {
  // A regex literal: `^claude-` at the start, `-\d{8}$` (eight digits) at the end.
  // `?? ''` only satisfies the type checker: split always returns one part.
  const [family = '', ...version] = id.replace(/^claude-/, '').replace(/-\d{8}$/, '').split('-')
  const name = family.charAt(0).toUpperCase() + family.slice(1)
  return version.length ? `${name} ${version.join('.')}` : name
}

// A remote URL's repo name: the last path segment, without '.git' or a trailing
// '/'. 'git@github.com:o/r.git', 'https://github.com/o/r' and
// 'ssh://git@host/o/r/' all give 'r'.
export function repoName(url: string): string | undefined {
  return /([^/:]+?)(?:\.git)?\/?$/.exec(url)?.[1]
}

// Whether an amount prints as non-zero: usd() shows 4 decimals under a cent,
// so anything smaller is float noise. The row and the pane both use it.
export function nonZero(x: number): boolean {
  return Math.abs(x) >= 0.00005
}

// Money: 4 decimals under one cent so tiny amounts don't read as $0.00.
export function usd(x: number): string {
  const digits = Math.abs(x) < 0.01 ? 4 : 2
  return `${x < 0 ? '-' : ''}$${Math.abs(x).toFixed(digits)}`
}

// Time left, like '1d12h13m' (D7). Anything under a minute, or negative, is '<1m'.
export function countdown(ms: number): string {
  if (ms < 60_000) return '<1m'
  const totalMinutes = Math.floor(ms / 60_000)
  const d = Math.floor(totalMinutes / 1440)
  const h = Math.floor(totalMinutes / 60) % 24
  const m = totalMinutes % 60
  const two = (n: number) => String(n).padStart(2, '0')
  if (d > 0) return `${d}d${two(h)}h${two(m)}m`
  if (h > 0) return `${h}h${two(m)}m`
  return `${m}m`
}

// '1 request' / '4 requests'.
function plural(n: number, word: string): string {
  return `${n} ${word}${n === 1 ? '' : 's'}`
}

// The per-turn row (D3). `describe` builds the text inside one model's brackets.
function entries(
  models: TurnCost['main']['models'],
  describe: (m: TurnCost['main']['models'][string]) => string,
): string {
  return Object.entries(models)
    .sort(([an, a], [bn, b]) => b.usd - a.usd || modelName(an).localeCompare(modelName(bn)))
    .map(([id, m]) => `${modelName(id)}: ${describe(m)}`)
    .join('; ')
}

export function row(turn: TurnCost): string {
  const parts = [`~${usd(turn.total)} this turn`]
  if (Object.keys(turn.main.models).length) {
    parts.push(`main ${usd(turn.main.usd)} (${entries(turn.main.models, (m) => plural(m.requests, 'request'))})`)
  }
  if (Object.keys(turn.sub.models).length) {
    const text = entries(turn.sub.models, (m) => `${plural(m.agents.length, 'agent')}, ${plural(m.requests, 'request')}`)
    parts.push(`subagents ${usd(turn.sub.usd)} (${text})`)
  }
  // Shown whenever it prints as non-zero, so the parts always add up to the total.
  if (turn.untracked !== undefined && nonZero(turn.untracked)) {
    parts.push(`untracked ${usd(turn.untracked)}`)
  }
  if (turn.unpriced.length) parts.push(`unpriced: ${turn.unpriced.map(modelName).join(', ')}`)
  return parts.join(' · ')
}

// Colour for a usage percentage: green under 50, amber under 80, red above.
export function percentColor(p: number): 'success' | 'warning' | 'error' {
  return p < 50 ? 'success' : p < 80 ? 'warning' : 'error'
}
