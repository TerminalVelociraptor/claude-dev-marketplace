#!/usr/bin/env python3
"""
telemetry setup: manage the statusLine entry that runs the telemetry status line.

  setup.py --check      SessionStart hook: if telemetry's status line isn't the one
                        in effect, tell the user to run /telemetry:setup
  setup.py --status     print (JSON) which status line is in effect and where it's set
  setup.py --install    point statusLine in ~/.claude/settings.json at telemetry
  setup.py --uninstall  remove telemetry's statusLine entry from ~/.claude/settings.json
  setup.py --dismiss    stop the startup reminder (user keeps their own status line)

Plugins can't set the main status line, a statusLine command can't use
${CLAUDE_PLUGIN_ROOT}, and installed plugin copies live in versioned
directories. So the entry reads the plugin's current directory from a file
that every telemetry hook run keeps up to date (cost_estimate.record_plugin_root).
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost_estimate  # noqa: E402

USER_SETTINGS = os.path.expanduser("~/.claude/settings.json")
DISMISSED_FILE = os.path.join(cost_estimate.STATE_ROOT, "setup_dismissed")
MARKER = "telemetry-state/plugin_root"
STATUS_LINE = {
    "type": "command",
    "command": 'python3 "$(cat ~/.claude/telemetry-state/plugin_root)/scripts/statusline.py"',
    "refreshInterval": 30,
}


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def settings_sources(cwd):
    """Settings files that can set statusLine, highest precedence first.
    (A --settings CLI flag can also set one; it can't be seen from here.)"""
    return [
        ("managed", "/etc/claude-code/managed-settings.json"),
        ("managed", "/Library/Application Support/ClaudeCode/managed-settings.json"),
        ("local project", os.path.join(cwd, ".claude", "settings.local.json")),
        ("project", os.path.join(cwd, ".claude", "settings.json")),
        ("user", USER_SETTINGS),
    ]


def effective_status_line(cwd):
    for source, path in settings_sources(cwd):
        value = read_json(path).get("statusLine")
        if isinstance(value, dict):
            return {"source": source, "path": path, "statusLine": value}
    return None


def is_telemetry(status_line):
    return MARKER in ((status_line or {}).get("command") or "")


def status(cwd):
    effective = effective_status_line(cwd)
    return {
        "plugin_root": cost_estimate.PLUGIN_ROOT,
        "effective": effective,
        "telemetry_active": bool(effective and is_telemetry(effective["statusLine"])),
        "dismissed": os.path.exists(DISMISSED_FILE),
    }


def write_settings(settings):
    os.makedirs(os.path.dirname(USER_SETTINGS), exist_ok=True)
    cost_estimate.write_atomic(USER_SETTINGS, json.dumps(settings, indent=2, ensure_ascii=False) + "\n")


def check(event):
    state = status(event.get("cwd") or os.getcwd())
    if state["telemetry_active"] or state["dismissed"]:
        return
    effective = state["effective"]
    if effective:
        message = (f"telemetry: the status line in effect comes from {effective['source']} settings "
                   f"({effective['path']}), so per-turn costs won't include calls missing from transcripts. "
                   "Run /telemetry:setup to switch to telemetry's status line.")
    else:
        message = ("telemetry: status line not set up, so per-turn costs won't include calls missing "
                   "from transcripts. Run /telemetry:setup.")
    print(json.dumps({"systemMessage": message}))


def install(cwd):
    cost_estimate.record_plugin_root()
    settings = read_json(USER_SETTINGS)
    previous = settings.get("statusLine")
    settings["statusLine"] = STATUS_LINE
    write_settings(settings)
    try:
        os.remove(DISMISSED_FILE)
    except FileNotFoundError:
        pass
    effective = effective_status_line(cwd)
    return {
        "installed": True,
        "path": USER_SETTINGS,
        "previous": previous,
        "statusLine": STATUS_LINE,
        "overridden_by": None if is_telemetry(effective["statusLine"]) else effective,
    }


def uninstall():
    settings = read_json(USER_SETTINGS)
    if not is_telemetry(settings.get("statusLine")):
        return {"uninstalled": False, "reason": f"{USER_SETTINGS} has no telemetry statusLine entry"}
    del settings["statusLine"]
    write_settings(settings)
    return {"uninstalled": True, "path": USER_SETTINGS}


def dismiss():
    cost_estimate.state_root()
    cost_estimate.write_atomic(DISMISSED_FILE, "")
    return {"dismissed": True}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--status"
    cwd = os.getcwd()
    if mode == "--check":
        raw = sys.stdin.read()
        try:
            event = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            event = {}
        check(event)
        return
    actions = {
        "--status": lambda: status(cwd),
        "--install": lambda: install(cwd),
        "--uninstall": uninstall,
        "--dismiss": dismiss,
    }
    if mode not in actions:
        sys.exit(f"usage: setup.py [{' | '.join(['--check', *actions])}]")
    print(json.dumps(actions[mode](), indent=2))


if __name__ == "__main__":
    main()
