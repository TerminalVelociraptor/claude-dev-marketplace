#!/usr/bin/env python3
"""
telemetry cost hooks: print an approximate dollar cost after each request,
from token usage in the session transcripts plus Claude Code's own running
cost total, which the telemetry status line records.

Invoked by Claude Code as a SessionStart, Stop, or SubagentStop command hook
(event JSON on stdin). statusline.py and setup.py import helpers from here.

Stop fires once per completed request/turn (not just once per session), so
all accounting here is scoped to "since the previous Stop" using a small
per-session state directory under ~/.claude/telemetry-state/<session_id>/:
  session_start    - ISO timestamp written by SessionStart for a session with
                      no cursor yet. Resumed/forked sessions copy old messages
                      into the new transcript (with the new sessionId), so
                      assistant messages older than this are ignored.
  agent_cursor_<id> - line count of that subagent's own transcript
                      (agent_transcript_path) already reported, so a resumed
                      subagent only accounts for its *new* turns.
  main_cursor      - transcript line count already reported by the previous
                      Stop, so each Stop only accounts for the current turn.
  subagents.jsonl  - one line per subagent SubagentStop event since the last
                      Stop: {cost, cc_equiv, per_model} or {untracked: true}
                      when the subagent left no transcript, consumed (and
                      cleared) by the next Stop so it rolls into that turn.
  cc_snapshot.json - {total_cost_usd, written_at}: Claude Code's session cost
                      as last seen by the status line.
  cc_reported      - the total_cost_usd already accounted for by a Stop (or
                      the first value the status line saw in this session), or
                      "resync" after a Stop found the status line had stopped
                      updating: the next Stop with a fresh total re-baselines.
  session_total    - running sum of every Stop's reported total, read by
                      session_cost() for the status line.
  last_turn        - the most recent Stop's reported total (last_turn_cost()).
  git.json         - the status line's cached git segment.
Plus ~/.claude/telemetry-state/plugin_root: this plugin's current directory,
which the statusLine command reads (see setup.py).

Claude Code's total covers calls that never reach a transcript (internal
subagents, WebSearch/WebFetch helpers, compaction, summaries), but prices
models it doesn't recognise (the GPT models via clodex) at Sonnet rates. So
Stop takes the total's delta, subtracts what Claude Code charged for the
transcript messages ("cc_equiv"), and reports the remainder as "untracked".
Without a fresh total (status line not set up), it reports transcript costs only.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)
PRICING_PATH = os.path.join(PLUGIN_ROOT, "pricing.json")
STATE_ROOT = os.path.expanduser("~/.claude/telemetry-state")
PLUGIN_ROOT_FILE = os.path.join(STATE_ROOT, "plugin_root")
# State written by the cost-estimate plugin this replaced.
LEGACY_STATE_ROOT = os.path.expanduser("~/.claude/cost-estimate-state")
# The status line is debounced 300ms after each assistant message; give it
# this long to catch up with the turn's final message before giving up on it.
SNAPSHOT_WAIT_SECONDS = 1.5
# Claude Code writes transcripts asynchronously, so the final response may not
# be on disk yet when Stop/SubagentStop fires; wait up to this long for it.
FLUSH_WAIT_SECONDS = 2.0


def load_pricing():
    with open(PRICING_PATH) as f:
        return json.load(f)


def read_transcript_lines(transcript_path):
    lines = []
    try:
        with open(transcript_path) as f:
            for line in f:
                # A line without its newline is still being written; leave it
                # (and the cursor) for the next run instead of skipping it forever.
                if not line.endswith("\n"):
                    break
                line = line.strip()
                if line:
                    lines.append(line)
    except FileNotFoundError:
        pass
    return lines


def message_text(record):
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def has_final_message(lines, start, sidechain, final_text):
    for line in reversed(lines[start:]):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (d.get("type") == "assistant" and bool(d.get("isSidechain")) == sidechain
                and message_text(d).strip() == final_text):
            return True
    return False


def read_transcript_when_flushed(transcript_path, start, sidechain, event):
    """read_transcript_lines, but first wait up to FLUSH_WAIT_SECONDS for the
    hook's last_assistant_message to reach the transcript. (Measured: it lands
    about 0.1s into the wait.) Internal subagents never create their transcript
    file, so a missing file isn't waited for."""
    if not os.path.exists(transcript_path):
        return []
    final_text = (event.get("last_assistant_message") or "").strip()
    deadline = time.time() + FLUSH_WAIT_SECONDS
    lines = read_transcript_lines(transcript_path)
    while final_text and not has_final_message(lines, start, sidechain, final_text) and time.time() < deadline:
        time.sleep(0.1)
        lines = read_transcript_lines(transcript_path)
    return lines


