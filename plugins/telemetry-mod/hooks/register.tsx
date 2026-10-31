// Entry point of the telemetry-mod plugin. Claude Code loads this file
// (hooks/hooks.json names it) and calls `register` once, handing it `on`,
// which adds hooks: functions Claude Code calls when something happens.
//
// How to read this mod:
//   register.tsx        the hooks: when Claude Code calls us, and what we save (this file)
//   session.ts          the saved state (atoms), its copy for --resume, and the session's spend
//   ledger.ts           one turn's cost, request by request
//   pricing.ts          the rates, and the price of one request
//   cache.ts            the prompt-cache estimate
//   format.ts           the strings the row, band and pane show
//   ../types/index.d.ts the shape of the saved state
//   band.tsx            what the band shows
//   pane.tsx            what the /telemetry pane shows, and how many turns it lists
//
// Every hook has the shape `($, e, next)`: `$` is how the mod calls Claude
// Code, `e` is the event, and `next(e)` passes the event on to the rest of the
// chain (other plugins, then Claude Code itself) and returns its result. A
// hook that forgets `next(e)` swallows the event.

import type { EngineInterface, Register, SessionContextBreakdown, SessionRateLimit, Timer } from 'claude-code'
import type { ContextView, Limit, TurnCost } from '../types'
import { bandTree } from './band'
import { cleared, observe, resumed, switched, writeTtl } from './cache'
import { modelName, repoName, row } from './format'
import { Ledger } from './ledger'
import { BIGGEST_ITEMS, PANE_COLUMNS, TABLE_TURNS, paneTree } from './pane'
import { readSnap, readTurns, restoreHistory, saveHistory, updateSnap, updateTurns } from './session'

// How often model, git, context, limits and cost are re-read, in ms (A4).
const REFRESH_MS = 30_000
// The id the pane is opened, closed and drawn under.
const PANE_ID = 'telemetry'

// Module variables. A hot reload of the mod resets them, while $.state
// survives (G4), so only the in-flight turn lives here: a reload mid-turn
// loses that turn's split, and session.start re-reads the baseline.
let ledger = new Ledger()
// Claude Code's session total when the last main turn ended.
let baseline: number | undefined
let timer: Timer | undefined

const ignore = () => undefined

// The context figures, emptied. After /clear Claude Code reports no context
// fill until the next response, and refresh and session.measure keep the old
// value when none is reported, so it has to be dropped by hand.
const NO_CONTEXT = { ctxPercent: undefined, ctxTokens: undefined, context: undefined }

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

// Cuts a context breakdown down to what the pane draws: the categories that
// fill the window, biggest first, and the biggest few memory files, MCP tools
// (the ones loaded), agents and skills, merged into one list.
function contextView(b: SessionContextBreakdown): ContextView {
  const items = [
    ...b.memoryFiles.map((m) => ({ kind: 'Memory', name: m.path, tokens: m.tokens })),
    ...b.mcpTools.filter((t) => t.isLoaded).map((t) => ({ kind: 'MCP', name: `${t.serverName}: ${t.name}`, tokens: t.tokens })),
    ...b.agents.map((a) => ({ kind: 'Agent', name: a.agentType, tokens: a.tokens })),
    ...(b.skills?.skillFrontmatter ?? []).map((k) => ({ kind: 'Skill', name: k.name, tokens: k.tokens })),
  ]
  return {
    categories: b.categories
      .filter((c) => c.kind === 'used')
      .map(({ name, tokens, color }) => ({ name, tokens, color }))
      .sort((a, c) => c.tokens - a.tokens),
    items: items.sort((a, c) => c.tokens - a.tokens).slice(0, BIGGEST_ITEMS),
  }
}

// Adds one turn's spend per model (main thread and subagents) to the session's
// running totals, which the pane's By model section shows.
function addSpend(spend: Record<string, number>, turn: TurnCost): Record<string, number> {
  const next = { ...spend }
  for (const group of [turn.main, turn.sub]) {
    for (const [id, m] of Object.entries(group.models)) next[id] = (next[id] ?? 0) + m.usd
  }
  return next
}

