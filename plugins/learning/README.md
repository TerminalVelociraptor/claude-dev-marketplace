# learning

Turns Claude Code into an interactive coding teacher for deliberate practice, across the languages
and growth edges in your profile.

Two session modes over a shared teaching core, a generated personal profile, and a global
spaced-repetition log. Measurable claims are verified with your project's own tooling before they
are taught.

## Skills

| Command | Who drives | Use it when |
|---|---|---|
| `/learning:pair` | **You write the code.** Claude is silent between check-ins. | You want to implement something yourself with coaching. |
| `/learning:guided` | **Claude writes**, narrating and stopping for your predictions. | You want the work done but want to learn from watching. |
| `/learning:flag` | — | "flag this", "what should I study", "I already know this". |

The two modes are **user-invoked only** (`disable-model-invocation: true`). Entering a learning
mode is a deliberate act, and it keeps `pair` and `guided` — which occupy nearly identical trigger
space — from being auto-selected wrongly. It also costs zero skill-listing context budget.

`flag` is the only one Claude triggers on its own, so a concept you hit during ordinary work still
reaches the queue.

Both modes close the same way. If a logged concept is due that the session did not cover, Claude
offers **one skippable recall question** on it. If the log shows a calibration threshold crossed on
an edge the session touched, it suggests `profile-update` in one line. When neither applies it says
nothing. This is what keeps spacing and graduation in use without a separate practice mode.

## Your profile

The teaching modes calibrate against a **personal profile** — who you are, the breadth to assume,
your **growth edges (each with its own level: novice / proficient / expert, and a depth note split
into conceptual and hands-on)**, the languages in scope, and your preferences. It is not shipped:
the first time you run `pair` or `guided` without one, they route you into `learning:profile-init`.
It interviews you, checks the result for coherence before writing anything, registers the final
edges and languages in your living vocabulary, and lints the written file.

| Command | Use it when |
|---|---|
| `/learning:profile-init` | First-time setup, or rebuilding the profile from scratch. |
| `/learning:profile-update` | Add a language or edge, adjust a level, or change preferences/goals. |

Levels are **starting priors**. Within a session Claude raises difficulty when you show mastery and
says so, but a lasting level change only happens through `profile-update`.

Each language is one line with a **role** and a proficiency:

```markdown
- `rust` (Rust) — role: learning. Proficiency: new; reads simple code, has written little.
- `java` (Java) — role: analogy. Proficiency: fluent; useful for contrasts.
```

A `learning` language is pitched at its own proficiency even off a growth edge. A `working`
language is one you use fluently. An `analogy` language is a bridge, and Claude will not switch an
exercise into one without asking. The older comma-separated list still loads; `learn-profile check`
flags it and `profile-update` migrates it.

Learning a language from scratch is just a **novice-level, language-oriented edge** named
`<lang>-fundamentals` (e.g. `rust-fundamentals`). It coexists with expert edges, and each is pitched
at its own level.

### Per-project focus (optional)

Drop a `.claude/learning.local.md` at a repo's root to scope a session's attention without
fragmenting the global log:

```markdown
---
edges: [concurrency]
languages: [kotlin]
---
Focus for this repo: coroutine cancellation in the sync worker.
```

Only the `edges:` and `languages:` keys count; the body is the focus description. The modes read it
at session start (from the git top level, or the current directory outside a repo), scope queue
views to it, and report slugs that are not in your vocabulary. A focus edge your profile does not
list gets an offer to run `profile-update`, since it needs a level. The overlay chooses *what* to
emphasize, never how deep, and an explicit session topic overrides it. The log stays global, so
spacing and cross-project transfer are unaffected.

## Shared core

Edit these once; all skills follow.

| File | Purpose |
|---|---|
| `shared/calibration-core.md` | Invariant teaching rules: the session-start profile bootstrap, the project overlay, precedence, the depth rule, calibration evidence, tuning constants, and the fixed `type`/`signal` vocabulary. |
| `shared/teaching-protocol.md` | Predict-before-reveal, bounded correction, escape valve, verification rule. |
| `shared/hint-ladder.md` | Graduated unblocking and the retrieval-first review. |

**Precedence**, when rules pull different ways: the invariants (verify before asserting, bounded
correction, two misses make it easier, `pair` never writes your code) beat explicit live requests
(the mode, the session topic, "just tell me"). Those beat your profile preferences, which shape
*how* depth is delivered. Preferences beat the depth rule's defaults.

The **calibration core** and protocol are **spliced into each mode SKILL.md at build time** by
`bin/sync-shared`, between `<!-- BEGIN shared:... -->` markers. `shared/` stays the single place you
edit; the skills carry a generated copy.

The **personal profile** is not shipped or spliced. It is generated per user by the
`learning:profile-init` skill into `~/.config/learning-toolkit/learning-profile.md` and loaded at
session start via `bin/learn-profile show`. A generic skeleton lives at
`templates/learning-profile.template.md`, and a filled reference at
`templates/learning-profile.example.md` (not loaded at runtime).

