// The running cost of the current turn, split by thread and model.
//
// A Ledger collects every model request of one turn (main thread and
// subagents alike), priced by pricing.ts. When the turn ends, close() compares
// that with how much Claude Code's own session total grew, so spend this file
// can't see (fast mode, web search fees, unknown models) shows up as
// "untracked" instead of disappearing. Pure: no hooks, no state.
// Where it sits: register.tsx (U5) keeps one Ledger in a module variable,
// adds to it from the turn.step hook and closes it in turn.complete; format.ts
// (U4) turns the TurnCost into the per-turn row. Used by: register.tsx and
// tests/ledger.test.ts.

import type { ModelUsage } from 'claude-code'
// `type WriteTtl` imports a type only; it disappears from the compiled code.
import { chargedByClaudeCode, priceUsage, type WriteTtl } from './pricing'

// One model request. agentId is undefined on the main thread and a
// subagent's id otherwise; the `?` makes the field optional.
export type Request = { model: string; agentId?: string; usage: ModelUsage }

// The cost of one thread (main or subagents) in a turn, with a per-model
// breakdown. `agents` lists the distinct subagent ids that used the model.
export type Group = { usd: number; models: Record<string, { usd: number; requests: number; agents: string[] }> }

export type TurnCost = {
  total: number                  // main.usd + sub.usd + (untracked ?? 0)
  main: Group
  sub: Group
  untracked?: number             // undefined when Claude Code's total was unavailable
  correction: number             // sum of (our price - Claude Code's charge) for priced non-claude requests
  unpriced: string[]             // model ids with no rates, sorted, unique
}

export class Ledger {
  private main = emptyGroup()
  private sub = emptyGroup()
  private tracked = 0            // what Claude Code charged for the requests we priced
  private correction = 0
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

    const charged = chargedByClaudeCode(request.model, request.usage, ttl)
    // Only requests we priced count as tracked. Claude Code still charges an
    // unpriced non-claude model (at the fallback rates), and leaving that out
    // of tracked lets it show up in untracked instead of vanishing.
    if (ours !== undefined && charged !== undefined) this.tracked += charged
    // Claude Code prices non-claude models at the fallback model's rates, so
    // its session total is off by this much; the session figure adds it back (A2).
    if (ours !== undefined && charged !== undefined && !request.model.startsWith('claude-')) {
      this.correction += ours - charged
    }
  }

  // Ends the turn. claudeCodeDelta is how much Claude Code's session total
  // grew over the turn, or undefined when it wasn't available. Returns the
  // turn's cost and starts a fresh turn.
  close(claudeCodeDelta: number | undefined): TurnCost {
    const untracked = claudeCodeDelta === undefined ? undefined : claudeCodeDelta - this.tracked
    const turn: TurnCost = {
      total: this.main.usd + this.sub.usd + (untracked ?? 0),
      main: this.main,
      sub: this.sub,
      untracked,
      correction: this.correction,
      unpriced: [...this.unpriced].sort(),
    }
    this.main = emptyGroup()
    this.sub = emptyGroup()
    this.tracked = 0
    this.correction = 0
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
