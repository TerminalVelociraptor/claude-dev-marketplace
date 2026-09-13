#!/usr/bin/env python3
"""
cost-estimate hook: prints an approximate dollar cost for the request(s) that
just finished, by reading token usage out of the session transcript.

Invoked by Claude Code as a Stop or SubagentStop command hook. Reads the hook
event JSON from stdin, does the accounting, writes "This request cost: ~$x"
(or a subagent-scoped line) to stdout.

Stop fires once per completed request/turn (not just once per session), so
all accounting here is scoped to "since the previous Stop" using a small
per-session state directory under ~/.claude/cost-estimate-state/<session_id>/:
  agent_cursor_<id> - line count of that subagent's own transcript
                      (agent_transcript_path) already reported, so a resumed
                      subagent only accounts for its *new* turns.
  main_cursor      - transcript line count already reported by the previous
                      Stop, so each Stop only accounts for the current turn.
  subagents.jsonl  - one line per subagent SubagentStop event since the last
                      Stop: {cost, per_model}, consumed (and cleared) by the
                      next Stop so its cost rolls into that turn's total.

See README.md for the attribution caveat around concurrent subagents.
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)
PRICING_PATH = os.path.join(PLUGIN_ROOT, "pricing.json")
STATE_ROOT = os.path.expanduser("~/.claude/cost-estimate-state")


def load_pricing():
    with open(PRICING_PATH) as f:
        return json.load(f)


def read_transcript_lines(transcript_path):
    lines = []
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    lines.append(line)
    except FileNotFoundError:
        pass
    return lines


def usage_cost(usage, model_cfg, pricing):
    if not usage or not model_cfg:
        return 0.0
    input_tok = usage.get("input_tokens", 0) or 0
    output_tok = usage.get("output_tokens", 0) or 0
    cache_read = usage.get("cache_read_input_tokens", 0) or 0
    cache_write = usage.get("cache_creation_input_tokens", 0) or 0

    in_rate = model_cfg["input"] / 1_000_000
    out_rate = model_cfg["output"] / 1_000_000
    cache_read_rate = in_rate * pricing.get("cache_read_multiplier", 0.1)
    cache_write_rate = in_rate * pricing.get("cache_write_multiplier", 1.25)

    return (
        input_tok * in_rate
        + output_tok * out_rate
        + cache_read * cache_read_rate
        + cache_write * cache_write_rate
    )


def sum_usage(lines, pricing, sidechain, start=0):
    """Sum cost for assistant messages in lines[start:] matching the given
    isSidechain value. Returns (total_cost, per_model_totals, unknown_models)."""
    total = 0.0
    per_model = {}
    unknown = set()
    models = pricing["models"]

    # One API response is written as several transcript lines (one per content
    # block), each repeating the full usage. Keep only the last line per message id.
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
        msg = d.get("message", {})
        by_id[msg.get("id") or f"line-{i}"] = msg

    for msg in by_id.values():
        model_id = msg.get("model")
        usage = msg.get("usage")
        if not usage:
            continue
        model_cfg = models.get(model_id)
        if model_cfg is None:
            unknown.add(model_id)
            continue
        cost = usage_cost(usage, model_cfg, pricing)
        total += cost
        per_model[model_cfg["label"]] = per_model.get(model_cfg["label"], 0.0) + cost

    return total, per_model, unknown


def fmt(cost):
    if cost < 0.01:
        return f"~${cost:.4f}"
    return f"~${cost:.2f}"


def breakdown_str(per_model):
    if len(per_model) <= 1:
        return ""
    parts = [f"{label} ${c:.4f}" for label, c in per_model.items()]
    return " (" + ", ".join(parts) + ")"


def emit(message):
    # Plain stdout from Stop/SubagentStop hooks is hidden; systemMessage is shown to the user.
    print(json.dumps({"systemMessage": message}))


def state_dir(session_id):
    d = os.path.join(STATE_ROOT, session_id)
    os.makedirs(d, exist_ok=True)
    return d


def main():
    event = json.load(sys.stdin)
    session_id = event.get("session_id", "unknown-session")
    transcript_path = event.get("transcript_path")
    hook_event = event.get("hook_event_name")

    if not transcript_path:
        return

    pricing = load_pricing()
    sdir = state_dir(session_id)
    main_cursor_path = os.path.join(sdir, "main_cursor")
    subagents_path = os.path.join(sdir, "subagents.jsonl")

    def read_cursor(path):
        if os.path.exists(path):
            try:
                return int(open(path).read().strip() or 0)
            except ValueError:
                return 0
        return 0

    if hook_event == "SubagentStop":
        # Subagent turns live in their own transcript, not the main one.
        agent_transcript = event.get("agent_transcript_path")
        if not agent_transcript:
            return
        lines = read_transcript_lines(os.path.expanduser(agent_transcript))
        # Per-agent cursor: a resumed subagent fires SubagentStop again on the same file.
        agent_cursor_path = os.path.join(sdir, f"agent_cursor_{event.get('agent_id', 'unknown')}")
        agent_cursor = read_cursor(agent_cursor_path)
        cost, per_model, unknown = sum_usage(lines, pricing, sidechain=True, start=agent_cursor)
        with open(agent_cursor_path, "w") as f:
            f.write(str(len(lines)))
        if cost > 0:
            with open(subagents_path, "a") as f:
                f.write(json.dumps({"cost": cost, "per_model": per_model}) + "\n")
            note = " (unrecognized model, not priced)" if unknown else ""
            emit(f"Subagent cost: {fmt(cost)}{breakdown_str(per_model)}{note}")
        return

    if hook_event == "Stop":
        lines = read_transcript_lines(transcript_path)
        main_cursor = read_cursor(main_cursor_path)
        main_cost, main_per_model, unknown = sum_usage(lines, pricing, sidechain=False, start=main_cursor)
        with open(main_cursor_path, "w") as f:
            f.write(str(len(lines)))

        sub_total = 0.0
        sub_per_model = {}
        sub_entries = []
        if os.path.exists(subagents_path):
            with open(subagents_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    sub_entries.append(entry)
                    sub_total += entry["cost"]
                    for label, c in entry.get("per_model", {}).items():
                        sub_per_model[label] = sub_per_model.get(label, 0.0) + c
            os.remove(subagents_path)  # consumed — belongs to this turn only

        grand_total = main_cost + sub_total

        if sub_entries:
            msg = (f"This request cost: {fmt(grand_total)} "
                   f"(main {fmt(main_cost)}{breakdown_str(main_per_model)} + "
                   f"{len(sub_entries)} subagent(s) {fmt(sub_total)}{breakdown_str(sub_per_model)})")
        else:
            msg = f"This request cost: {fmt(grand_total)}{breakdown_str(main_per_model)}"

        if unknown:
            msg += f"\n  note: no pricing entry for model id(s) {sorted(unknown)}, excluded from total"

        emit(msg)


if __name__ == "__main__":
    main()
