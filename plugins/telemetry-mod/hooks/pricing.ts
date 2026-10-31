// What a model request costs, in US dollars.
//
// This file is the mod's single source for prices. It holds a rate table and
// a pure function, priceUsage: no hooks, no state, nothing that talks to
// Claude Code. Where it sits: the turn.step hook (register.tsx, U5) hands each
// request's token counts to ledger.ts, and ledger.ts calls priceUsage to
// price them. Used by: ledger.ts, and the tests in tests/pricing.test.ts.
//
// Sources, all read on 2026-10-29:
// - Anthropic: https://platform.claude.com/docs/en/about-claude/pricing
//   and https://platform.claude.com/docs/en/models/haiku-5-5/overview
// - OpenAI: https://developers.openai.com/api/docs/pricing
//   and the model pages under https://developers.openai.com/api/docs/models/
//   (gpt-6.1-sol, gpt-6-luna) for the long-prompt rule.
// Claude Sonnet 5's $10 output rate was blank on Anthropic's page; it comes
// from secondary sources that agree with each other.
// plugins/telemetry/pricing.json is the old plugin's table; nothing here reads it.

import type { ModelUsage } from 'claude-code'

// Rates for one model, in USD per 1M tokens.
export type Rates = {
  input: number
  cacheRead: number
  output: number
  // A fixed cache-write multiplier for providers whose writes don't follow
  // Claude's 5-minute / 1-hour lifetimes. When it's absent, the write is
  // priced by the lifetime Claude Code is using (CACHE_WRITE_MULTIPLIER).
  cacheWrite?: number
  // A long-prompt price tier: when a request's prompt is longer than
  // aboveInputTokens, the whole request is priced at the raised rates.
  tier?: { aboveInputTokens: number; multiplier: { input: number; output: number } }
}

// GPT models through clodex. OpenAI charges 1.25x input for a cache write
// with its default 30-minute retention, and above 272K prompt tokens doubles
// input and cache rates and raises output 1.5x for the whole request.
const GPT_CACHE_WRITE = 1.25
const GPT_TIER = { aboveInputTokens: 272_000, multiplier: { input: 2, output: 1.5 } }

// Keyed by model id exactly as usage.model reports it. The GPT keys are the
// clodex aliases; the comment beside each says which OpenAI model it runs.
// `Readonly<Record<string, Rates>>` is the type of an object whose keys are
// any string and whose values are Rates, and which code may not change.
export const RATES: Readonly<Record<string, Rates>> = {
  'claude-opus-5-5': { input: 4, cacheRead: 0.2, output: 20 },
  'claude-opus-5': { input: 5, cacheRead: 0.5, output: 25 },
  'claude-sonnet-5-5': { input: 2, cacheRead: 0.1, output: 10 },
  'claude-sonnet-5': { input: 2, cacheRead: 0.2, output: 10 },
  // Haiku 5.5's prompt length counts cache reads and writes too, and every
  // rate (cache reads and writes included) is 5x above 100K.
  'claude-haiku-5-5': {
    input: 0.1, cacheRead: 0.01, output: 0.5,
    tier: { aboveInputTokens: 100_000, multiplier: { input: 5, output: 5 } },
  },
  'claude-haiku-4-5': { input: 1, cacheRead: 0.1, output: 5 },
  'claude-haiku-4-5-20251001': { input: 1, cacheRead: 0.1, output: 5 },
  'claude-fable-5-1': { input: 10, cacheRead: 0.25, output: 50 },
  luna: { input: 0.1, cacheRead: 0.01, output: 0.5, cacheWrite: GPT_CACHE_WRITE, tier: GPT_TIER },   // GPT-6 Luna
  terra: { input: 1, cacheRead: 0.05, output: 5, cacheWrite: GPT_CACHE_WRITE, tier: GPT_TIER },     // GPT-6.1 Terra
  sol: { input: 2, cacheRead: 0.1, output: 10, cacheWrite: GPT_CACHE_WRITE, tier: GPT_TIER },       // GPT-6.1 Sol
  astra: { input: 10, cacheRead: 1, output: 50, cacheWrite: GPT_CACHE_WRITE, tier: GPT_TIER },      // GPT-6 Astra
}


// What a Claude cache write costs, as a multiple of the input rate, for each
// cache lifetime. `as const` keeps the exact keys and values as the type
// instead of widening them to string and number.
export const CACHE_WRITE_MULTIPLIER = { '5m': 1.25, '1h': 2 } as const

// `keyof typeof` turns the object's keys into a union type: '5m' | '1h'.
export type WriteTtl = keyof typeof CACHE_WRITE_MULTIPLIER

// Our price for one request; undefined when the model has no rates.
export function priceUsage(model: string, usage: ModelUsage, ttl: WriteTtl): number | undefined {
  const rates = RATES[model]
  return rates && priceWith(rates, usage, ttl)
}

function priceWith(rates: Rates, usage: ModelUsage, ttl: WriteTtl): number {
  const promptTokens = usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation_input_tokens
  // The tier applies only strictly above its threshold, and then to the
  // whole request: cache reads and writes scale with the input rate.
  const scale = rates.tier && promptTokens > rates.tier.aboveInputTokens
    ? rates.tier.multiplier
    : { input: 1, output: 1 }
  const input = rates.input * scale.input
  const cacheRead = rates.cacheRead * scale.input
  const cacheWrite = input * (rates.cacheWrite ?? CACHE_WRITE_MULTIPLIER[ttl])
  const output = rates.output * scale.output
  return (
    usage.input_tokens * input +
    usage.cache_read_input_tokens * cacheRead +
    usage.cache_creation_input_tokens * cacheWrite +
    usage.output_tokens * output
  ) / 1e6
}
