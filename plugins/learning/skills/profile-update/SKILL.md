---
name: profile-update
description: Update the existing learner profile — add a language or growth edge, adjust per-edge levels, or change preferences, background, pronoun, or goals. Use when the user says "add a language/edge to my learning profile", "update my learning preferences", "change my learning profile", or similar. Evaluates the whole resulting profile for coherence before writing rather than blindly applying the change.
argument-hint: [what to change]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-profile *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-vocab *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-queue *), Read, Write, Edit
---

# Update the learner profile

Binaries are at `${CLAUDE_SKILL_DIR}/../../bin/`.

**Order:** load → draft the change → advisory evaluation of the whole profile → final slug set →
register vocabulary → write → check → show. Nothing is registered or written until the user has
resolved the evaluation.

## 0. Load the current profile

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile show
```

If it reports `NO_PROFILE`, there is nothing to update — offer `learning:profile-init` instead and
stop.

## 1. Draft the targeted change

Draft it; register and write nothing yet.

- **Adding an edge**: a scope, a **level** (`novice` — little hands-on; `proficient` — works
  unaided, with gaps in mechanism; `expert` — could teach it), and a depth note in two halves:
  conceptual and hands-on. For a from-scratch language, `<lang>-fundamentals` at novice.
- **Adding a language**: one line — the slug (normalize display names: "C++" → `cpp`), the display
  name, a role `learning | working | analogy`, and a one-line proficiency that states conceptual vs
  hands-on when they differ.
- **Adjusting level / depth / preferences / background / pronoun / goals**: change the prose of the
  relevant section. For preferences, the four teaching-control items in `learning:profile-init`
  (theory-to-practice, reveal boundary, levels as priors, analogy limits) are a useful checklist.
- **A level change prompted by calibration evidence**: show the evidence first
  (`${CLAUDE_SKILL_DIR}/../../bin/learn-queue --signals --all --edge <edge>`); the user decides.
- **Migrate language lines you touch** to the one-line format
  (`` - `slug` (Name) — role: … Proficiency: … ``). If the section is still an old comma list or
  grouped bullets, offer to migrate all of it.

Current repo focus goes in that repo's `.claude/learning.local.md` overlay, never the profile.

## 2. Advisory evaluation of the whole profile (do NOT blindly accept)

Re-evaluate the ENTIRE resulting profile, not just the delta, with the same checks as
`learning:profile-init`:

- Edge ↔ language coherence.
- Learning-language coverage: each `role: learning` language has a `<lang>-fundamentals` edge or an
  edge depth note saying how its material is pitched; otherwise the tutor is terse on it.
- Level coherence against the recorded language proficiencies.
- Preferences vs the core: the novice default of more worked examples, Rule 2, Rule 4, and `guided`
  writing the code. Record the resolution in the preference wording.
- Stable vs dynamic: no undated progress markers; gates phrased as evidence the log can show; no
  mastery or queue state.
- Redundancy / overlap, focus (few edges), and slug reuse (check `learn-vocab list`; reuse beats
  coining).

Discuss and resolve with the user. Advisory — they decide — but raise concerns rather than
rubber-stamping.

## 3. Register the final vocabulary

Add only the final slugs that are not already registered:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-vocab add --edges <edge> --langs <lang>
```

If it fails, stop and report the error; do not write the profile.

## 4. Write, check, and confirm

Get the path:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile path
```

Write the full updated content with the `Write` tool (or use `Edit` for a small in-place change to
the file at that path). Then:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile check
${CLAUDE_SKILL_DIR}/../../bin/learn-profile show
```

Fix any warning that is a real mistake, with the user's agreement, then state in one or two lines
what changed.

> Note: the global profile is loaded once at session start, so a change here applies to the NEXT
> learning session, not the one in progress.
