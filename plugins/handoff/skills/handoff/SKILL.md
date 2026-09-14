---
name: handoff
description: Write a self-contained handoff brief of the current session to a local Markdown file so the user can /clear and resume in a fresh agent. Use when the user says "handoff", "write a handoff", "prepare a brief for a new agent/session", or "I want to clear and restart".
argument-hint: "[focus or output path]"
---

# Handoff

Write a brief that a fresh agent with **no context** can act on. You are the only one who has this
session's context; the next agent sees only the file. Run in this session on its current model:
do not delegate the brief to a subagent, which cannot see the conversation.

## 1. Verify state instead of recalling it

Facts drift during a long session. Before writing, cheaply check what the brief will assert:

- In each git repo touched this session: `git status --short`, `git branch --show-current`, and
  `git log --oneline -5`.
- That files and paths you will reference exist.

Do not rerun slow test suites or builds. Report the last known result and when it was observed.
Mark anything you could not verify as **unverified**.

## 2. Write the brief

**Path:** if the user passed arguments and they include a file path, write there. Otherwise
write to `~/.claude/handoffs/<timestamp>-<slug>.md`, where `<timestamp>` comes from
`date +%Y-%m-%d-%H%M` and `<slug>` is two to four kebab-case words naming the work. Treat any
other argument text as what the brief should focus on.

Arguments (may be empty): $ARGUMENTS

Use this structure, in this order:

```markdown
# Handoff: <short title>

Written <timestamp> from <working directory>.

## Goal
What the user is ultimately trying to achieve, and what "done" looks like.

## Current state
What is done, what is in progress, and what is untouched. Include branch and uncommitted changes.
Mark each claim verified or unverified.

## Decisions
Each decision made this session and why, including options rejected and the reason.

## Dead ends
Approaches tried that failed or were abandoned, and why, so they are not retried.

## Constraints and preferences
Requirements, gotchas, and user preferences stated this session that are not already in
CLAUDE.md or memory.

## Key files
`path:line` references with one line on each file's role.

## Open questions
Unresolved questions, and who or what can answer them.

## Next steps
An ordered list the next agent can start on immediately, with exact commands where relevant.
```

Rules:

- Keep it tight: aim for under 150 lines. Prefer `path:line` references over pasted code.
- Include exact commands, error messages, and identifiers where the next agent needs them.
- Record reasons, not just outcomes. A decision without its reason gets relitigated.
- Write "None" for an empty section rather than padding it.
- Never include secrets, tokens, or credentials.
- Do not repeat what CLAUDE.md, memory, or git history already records.

## 3. Report

Reply with only:

1. The file path.
2. A one-line summary of the brief.
3. A resume prompt to paste after `/clear`: `Read <path> and continue from "Next steps".`
4. A reminder to skim the brief and correct anything wrong before clearing.