def usage_cost(usage, model_cfg, pricing):
    if not usage or not model_cfg:
        return 0.0
    input_tok = usage.get("input_tokens", 0) or 0
    output_tok = usage.get("output_tokens", 0) or 0
    cache_read = usage.get("cache_read_input_tokens", 0) or 0
    cache_write = usage.get("cache_creation_input_tokens", 0) or 0

    # 1h-TTL cache writes cost more than 5m ones. Older transcripts have no
    # breakdown, so everything is treated as 5m there.
    ttl_split = usage.get("cache_creation") or {}
    write_1h = min(ttl_split.get("ephemeral_1h_input_tokens", 0) or 0, cache_write)
    write_5m = cache_write - write_1h

    in_rate = model_cfg["input"]
    out_rate = model_cfg["output"]
    read_rate = model_cfg.get("cache_read", in_rate * 0.1)

    fast = model_cfg.get("fast")
    if fast and usage.get("speed") == "fast":
        read_rate *= fast["input"] / in_rate
        in_rate, out_rate = fast["input"], fast["output"]

    long_ctx = pricing.get("long_context", {}).get(model_cfg.get("long_context"))
    if long_ctx and input_tok + cache_read + cache_write > long_ctx["threshold_input_tokens"]:
        in_rate *= long_ctx["input_multiplier"]
        read_rate *= long_ctx["input_multiplier"]
        out_rate *= long_ctx["output_multiplier"]

    cost = (
        input_tok * in_rate
        + output_tok * out_rate
        + cache_read * read_rate
        + write_5m * in_rate * pricing.get("cache_write_5m_multiplier", 1.25)
        + write_1h * in_rate * pricing.get("cache_write_1h_multiplier", 2.0)
    ) / 1_000_000

    searches = (usage.get("server_tool_use") or {}).get("web_search_requests", 0) or 0
    return cost + searches * pricing.get("web_search_usd_per_request", 0.0)


def is_known_to_claude_code(model_id):
    return bool(model_id) and model_id.startswith("claude-")


def sum_usage(lines, pricing, sidechain, start=0, min_timestamp=None):
    """Sum cost for assistant messages in lines[start:] matching the given
    isSidechain value. Returns a dict with:
      cost, per_model  - priced from pricing.json
      unknown          - model ids with no pricing entry (excluded from cost)
      cc_equiv         - what Claude Code's own total charged for these messages
      last_timestamp   - newest assistant message timestamp seen"""
    result = {"cost": 0.0, "per_model": {}, "unknown": set(), "cc_equiv": 0.0, "last_timestamp": None}
    models = pricing["models"]
    fallback_cfg = models.get(pricing.get("claude_code_fallback_model"))

    # One API response is written as several transcript lines (one per content
    # block); earlier lines can carry zeroed usage, so keep only the last line per message id.
    by_id = {}
    for i, line in enumerate(lines[start:]):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "assistant":
            continue
        if bool(d.get("isSidechain")) != sidechain:
            continue
        timestamp = d.get("timestamp") or ""
        if min_timestamp and timestamp < min_timestamp:
            continue
        result["last_timestamp"] = max(result["last_timestamp"] or "", timestamp) or None
        msg = d.get("message", {})
        by_id[msg.get("id") or f"line-{i}"] = msg

    for msg in by_id.values():
        model_id = msg.get("model")
        usage = msg.get("usage")
        if not usage or model_id == "<synthetic>":
            continue
        model_cfg = models.get(model_id)
        cost = usage_cost(usage, model_cfg, pricing) if model_cfg else 0.0
        if model_cfg is None:
            result["unknown"].add(model_id)
        else:
            result["cost"] += cost
            label = model_cfg["label"]
            result["per_model"][label] = result["per_model"].get(label, 0.0) + cost
        # Claude Code prices Claude models at list price (same as pricing.json)
        # and anything else at its fallback (Sonnet) rates. An unpriced Claude
        # model contributes nothing here, so its cost surfaces as "untracked".
        if is_known_to_claude_code(model_id):
            result["cc_equiv"] += cost
        else:
            result["cc_equiv"] += usage_cost(usage, fallback_cfg, pricing)

    return result


def fmt(cost):
    sign = "-" if cost < 0 else ""
    cost = abs(cost)
    if cost < 0.01:
        return f"{sign}~${cost:.4f}"
    return f"{sign}~${cost:.2f}"


def breakdown_str(per_model):
    if len(per_model) <= 1:
        return ""
    parts = [f"{label} ${c:.4f}" for label, c in per_model.items()]
    return " (" + ", ".join(parts) + ")"


def emit(message):
    # Plain stdout from Stop/SubagentStop hooks is hidden; systemMessage is shown to the user.
    print(json.dumps({"systemMessage": message}))


