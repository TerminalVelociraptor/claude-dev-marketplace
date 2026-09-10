# learning

Turns Claude Code into an interactive coding teacher for deliberate practice on **language
internals** and **HPC/optimization**, across the languages and growth edges in your profile.

Session skills over a shared teaching core, a generated personal profile, a global spaced-repetition log, and a measurement
harness that refuses to state a performance claim it has not measured.

## Skills

| Command | Who drives | Use it when |
|---|---|---|
| `/learning:pair` | **You write the code.** Claude is silent between check-ins. | You want to implement something yourself with coaching. |
| `/learning:guided` | **Claude writes**, narrating and stopping for your predictions. | You want the work done but want to learn from watching. |
| `/learning:drill` | **Claude drives** targeted practice from your logged weaknesses. | Deliberate practice instead of shipping something. |
| `/learning:flag` | — | "flag this", "what should I study", "I already know this". |

The first three are **user-invoked only** (`disable-model-invocation: true`). Entering a learning
mode is a deliberate act, and it keeps `pair` and `guided` — which occupy nearly identical trigger
space — from being auto-selected wrongly. It also costs zero skill-listing context budget.

`flag` is the only one Claude triggers on its own, so a concept you hit during ordinary work still
reaches the queue.

## Your profile

The teaching modes calibrate against a **personal profile** — who you are, the breadth to assume,
your **growth edges (each with its own level: novice / proficient / expert)**, the languages in
scope, and your preferences. It is not shipped: the first time you run `pair`, `guided`, or `drill`
without one, they route you into `learning:profile-init`, which interviews you, checks the result
for coherence (edge↔language fit, level coherence, redundancy, focus) before writing, and registers
any new edges/languages in your living vocabulary.

| Command | Use it when |
|---|---|
| `/learning:profile-init` | First-time setup, or rebuilding the profile from scratch. |
| `/learning:profile-update` | Add a language or edge, adjust a level, or change preferences/goals. |

Learning a language from scratch is just a **novice-level, language-oriented edge** named
`<lang>-fundamentals` (e.g. `rust-fundamentals`) — it coexists with expert edges like `hpc`, and
each is pitched at its own level.

### Per-project focus (optional)

Drop a `.claude/learning.local.md` in a repo to scope a session's attention without fragmenting the
global log:

```markdown
---
edges: [hpc, internals]
languages: [cpp]
---
Focus for this repo: the ray-tracer hot loops.
```

The modes read it at session start and emphasize those edges/languages; the log stays global, so
spacing and cross-project transfer are unaffected.

## Shared core

Edit these once; all skills follow.

| File | Purpose |
|---|---|
| `shared/calibration-core.md` | Invariant teaching rules: depth rule, trigger phrases, tuning constants, the fixed `type`/`signal` vocabulary, the session-start profile bootstrap, and the project-focus overlay rule. |
| `shared/teaching-protocol.md` | Predict-before-reveal, bounded correction, escape valve, verification rule. |
| `shared/hint-ladder.md` | Graduated unblocking and the retrieval-first review. |

The **calibration core** and protocol are **spliced into each mode SKILL.md at build time** by
`bin/sync-shared`, between `<!-- BEGIN shared:... -->` markers. `shared/` stays the single place you
edit; the skills carry a generated copy.

The **personal profile** is not shipped or spliced. It is generated per user by the
`learning:profile-init` skill into `~/.config/learning-toolkit/learning-profile.md` and loaded at
session start via `bin/learn-profile show`. A generic skeleton lives at
`templates/learning-profile.template.md`, and a filled reference at
`templates/learning-profile.example.md` (not loaded at runtime).

