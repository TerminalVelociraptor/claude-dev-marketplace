// Entry point of the telemetry-mod plugin. Claude Code loads this file
// (hooks/hooks.json names it) and calls `register` once, handing it `on`,
// which adds hooks: functions Claude Code calls when something happens.
//
// How to read this mod:
//   register.tsx        the hooks: when Claude Code calls us, and what we save (this file)
//   session.ts          the saved state (atoms) and the session's spend
//   ledger.ts           one turn's cost, request by request
//   pricing.ts          the rates, and the price of one request
//   cache.ts            the prompt-cache estimate
//   format.ts           the strings the row, band and pane show
//   ../types/index.d.ts the shape of the saved state
//   band.tsx            what the band shows
//   pane.tsx (U7) draws from the saved state.
//
// Every hook has the shape `($, e, next)`: `$` is how the mod calls Claude
// Code, `e` is the event, and `next(e)` passes the event on to the rest of the
// chain (other plugins, then Claude Code itself) and returns its result. A
// hook that forgets `next(e)` swallows the event.

import type { EngineInterface, Register, SessionRateLimit, Timer } from 'claude-code'
import type { Limit } from '../types'
import { bandTree } from './band'
import { observe, resumed, switched, writeTtl } from './cache'
import { modelName, row } from './format'
import { Ledger } from './ledger'
import { readSnap, updateSnap, updateTurns } from './session'

const REFRESH_MS = 30_000 // A4
const KEEP_TURNS = 200 // A3

// Module variables. A hot reload of the mod resets them, while $.state
// survives (G4), so only the in-flight turn lives here: a reload mid-turn
// loses that turn's split, and session.start re-reads the baseline.
let ledger = new Ledger()
// Claude Code's session total when the last main turn ended.
let baseline: number | undefined
let timer: Timer | undefined

const ignore = () => undefined

// Resolves to undefined instead of rejecting, so one failing source doesn't
// stop the others.
function settled<T>(p: Promise<T>): Promise<T | undefined> {
  return p.catch(ignore)
}

async function git($: EngineInterface, ...args: string[]): Promise<string | undefined> {
  const ran = await $.process.run(['git', ...args], { timeoutMs: 2000 })
  return ran.exitCode === 0 ? ran.stdout.trim() : undefined
}

function limits(rateLimits: SessionRateLimit[]): Limit[] {
  return rateLimits.map((l) => ({ kind: l.kind, percent: l.percentUsed, resetsAt: l.resetsAt }))
}

// Re-reads model, git, context, limits and cost into the snapshot. Runs every
// 30 s, after a model switch and after each turn (A4). Never throws.
async function refresh($: EngineInterface): Promise<void> {
  const [model, usage, branch, dirty] = await Promise.all([
    settled($.session.model()),
    settled($.session.usage()),
    settled(git($, 'branch', '--show-current').then((b) => b || git($, 'rev-parse', '--short', 'HEAD'))),
    settled(git($, 'status', '--porcelain')),
  ])
  // updateSnap applies the function to the latest saved value, so the timer
  // and a hook can't undo each other's changes.
  await updateSnap($, (s) => ({
    ...s,
    model: model === undefined ? s.model : modelName(model),
    git: branch || s.git,
    gitDirty: dirty === undefined ? s.gitDirty : dirty !== '',
    ctxPercent: usage?.context.percent ?? s.ctxPercent,
    ctxTokens: usage?.context.tokens ?? s.ctxTokens,
    limits: usage ? limits(usage.rateLimits) : s.limits,
    ccTotal: usage?.cost?.usd ?? s.ccTotal,
    startedAt: usage?.startedAt ?? s.startedAt,
  })).catch(ignore)
}