// The agent states that mean "still working": not started, mid-turn, or held
// on background work. `idle` and the ended states are not.
const BUSY: ReadonlySet<string> = new Set(['pending', 'running', 'waiting'])

// Whether any background subagent is still working. Teammates are left out:
// one can run for the whole session, which would hide every row. A failed
// list counts as not busy, so the row prints.
async function agentsBusy($: EngineInterface): Promise<boolean> {
  const agents = await settled($.agent.list())
  return agents?.some((a) => a.teammateId === undefined && BUSY.has(a.status)) ?? false
}

// Re-reads model, git, context, limits and cost into the snapshot. Runs every
// 30 s, after a model switch and after each turn (A4). Never throws.
// While the pane is open it also asks for the context breakdown, counted as
// /context counts it (`full`, 24 ms in the one live sample). The cheaper
// `summary` estimate is not used: its total was right but it counted the tool
// schemas 12K too high and Messages 12K too low. A closed pane costs nothing.
async function refresh($: EngineInterface): Promise<void> {
  const paneOpen = (await settled($.ui.panes()))?.some((pane) => pane.id === PANE_ID) ?? false
  const [model, usage, branch, dirty, origin] = await Promise.all([
    settled($.session.model()),
    settled($.session.usage(paneOpen ? { breakdown: 'full' } : undefined)),
    settled(git($, 'branch', '--show-current').then((b) => b || git($, 'rev-parse', '--short', 'HEAD'))),
    settled(git($, 'status', '--porcelain')),
    settled(git($, 'remote', 'get-url', 'origin')),
  ])
  // updateSnap applies the function to the latest saved value, so the timer
  // and a hook can't undo each other's changes.
  await updateSnap($, (s) => ({
    ...s,
    model: model === undefined ? s.model : modelName(model),
    repo: origin === undefined ? s.repo : repoName(origin),
    git: branch || s.git,
    gitDirty: dirty === undefined ? s.gitDirty : dirty !== '',
    ctxPercent: usage?.context.percent ?? s.ctxPercent,
    ctxTokens: usage?.context.tokens ?? s.ctxTokens,
    limits: usage ? limits(usage.rateLimits) : s.limits,
    ccTotal: usage?.cost?.usd ?? s.ccTotal,
    startedAt: usage?.startedAt ?? s.startedAt,
    // Kept as it was while the pane is closed or the call failed.
    context: usage?.context.breakdown ? contextView(usage.context.breakdown) : s.context,
  })).catch(ignore)
}