**After editing anything in `shared/`, run `bin/sync-shared`.** Use `bin/sync-shared --check` in CI
or a pre-commit hook to catch drift.

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
learn-log      --type hit --concept false-sharing --edge hpc --lang cpp   # validated append
learn-queue    --pick 4          # what to practise, interleaved across edges
learn-queue    --stats           # success rate vs target, graduations, reactivations
learn-queue    --concepts        # existing slugs, to avoid coining duplicates
learn-vocab    list|add|remove --edges X --langs Y   # the living edge/lang vocabulary
learn-profile  path [--ensure-dir] | show            # load/locate the personal profile
learn-baseline set|commits|advance|clear                                  # pair check-in windows
learn-session  start|end|status|config reinject on
bench          doctor|run|compare|vec|perf|cachegrind
sync-shared    [--check]        # splice shared/ into the skills after editing it
```

### `bench` — the anti-bullshit harness

The worst outcome this system can produce is encoding a **wrong** performance claim, because
spaced repetition would then drill it in. So `bench`:

- **Interleaves A/B** runs rather than running all of A then all of B, so thermal drift and
  frequency scaling hit both variants equally instead of masquerading as a difference.
- Reports a **bootstrap 95% CI on the difference of medians** (nonparametric — timing
  distributions are right-skewed and bounded below, so assuming normality would be wrong).
- **Refuses to name a winner** when that interval contains zero, or when the effect is under 2%.
- Uses **median and MAD**, not mean and stdev, so one interference spike does not move the answer.
- Decides vectorization from **the actual disassembly plus the compiler's own remarks**, attributed
  per-function, and reports `UNCLEAR` when those two disagree rather than picking one.

### Compilers

**clang is the default**, because Intel's `icx`/`icpx` are LLVM-based and clang is much the closer
proxy for them than GCC. On the clang family (including icx), `bench vec` reads
`-fsave-optimization-record` YAML, which carries an explicit `Function` field and *named* causes
like `CantReorderFPOps` — exact attribution, no source-line guessing. GCC uses `-fopt-info-vec-all`
text remarks with line-range attribution.

`bench vec --both` compares across the configurations in
`~/.config/learning-toolkit/compilers.json` (written with defaults on first use). Add your work
compiler there:

```json
{"name": "icx (work)", "cc": "icx", "cxx": "icpx", "flags": "-O3 -xHost"}
```

Configurations whose compiler is absent are skipped with a note, so the same config works at home
and at work. Divergence matters because "does this vectorize?" has **no compiler-independent
answer**:

```
clang              NOT vectorized
clang -ffast-math  VECTORIZED
gcc                VECTORIZED

DIVERGES -- vectorisation here is a property of the compiler, not the code.
  why clang declined:
    [CantReorderFPOps] loop not vectorized: cannot prove it is safe to
    reorder floating-point operations
```

`drill` uses this in two ways: silently, to *find* exercise material (functions where compilers
agree are dead ends; the boundary is where the mechanism lives), and visibly as the **reveal** in
a two-stage exercise — predict for clang, measure, then predict whether GCC agrees, then `--both`.

### icx: verified, and clang was the wrong proxy

Measured on oneAPI 2026.1 here. **icx passes `-mreassociate` and
`-ffp-contract=fast-honor-pragmas` by default**, so a float reduction vectorizes at plain `-O3`
with no fast-math flag — while stock clang refuses it. On this axis icx behaves like **gcc**, not
like clang:

```
icx (work)     VECTORIZED
clang          NOT vectorized
gcc            VECTORIZED
```

So "float reductions don't auto-vectorize", learned from stock clang, would have been **false for
the compiler you actually ship**. That is exactly the failure `--both` exists to prevent.
`-fp-model=precise`, `-fp-model=strict`, and `-fno-reassociate` each turn it back off.

Two icx quirks the harness accounts for:

- icx ships its own vectorizer and emits **no `loop-vectorize` records**, only
  `intel-slp-vectorizer` ones. SLP is a *different* transformation, so a missed SLP says nothing
  about loop vectorization — counting it would produce false negatives. The record filter stays
  strict, and icx verdicts come from the disassembly, reported honestly as
  `(from disassembly (no compiler remark))`.
- `-qopt-report=3` is accepted but produced no report file in 2026.1.

**No `setvars.sh` needed.** `bench` finds `icx`/`icpx` under `/opt/intel/oneapi` automatically and
runs them by absolute path, so it works in any shell. Give an absolute path in `compilers.json` to
override.

`"default": "clang"` in `compilers.json` sets which compiler plain `bench vec` uses. Change it to
`"icx"` to match your work toolchain.

Note also that this machine is Zen 2: **AVX2/FMA, no AVX-512**. Since `bench vec` is static, you
can still compile `-march=skylake-avx512` here and inspect work-target codegen — only the *timing*
subcommands need the real silicon.

`bench doctor` reports toolchain and environment, including `perf_event_paranoid` and CPU governor.

For Java, external process timing measures JVM startup and JIT warmup rather than your code.
Use `templates/BenchHarness.java`, which warms up and measures inside the JVM, consumes results
through a volatile sink to defeat dead-code elimination, and interleaves variants. It is not JMH
and says so; confirm anything load-bearing with real JMH.

## Config files

Everything lives in `${XDG_CONFIG_HOME:-$HOME/.config}/learning-toolkit/`. All of these are
created **lazily on first use**, so "missing" is normal rather than broken:

| File | What | Created by |
|---|---|---|
| `learning-log.jsonl` | the learning log | first logged entry |
| `config.json` | toolkit settings (`reinject`) | `learn-session config <key> <val>` |
| `compilers.json` | `bench --both` compiler set | `bench config --init` |
| `vocab.json` | living edge/lang vocabulary | `learn-vocab add`, or any first use (seeded) |
| `learning-profile.md` | the personal learner profile | `learning:profile-init` |

```bash
learn-session status     # where everything is, and what exists yet
bench config             # compiler set + which compilers actually resolve
bench config --init      # write the defaults out so you can edit them
```

## The log

Global and append-only at `${XDG_CONFIG_HOME:-$HOME/.config}/learning-toolkit/learning-log.jsonl`.
One log across **all** projects, because language internals and HPC are cross-project skills — a
concept practised in one repo should inform spacing everywhere. Every entry carries `project`, so
extractors can slice per-repo while the default view stays global.

One JSON object per line, optimised for `tail`/`grep` rather than for reading. `type` and `signal` are closed and enforced by `learn-log` (they are bound to the queue's
scheduling logic). `edge` and `lang` are a living vocabulary you grow with `learn-vocab`; `skill`
is derived from the installed skills. A value outside the valid set is rejected rather than
silently corrupting the queue.

```
type    taught skipped edge-confirmed calibration to-cover escape hit miss
        graduated reactivated self-assessment
