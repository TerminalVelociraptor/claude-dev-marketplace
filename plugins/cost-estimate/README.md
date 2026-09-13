# cost-estimate

Prints `This request cost: ~$x` after every Claude Code turn, using a fixed
per-model pricing table and the token usage recorded in the session
transcript. Works across model switches (`/fast`, different subagent models)
and gives a per-subagent breakdown when a turn spawned subagents.

## Install / uninstall

This plugin lives in the `dev-toolkits` marketplace
(`/home/david/agent-tools/plugin-marketplace`), already registered in your
`~/.claude/settings.json` under `extraKnownMarketplaces`.

- **Install**: `/plugin install cost-estimate@dev-toolkits`
- **Uninstall**: `/plugin uninstall cost-estimate@dev-toolkits`
- Or manage it via the `/plugin` menu.

Hooks load at session start, so restart Claude Code after installing or
uninstalling. Confirm it's active with `/hooks` in a new session.

## How it works

Claude Code writes every message to a session transcript (JSONL) at
`~/.claude/projects/<project>/<session_id>.jsonl`. Each assistant message in
that file carries the model id that generated it and a `usage` block
(input/output/cache tokens) for that one API call. A single API response is
written as several lines (one per content block) that repeat the same
`usage`, so the hook counts each `message.id` once. Subagent turns land in a
*separate* transcript, `<session_id>/subagents/agent-<agent_id>.jsonl`,
which Claude Code passes to the hook as `agent_transcript_path`.

Output is returned as `{"systemMessage": "..."}` JSON, because plain stdout
from `Stop`/`SubagentStop` hooks only goes to the debug log.

`hooks/cost_estimate.py` is invoked twice by Claude Code (wired up in
`hooks/hooks.json`, using `${CLAUDE_PLUGIN_ROOT}` so it works regardless of
where the plugin is installed from):

- **`SubagentStop`** — fires when a subagent finishes. The hook sums the
  usage in that subagent's own transcript that's new since its last
  `SubagentStop` (a resumed subagent fires again), prices it from
  `pricing.json`, prints `Subagent cost: ~$x`, and appends the result to a
  small per-session state file.
- **`Stop`** — fires when the main agent finishes a turn. The hook sums the
  *main-chain* usage new since the previous `Stop`, adds in whatever
  subagent costs were logged since then, and prints the combined total:

  ```
  This request cost: ~$0.71 (main ~$0.58 + 2 subagent(s) ~$0.13)
  ```

  or, with no subagents:

  ```
  This request cost: ~$0.04
  ```

Everything is scoped to "since the previous Stop", not the whole session —
Stop fires once per turn, so each line reports just that turn's cost.

State lives under `~/.claude/cost-estimate-state/<session_id>/` (line-count
cursors + a small queue of pending subagent costs). It's created lazily,
stays tiny, and is safe to delete by hand (`rm -rf`) any time between
sessions — the hook rebuilds it as needed and never re-reads old lines twice.
Uninstalling the plugin does not clean this up automatically; delete
`~/.claude/cost-estimate-state` yourself if you want it gone.

## Model selection

The hook doesn't choose a model — it reads whatever model id Claude Code
already stamped on each transcript message and looks that id up in
`pricing.json`. If your main thread and a subagent use different models,
each is priced correctly on its own. If a model id appears in the transcript
with no matching entry in `pricing.json`, that message's tokens are skipped
and a note is appended to the cost message so the total doesn't silently
include a wrong price.

## Cache tokens

The pricing table only lists flat input/output rates, but Claude bills
prompt-cache reads and writes at different rates. `pricing.json` has two
global multipliers applied to every model's input rate:

- `cache_read_multiplier` (default `0.1`) — cache reads are cheap.
- `cache_write_multiplier` (default `1.25`) — cache writes cost a premium.

These are approximations of Anthropic's real cache pricing ratios, applied
uniformly since the table you gave doesn't break out per-model cache rates.
Adjust them in `pricing.json` if you want to tune accuracy for a specific
provider.

## Adding or updating a model

Edit `pricing.json` (at the plugin root, alongside `hooks/` — editing it
in place in the marketplace checkout takes effect on the next Claude Code
restart, no reinstall needed). Each entry is keyed by the exact model id
string Claude Code puts in the transcript, e.g.:

```json
"claude-sonnet-5": { "label": "Claude Sonnet 5", "input": 2, "output": 10 }
```

To find the id for a model you're unsure about, run one turn with it and
check the most recent transcript:

```bash
tail -c 4000 ~/.claude/projects/<project>/<session_id>.jsonl | \
  python3 -c "import sys,json; [print(json.loads(l)['message'].get('model')) for l in sys.stdin if l.strip() and json.loads(l).get('type')=='assistant']"
```

Prices are $ per 1,000,000 tokens, input/output.

## Known limitations

- **Background subagents still running at `Stop`**: a subagent's cost is
  added to whichever `Stop` comes after its `SubagentStop`, so a background
  subagent that finishes after the turn ends is counted in the next turn.
- **Cache multipliers are approximate** (see above) — this is an estimate,
  not a billing-accurate figure.
- **Unknown model ids are excluded** from the total (with a note in the
  message) rather than guessed at — keep `pricing.json` in sync when you use
  a new model.
- State directories for old/abandoned sessions aren't auto-cleaned; they're
  tiny (a couple of small text files each) but you can safely `rm -rf
  ~/.claude/cost-estimate-state` any time no session is running.
