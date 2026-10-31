# telemetry-mod

Cost and session telemetry for Claude Code, built as a mod (in-process hooks). Replaces what the `telemetry` plugin does with a status line and transcript parsing.

## What it shows

- **Status band** above the prompt, always on, in a bordered box:
  `Opus 5.5 · high · main*`
  `ctx 64% (128K) · $0.28 / $3.21 · 5h 42% ↻1h12m · 7d 18% ↻1d12h13m · cache 91% 23m left`
- **A cost row after every turn:**
  `~$0.28 this turn · main $0.20 (Opus 5.5: 4 requests) · subagents $0.05 (Terra: 1 agent, 3 requests; Haiku 5.5: 2 agents, 4 requests) · untracked $0.03`
- **`/telemetry`** toggles a pane, docked beside the chat in a wide terminal or above the prompt in a narrow one. It shows the session's spend, rate limits, cache, cost by model, recent turns and what fills the context.

## How costs are worked out

- Each model request's token usage comes from Claude Code (`turn.step`), main thread and subagents alike, and is priced from `hooks/pricing.ts`.
- **untracked** is Claude Code's own cost total for the turn minus what the mod priced: requests the mod never sees (Claude Code makes a small one after each turn, and helpers such as titles or compaction), plus anything the mod can't price exactly (fast mode). It shows whenever it prints as non-zero.
- In a turn that used a model Claude Code doesn't know (the clodex GPT models), Claude Code's charge isn't reliable, so the row shows the mod's prices alone and no `untracked`. Spend the mod can't see in such a turn is not counted.
- Subagents write the cache with a 5-minute lifetime, the main thread with the learned one, and the mod prices them that way.
- While background agents are still working, a turn prints no row; its spend goes into the row printed once they have all finished.

## Cache estimate

The cache lifetime is learned: a cache hit after more than 5 minutes means 1 hour; a model switch reports it directly. Until then it assumes 1 hour and marks the countdown `(est.)`. After a model switch, or when no reply has come yet, the band shows `cache cold`; resuming a session uses Claude Code's own "likely expired" flag.

## Install

`/plugin install telemetry-mod@dev-toolkits`, then `/reload-plugins`. No setup step and no settings changes.

To work on it from this repo, start Claude Code with `claude --plugin-dir plugins/telemetry-mod`. A marketplace install runs a cached copy, and only `--plugin-dir` writes the type files `tsc` needs into `.claude-plugin/types/`.

## How the code fits together

A mod is TypeScript that Claude Code runs inside itself. `hooks/hooks.json` names the entry file; Claude Code calls its `register` function, which subscribes to events with `on(event, hook)`. Each hook receives `$` (everything the mod can ask Claude Code for) and `e` (the event's data), and calls `next(e)` to let Claude Code carry on.

Start at `hooks/register.tsx`; its header maps every file, and each hook's comment says when Claude Code calls it.

## Changing it

- Rates: `hooks/pricing.ts` (`RATES`, keyed by the model id Claude Code reports). An unknown model shows as `unpriced: …` in the row.
- Test: `claude plugin test plugins/telemetry-mod`
- Validate: `claude plugin validate plugins/telemetry-mod`
- Type-check: `tsc -p plugins/telemetry-mod`

### Tweakable parameters

Named constants (and two functions) near the top of each file; the comment beside each says what it sets.

| File | Parameters |
|---|---|
| `hooks/pane.tsx` | `TABLE_TURNS`, `BIGGEST_ITEMS`, `PANE_COLUMNS`, `MODEL_BAR_CELLS`, `LIMIT_BAR_CELLS`, `MODEL_COLORS` |
| `hooks/register.tsx` | `REFRESH_MS` |
| `hooks/session.ts` | `KEEP_SESSIONS` |
| `hooks/cache.ts` | `FIVE_MIN`, `ONE_HOUR` |
| `hooks/pricing.ts` | `RATES`, `CACHE_WRITE_MULTIPLIER`, `GPT_CACHE_WRITE`, `GPT_TIER` |
| `hooks/format.ts` | `percentColor` (colour thresholds), `row` (when `untracked` shows) |

## Known limits

- The cost row can't have a border: Claude Code draws it outside any component a mod can redraw.
- A hot reload in the middle of a turn loses that turn's main/subagent split (the total is still right next turn).
- Fast mode can't be priced per request; its difference shows as untracked.
- Switching model before the first turn changes the band's model name on the next refresh, not at once (`cache cold` shows at once). Mid-conversation both change at once.
- Results that arrive after every background agent has finished wake one more turn, which gets its own small row.
- Exiting while background agents are still running loses the held spend from the pane and the saved history; Claude Code's session total keeps it.
- `claude --resume` brings back the turns, turn count, spend by model and last turn. Sessions run before this version, and forks (`--fork-session`), start empty.
