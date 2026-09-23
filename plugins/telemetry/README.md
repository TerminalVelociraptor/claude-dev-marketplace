# telemetry

Per-turn cost reports and a two-line status line for Claude Code.

After each turn:

```
This request cost: ~$1.02 (main ~$0.61 + 2 subagent(s) ~$0.30 + untracked ~$0.11)
```

Below the prompt:

```
Opus 5 · high ⚡ · main*
ctx 64% (128K) · $1.02 / $3.21 · 5h 42% ↻1h12m · cache 91% 23m left
```

## Install

1. `/plugin install telemetry@dev-toolkits`
2. `/telemetry:setup` adds the `statusLine` entry to `~/.claude/settings.json`.
   Plugins can't set the status line themselves. Until it's installed (or you
   decline), each new session starts with a reminder.

Other commands:

- `/telemetry:setup status`: which status line is in effect and where it's set.
- `/telemetry:setup uninstall`: remove telemetry's `statusLine` entry. Run it
  **before** `/plugin uninstall telemetry@dev-toolkits`, or the entry is left
  pointing at a removed plugin and the status line goes blank.

Cost reports work without the status line, but only from transcripts (see below).

### Moving from cost-estimate / session-line

1. `/plugin uninstall cost-estimate@dev-toolkits` (and `session-line`, if
   installed). Keeping cost-estimate would report every turn twice.
2. Install telemetry and run `/telemetry:setup`; it replaces the old
   `statusLine` entry.

`~/.claude/cost-estimate-state` is moved to `~/.claude/telemetry-state` on
first run, so sessions that span the switch don't re-report their history.

## Per-turn cost

Claude Code writes every message to a session transcript (JSONL) at
`~/.claude/projects/<project>/<session_id>.jsonl`; subagents get their own at
`<session_id>/subagents/agent-<agent_id>.jsonl`. Each assistant message
carries its model id and a `usage` block. One API response is written as
several lines, so each `message.id` is counted once (the last line).

- **`SessionStart`** records the start time for a new session. Resumed or
  forked sessions copy earlier messages into the new transcript under the
  new session id; messages older than the start time are ignored.
- **`SubagentStop`** prices the new part of that subagent's transcript and
  queues the result for the next `Stop`.
- **`Stop`** prices the main transcript since the previous `Stop`, adds the
  queued subagents, adds untracked cost, and prints the total.

Claude Code writes transcripts asynchronously: when `Stop` or `SubagentStop`
fires, the final response is usually not on disk yet. Both hooks wait up to
2s for the hook input's `last_assistant_message` to appear in the transcript
(it has taken about 0.1s) before pricing it. A subagent with no transcript
file isn't waited for.

Every usage block is priced from `pricing.json` in four input buckets:

| Bucket | Rate |
|---|---|
| `input_tokens` (uncached) | `input` |
| `cache_read_input_tokens` | the model's `cache_read` (0.1× input; Opus 5.5 0.05×; Fable 5.1 0.025×) |
| `cache_creation` 5-minute writes | 1.25× input |
| `cache_creation` 1-hour writes | 2× input |

plus `output_tokens` (thinking included) at `output`, fast mode
(`speed: "fast"`), the GPT >272K-input surcharge, and $0.01 per server-side
web search. For GPT models via clodex, `input_tokens` already excludes
cached tokens.

### Untracked cost

Transcripts miss real spend: internal subagents that write no transcript,
WebSearch/WebFetch helper calls, compaction, away summaries, titles. In one
audited session that was ~25% of the cost. Claude Code's own
`cost.total_cost_usd` includes it, but is only sent to the status line, so
telemetry's status line saves it on every refresh (`record_cc_snapshot`).

At `Stop`, the change in that total since the previous `Stop`, minus what
Claude Code charged for the messages already counted from transcripts, is
reported as `untracked`.

- Claude Code prices Claude models at list price (matching `pricing.json`)
  and model ids it doesn't know (the GPT models) at Sonnet rates
  (`claude_code_fallback_model`). That share is backed out and GPT messages
  are priced from `pricing.json`. A GPT call that writes no transcript would
  still appear at Sonnet rates.
- `Stop` waits up to 1.5s for a total newer than the turn's last message
  (the status line runs 300ms after each message). Without one (no status
  line, or it stopped mid-session) that turn is transcript-only, and the
  baseline is reset at the next `Stop` that has a fresh total.
- `untracked` can be negative: a background subagent's spend is counted by
  Claude Code while it runs, but from its transcript only when it finishes.
  Across turns it nets out.

## Status line

