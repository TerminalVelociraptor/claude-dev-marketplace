---
name: setup
description: Install, check, or uninstall the telemetry status line in ~/.claude/settings.json. The status line shows model, effort, git, context, last-turn and session cost, rate limit, and prompt cache state, and feeds Claude Code's running cost total to telemetry's per-turn cost reports.
argument-hint: "[status | uninstall]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/../../scripts/setup.py *)
---

# telemetry status line setup

Argument: `$ARGUMENTS` (empty means install).

All changes go through `python3 ${CLAUDE_SKILL_DIR}/../../scripts/setup.py`, which prints JSON. Don't edit settings files by hand.

1. Run `python3 ${CLAUDE_SKILL_DIR}/../../scripts/setup.py --status`.

2. Act on the argument:

   - **`status`**: say which status line is in effect, which settings file sets it, and whether it's telemetry's (`telemetry_active`). Stop.

   - **`uninstall`**: run `--uninstall` and report the result. Mention that the plugin stays installed, that per-turn costs fall back to transcript-only until the status line is installed again, and that `/plugin uninstall telemetry@dev-toolkits` removes the plugin itself. Stop.

   - **Empty (install)**:
     - If `telemetry_active` is true, say it's already installed. Stop.
     - If `effective` shows another status line in **user** settings, show its `command` and ask whether to replace it: only one status line can be active, and telemetry needs its own to report untracked cost. If they decline, run `--dismiss` so the startup reminder stops, tell them `/telemetry:setup` still works later, and stop.
     - Run `--install`. Report the file written and, if `previous` is set, the entry it replaced (so they can restore it).
     - If `overridden_by` is set, a higher-precedence settings file (project, local project or managed) still wins. Tell them which file, and that telemetry's status line won't show in that project until that entry is removed. Don't edit that file.

3. After an install, say the status line appears on its next refresh (within 30 seconds, or after the next reply); no restart is needed.
