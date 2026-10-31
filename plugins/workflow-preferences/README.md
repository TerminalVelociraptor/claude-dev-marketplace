# workflow-preferences

Workflow preferences for Claude Code, packaged as skills so they load only when relevant
instead of sitting in `CLAUDE.md` for every session.

Each skill lives in `skills/<name>/SKILL.md`, which is the source of truth for what it does
and when it loads. Invoke one explicitly with `/workflow-preferences:<name>`.