| Segment | Source | Notes |
|---|---|---|
| Model | `model.display_name` | |
| Effort | `effort.level`, `fast_mode` | ⚡ in fast mode |
| Git | `git branch --show-current`, `git status --porcelain` | yellow `*` when dirty; short sha when detached; cached 5s |
| Context | `context_window.used_percentage`, `.total_input_tokens` | `ctx 40% (150K)`: percentage coloured green < 50%, yellow < 80%, red above; size rounded to the nearest thousand tokens |
| Cost | telemetry state | `$last turn / $session`: the last completed turn's reported cost, and the session so far (reported turns plus Claude Code's spend since, corrected at the next `Stop`) |
| 5h limit | `rate_limits.five_hour` | same colours; `↻` = time until reset. Pro/Max only |
| Cache | `prompt_cache` | hit ratio and time until the cache goes cold, or `cache cold` |

When the terminal is too narrow, segments are dropped from the right of
each line; the order above is the priority order.

### How setup works

A plugin's `settings.json` only supports `agent` and `subagentStatusLine`, a
`statusLine` command can't use `${CLAUDE_PLUGIN_ROOT}`, and installed plugin
copies live in versioned directories. So `/telemetry:setup` writes an entry
that looks up the plugin's current directory:

```json
"statusLine": {
  "type": "command",
  "command": "python3 \"$(cat ~/.claude/telemetry-state/plugin_root)/scripts/statusline.py\"",
  "refreshInterval": 30
}
```

Every telemetry hook run rewrites `plugin_root`, so after `/plugin update`
the status line follows the new version from the next hook run.

The startup check (`setup.py --check`) looks for `statusLine` in managed,
local project, project and user settings, in that order of precedence. It
can't see a status line passed with `--settings` on the command line.

### Adding a segment

1. In `scripts/statusline.py`, write a function that takes the input JSON and
   returns a string, or `None` to hide the segment.
2. Add `safe(your_segment, data)` to one of the lists in `main()`; earlier
   means higher priority when narrow.
3. Keep the `record_cc_snapshot` call in `main()`: untracked cost depends on it.

```python
def lines_changed_segment(data):
    cost = data.get("cost") or {}
    added, removed = cost.get("total_lines_added") or 0, cost.get("total_lines_removed") or 0
    return f"{GREEN}+{added}{RESET} {RED}-{removed}{RESET}" if added or removed else None
```

Input fields: https://code.claude.com/docs/en/statusline#available-data

Test with mock input. Use a made-up `session_id`, since a real one would
overwrite that session's saved cost total:

```bash
echo '{"session_id":"sl-test","model":{"display_name":"Opus 5"},"effort":{"level":"high"},
  "workspace":{"current_dir":"'"$PWD"'"},"context_window":{"used_percentage":83},
  "cost":{"total_cost_usd":1.23},
  "rate_limits":{"five_hour":{"used_percentage":42,"resets_at":'"$(($(date +%s)+4300))"'}},
  "prompt_cache":{"caching_observed":true,"warm":true,"hit_ratio":0.91,"expires_at":'"$(($(date +%s)+1400))"'}}' \
| COLUMNS=100 python3 plugins/telemetry/scripts/statusline.py
rm -rf ~/.claude/telemetry-state/sl-test
```

## Changing the plugin

Claude Code runs the installed copy, not this folder. After editing, bump
`version` in `.claude-plugin/plugin.json` and run
`/plugin update telemetry@dev-toolkits`, then `/reload-plugins`.

### Adding or updating a model

Edit `pricing.json`. Keys are the exact model id Claude Code writes into the
transcript (`message.model`). Prices are USD per million tokens. Unknown ids
are excluded from the total with a note rather than guessed.

## Files

| Path | Role |
|---|---|
| `scripts/cost_estimate.py` | `SessionStart`/`Stop`/`SubagentStop` hooks and shared state helpers |
| `scripts/statusline.py` | the status line |
| `scripts/setup.py` | `--check` (startup hook), `--status`, `--install`, `--uninstall`, `--dismiss` |
| `skills/setup/SKILL.md` | `/telemetry:setup` |
| `hooks/hooks.json` | hook wiring |
| `pricing.json` | rates |

State lives in `~/.claude/telemetry-state/`: `plugin_root`,
`setup_dismissed`, and one directory per session (cursors, queued subagent
costs, saved Claude Code totals, `last_turn`, `session_total`, git cache).
It's never cleaned automatically; delete it any time no session is running.

## Known limitations

- A background subagent that finishes after the turn ends is counted in the
  next turn.
- `Stop` doesn't fire for interrupted turns; their cost rolls into the next.
- While the status line has stopped updating, each `Stop` waits 1.5s.
- A final response that takes over 2s to reach the transcript is counted at
  the next `Stop` (a subagent's is counted as untracked, or not at all
  without the status line).
- Only one status line can be active; telemetry's replaces any other.