export const register: Register = (on) => {
  // Called once when the session starts (and again after a hot reload).
  // Starts the 30 s refresh and records Claude Code's total so the first
  // turn's cost can be measured from it.
  on('session.start', async ($, e, next) => {
    timer?.cancel()
    timer = $.clock.every(REFRESH_MS, () => void refresh($))
    baseline = (await settled($.session.usage()))?.cost?.usd
    // `void` starts it without waiting: git can take up to 2 s, and the
    // session shouldn't wait for the band.
    void refresh($)
    return next(e)
  })

  // Called when a session starts from an older transcript. On resume or fork,
  // Claude Code says how long ago the last response was, which dates the cache.
  // `classic.*` hooks can hold Claude Code up, so `.catch` passes the event on
  // if this one fails (G2).
  on('classic.SessionStart', async ($, e, next) => {
    if (e.source === 'resume' || e.source === 'fork') {
      const now = await $.clock.now()
      await updateSnap($, (s) => ({
        ...s,
        cache: resumed(s.cache, e.seconds_since_last_response, e.prompt_cache_likely_expired, now),
      }))
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  // Called after /model (or any other switch). Shows the new model and its
  // cache lifetime at once, then refreshes the rest (D10).
  on('classic.PostModelSwitch', async ($, e, next) => {
    await updateSnap($, (s) => ({
      ...s,
      model: modelName(e.to_model),
      cache: switched(s.cache, e.to_model, e.cache_ttl),
    }))
    void refresh($)
    return next(e)
  }).catch(($, e, next) => next(e))

  // Called for every model request, on the main thread and in subagents.
  // `async function*` makes this an async generator: the request's response
  // streams through it, and `yield* next(e)` passes the stream on and returns
  // the finished response (G3). Work after that point delays the turn, so it
  // stays short: price the request, and on the main thread note the effort
  // and what the cache did. Subagents write the cache with a 5-minute
  // lifetime (seen in a live session: Claude Code charged a subagent's write
  // at 1.25x), so only main-thread requests use the learned lifetime.
  on('turn.step', async function* ($, e, next) {
    const response = yield* next(e)
    const usage = response.usage
    if (!usage) return response

    const model = usage.model || e.model
    const { cache } = await readSnap($)
    ledger.add({ model, agentId: e.agentId, usage }, e.agentId === undefined ? writeTtl(cache) : '5m')

    if (e.agentId === undefined) {
      const now = await $.clock.now()
      await updateSnap($, (s) => ({
        ...s,
        effort: e.effort === undefined ? s.effort : String(e.effort),
        cache: observe(s.cache, model, usage, now),
      })).catch(ignore)
    }
    return response
  })

  // Called when a turn ends, on the main thread and in subagents. At the end of
  // a main turn: compare Claude Code's total with the last one, close the
  // ledger, save the turn, and return the row, which Claude Code draws under
  // the answer. A subagent's turn ending is not the end of the main turn, so it
  // leaves the ledger open.
  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)

    const answer = await next(e)
    const cc = (await settled($.session.usage()))?.cost?.usd
    const delta = cc !== undefined && baseline !== undefined ? cc - baseline : undefined
    baseline = cc ?? baseline
    const turn = ledger.close(delta)

    const now = await $.clock.now()
    await updateTurns($, (turns) =>
      // `.at(-1)` is the last element; `.slice(-200)` keeps the last 200.
      [...turns, { ...turn, index: (turns.at(-1)?.index ?? 0) + 1, doneAt: now }].slice(-KEEP_TURNS),
    ).catch(ignore)
    await updateSnap($, (s) => ({
      ...s,
      lastTurn: turn.total,
      correction: s.correction + turn.correction,
      ccTotal: cc ?? s.ccTotal,
    })).catch(ignore)
    void refresh($)

    // `...answer` copies the answer's fields; `text` replaces its text.
    return { ...answer, text: row(turn) }
  })

  // Called when Claude Code's context, rate-limit or cost figures change.
  on('session.measure', async ($, e, next) => {
    await updateSnap($, (s) => ({
      ...s,
      ctxPercent: e.context.percent ?? s.ctxPercent,
      ctxTokens: e.context.tokens ?? s.ctxTokens,
      limits: limits(e.rateLimits),
      ccTotal: e.cost?.usd ?? s.ccTotal,
    })).catch(ignore)
    return next(e)
  })

  // The band above the prompt. Reading the snapshot inside a ui.render hook
  // makes Claude Code redraw the band whenever the snapshot changes. Nothing
  // to show before the first refresh, and a survey takes the band's place
  // while it is up.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const s = await readSnap($)
    if (s.model === '') return next(e)
    return bandTree($.ui.resolve(e), s, await $.clock.now())
  })
}
