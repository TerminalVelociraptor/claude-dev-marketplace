---
name: model-picker
description: >-
  Recommend which Claude/GPT model and effort level to use for an upcoming task. Use when the
  user is mid-conversation and asks something like "what model should I use for this", "should I
  switch models", "recommend a model/effort for X", or wants a model switch decision before
  starting a task.
---

# Model Picker

Recommend a model and supported effort/thinking setting for the user's task using the bundled
reference. Do not switch models, launch the recommended task, or change configuration yourself.

## Step 1: Capture the task and decision constraints

Use the task and constraints already in the conversation; do not ask the user to repeat them.
Preserve the task description verbatim, then attach a short constraint summary:

- Task family and scope: code, research, documents, writing, operations, security, or another
  category in the reference; bounded versus open-ended; independent versus dependent steps.
- Required quality, consequence of errors, and available tests or output checks.
- Latency tolerance: interactive response versus asynchronous completion.
- Context size and required tools, modalities, or access/retention restrictions.
- Available models, current model/effort, budget, and API versus subscription/OAuth billing.

Do not infer missing constraints. Ask one focused question only if its answer would materially
change the recommendation; otherwise state the relevant limitation in the recommendation.

## Step 2: Delegate the lookup to the picker agent

Launch the **`model-picker:picker`** agent (Opus 5, defined in this plugin). Invoking this skill is
the user's explicit request to use that named agent; do not skip delegation for want of separate
authorization. Launch exactly one, not a fork or a fleet, and do not substitute another model.

Pass it:

- The task verbatim and the constraint summary from Step 1.
- Absolute paths to `reference/models-condensed.md` and `reference/evidence.md`, resolved from
  this skill's base directory.

Relay its recommendation without adding to it, and state in one line that the lookup ran in the
picker subagent.

**Fallback:** if the agent type is unavailable or the launch fails, say so, read
`../../agents/picker.md` relative to this skill's base directory, and follow its instructions and
output format inline. State that the lookup ran inline and why.
