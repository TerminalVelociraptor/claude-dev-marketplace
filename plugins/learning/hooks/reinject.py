#!/usr/bin/env python3
"""Re-inject the teaching protocol's core rules on each prompt during a learning session.

Why this exists: skill content is loaded into the conversation once and never re-read, and
auto-compaction keeps only the first ~5,000 tokens of each skill under a shared budget. In a
long session the protocol can therefore decay -- and the first rules to go are the ones that
fight the model's drive to completion, above all "ask him to predict, then STOP and wait".

This hook is a deterministic backstop for that decay. It is OFF by default: it emits nothing
unless BOTH of the following hold, so it stays silent during all ordinary work.

  1. A learning session is active  -> sessions/<session_id>.active exists
  2. Re-injection is enabled       -> config.json has {"reinject": true}

Enable with:  learning-toolkit config reinject on   (see README)

Exits 0 always. A hook that fails must never break the session.
"""

import json
import os
import sys
from pathlib import Path

REMINDER = """<learning-session-active>
Standing rules for this learning session (see teaching-protocol.md):
- Before revealing any growth-edge mechanism (internals/hpc), ask him to PREDICT first, then
  STOP and end the turn. Do not answer your own question.
- Wrong answer: ONE hint, ask again. Wrong twice: give the full correction and move on.
  The correction always arrives; never loop Socratically.
- In `pair` mode you are SILENT between check-ins and you do not write his code.
- Never assert a measurable claim you have not measured with `bench`.
</learning-session-active>"""


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "learning-toolkit"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    session_id = payload.get("session_id")
    if not session_id:
        return

    root = config_dir()

    if not (root / "sessions" / f"{session_id}.active").exists():
        return

    try:
        cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return  # absent or unreadable config means the feature stays off

    if cfg.get("reinject") is not True:
        return

    # UserPromptSubmit stdout is added to the model's context for this turn.
    print(REMINDER)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never let a backstop take down the session it is meant to protect.
        pass
    sys.exit(0)
