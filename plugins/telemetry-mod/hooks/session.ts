// The mod's saved state, and the session's spend.
//
// Holds the two atoms (named values in `$.state`, the engine's store that
// survives a hot reload), the functions every other file reads and writes
// them through, and sessionUsd, the session figure the band shows.
// Where it sits: register.tsx writes through these functions; band.tsx (U6)
// and pane.tsx (U7) read through them. They live here rather than in
// register.tsx so those files don't import the file that imports them.

import { atom, read, update } from 'claude-code'
import type { StateDollar } from 'claude-code'
import type { Snapshot, Turn } from '../types'
import { INITIAL } from './cache'

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
