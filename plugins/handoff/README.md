# handoff

Write a session brief a fresh agent can pick up, then `/clear` and restart.

## Install / uninstall

- **Install:** `/plugin install handoff@dev-toolkits`
- **Uninstall:** `/plugin uninstall handoff@dev-toolkits`

## Usage

1. At a natural stopping point, run `/handoff:handoff`, optionally with a focus or an output path:
   `/handoff:handoff focus on the auth migration`.
2. The brief is written to `~/.claude/handoffs/<timestamp>-<slug>.md` by default, with the
   sections defined in `templates/brief.md`.
3. Skim it and fix anything wrong, then `/clear` and paste the resume prompt it gives you.

The skill writes the brief in the current session on the current model. Only that session has the
context, and switching models or delegating the writing would reread the whole transcript without
cache.

## How a brief is checked

1. `bin/check-handoff <brief>` runs the checks that need no judgment: structure against the
   template, Key files paths, `path:line` references, likely secrets, and length.
2. The `brief-reader` subagent reads only the brief and lists what a fresh agent would have to
   guess or ask. It runs once per handoff, on Sonnet, and isn't cheap. In the first test, a
   stand-in for `brief-reader` took about two minutes and 96k tokens over two requests to read a
   300-line brief: 47k cache writes, 36k cache reads, and 12k output.

Each cold read's token usage appears in the handoff report and is appended to a log, read from the
subagent's transcript rather than its completion notice (that figure is roughly the last request's
size, not the run's total). To see medians and maximums across runs, and where the log is:

```bash
/home/david/agent-tools/plugin-marketplace/plugins/handoff/bin/cold-read-usage --summary
```

`templates/brief.md` is the single source of truth for the brief's structure. The skill, the
script, and the tests all read it, so adding or changing a section means editing only the
template. Its `<!-- check: ... -->` comments mark optional sections, the plan section, the section
whose paths must exist, and the line target.

## Development testing

```bash
claude --plugin-dir /home/david/agent-tools/plugin-marketplace/plugins/handoff
python3 -m unittest discover -s /home/david/agent-tools/plugin-marketplace/plugins/handoff/tests
```
