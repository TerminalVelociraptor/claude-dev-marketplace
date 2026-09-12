---
name: flag
description: Records a concept in the global learning log to study later, and reports what is currently due. Use when the user says "flag this", "flag that", "add that to my learning list", "I want to learn that later", or asks what they should study, what is due, or what is in their learning queue. Also use when they say "I already know this" while being explained something, which records a calibration signal.
when_to_use: Triggers on "flag this", "flag that for later", "note that down to learn", "what should I study", "what's due", "what's in my learning queue", "I already know this". Keep the response to one or two lines - this is a logging action during other work, not a teaching session.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-log *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-vocab *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-queue *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-profile *)
---

# Flag a concept / check the queue

A one-line logging action taken **during other work**. Do not start teaching, do not explain the
concept, do not derail what they were doing. Log it, confirm in one line, return to the task.

Binaries are at `${CLAUDE_SKILL_DIR}/../../bin/`.

## Flagging something to learn

Pick a **stable kebab-case slug in the global namespace** — the same concept must carry the same
slug in every repo, because that shared namespace is what makes cross-project spacing work.
Check for an existing one before coining a new one:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-queue --concepts
```

Reuse beats coining. `false-sharing` is right; `false-sharing-in-the-worker-pool` is not.

```
${CLAUDE_SKILL_DIR}/../../bin/learn-log --type to-cover --concept <slug> \
  --edge <edge> --lang <lang> --skill flag
```
Valid `edge`/`lang` values are the user's own living vocabulary — list them with
`${CLAUDE_SKILL_DIR}/../../bin/learn-vocab list`. `none` is always valid. If the right edge/lang
does not exist yet, `learn-log` will reject it and tell you the `learn-vocab add` command to create
it.

Infer `edge` and `lang` from context. If the edge is ambiguous, read the profile's growth edges
with `${CLAUDE_SKILL_DIR}/../../bin/learn-profile show` and prefer those slugs over the rest of the
vocabulary. Ask only if it is still genuinely ambiguous — a question here defeats the purpose of a
quick flag.

Confirm in one line: `flagged lock-ordering (concurrency/java)`.

## "I already know this"

They are correcting an explanation pitched too low. **Stop explaining immediately.** Do not apologise,
do not re-explain at a higher level unless they ask.

```
${CLAUDE_SKILL_DIR}/../../bin/learn-log --type calibration --concept <slug> \
  --edge <edge> --lang <lang> --skill flag --signal already-known
```

If they decline an offered deep-dive instead, use `--signal declined-deepdive`.

## "What should I study?" / "what's due?"

```
${CLAUDE_SKILL_DIR}/../../bin/learn-queue --due
```

Report it as-is. Add `--pick 4` if they want a session's worth, interleaved. Due items also come up
on their own: `pair` and `guided` offer one recall question on a due concept when a session closes.
