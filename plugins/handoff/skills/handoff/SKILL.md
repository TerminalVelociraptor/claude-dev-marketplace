---
name: handoff
description: Write a self-contained handoff brief of the current session to a local Markdown file so the user can /clear and resume in a fresh agent. Use when the user says "handoff", "write a handoff", "prepare a brief for a new agent/session", or "I want to clear and restart".
argument-hint: "[focus or output path]"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/check-handoff *), Bash(${CLAUDE_SKILL_DIR}/../../bin/cold-read-usage *)
---

# Handoff

Write a brief that a fresh agent with **no context** can act on. You are the only one who has this
session's context; the next agent sees only the file. Write the brief yourself, in this session on
its current model: a subagent cannot see the conversation. A subagent only *reads* the finished
brief in step 4, because a reader with no context is the best test of whether the brief is enough.

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

**Structure:** read `${CLAUDE_SKILL_DIR}/../../templates/brief.md` and follow it: its sections, their
order, and the guidance under each heading. Replace the guidance with content, and leave out the
`<!-- check: ... -->` comments. Include a section marked optional only when its guidance applies.

Rules:

- Keep it tight, and stay within the template's line target unless the brief has a Plan. Never cut
  reasons, step detail, or undecided items to meet the target. Prefer `path:line` references over
  pasted code.
- Include exact commands, error messages, and identifiers where the next agent needs them.
- Record reasons, not just outcomes. A decision without its reason gets relitigated.
- Separate what the user agreed from what you assumed. If you assumed a detail and the user never
  confirmed it, put it under Undecided in its Plan step or under Open questions, never under
  Decisions or Agreed.
- If the session produced a plan, carry its detail into the Plan section instead of summarizing it
  in a line under Goal. For each step, ask what you would have to decide while building it, even
  if nobody raised it, and list those details as Undecided.
- Use the Terms section for any word this session gave a local meaning, especially one that clashes
  with the project's own docs.
- Write "None" for an empty section rather than padding it.
- Never include secrets, tokens, or credentials.
- Do not repeat what CLAUDE.md, memory, or git history already records.

## 3. Run the deterministic checks

```bash
${CLAUDE_SKILL_DIR}/../../bin/check-handoff <brief path>
```

It checks structure against the template, Key files paths, `path:line` references, likely secrets,
and length. Fix every error. A warning is a judgment call: fix it, or keep it for a reason you can
state.

## 4. Cold read

Launch the `handoff:brief-reader` agent once, passing only the brief's absolute path. Add nothing
from the session: the point is to learn what the brief conveys on its own. From the Agent result,
keep the transcript path (`output_file`) and the agent id for step 5.

Resolve each gap it reports:

- **You know the answer from the session, or the brief was ambiguous:** add the detail or reword
  the brief. Count it as filled.
- **Nobody decided it:** add it under Undecided in its Plan step, or under Open questions. Count it
  as undecided.

Do not launch the reader a second time. Rerun `check-handoff` after your edits and fix any errors.

## 5. Record the cold read's usage, then report

Record the cold read's token usage, with the transcript path and agent id from step 4 and your
counts from resolving its gaps. Leave out either one the Agent result didn't give:

```bash
${CLAUDE_SKILL_DIR}/../../bin/cold-read-usage <transcript path> --agent-id <agent id> --brief <brief path> --filled <N> --undecided <M>
```

It prints one line and appends a record to its log. A non-zero exit means usage couldn't be read,
but the line is still printed.

Reply with only:

1. The file path.
2. A one-line summary of the brief.
3. The line `cold-read-usage` printed, verbatim.
4. A resume prompt to paste after `/clear`: `Read <path> and continue from "Next steps".`
5. A reminder to skim the brief and correct anything wrong before clearing.
