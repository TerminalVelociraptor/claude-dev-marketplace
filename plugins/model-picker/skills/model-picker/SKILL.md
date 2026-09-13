---
name: model-picker
description: >-
  Recommend which Claude/GPT model and effort level to use for an upcoming task. Use when the
  user is mid-conversation and asks something like "what model should I use for this", "should I
  switch models", "recommend a model/effort for X", or wants a model switch decision before
  starting a task.
---

# Model Picker

Recommend a model + effort-level combo for a task the user is about to do. Never make this call
yourself in the current conversation — always delegate to a subagent, regardless of what model is
currently running this skill. This matters for two reasons:

1. **Accuracy**: if the current session is on a low/cheap model, it may not weigh the tradeoffs
   in `reference/models-condensed.md` correctly.
2. **Cost**: if the current session is on an expensive model (e.g. Fable 5.1, Opus 5), doing the
   lookup inline burns frontier-model rates on a task a cheap worker handles fine. A subagent on
   Sonnet 5 costs a fraction as much for this specific job.

## Step 1: Get the task description

Get a 1-2 sentence description of the task the user is about to do (what kind of work, how
well-defined it is, whether facts/recency matter, whether it's code vs. writing vs. research vs.
security work, roughly how high-stakes a wrong answer or rework would be). If the user already
gave this in their request, don't ask again — just use it.

## Step 2: Spawn a subagent to do the lookup

Spawn a subagent (not a fork — this needs no conversation context, just the task description) with
`model: sonnet` to:

1. Read `reference/models-condensed.md` in this skill directory.
2. Match the task description against the quick-picker table, per-model notes, and general rules
   (bigger-model-low-effort-beats-smaller-high-effort, effort diminishing returns, orchestrator
   patterns, security refusals, pricing traps).
3. Return a recommendation in the exact output format below.

Give the subagent the task description verbatim plus this instruction: "Recommend one model +
effort level combo for this task, using reference/models-condensed.md in this skill directory.
Follow the output format exactly."

## Output format

State the primary recommendation as: **Model (effort level)** followed by 1-2 sentences of why —
grounded in the specific tradeoff from the reference doc (complexity match, cost per solved task,
recency needs, refusal risk, etc.), not generic praise.

If a second combo is genuinely competitive (not just technically possible), add one line starting
with "Alternative:" naming that combo and a single concrete cost/benefit delta (e.g. "half the
price," "1.5x the cost but less rework risk," "2 points higher intelligence score"). Only include
an alternative when it's a real tradeoff worth knowing about — don't pad every answer with one.

**Example, clear choice, no alternative:**

> GPT-5.6 Luna (low) — This is a summarizing task, but it's shorter and simpler than what needs medium effort.

**Example, two viable choices:**

> Fable 5.1 (low) — Well-defined general coding task where current facts don't matter.
> Alternative: Opus 5 (low) — Slightly lower performance but at half the price.

## Guidelines

- Keep the final answer to the user short: the recommendation line(s) only, no restating the task
  description back to them, no long justification beyond the 1-2 sentences.
- If the task description is too vague to pick between models with real confidence (e.g. "help me
  with some stuff"), ask one clarifying question rather than guessing — a wrong model pick can mean
  expensive rework.
- Don't recommend an effort level the model doesn't support — check `reference/models-condensed.md`
  for which effort levels apply to which model.
