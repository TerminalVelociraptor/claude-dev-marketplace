#!/usr/bin/env python3
"""Re-inject the teaching protocol's core rules on each prompt during a learning session.

Why this exists: skill content is loaded into the conversation once and never re-read, and
auto-compaction keeps only the first ~5,000 tokens of each skill under a shared budget. In a
long session the protocol can therefore decay -- and the first rules to go are the ones that
fight the model's drive to completion, above all "ask them to predict, then STOP and wait".

This hook is a deterministic backstop for that decay. It is OFF by default: it emits nothing
unless BOTH of the following hold, so it stays silent during all ordinary work.

  1. A learning session is active  -> sessions/<session_id>.active exists and is under 24h old
  2. Re-injection is enabled       -> config.json has {"reinject": true}

Enable with:  learn-session config reinject on   (see README)

A marker older than 24 hours is a session that ended without cleanup; the hook stays silent and
leaves deleting it to learn-session's sweep. The reminder is deliberately generic: the hook never
parses or injects the learner profile.

Exits 0 always. A hook that fails must never break the session.
"""

import json
import os
import sys
import time
from pathlib import Path

REMINDER = """<learning-session-active>
Standing rules for this learning session (see teaching-protocol.md):
- Before revealing a mechanism on any growth edge in the loaded profile, ask them to PREDICT
  first, then STOP and end the turn. Do not answer your own question.
- Wrong answer: ONE hint, ask again. Wrong twice: give the full correction and move on.
  The correction always arrives; never loop Socratically.
- In `pair` mode you are SILENT between check-ins and you do not write their code.
- Never assert a measurable claim you have not verified.
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

    try:
        age = time.time() - (root / "sessions" / f"{session_id}.active").stat().st_mtime
    except OSError:
        return  # no marker: not a learning session

    # The staleness window is shared with learn-session. Imported only once a marker exists, so
    # ordinary prompts never load it; a failed import is swallowed like any other hook error.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
    from _toolkit import SESSION_STALE_SECONDS

    if age > SESSION_STALE_SECONDS:
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
