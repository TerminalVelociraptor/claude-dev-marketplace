# handoff

Write a session brief a fresh agent can pick up, then `/clear` and restart.

## Install / uninstall

- **Install:** `/plugin install handoff@dev-toolkits`
- **Uninstall:** `/plugin uninstall handoff@dev-toolkits`

## Usage

1. At a natural stopping point, run `/handoff:handoff`, optionally with a focus or an output path:
   `/handoff:handoff focus on the auth migration`.
2. The brief is written to `~/.claude/handoffs/<timestamp>-<slug>.md` by default: goal, current
   state, decisions, dead ends, constraints, key files, open questions, next steps.
3. Skim it and fix anything wrong, then `/clear` and paste the resume prompt it gives you.

The skill runs in the current session on the current model. Only that session has the context,
and switching models or delegating would reread the whole transcript without cache.

## Development testing

```bash
claude --plugin-dir /home/david/agent-tools/plugin-marketplace/plugins/handoff
```