**After editing anything in `shared/`, run `bin/sync-shared`.** Use `bin/sync-shared --check` in CI
or a pre-commit hook to catch drift. `--check` also fails if `pair` or `guided` is missing, or has
lost one of its required shared blocks.

This is build-time rather than runtime for a concrete reason. Claude Code's dynamic context
injection (`` ```! `` blocks) is permission-checked, and the check matches the *entire block* as one
opaque string — so no `allowed-tools` rule can ever satisfy it. In default permission mode the
injection fails and the whole turn is discarded: empty output, zero turns, no visible error. That
was verified here against an installed build, not assumed. Splicing at build time delivers what
runtime injection promised (the text is guaranteed present, byte for byte) with no runtime
dependency and no silent-failure mode.

The hint ladder is *not* spliced — it is referenced by path and read only when someone is actually
stuck, which is real progressive disclosure rather than a permanent token cost.

## Tools

All in `bin/`, all dependency-free Python 3.

```bash
learn-log      --type hit --concept lock-ordering --edge concurrency --lang java   # validated append
learn-queue    --due             # due now; graduated concepts due a retention check follow, as maint
learn-queue    --pick 4          # what to practise, interleaved across edges
learn-queue    --due --edge concurrency,memory --lang kotlin   # any view, scoped (comma list or repeat)
learn-queue    --stats           # success rate vs target, per-edge rates, graduations, reactivations
learn-queue    --signals         # calibration evidence: threshold crossings only (--all for counts)
learn-queue    --concepts        # existing slugs, to avoid coining duplicates
learn-vocab    list|add|remove --edges X --langs Y             # the living edge/lang vocabulary
learn-profile  path [--ensure-dir] | show | check [--strict]   # locate, load, or lint the profile
learn-baseline set|commits|advance|clear                        # pair check-in windows
learn-session  start|end|status|config reinject on
sync-shared    [--check]        # splice shared/ into the skills after editing it
```

`learn-profile check` is read-only and tolerant. It warns on missing sections, an edge without
`Level:`/`Depth:` or with an unknown level, edge or language slugs `learn-log` would reject,
`learning` languages that no edge covers, and undated progress markers such as "chapter 3" or "this
week". It exits 0 regardless unless you pass `--strict`; a missing profile exits 1, as `show` does.
`profile-init` and `profile-update` run it after writing.

Verification uses **your project's own tooling**: its build, tests, performance harness and
profilers. No build or test command is pre-approved in the skills, so Claude asks before running
one.

## Config files

Everything lives in `${XDG_CONFIG_HOME:-$HOME/.config}/learning-toolkit/`. All of these are
created **lazily on first use**, so "missing" is normal rather than broken:

| File | What | Created by |
|---|---|---|
| `learning-log.jsonl` | the learning log | first logged entry |
| `config.json` | toolkit settings (`reinject`) | `learn-session config <key> <val>` |
| `vocab.json` | living edge/lang vocabulary | `learn-vocab add`, or any first use (seeded) |
| `learning-profile.md` | the personal learner profile | `learning:profile-init` |

```bash
learn-session status     # where everything is, and what exists yet
```

A malformed `vocab.json` is never rewritten. Reads fall back to the seed vocabulary with a warning
that names the file, so logging keeps working, and `learn-vocab add`/`remove` refuse until you fix
the file or move it aside.

## The log

Global and append-only at `${XDG_CONFIG_HOME:-$HOME/.config}/learning-toolkit/learning-log.jsonl`.
One log across **all** projects, because growth edges are cross-project skills — a concept practised
in one repo should inform spacing everywhere. Every entry carries `project`, so extractors can slice
per-repo while the default view stays global.

One JSON object per line, optimised for `tail`/`grep` rather than for reading. `type` and `signal` are closed and enforced by `learn-log` (they are bound to the queue's
scheduling logic). `edge` and `lang` are a living vocabulary you grow with `learn-vocab`; `skill`
is derived from the installed skills. A value outside the valid set is rejected rather than
silently corrupting the queue.

```
type    taught skipped edge-confirmed calibration to-cover escape hit miss
        graduated reactivated self-assessment
edge    living — your own vocabulary; see `learn-vocab list`; `none` always valid
lang    living — your own vocabulary; see `learn-vocab list`; `none` always valid
signal  calibration     -> already-known declined-deepdive below-level above-level
        self-assessment -> found-self missed-self overconfident underconfident
```

- `calibration` and `self-assessment` entries **require** a `signal`; older entries without one are
  still read. `below-level` means an explanation was pitched below you, `above-level` above you.
- Each entry is appended with a single write on an `O_APPEND` descriptor, so concurrent sessions
  cannot split a line.
- When a known concept is logged under an edge it has never carried, `learn-log` prints a note; it
  is usually a mislabel.
- A concept's edges and languages are every non-`none` value it has been logged under. Filters
  match any of them, and tables show the most frequent (ties go to the latest).

The `pair` baseline commit is deliberately **not** here — a SHA is project-specific and lives in
`.git/learning-baseline`, where it survives restarts and can never be committed or dirty
`git status`.

### Scheduling

`learn-queue` derives everything from the log:

- A concept is **schedulable** only once it is queued (`to-cover`, `edge-confirmed`) or practised (a
  hit or miss). Concepts with only calibration, skipped, taught or escape entries are listed but
  never due or picked.
- A concept graduates after **3 successes**, each separated by at least **1, then 7 days**.
  Successes closer together than the current interval record but do not advance the stage —
  cramming does not earn graduation.
- A graduated concept is due for a **maintenance check 30 days** after its last counted success.
  `--due` lists these after active items, labeled `maint`; `--pick` adds at most one; the modes'
  closing recall can serve them. A maintenance hit schedules the next check.
- **Any miss returns a concept to active rotation**, resetting its stage and counting a
  reactivation. Retired is not deleted.
- Difficulty targets an **85% success rate**. Two misses running, or two recent escapes, force the
  next exercise *easier*, never harder — retrieval practice only pays off when retrieval mostly
  succeeds.

### Calibration evidence

`learn-queue --signals [--edge …] [--lang …] [--days N]` is read-only. By default it looks at the
last 14 days and prints only threshold crossings:

| On one edge, within the window | Crossing |
|---|---|
| ≥2 `already-known` / `below-level` | baseline may be higher |
| ≥2 `above-level`, or ≥3 escapes | pitched too high |
| ≥3 hits and 0 misses, across ≥2 concepts | consider raising level |

The modes check it at close for the edges a session touched and suggest `profile-update` when
something crosses. Nothing changes a level automatically.

## Tuning

Every constant lives in exactly two places, kept in sync: `shared/calibration-core.md` (what Claude
reads) and the top of `bin/learn-queue` (what is computed). That includes the `--signals`
thresholds.

```python
GRADUATION_SUCCESSES = 3
SPACING_DAYS         = [1, 7, 30]
SUCCESS_TARGET       = 0.85
```

**These are placeholders, not findings.** The two most likely to need real-world adjustment are the
success-rate target and the graduation threshold. Run `learn-queue --stats` after a few weeks: if
your success rate sits well under target the exercises are too hard, and well over means too easy.

## Protocol decay in long sessions

Skill content is loaded into the conversation **once and never re-read**, and auto-compaction keeps
only roughly the first 5,000 tokens of each skill. In a long session the protocol can therefore
fade — and the first rule to go is the one that fights the drive to finish: *ask them to predict,
then stop and wait*.

Two defences ship here. The shared core is kept small with the hard rules front-loaded, so
compaction's per-skill retention preserves them. And a `UserPromptSubmit` hook can deterministically
re-inject the core rules every turn. **The hook is off by default** and emits nothing unless a
learning session is active *and* it has been enabled:

```bash
bin/learn-session config reinject on
```

Turn it on if you notice Claude answering its own prediction questions, or writing code during
`pair`. Turn it off again when you do not need it — it costs tokens on every turn.

The reminder is generic: it names no edges and never injects your profile. A session marker older
than 24 hours is ignored, so a session that ended without `learn-session end` stops receiving
reminders; the next `learn-session start` deletes it.

## Install

```bash
claude plugin marketplace add /home/david/agent-tools/plugin-marketplace
claude plugin install learning@dev-toolkits --scope user
# restart Claude Code
```

To try it for a single session without installing:

```bash
claude --plugin-dir /home/david/agent-tools/plugin-marketplace/plugins/learning
```

After editing the plugin:

```bash
claude plugin marketplace update dev-toolkits
claude plugin update learning@dev-toolkits
```

If an update reports "already at latest" but you know it changed, uninstall and reinstall — that
path is reliable where `update` sometimes is not.

## Drill (removed in 0.5.0)

Version 0.4.0 shipped a third mode, `/learning:drill`, with a C/C++/Java measurement harness
(`bin/bench`, `templates/BenchHarness.java`). Both were removed in 0.5.0. The queue, graduation and
`--pick` logic a practice mode needs are kept and tested. To restore drill:

```bash
git checkout learning-drill-v0.4.0 -- skills/drill bin/bench templates/BenchHarness.java
```

Then:

- Add `"drill": {"calibration-core", "teaching-protocol"}` to `REQUIRED` in `bin/sync-shared`, and
  run `bin/sync-shared`.
- Rewrite its verification section for languages other than C/C++; under the generic Rule 7 it must
  use the project's tooling or label a claim unverified.
- Give its exercise subagent the profile's level, depth note, language proficiency and analogy rules
  for the target, and keep the expected answer separate from the student-facing prompt.

## Honest limits

The principles here — retrieval practice, spacing, interleaving, expertise reversal, desirable
difficulty, the guidance hypothesis, incomplete-example transfer — are well-supported for
deliberate factual and procedural learning, largely in lab settings.

Applying them to an experienced developer learning via LLM tutoring on real work is **principled
extrapolation, not a validated method**. Complex-skill transfer is where the underlying evidence is
weakest and most mixed.

The log exists so this can be checked rather than believed. If `learn-queue --stats` shows nothing
improving after a few months, that is data, and abandoning or reshaping this is the correct
response to it.
