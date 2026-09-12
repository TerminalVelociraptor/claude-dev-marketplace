---
name: profile-init
description: Create the personal learner profile the teaching modes calibrate against. Use when no profile exists yet (the pair/guided modes route here automatically on first use), or when the user asks to set up or create their learning profile from scratch. Interviews the user, evaluates the result for coherence before writing, and registers any new edges or languages in the living vocabulary.
argument-hint: [optional: anything to seed the interview]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-profile *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-vocab *), Bash(${CLAUDE_SKILL_DIR}/../../bin/learn-queue *), Write, Read
---

# Create the learner profile

Builds the personal half of the profile (`~/.config/learning-toolkit/learning-profile.md`) through
a short interview, then writes it. The invariant teaching rules live in
`shared/calibration-core.md` and are NOT part of this interview.

Binaries are at `${CLAUDE_SKILL_DIR}/../../bin/`.

**Order:** interview → advisory evaluation → final slug set → register vocabulary → write → check
→ show. Nothing is registered or written until the user has resolved the evaluation.

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

Ask these in order, one topic at a time. Use `AskUserQuestion` for the structured items. It takes
2–4 options, so when a vocabulary list has more than 3 entries, ask in free text instead, normalize
the answer to existing slugs, and confirm any new one.

1. **Background / breadth to assume** (free text). What should the coach treat as already-known and
   never re-explain?
2. **Pronoun** (`AskUserQuestion`: they/them, he/him, she/her, other).
3. **Growth edges.** Offer the current vocabulary:
   ```
   ${CLAUDE_SKILL_DIR}/../../bin/learn-vocab list --edges
   ```
   plus a custom option. Keep it to a FEW — many edges dilute spaced practice. For each chosen edge,
   collect:
   - **scope** (one line);
   - **level**: `novice` — little hands-on; `proficient` — works unaided, with gaps in mechanism;
     `expert` — could teach it;
   - a **depth note** in two halves: what they understand *conceptually*, and what they have done
     *hands-on*.

   To learn a language from scratch, name the edge `<lang>-fundamentals` at level novice.
4. **Languages in scope.** Offer:
   ```
   ${CLAUDE_SKILL_DIR}/../../bin/learn-vocab list --langs
   ```
   For each chosen language, record one line: the slug (normalize display names — "C++" → `cpp`,
   "Rust" → `rust`), the display name, a **role** — `learning` (being learned), `working` (used
   fluently), or `analogy` (a reference to bridge from) — and a one-line **proficiency** that states
   conceptual vs hands-on when they differ.
5. **Per-edge goals** (free text, optional). What does "better" look like per edge? Phrase each as
   evidence the log can show, not a date or a chapter.
6. **Teaching-control preferences.** One multi-select `AskUserQuestion` with four defaults to
   confirm or edit:
   - (a) *Theory-to-practice:* brief theory, one compact example, then practice.
   - (b) *Reveal boundary:* hints before the answer; the full correction after two attempts
     (Rule 2); an explicit "just tell me" is honored (Rule 4).
   - (c) *Calibration stance:* levels are priors; raise difficulty on demonstrated mastery and say so.
   - (d) *Analogies:* use the `analogy`-role languages as bridges and name where each one breaks.

   Then ask in free text for anything else or any deviation. Record each confirmed item as one
   short bullet.

Do NOT ask about tuning constants, the `type`/`signal` vocabulary, or the honesty note — those are
invariant and live in `calibration-core`.

**Route by lifetime.** Stable ability, background and preferences go in the profile. Current repo
focus ("focus on Android in this repo") goes in that repo's `.claude/learning.local.md` overlay,
never the profile. Concept outcomes belong in the log. Do not add a global current-priority field.

## 2. Advisory evaluation (do NOT blindly accept)

Before registering or writing anything, evaluate the WHOLE profile for coherence and raise anything
off with the user:

- **Edge ↔ language coherence** — e.g. `hpc` with only Python in scope is thin; is a systems
  language intended, or did they mean numpy/Cython?
- **Learning-language coverage** — each `role: learning` language needs a `<lang>-fundamentals`
  edge, or an edge whose depth note says how that language's own material is pitched. Otherwise
  warn: outside a growth edge the tutor is terse.
- **Level coherence** — compare each edge's level with the proficiency recorded for the languages
  it will be practised in (an `expert` edge taught only through a language they are new to is
  suspect).
- **Preferences vs the core** — flag preferences that interact with the invariants: the novice
  default of more worked examples, Rule 2's full correction after two attempts, Rule 4's escape
  valve, and `guided`, where Claude writes the code. Record the user's resolution in the preference
  wording.
- **Stable vs dynamic** — no undated progress markers ("read chapter 1", "just starting", "this
  week"): date them ("as of 2026-09") or leave them out. Phrase gates as evidence the log can show
  ("until the log shows hits on ownership"). No mastery, queue state or toolchain in the profile.
- **Redundancy / overlap** — near-duplicate edges (`concurrency` vs `parallelism`), duplicate
  scopes.
- **Focus** — the system's own wisdom is "few edges." Many edges dilute spaced practice; suggest
  prioritizing.
- **Slug reuse** — a proposed edge/lang that duplicates an existing one under a different name
  (check `learn-vocab list`); reuse beats coining.

Discuss and resolve with the user. This is advisory — they decide — but raise it, don't
rubber-stamp.

## 3. Register the final vocabulary

From the resolved profile, compute the final edge and language slugs and add only those not
already registered, in one command:

```
${CLAUDE_SKILL_DIR}/../../bin/learn-vocab add --edges rust-fundamentals --langs rust
```

This is what makes the new values loggable. **If it fails** (for example on a malformed
`vocab.json`), stop, report the error, and do not write the profile.

## 4. Write the profile

Compose from `${CLAUDE_PLUGIN_ROOT}/templates/learning-profile.template.md`, filling every section:
per-edge level and two-part depth note, one line per language with its role and proficiency, and
one bullet per preference. Replace every `<…>` placeholder. Write it with the `Write` tool to the
path reported by `learn-profile path` in step 0.

## 5. Check and confirm

```
${CLAUDE_SKILL_DIR}/../../bin/learn-profile check
${CLAUDE_SKILL_DIR}/../../bin/learn-profile show
```

`check` is a tolerant lint. Fix any warning that is a real mistake, with the user's agreement;
intentional prose can stand. Then summarize in two or three lines what was set, plus:

- one line on the per-repo overlay: a `.claude/learning.local.md` with `edges:`/`languages:` scopes a
  repo's sessions without touching the profile;
- if seed edges remain in the vocabulary that this profile does not use, name them in one line and
  offer `learn-vocab remove --edges <…>`. The user decides; removal never rewrites the log.
