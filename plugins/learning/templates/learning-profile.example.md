# Learner profile — lead developer (example)

> This is a filled EXAMPLE, kept in the repo for reference. It is NOT loaded at runtime — every
> user generates their own via `learning:profile-init`, written to
> `~/.config/learning-toolkit/learning-profile.md`.

## Who you are teaching

A lead developer. Strong breadth: architecture, general patterns, problem-solving, critical
thinking. Assume that competence and do not re-explain it.

Pronoun: he/him.

## Growth edges

Levels are starting priors, not ceilings: difficulty rises within a session on demonstrated
mastery, and a lasting level change goes through `learning:profile-update`.

- **`internals`** — scope: memory model, allocator behavior, compiler/runtime execution, codegen.
  Level: proficient. Depth: conceptual: explains the memory model and common codegen; hands-on:
  reads disassembly but rarely writes allocator-aware code. Deep and terse; tie mechanism to real
  codegen, no hand-holding.
- **`hpc`** — scope: cache behavior, vectorization, branch prediction, memory bandwidth,
  parallelism, profiling. Level: proficient. Depth: conceptual: knows the hardware model;
  hands-on: has profiled but not tuned hot loops. Deep and terse; always tie to real numbers.

## Languages in scope

- `cpp` (C++) — role: working. Proficiency: fluent; writes production code daily.
- `c` (C) — role: working. Proficiency: fluent reading, occasional writing.
- `python` (Python) — role: working. Proficiency: scripting and tooling; not performance work.
- `java` (Java) — role: analogy. Proficiency: past professional use; useful for JIT and GC contrasts.

## Per-edge goals (optional)

- `hpc`: predict-then-measure until predictions match measurements on the first try.

## Preferences & learning styles

- Brief theory, one compact example, then practice.
- Hints before the answer; the full correction after two attempts; an explicit "just tell me" is
  honored.
- Levels are priors: raise difficulty on demonstrated mastery and say so.
- Java analogies are welcome; name where each one breaks.
- Terse on breadth, deep on the edges. Corrections delivered straight, no apology.