edge    living — your own vocabulary; see `learn-vocab list`; `none` always valid
lang    living — your own vocabulary; see `learn-vocab list`; `none` always valid
signal  calibration     -> already-known declined-deepdive below-level
        self-assessment -> found-self missed-self overconfident underconfident
```

The `pair` baseline commit is deliberately **not** here — a SHA is project-specific and lives in
`.git/learning-baseline`, where it survives restarts and can never be committed or dirty
`git status`.

### Scheduling

`learn-queue` derives everything from the log:

- A concept graduates after **3 successes**, each separated by at least **1, then 7 days**.
  Successes closer together than the current interval record but do not advance the stage —
  cramming does not earn graduation.
- Graduated concepts return for a maintenance check after **30 days**.
- **Any miss returns a concept to active rotation**, resetting its stage. Retired is not deleted.
- Difficulty targets an **85% success rate**. Two misses running forces the next exercise
  *easier*, never harder — retrieval practice only pays off when retrieval mostly succeeds.

## Tuning

Every constant lives in exactly two places, kept in sync: `shared/calibration-core.md` (what Claude
reads) and the top of `bin/learn-queue` (what is computed).

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

## Measurement environment

Hardware counters need `perf_event_paranoid` low enough for unprivileged access:

```bash
sudo sysctl kernel.perf_event_paranoid=1        # own-process cache/branch counters
echo 'kernel.perf_event_paranoid=1' | sudo tee /etc/sysctl.d/99-perf.conf
```

Level `0` additionally allows system-wide uncore counters (memory bandwidth via `amd_df`).
`bench doctor` reports the current level and what it permits.

For the steadiest numbers, pin to a core and reduce frequency variance:

```bash
bench compare --a "./a" --b "./b" --pin 3
sudo cpupower frequency-set -g performance      # optional
```

Cachegrind needs none of this: it simulates rather than measures, so its cache and branch figures
are exact and repeatable. For teaching that is often better than live counters, because a
prediction can be checked against a number that does not wobble.

## Honest limits

The principles here — retrieval practice, spacing, interleaving, expertise reversal, desirable
difficulty, the guidance hypothesis, incomplete-example transfer — are well-supported for
deliberate factual and procedural learning, largely in lab settings.

Applying them to an expert developer learning via LLM tutoring on real work is **principled
extrapolation, not a validated method**. Complex-skill transfer, which is exactly the HPC goal, is
where the underlying evidence is weakest and most mixed.

The log exists so this can be checked rather than believed. If `learn-queue --stats` shows nothing
improving after a few months, that is data, and abandoning or reshaping this is the correct
response to it.