export const register: Register = (on) => {
  // Called once when the session starts (and again after a hot reload).
  // Starts the 30 s refresh and records Claude Code's total so the first
  // turn's cost can be measured from it. Also declares the /telemetry command,
  // which lists it in the typeahead; the command.run hook below serves it.
  on('session.start', async ($, e, next) => {
    await settled($.command.register({ name: PANE_ID, description: 'Toggle the telemetry details pane.' }))
    timer?.cancel()
    timer = $.clock.every(REFRESH_MS, () => void refresh($))
    baseline = (await settled($.session.usage()))?.cost?.usd
    // `void` starts it without waiting: git can take up to 2 s, and the
    // session shouldn't wait for the band.
    void refresh($)
    return next(e)
  })

  // Called when a session starts: fresh, from an older transcript, after
  // /clear or after /compact. On /clear, everything kept from the old session
  // is dropped; on /compact, the old cache timing. On resume, the session's
  // history comes back from the store (session.ts). On resume or fork, Claude
  // Code says how long ago the last response was, which dates the cache.
  // `classic.*` hooks can hold Claude Code up, so `.catch` passes the event on
  // if this one fails (G2).
  on('classic.SessionStart', async ($, e, next) => {
    // /clear starts a new session in the same process: Claude Code's cost
    // restarts at 0 and session.start does not fire again, so what the mod
    // kept from the old session must be dropped here.
    if (e.source === 'clear') {
      baseline = (await settled($.session.usage()))?.cost?.usd
      ledger = new Ledger()
      await updateTurns($, () => [])
      await updateSnap($, (s) => ({
        ...s, ...NO_CONTEXT, ccTotal: baseline, correction: 0, lastTurn: undefined, turnCount: 0, byModel: {}, cache: cleared(s.cache),
      }))
      void refresh($)
    }
    // /compact replaces the conversation with a summary. The session, its cost
    // and its history carry on; the cache timing describes the old
    // conversation. The context figures are left alone: Claude Code reports a
    // fill right after a compact and corrects it on the next response.
    // baseline and the ledger stay: auto-compact can run mid-turn, and the
    // turn's requests still count.
    if (e.source === 'compact') {
      await updateSnap($, (s) => ({ ...s, cache: cleared(s.cache) }))
      void refresh($)
    }
    if (e.source === 'resume') await restoreHistory($).catch(ignore)
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
    // While background agents are still working, print no row: each agent's
    // result wakes the model for a turn of its own, which would add a row each.
    // The ledger stays open and the baseline unchanged, so the row printed once
    // they have all finished covers these turns too.
    if (await agentsBusy($)) return answer
    const cc = (await settled($.session.usage()))?.cost?.usd
    const delta = cc !== undefined && baseline !== undefined ? cc - baseline : undefined
    baseline = cc ?? baseline
    const turn = ledger.close(delta)

    const now = await $.clock.now()
    await updateTurns($, (turns) =>
      // `.at(-1)` is the last element; `.slice(-n)` keeps the last n, which is
      // all the pane's table lists.
      [...turns, { ...turn, index: (turns.at(-1)?.index ?? 0) + 1, doneAt: now }].slice(-TABLE_TURNS),
    ).catch(ignore)
    await updateSnap($, (s) => ({
      ...s,
      lastTurn: turn.total,
      correction: s.correction + turn.correction,
      ccTotal: cc ?? s.ccTotal,
      turnCount: s.turnCount + 1,
      byModel: addSpend(s.byModel, turn),
    })).catch(ignore)
    // A copy that outlives the process, for `claude --resume`.
    await saveHistory($, now).catch(ignore)
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

  // Called when the person types /telemetry. Closes the pane if it is open,
  // opens it if not. The answer is the text printed in the transcript. `focus`
  // is left out so the prompt keeps the keyboard. Whether the pane docks beside
  // the chat or sits above the prompt is the terminal layout's choice.
  on('command.run', { command: 'telemetry' }, async ($) => {
    const isOpen = (await $.ui.panes()).some((pane) => pane.id === PANE_ID)
    if (isOpen) {
      await $.ui.close({ id: PANE_ID })
      return { text: 'Telemetry pane closed.' }
    }
    await $.ui.open({ id: PANE_ID, title: 'Telemetry', columns: PANE_COLUMNS })
    // Now that the pane is open, fetch its context breakdown without waiting for the 30 s refresh.
    void refresh($)
    return { text: 'Telemetry pane opened.' }
  })

  // The pane's body. Like the band, reading the saved state here makes Claude
  // Code redraw the pane whenever it changes. The context window comes from
  // Claude Code directly, as the snapshot doesn't keep it.
  on('ui.render', { component: 'Pane', requestId: PANE_ID }, async ($, e) => {
    const [s, turns, usage, now] = await Promise.all([
      readSnap($),
      readTurns($),
      settled($.session.usage()),
      $.clock.now(),
    ])
    return paneTree($.ui.resolve(e), s, turns, now, {
      bodyColumns: e.props.bodyColumns,
      rows: e.props.scroll.bodyRows,
      windowTokens: usage?.context.window,
    })
  })
}