def state_root():
    if not os.path.exists(STATE_ROOT) and os.path.isdir(LEGACY_STATE_ROOT):
        # One-time move from the cost-estimate plugin, so sessions that span the
        # switch keep their cursors instead of re-reporting their whole history.
        try:
            os.rename(LEGACY_STATE_ROOT, STATE_ROOT)
        except OSError:
            pass
    os.makedirs(STATE_ROOT, exist_ok=True)
    return STATE_ROOT


def state_dir(session_id):
    d = os.path.join(state_root(), session_id)
    os.makedirs(d, exist_ok=True)
    return d


def write_atomic(path, text):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def read_float(path):
    try:
        with open(path) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return None


def record_plugin_root():
    """Point the statusLine command at this copy of the plugin. Installed copies
    live in versioned directories, so this is refreshed on every hook run."""
    state_root()
    try:
        with open(PLUGIN_ROOT_FILE) as f:
            if f.read() == PLUGIN_ROOT:
                return
    except OSError:
        pass
    write_atomic(PLUGIN_ROOT_FILE, PLUGIN_ROOT)


def iso_to_epoch(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()


def read_cc_total(sdir, after_timestamp):
    """Claude Code's cost.total_cost_usd as written by the status line after the
    turn's last message, or None if no status line is feeding this session or
    it has stopped updating. (A stale total would make the whole turn look
    like it had already been counted.)"""
    path = os.path.join(sdir, "cc_snapshot.json")
    after = iso_to_epoch(after_timestamp) if after_timestamp else 0.0
    deadline = time.time() + SNAPSHOT_WAIT_SECONDS
    while True:
        try:
            with open(path) as f:
                snapshot = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        if snapshot.get("written_at", 0) >= after:
            return snapshot.get("total_cost_usd")
        if time.time() >= deadline:
            return None
        time.sleep(0.1)


def record_cc_snapshot(data):
    """Save Claude Code's running session cost (from status line input) for the Stop hook."""
    session_id = data.get("session_id")
    total = (data.get("cost") or {}).get("total_cost_usd")
    if not session_id or not isinstance(total, (int, float)):
        return
    sdir = state_dir(session_id)
    write_atomic(os.path.join(sdir, "cc_snapshot.json"),
                 json.dumps({"total_cost_usd": total, "written_at": time.time()}))
    # First sighting in this session: count only from here. A resumed
    # session starts with its earlier total already restored.
    try:
        fd = os.open(os.path.join(sdir, "cc_reported"), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write(repr(total))
    except FileExistsError:
        pass


def session_cost(session_id, cc_total=None):
    """Whole-session estimate for display: everything Stop has reported so far,
    plus Claude Code's spend since the last Stop (at Claude Code's prices until
    the next Stop replaces it with the corrected figure)."""
    sdir = os.path.join(STATE_ROOT, session_id)
    reported = read_float(os.path.join(sdir, "session_total")) or 0.0
    cc_prev = read_float(os.path.join(sdir, "cc_reported"))
    if isinstance(cc_total, (int, float)) and cc_prev is not None:
        reported += max(0.0, cc_total - cc_prev)
    return reported


def last_turn_cost(session_id):
    """The most recent Stop's reported total, or None before the first one."""
    return read_float(os.path.join(STATE_ROOT, session_id, "last_turn"))


def main():
    event = json.load(sys.stdin)
    session_id = event.get("session_id", "unknown-session")
    transcript_path = event.get("transcript_path")
    hook_event = event.get("hook_event_name")

    record_plugin_root()
    if not transcript_path:
        return

    pricing = load_pricing()
    sdir = state_dir(session_id)
    main_cursor_path = os.path.join(sdir, "main_cursor")
    session_start_path = os.path.join(sdir, "session_start")
    subagents_path = os.path.join(sdir, "subagents.jsonl")
    cc_reported_path = os.path.join(sdir, "cc_reported")

    def read_cursor(path):
        if os.path.exists(path):
            try:
                return int(open(path).read().strip() or 0)
            except ValueError:
                return 0
        return 0

    if hook_event == "SessionStart":
        # Only for sessions this hook hasn't reported on yet; an existing
        # cursor already excludes everything counted before.
        if not os.path.exists(main_cursor_path) and not os.path.exists(session_start_path):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            with open(session_start_path, "w") as f:
                f.write(now)
        return

    if hook_event == "SubagentStop":
        # Subagent turns live in their own transcript, not the main one.
        agent_transcript = event.get("agent_transcript_path")
        if not agent_transcript:
            return
        # Per-agent cursor: a resumed subagent fires SubagentStop again on the same file.
        agent_cursor_path = os.path.join(sdir, f"agent_cursor_{event.get('agent_id', 'unknown')}")
        agent_cursor = read_cursor(agent_cursor_path)
        lines = read_transcript_when_flushed(os.path.expanduser(agent_transcript), agent_cursor, True, event)
        sub = sum_usage(lines, pricing, sidechain=True, start=agent_cursor)
        with open(agent_cursor_path, "w") as f:
            f.write(str(len(lines)))
        if sub["cost"] > 0 or sub["cc_equiv"] > 0:
            with open(subagents_path, "a") as f:
                f.write(json.dumps({"cost": sub["cost"], "cc_equiv": sub["cc_equiv"],
                                    "per_model": sub["per_model"]}) + "\n")
            note = " (unrecognized model, not priced)" if sub["unknown"] else ""
            emit(f"Subagent cost: {fmt(sub['cost'])}{breakdown_str(sub['per_model'])}{note}")
        elif not lines and agent_cursor == 0:
            # Some internal subagents fire SubagentStop but never write a
            # transcript, so their (real) cost can't be read. Count them.
            with open(subagents_path, "a") as f:
                f.write(json.dumps({"untracked": True}) + "\n")
        return

    if hook_event == "Stop":
        main_cursor = read_cursor(main_cursor_path)
        lines = read_transcript_when_flushed(transcript_path, main_cursor, False, event)
        session_start = open(session_start_path).read().strip() if os.path.exists(session_start_path) else None
        main_usage = sum_usage(lines, pricing, sidechain=False, start=main_cursor, min_timestamp=session_start)
        with open(main_cursor_path, "w") as f:
            f.write(str(len(lines)))

        sub_total = 0.0
        sub_cc_equiv = 0.0
        sub_per_model = {}
        sub_count = 0
        untracked_agents = 0
        if os.path.exists(subagents_path):
            # Move the queue aside first so a SubagentStop appending concurrently
            # starts a fresh file instead of being deleted with this one.
            consumed_path = subagents_path + f".{os.getpid()}"
            os.replace(subagents_path, consumed_path)
            with open(consumed_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if entry.get("untracked"):
                        untracked_agents += 1
                        continue
                    sub_count += 1
                    sub_total += entry["cost"]
                    sub_cc_equiv += entry.get("cc_equiv", entry["cost"])
                    for label, c in entry.get("per_model", {}).items():
                        sub_per_model[label] = sub_per_model.get(label, 0.0) + c
            os.remove(consumed_path)  # consumed — belongs to this turn only

        main_cost = main_usage["cost"]
        grand_total = main_cost + sub_total

        # Claude Code's own total, if the status line is recording it.
        untracked = None
        cc_total = read_cc_total(sdir, main_usage["last_timestamp"])
        if cc_total is not None:
            cc_prev = read_float(cc_reported_path)
            if cc_prev is not None and cc_total >= cc_prev:
                untracked = (cc_total - cc_prev) - (main_usage["cc_equiv"] + sub_cc_equiv)
                grand_total += untracked
            write_atomic(cc_reported_path, repr(cc_total))
        elif os.path.exists(cc_reported_path):
            # The status line fed this session before but has stopped updating.
            # Invalidate the baseline so the next fresh total starts a new one
            # here at a Stop, rather than being diffed against a stale value.
            write_atomic(cc_reported_path, "resync")

        # For the status line (see last_turn_cost and session_cost).
        session_total_path = os.path.join(sdir, "session_total")
        write_atomic(session_total_path, repr((read_float(session_total_path) or 0.0) + grand_total))
        write_atomic(os.path.join(sdir, "last_turn"), repr(grand_total))

        parts = []
        if sub_count:
            parts.append(f"{sub_count} subagent(s) {fmt(sub_total)}{breakdown_str(sub_per_model)}")
        if untracked is not None and abs(untracked) >= 0.005:
            parts.append(f"untracked {fmt(untracked)}")
        if parts:
            msg = (f"This request cost: {fmt(grand_total)} "
                   f"(main {fmt(main_cost)}{breakdown_str(main_usage['per_model'])} + " + " + ".join(parts) + ")")
        else:
            msg = f"This request cost: {fmt(grand_total)}{breakdown_str(main_usage['per_model'])}"

        unknown = main_usage["unknown"]
        if unknown:
            msg += f"\n  note: no pricing entry for model id(s) {sorted(unknown)}, excluded from total"
            if untracked is not None and all(is_known_to_claude_code(m) for m in unknown):
                msg += " (Claude Code's price for them is in 'untracked')"
        if untracked_agents and untracked is None:
            msg += f"\n  note: {untracked_agents} internal subagent call(s) wrote no transcript, cost not included"

        emit(msg)


if __name__ == "__main__":
    main()
