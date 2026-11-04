---
name: over-engineering-check
description: >-
  Reviews a design against its stated goal for over-engineering: patches on patches, fixes made
  at the symptom, and scope wider than asked. Reports where each finding came from and proposes
  reworks. Use when the user says things are getting complicated, "patching a patch" or "going
  off the rails", or asks to check for over-engineering.
---

Say `over-engineering-check loaded`.

# Over-engineering check

Check whether a design still serves its goal, or has grown by patching instead of reworking.
The design can be rules, processes, skills, tooling or code. Report and propose only: change
nothing until the user approves.

## 1. Find the goal

Use the goal and non-goals stated in the conversation, or in the plan, spec or issue the work
follows. Restate each in one sentence. If no goal is stated, ask the user for it and stop; never
infer the goal from the current design.

## 2. Find what changed

List each rule, field, exception, option, unit, file or code path added or changed while working
toward that goal. Take the history from the conversation. When it is not in context, use git
(`git log` and `git diff` on the files involved) and the plan or issue. If no history is
available, say so and review the current design only.

## 3. Check each change

A change is a finding when any of these holds:

- **Patch on a patch:** it was added to fix a problem another change created.
- **Fixed at the symptom:** it changes where the problem showed up, not where it was caused,
  including special-casing one input or changing a test assertion so it passes.
- **Out of scope:** it serves no stated goal, falls under a non-goal, or reads an instruction more
  broadly than it was given.
- **Not needed yet:** it handles a case, value or caller that does not exist, or adds machinery
  (a script, hook, option or layer) where a sentence or a direct edit would do.

Then test the design as a whole:

- **Deletion test:** would removing an earlier change make any later one unnecessary? That
  earlier change is the root cause; propose reworking it rather than keeping its patches.
- **Fresh-start test:** designing it today with every requirement now known, would we arrive
  here? If not, describe the design we would arrive at.

## 4. Find where each finding came from

Name one source per finding, with evidence:

- **User instruction:** quote the message.
- **Gap:** what the user did not specify, and what was assumed instead.
- **Agent assumption:** say what was assumed.
- **Existing design:** name the file it was built on.
- **Another rule or skill:** name the file and line.

An agent's account of why it did something is reconstructed, not remembered. With no evidence,
write `no source found, probably an agent assumption`; never present a guessed source as fact.

## 5. Report

1. **Goal** and **Non-goals**, one sentence each.
2. **Findings.** For each: what it is, its category from step 3, its source with evidence, the
   root cause from the deletion test, and how to avoid it next time (an instruction the user
   could give, or a rule change).
3. **Optional simplifications**, labelled optional: changes that would simplify the design but
   are not findings.
4. **Proposed reworks** in the `workflow-preferences:propose-changes` format. Propose removing or
   reworking the root cause before any new patch.

If nothing is found, say `No over-engineering found against the goal` and list what was checked.
Never invent a finding to have something to report. Then stop and wait for the user.
