// cache.ts — estimates whether the prompt cache is warm, how much of the last
// prompt it served, and how long the entry has left.
//
// Why it exists: a warm cache makes the next request cheap (reads cost a tenth of
// normal input), a cold one pays to rebuild it. The band and the /telemetry pane
// show this so you know what your next prompt will cost. The API never reports the
// cache lifetime (5 minutes or 1 hour), so this file starts by assuming 1 hour and
// learns the real value from the gaps between requests.
//
// Flow: register.tsx calls observe() for each main-thread request, switched() on a
// model switch and resumed() when a session resumes. band.tsx and pane.tsx call
// view() to render. pricing.ts's callers use writeTtl() to price cache writes.
//
// Every function is pure: it takes the old CacheState and returns a new one, and
// never changes its input.

import type { ModelUsage } from 'claude-code'
// CacheState describes saved state, so it lives in the state contract.
import type { CacheState } from '../types'

const FIVE_MIN = 300_000
const ONE_HOUR = 3_600_000

// Default lifetime is 1 hour until evidence says otherwise (A1).
export const INITIAL: CacheState = { ttlMs: ONE_HOUR, ttlSource: 'assumed' }

// Called for each main-thread request. Records when the cache was last touched and
// how much of the prompt it served, and learns the lifetime from the gap since then.
export function observe(s: CacheState, model: string, usage: ModelUsage, at: number): CacheState {
  const read = usage.cache_read_input_tokens
  const created = usage.cache_creation_input_tokens
  // No cache activity says nothing about the cache: leave the state alone.
  if (read + created === 0) return s

  // A different model has its own cache. Keep what we know about the lifetime,
  // drop the timing (lastAt, hitRatio) that belonged to the old model.
  const base: CacheState = s.model !== undefined && s.model !== model
    ? { ...INITIAL, ttlMs: s.ttlMs, ttlSource: s.ttlSource, model }
    : s

  let { ttlMs, ttlSource } = base
  // After a model switch the lifetime is known, so learning is off.
  if (base.lastAt !== undefined && ttlSource !== 'switch') {
    const gap = at - base.lastAt
    if (gap > FIVE_MIN && read > 0) {
      // The entry was still readable after more than 5 minutes: it's a 1h cache.
      ttlMs = ONE_HOUR
      ttlSource = 'learned'
    } else if (gap > FIVE_MIN && gap < ONE_HOUR && read === 0 && created > 0 && ttlSource === 'assumed') {
      // Rewritten from scratch after 5 to 60 minutes: the old entry had expired.
      ttlMs = FIVE_MIN
      ttlSource = 'learned'
    }
  }

  const promptTokens = usage.input_tokens + read + created
  return { ...base, model, ttlMs, ttlSource, lastAt: at, hitRatio: read / promptTokens }
}

// Called when the user switches model. The new model's cache is cold (no lastAt),
// and the switch tells us its lifetime.
export function switched(s: CacheState, toModel: string, ttl: '5m' | '1h'): CacheState {
  return { model: toModel, ttlMs: ttl === '5m' ? FIVE_MIN : ONE_HOUR, ttlSource: 'switch' }
}

// Called when a session resumes. Claude Code may say how long ago the last response
// was, or that the cache has probably expired; either beats our own timing.
export function resumed(
  s: CacheState,
  secondsSinceLastResponse: number | undefined,
  likelyExpired: boolean | undefined,
  now: number,
): CacheState {
  if (likelyExpired === true) {
    // `...rest` collects every field except lastAt, so the result has no lastAt: cold.
    const { lastAt, ...rest } = s
    return rest
  }
  if (secondsSinceLastResponse !== undefined) return { ...s, lastAt: now - secondsSinceLastResponse * 1000 }
  return s
}

// What the UI shows. `as const` keeps `kind` as the exact string, so callers can
// switch on it and TypeScript knows which other fields exist.
export function view(s: CacheState, now: number) {
  if (s.lastAt === undefined && s.hitRatio === undefined) return { kind: 'none' as const }
  if (s.lastAt === undefined || s.lastAt + s.ttlMs <= now) return { kind: 'cold' as const }
  return {
    kind: 'warm' as const,
    hitRatio: s.hitRatio,
    leftMs: s.lastAt + s.ttlMs - now,
    estimated: s.ttlSource === 'assumed',   // true while the lifetime is still our default guess
  }
}

// Cache writes are priced by lifetime; pricing.ts wants '5m' or '1h'.
export function writeTtl(s: CacheState): '5m' | '1h' {
  return s.ttlMs === FIVE_MIN ? '5m' : '1h'
}
