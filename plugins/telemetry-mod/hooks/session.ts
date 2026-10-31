// The mod's saved state, and the session's spend.
//
// Holds the two atoms (named values in `$.state`, the engine's store that
// survives a hot reload but not the end of the process), the functions every
// other file reads and writes them through, and sessionUsd, the session figure
// the band shows. Also copies the session's history to `$.store`, which is
// kept between sessions, so `claude --resume` can bring it back.
// Where it sits: register.tsx writes through these functions; band.tsx (U6)
// and pane.tsx (U7) read through them. They live here rather than in
// register.tsx so those files don't import the file that imports them.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, StateDollar } from 'claude-code'
import type { Snapshot, Turn } from '../types'
import { INITIAL } from './cache'

// How many sessions' histories the store keeps; saving one more deletes the
// one saved longest ago. About 5 KB each, against the store's 4 MiB cap.
export const KEEP_SESSIONS = 50

// What the snapshot reads as before anything has been saved.
const INITIAL_SNAP: Snapshot = {
  model: '', gitDirty: false, correction: 0, limits: [], cache: INITIAL, turnCount: 0, byModel: {},
}

// `atom(ref, initial, { shape })` names one value in $.state. The plugin and
// key must be written out literally (`as const` keeps them as exact strings
// rather than plain `string`), or the validator can't list what the mod
// stores (G1). `shape` is a version tag saved with the value: change it when
// the type changes, and a value saved under the old tag reads as the initial.
const snapAtom = atom({ plugin: 'telemetry-mod', key: 'snap' } as const, INITIAL_SNAP, { shape: 'snap-v3' })
const turnsAtom = atom({ plugin: 'telemetry-mod', key: 'turns' } as const, [] as Turn[], { shape: 'turns-v1' })

// `claude plugin validate` accepts read/update only next to the atom's own
// definition, and follows `$` into another file only through a `function`
// declaration (not an arrow function), so these stay plain functions here.
// `read` inside a ui.render hook also makes the drawing redraw when the value
// changes. `update` re-reads and retries if another write landed in between.
export function readSnap($: StateDollar) {
  return read($, snapAtom)
}

export function updateSnap($: StateDollar, change: (s: Snapshot) => Snapshot) {
  return update($, snapAtom, change)
}

// The saved turns, newest last; the pane's table reads them.
export function readTurns($: StateDollar) {
  return read($, turnsAtom)
}

export function updateTurns($: StateDollar, change: (turns: Turn[]) => Turn[]) {
  return update($, turnsAtom, change)
}

// What the session has cost: Claude Code's own total, plus the correction for
// non-Claude models it prices at the wrong rates (A2).
export function sessionUsd(s: Snapshot): number {
  return (s.ccTotal ?? 0) + s.correction
}

// What is kept in $.store for one session: what the mod adds up turn by turn
// and can't read again from Claude Code. Model, context, limits and git are
// re-read live, and the cache estimate has its own resume rule (cache.ts).
// `v` is a version tag, like an atom's shape: a value under another tag is
// ignored. `savedAt` picks the oldest session to delete.
type History = {
  v: 1
  savedAt: number
  turns: Turn[]
  turnCount: number
  byModel: Record<string, number>
  correction: number
  lastTurn?: number
}

const PREFIX = 'session:'

// Copies the session's history to the store, under the session's id, then
// deletes the oldest sessions past KEEP_SESSIONS. Called after each main turn.
export async function saveHistory($: EngineInterface, now: number): Promise<void> {
  const [id, s, turns] = await Promise.all([$.session.id(), readSnap($), readTurns($)])
  const history: History = {
    v: 1, savedAt: now, turns, turnCount: s.turnCount, byModel: s.byModel, correction: s.correction, lastTurn: s.lastTurn,
  }
  await $.store.set(PREFIX + id, history)

  const keys = (await $.store.keys()).filter((k) => k.startsWith(PREFIX))
  if (keys.length <= KEEP_SESSIONS) return
  const dated = await Promise.all(keys.map(async (k) => ({ k, at: ((await $.store.get(k)) as Partial<History> | undefined)?.savedAt ?? 0 })))
  dated.sort((a, b) => a.at - b.at)
  for (const { k } of dated.slice(0, keys.length - KEEP_SESSIONS)) await $.store.delete(k)
}

// Puts a resumed session's saved history back into $.state, replacing what is
// there. Returns false, changing nothing, when the store has none for this
// session (one run before this version, or a fork, which has a new id).
export async function restoreHistory($: EngineInterface): Promise<boolean> {
  const h = (await $.store.get(PREFIX + (await $.session.id()))) as History | undefined
  if (h?.v !== 1) return false
  await updateTurns($, () => h.turns)
  await updateSnap($, (s) => ({
    ...s, turnCount: h.turnCount, byModel: h.byModel, correction: h.correction, lastTurn: h.lastTurn,
  }))
  return true
}
