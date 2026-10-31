// The running cost of the current turn, split by thread and model.
//
// A Ledger collects every model request of one turn (main thread and
// subagents alike), priced by pricing.ts. When the turn ends, close() compares
// that with how much Claude Code's own session total grew, so spend this file
// can't see (fast mode, web search fees, unknown models, requests the hooks
// never see) shows up as "untracked" instead of disappearing. Except in a turn
// with a non-Claude model: there Claude Code's total includes its own price
// for that model, which can't be predicted, so our prices stand in for it.
// Pure: no hooks, no state.
// Where it sits: register.tsx (U5) keeps one Ledger in a module variable,
// adds to it from the turn.step hook and closes it in turn.complete; format.ts
// (U4) turns the TurnCost into the per-turn row. Used by: register.tsx and
// tests/ledger.test.ts.

import type { ModelUsage } from 'claude-code'
// `type WriteTtl` imports a type only; it disappears from the compiled code.
import { priceUsage, type WriteTtl } from './pricing'
// Group and TurnCost describe saved state, so they live in the state contract.
import type { Group, TurnCost } from '../types'

// One model request. agentId is undefined on the main thread and a
// subagent's id otherwise; the `?` makes the field optional.
export type Request = { model: string; agentId?: string; usage: ModelUsage }

export class Ledger {
  private main = emptyGroup()
  private sub = emptyGroup()
  private unpriced = new Set<string>()
  private requests = 0

  // Adds one request. ttl is the cache lifetime the estimator believes in
  // now (A1); it's applied here because close() doesn't know it.
  add(request: Request, ttl: WriteTtl): void {
    const group = request.agentId === undefined ? this.main : this.sub
    // `??=` assigns only when the left side is undefined: the first request
    // for a model creates its entry.
    const entry = group.models[request.model] ??= { usd: 0, requests: 0, agents: [] }
    entry.requests += 1
    this.requests += 1
    if (request.agentId !== undefined && !entry.agents.includes(request.agentId)) {
      entry.agents.push(request.agentId)
    }

    const ours = priceUsage(request.model, request.usage, ttl)
    if (ours === undefined) {
      this.unpriced.add(request.model)
    } else {
      entry.usd += ours
      group.usd += ours
    }
  }

  // Ends the turn. claudeCodeDelta is how much Claude Code's session total
  // grew over the turn, or undefined when it wasn't available. Returns the
  // turn's cost and starts a fresh turn.
  close(claudeCodeDelta: number | undefined): TurnCost {
    const ours = this.main.usd + this.sub.usd
    const models = [...Object.keys(this.main.models), ...Object.keys(this.sub.models)]
    const base = { main: this.main, sub: this.sub, unpriced: [...this.unpriced].sort() }
    let turn: TurnCost
    if (models.some((m) => !m.startsWith('claude-'))) {
      // Claude Code prices models it doesn't know at rates we can't predict
      // (Opus 5.5's in one live session, about nothing in the next), so its
      // total says nothing reliable about this turn. Our prices stand in, and
      // `correction` swaps Claude Code's amount for ours in the session figure
      // (A2). Spend the hooks can't see goes uncounted in this turn.
      const correction = claudeCodeDelta === undefined ? 0 : ours - claudeCodeDelta
      turn = { ...base, total: ours, untracked: undefined, correction }
    } else {
      const untracked = claudeCodeDelta === undefined ? undefined : claudeCodeDelta - ours
      turn = { ...base, total: ours + (untracked ?? 0), untracked, correction: 0 }
    }
    this.main = emptyGroup()
    this.sub = emptyGroup()
    this.unpriced = new Set()
    this.requests = 0
    return turn
  }

  // True when no request has been added since the last close().
  isEmpty(): boolean {
    return this.requests === 0
  }
}

function emptyGroup(): Group {
  return { usd: 0, models: {} }
}
