// The state contract: the shape of everything telemetry-mod saves in
// `$.state`, the engine's store that survives a hot reload of the mod.
//
// Where it sits: register.tsx writes these values, band.tsx (U6) and
// pane.tsx (U7) read them, and session.ts holds the atoms that point at
// them. cache.ts, ledger.ts and format.ts import their data types from here.
//
// Why the data types live here and not in hooks/: `claude plugin validate`
// requires this file to be self-contained (no imports), so the types the
// saved state is built from have to be defined in it.

// The prompt-cache estimate (cache.ts).
// A union type: ttlSource can only be one of these three strings, so a typo fails to compile.
//   assumed — the 1h default, nothing seen yet
//   learned — worked out from the gap between two requests
//   switch  — told to us by a model switch, so never overridden by learning
// Fields ending in `?` may be missing (undefined).
export type CacheState = {
  model?: string      // session model the estimate is for
  ttlMs: number       // 3_600_000 or 300_000
  ttlSource: 'assumed' | 'learned' | 'switch'
  lastAt?: number     // ms epoch of the last main-thread request that read or wrote the cache
  hitRatio?: number   // that request's cache reads / prompt tokens, 0..1
}

// The cost of one thread (main or subagents) in a turn, with a per-model
// breakdown. `agents` lists the distinct subagent ids that used the model.
export type Group = { usd: number; models: Record<string, { usd: number; requests: number; agents: string[] }> }

// One turn's cost (ledger.ts).
export type TurnCost = {
  total: number                  // main.usd + sub.usd + (untracked ?? 0)
  main: Group
  sub: Group
  untracked?: number             // undefined when Claude Code's total was unavailable, or the turn used a non-Claude model
  correction: number             // in a turn with a non-Claude model: our total - Claude Code's delta; else 0
  unpriced: string[]             // model ids with no rates, sorted, unique
}

// One rate-limit window, e.g. kind 'five_hour' at 23.5 percent.
export type Limit = { kind: string; percent: number; resetsAt?: string }

// The session as the band and the pane show it.
export type Snapshot = {
  model: string                  // display name, e.g. 'Opus 5.5'; '' until the first refresh
  effort?: string
  git?: string                   // branch, or short sha when detached
  gitDirty: boolean
  ctxPercent?: number
  ctxTokens?: number
  ccTotal?: number               // Claude Code's session total (session.usage / session.measure)
  correction: number             // sum of TurnCost.correction this session (A2)
  lastTurn?: number              // last TurnCost.total
  limits: Limit[]
  cache: CacheState
  startedAt?: number
}

// A finished turn as the pane lists it: its cost, its number in the session
// (1, 2, ...) and when it ended. `&` combines two object types into one.
export type Turn = TurnCost & { index: number; doneAt: number }

// `declare module` adds to the engine's own type list: this tells TypeScript
// (and the validator) which keys telemetry-mod keeps in $.state.
// `Shaped<T>` means the value is saved with a shape tag (see session.ts), so a
// value saved by an older version of the mod reads as absent instead of
// arriving in the wrong shape.
declare module 'claude-code' {
  interface PluginState {
    'telemetry-mod': { snap: Shaped<Snapshot>; turns: Shaped<Turn[]> }
  }
}
