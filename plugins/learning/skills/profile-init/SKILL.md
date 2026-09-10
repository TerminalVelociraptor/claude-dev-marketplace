---
name: profile-init
description: Create the personal learner profile the teaching modes calibrate against. Use when no profile exists yet (the pair/guided/drill modes route here automatically on first use), or when the user asks to set up or create their learning profile from scratch. Interviews the user, evaluates the result for coherence before writing, and registers any new edges or languages in the living vocabulary.
argument-hint: [optional: anything to seed the interview]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-profile *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-vocab *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-queue *), Write, Read
---

# Create the learner profile

Builds the personal half of the profile (`~/.config/learning-toolkit/learning-profile.md`) through
a short interview, then writes it. The invariant teaching rules live in
`shared/calibration-core.md` and are NOT part of this interview.

Binaries are at `${CLAUDE_SKILL_DIR}/../../bin/`.

## 0. Don't clobber an existing profile

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile show
```

If it already prints a profile, stop and offer `learning:profile-update` instead — this skill is
for first-time creation. Only continue if it reports `NO_PROFILE`.

Get the target path (and create the config dir):

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile path --ensure-dir
```

## 1. Interview

Ask these in order. Use `AskUserQuestion` for the structured items, free text for the open ones.
One topic at a time.

1. **Background / breadth to assume** (free text). What should the coach treat as already-known and
   never re-explain?
2. **Pronoun** (`AskUserQuestion`: they/them, he/him, she/her, other).
3. **Growth edges** (`AskUserQuestion`, multi-select). Offer the current vocabulary as the menu:
   ```
   ${CLAUDE_SKILL_DIR}/../../bin/learn-vocab list --edges
   ```
   plus a custom option. Keep it to a FEW — many edges dilute practice. For each chosen edge,
   collect: scope (one line), **level** (novice / proficient / expert), and a depth note. To learn
   a language from scratch, name the edge `<lang>-fundamentals` at level novice.
4. **Languages in scope** (`AskUserQuestion`, multi-select). Menu from:
   ```
   ${CLAUDE_SKILL_DIR}/../../bin/learn-vocab list --langs
   ```
   plus custom.
5. **Per-edge goals** (free text, optional). What does "better" look like per edge?
6. **Preferences / learning styles** (free text). Pacing, how they want corrections, examples vs
   theory.

Do NOT ask about tuning constants, the `type`/`signal` vocabulary, or the honesty note — those are
invariant and live in `calibration-core`.

## 2. Register new vocabulary

For every edge or language the user named that is not already in the vocabulary, add it (one
command per axis):

```
${CLAUDE_SKILL_DIR}/../../bin/learn-vocab add --edges rust-fundamentals --langs rust
```

This is what makes the new value loggable by `learn-log` — without it, logging that edge/lang is
rejected.

## 3. Advisory evaluation (do NOT blindly accept)

Before writing, evaluate the WHOLE profile for coherence and raise anything off with the user:

- **Edge ↔ language coherence** — e.g. `hpc` with only Python in scope is thin; is a systems
  language intended, or did they mean numpy/Cython?
- **Level coherence** — an edge marked expert against a language marked novice, and similar
  mismatches.
- **Redundancy / overlap** — near-duplicate edges (`concurrency` vs `parallelism`), duplicate
  scopes.
- **Focus** — the system's own wisdom is "few edges." Many edges dilute spaced practice; suggest
  prioritizing.
- **Slug reuse** — a proposed edge/lang that duplicates an existing one under a different name
  (check `learn-vocab list`); reuse beats coining.

Discuss and resolve with the user. This is advisory — they decide — but raise it, don't
rubber-stamp.

## 4. Write the profile

Compose from `${CLAUDE_PLUGIN_ROOT}/templates/learning-profile.template.md`, filling every section
from the interview (including per-edge level and depth note). Write it with the `Write` tool to the
path reported by `learn-profile path` in step 0.

Then confirm: run `learn-profile show` to prove it loads, and summarize in two or three lines what
was set.
