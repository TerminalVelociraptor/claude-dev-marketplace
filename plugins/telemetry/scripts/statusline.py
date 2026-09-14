#!/usr/bin/env python3
"""
telemetry status line.

  Opus 5 · high ⚡ · main*
  ctx 64% (128K) · $1.02 / $3.21 · 5h 42% ↻1h12m · cache 91% 23m left

Claude Code runs this with the session's JSON on stdin after each assistant
message (and every refreshInterval seconds) and shows what it prints. Plugins
can't set the main status line, so /telemetry:setup adds a statusLine entry
to ~/.claude/settings.json that runs this file (see setup.py).

Each run also records Claude Code's running cost total for the Stop hook
(cost_estimate.record_cc_snapshot) and shows the session total
(cost_estimate.session_cost).

Each segment is a function of the input JSON that returns a string or None.
Segments are listed in priority order per line: when the terminal is too
narrow, the rightmost ones are dropped first.
"""
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True  # don't leave __pycache__ in the plugin's install dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost_estimate  # noqa: E402

GIT_CACHE_SECONDS = 5
# Columns left free for Claude Code's own spacing around the status line.
EDGE_MARGIN = 2
SEPARATOR = " · "

RESET, DIM, GREEN, YELLOW, RED = "\033[0m", "\033[2m", "\033[32m", "\033[33m", "\033[31m"
ANSI_ESCAPE = re.compile(r"\033\[[0-9;]*m")


def usage_color(percent):
    return GREEN if percent < 50 else YELLOW if percent < 80 else RED


def duration(seconds):
    minutes = max(0, int(seconds // 60))
    if minutes < 1:
        return "<1m"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


# --- segments -----------------------------------------------------------------

def model_segment(data):
    return (data.get("model") or {}).get("display_name")


def effort_segment(data):
    level = (data.get("effort") or {}).get("level")
    fast = "⚡" if data.get("fast_mode") else None
    return " ".join(p for p in (level, fast) if p) or None


def git_segment(data):
    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd")
    if not cwd:
        return None
    # git status can be slow in big repos, and this runs after every message.
    session_id = data.get("session_id")
    cache_path = os.path.join(cost_estimate.state_dir(session_id), "git.json") if session_id else None
    if cache_path:
        try:
            with open(cache_path) as f:
                cached = json.load(f)
            if cached["cwd"] == cwd and time.time() - cached["at"] < GIT_CACHE_SECONDS:
                return cached["text"]
        except (OSError, ValueError, KeyError):
            pass

    def git(*args):
        return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=1).stdout.strip()

    branch = git("branch", "--show-current") or git("rev-parse", "--short", "HEAD")  # sha when detached
    text = branch + (f"{YELLOW}*{RESET}" if git("status", "--porcelain") else "") if branch else None

    if cache_path:
        cost_estimate.write_atomic(cache_path, json.dumps({"cwd": cwd, "at": time.time(), "text": text}))
    return text


def context_segment(data):
    """ctx 40% (150K): share of the context window, and its size in thousands of tokens."""
    window = data.get("context_window") or {}
    used = window.get("used_percentage")
    if not isinstance(used, (int, float)):
        return None
    text = f"ctx {usage_color(used)}{used:.0f}%{RESET}"
    tokens = window.get("total_input_tokens")  # input + cache reads + cache writes of the last response
    if isinstance(tokens, (int, float)) and tokens > 0:
        text += f" ({round(tokens / 1000)}K)"
    return text


def cost_segment(data):
    """$last turn / $session: the last completed turn's reported cost, and the session so far."""
    session_id = data.get("session_id")
    if not session_id:
        return None
    last_turn = cost_estimate.last_turn_cost(session_id) or 0.0
    total = cost_estimate.session_cost(session_id, (data.get("cost") or {}).get("total_cost_usd"))
    return f"${last_turn:.2f} / ${total:.2f}"


def rate_limit_segment(data):
    five_hour = (data.get("rate_limits") or {}).get("five_hour") or {}
    used = five_hour.get("used_percentage")
    if not isinstance(used, (int, float)):
        return None  # only sent for Pro/Max subscriptions, after the first response
    text = f"5h {usage_color(used)}{used:.0f}%{RESET}"
    resets_at = five_hour.get("resets_at")
    if isinstance(resets_at, (int, float)):
        text += f" ↻{duration(resets_at - time.time())}"
    return text


def cache_segment(data):
    cache = data.get("prompt_cache")
    if not cache or not cache.get("caching_observed"):
        return None
    if not cache.get("warm"):
        return f"{DIM}cache cold{RESET}"
    parts = ["cache"]
    hit_ratio = cache.get("hit_ratio")
    if isinstance(hit_ratio, (int, float)):
        parts.append(f"{hit_ratio:.0%}")
    expires_at = cache.get("expires_at")
    if isinstance(expires_at, (int, float)):
        parts.append(f"{duration(expires_at - time.time())} left")
    return " ".join(parts)


# --- layout ---------------------------------------------------------------------

def safe(function, *args):
    """A failing segment is left out instead of blanking the status line."""
    try:
        return function(*args)
    except Exception:
        return None


def terminal_width():
    try:
        return max(20, int(os.environ["COLUMNS"]) - EDGE_MARGIN)
    except (KeyError, ValueError):
        return 80 - EDGE_MARGIN


def visible_length(text):
    return len(ANSI_ESCAPE.sub("", text))


def fit_line(segments, width):
    """Join segments, dropping the rightmost (lowest-priority) ones until the line fits."""
    segments = [s for s in segments if s]
    while len(segments) > 1 and visible_length(SEPARATOR.join(segments)) > width:
        segments.pop()
    line = SEPARATOR.join(segments)
    if visible_length(line) > width:
        line = ANSI_ESCAPE.sub("", line)[: width - 1] + "…"
    return line


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}

    # Feeds the Stop hook's untracked-cost calculation; keep this if you rewrite the layout.
    safe(cost_estimate.record_cc_snapshot, data)

    width = terminal_width()
    lines = [
        [safe(model_segment, data), safe(effort_segment, data), safe(git_segment, data)],
        [safe(context_segment, data), safe(cost_segment, data),
         safe(rate_limit_segment, data), safe(cache_segment, data)],
    ]
    print("\n".join(line for line in (fit_line(segments, width) for segments in lines) if line))


if __name__ == "__main__":
    main()
