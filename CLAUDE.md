# plugin-marketplace

Claude Code plugins, one per directory under `plugins/`, each listed in `.claude-plugin/marketplace.json`.

## Rules for every plugin
- Deterministic checks go in scripts in `plugins/<plugin>/bin/`. Agents only judge prose.
- Scripts are standard-library Python: no file extension, executable, `#!/usr/bin/env python3`.
- Tests use unittest in `plugins/<plugin>/tests/` and run scripts through `subprocess` with `sys.executable`.
- Keep one source of truth per fact. Other files read it or point to it.

## Commands
- Test a plugin: `python3 -m unittest discover -s plugins/<plugin>/tests`
- Validate a plugin: `claude plugin validate plugins/<plugin>`
