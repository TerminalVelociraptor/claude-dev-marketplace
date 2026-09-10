---
name: profile-update
description: Update the existing learner profile — add a language or growth edge, adjust per-edge levels, or change preferences, background, pronoun, or goals. Use when the user says "add a language/edge to my learning profile", "update my learning preferences", "change my learning profile", or similar. Evaluates the whole resulting profile for coherence before writing rather than blindly applying the change.
argument-hint: [what to change]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-profile *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-vocab *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-queue *), Read, Write, Edit
---

# Update the learner profile

Binaries are at `${CLAUDE_SKILL_DIR}/../../bin/`.

## 0. Load the current profile

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile show
```

If it reports `NO_PROFILE`, there is nothing to update — offer `learning:profile-init` instead and
stop.

## 1. Make the targeted change

- **Adding a language or edge**: register it in the living vocabulary first, then reflect it in the
  profile prose with a scope and a **level** (for a from-scratch language, `<lang>-fundamentals` at
  novice):
  ```
  ${CLAUDE_SKILL_DIR}/../../bin/learn-vocab add --edges <edge> --langs <lang>
  ```
- **Adjusting level / depth / preferences / background / pronoun / goals**: change the prose of the
  relevant section.

## 2. Advisory evaluation of the whole profile (do NOT blindly accept)

Re-evaluate the ENTIRE resulting profile, not just the delta, and raise anything off before
writing:

- Edge ↔ language coherence, level coherence, redundancy / overlap, focus (few edges), and slug
  reuse (check `learn-vocab list`; reuse beats coining).

Discuss and resolve with the user. Advisory — they decide — but raise concerns rather than
rubber-stamping.

## 3. Write and confirm

Get the path:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile path
```

Write the full updated content with the `Write` tool (or use `Edit` for a small in-place change to
the file at that path). Then run `learn-profile show` and state in one or two lines what changed.

> Note: the global profile is loaded once at session start, so a change here applies to the NEXT
> learning session, not the one in progress.
```
