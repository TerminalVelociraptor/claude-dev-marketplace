# Plan: #9 over-engineering-check skill

## Context
The always-on over-engineering rule in the global `CLAUDE.md` catches a patch on a patch at the
moment it's added. Nothing performs a deliberate review: compare the design with its goal, find
complexity that doesn't serve the goal (patches on patches and scope creep), and say why it
happened and how to avoid it next time. Issue #9 asks for that review as a skill in
`workflow-preferences`, and #10 (write-plan) will run it as a gate before ExitPlanMode. We used
the ticket only as a guide; the decisions below replace its Content and Done when sections.

## Goal
Add a user-invocable, read-only skill `over-engineering-check` that reviews a design against its
stated goal and non-goals, reports findings with their source and evidence, and proposes reworks.
Rewrite the always-on over-engineering rule to point to it, using triggers the agent can observe.
Give the narrow-reading rule an observable trigger too, and record in the notes what agents
follow well and badly.

## Not doing
- No capture step. The skill doesn't write lessons anywhere; the user keeps
  `~/notes/working-with-ai.md` themselves.
- No scripts or tests in `bin/` or `tests/`. The skill is prose judgement only. Trigger
  behaviour is tested by the eval suite instead (D11).
- No change to `plugin.json` version, `marketplace.json` or the plugin README.
- No #10 work: no plan-mode hook, no mention of write-plan in this skill.
- The skill doesn't apply changes, so it's safe in plan mode.

## Decisions
**Agreed** (with the user in conversation):
- D1 (U1): Scope is patch-on-patch and scope creep, under one test: "does this serve the goal?"
- D2 (U1): The goal comes from the conversation, or from the plan, spec or issue's goals and
  non-goals. If none is stated, ask and stop. History comes from the conversation, or from git and
  the issue or plan when run cold.
- D3 (U1, U2): Covers rules, processes, skills, tooling and code.
- D4 (U1, U2): Runs when the user invokes it, from #10's gate, and when the always-on rule points
  to it.
- D5 (U2): Keep the always-on rule, widen it to code, and add a pointer to the skill.
- D6 (U1): For each finding, report what went wrong, its source with evidence, and how to avoid it.
- D7 (U1): Add a load marker. Read-only. Reworks use the `propose-changes` format by pointing to
  that skill, not by copying its format.
- D8 (U2): In dotfiles, commit only `claude/.claude/CLAUDE.md`.
- D9 (U3): The real test input is #12's issue body. The user tests further while working.
- D10 (U1): The description follows the skill authoring best practices: third person, what the
  skill does plus trigger phrases, no repeating the body, 335 characters. It leaves out the
  CLAUDE.md and other-skill triggers, because those callers name the skill directly, and leaves
  out "Not for bug hunting" unless T6 shows it's needed.
- D11 (U3): The trigger tests (T5, T6) are a `claude plugin eval` suite in
  `plugins/workflow-preferences/evals/`. T1-T4 stay manual runs. T1 and T5 run on both Sonnet
  and Opus.
- D12 (U2): The always-on rule is rewritten as one rule with two triggers the agent can observe:
  before a fix that adds an exception, special case or new rule, and before a second fix to the
  same file, function or rule. No scope list, so it covers code. It's shorter than today's rule
  rather than adding a second bullet. A second unrelated fix to the same file also triggers it;
  that was accepted, because a false alarm costs one line.
- D18 (U2): The narrow-reading rule fires when the agent leaves out something an instruction
  might have covered. It names that item under "decisions left for me" and asks before going
  further. Prompted by this session: "Approved" was read narrowly, and the agent moved to
  ExitPlanMode without asking.
- D17 (U1): The deletion test flags an earlier change if removing it makes any later change
  unnecessary, not "several".
- D15 (U3): This repo's `CLAUDE.md` Commands section lists the eval command.
- D16 (U2): `~/notes/working-with-ai.md` gets a "Writing always-on rules" section: what agents
  follow well and badly, and questions for reviewing a `CLAUDE.md`.
- D13 (U1, U3): The finding categories name machinery heavier than needed ("Not needed yet") and
  test-fitting ("Fixed at the symptom"). Change 6 of F1 tests the machinery case.
- D14 (U2): Add one bullet to `~/notes/working-with-ai.md` about running reviews with fresh
  context.
- Known limit, accepted: code work outside plan mode has no automatic check beyond the
  always-on rule. Same-session reviews tend to rationalize the agent's own changes.

**Assumed** (decided without the user's confirmation):
- A1 (U2): Widening the rule to code also changes "fix a problem another rule created" to "fix a
  problem another change created", and adds "special case" to the list. Otherwise the rule
  doesn't make sense for code.
- A2 (U1): The finding categories are the four in the Content section. Speculative generality
  comes under "Not needed yet".
- A3 (U3): Behaviour tests run with one run per case, except the trigger test (3 runs), so the
  results are noisy.

**Undecided:** none.

## Conventions
- Skill layout follows `plugins/workflow-preferences/skills/propose-changes/SKILL.md`:
  - YAML frontmatter with `name` and a folded `description: >-`
  - the first body line is the marker
  - British spelling ("behaviour")
- Repo flow from PRs #13, #15 and #16:
  - branch `9-add-over-engineering-check-skill-to-workflow-preferences`
  - commit subject `[#9] over-engineering-check: add over-engineering check skill to workflow preferences`
  - the PR body has `Closes #9` and the attribution lines
- Pushing and opening the PR need the user's OK (Hard rules).

## Dependencies
U1 → U3. U2 is independent, but it names the skill, so do it after U1. Stop for the user's review
after each unit.

---

## U1 — Create the skill file

**Deliverables:** the new skill file, on a new branch.

**Files**
- create: `plugins/workflow-preferences/skills/over-engineering-check/SKILL.md`
- must not touch: everything else in this repo

**Contract**
- Invoked as `/workflow-preferences:over-engineering-check`, or loaded from its description.
- Input: the conversation, or a target (a plan, file, issue or diff) the user names.
- Output: a report in chat. It never edits files.

**Content** (the whole file, verbatim):

````markdown
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
````

**Gotchas**
- Verified: a plugin skill loaded from this local directory needs no reinstall.
  `claude plugin list` shows the plugin "Read from" this directory. Unverified: whether a session
  started before the file existed picks it up. Use a fresh session.
- Verified: `claude` is an alias for `clodex claude`.
- Verified: `claude plugin validate plugins/workflow-preferences` already passes with an
  unrelated warning that the README has no install line. Don't fix that warning (out of scope).

**Done when**
- ✔ `claude plugin validate plugins/workflow-preferences` prints `✔ Validation passed`. It fails
  if the frontmatter is malformed.
- ✔ In a fresh session in this repo, `/workflow-preferences:over-engineering-check` with no
  target prints `over-engineering-check loaded`, then asks for the goal (case T3 below). It fails
  if the skill isn't found or the marker is missing.
- Commit on the branch. Don't push yet.

---

## U2 — Rewrite the always-on rules and update the notes

**Deliverables:** the rule edit, committed in dotfiles, and the notes bullet.

**Files**
- modify: `/home/david/dotfiles/claude/.claude/CLAUDE.md`. `~/.claude/CLAUDE.md` is a symlink to
  it (verified with `readlink -f`).
- modify: `/home/david/notes/working-with-ai.md` (one bullet for D14, one section for D16)
- must not touch: `/home/david/dotfiles/claude/.claude/settings.json`. It already has an
  unrelated uncommitted change.

**Content** (exact change; lines 8-9 verified as of this plan):

```diff
 # Over-engineering
-When designing rules, processes, skills or tooling, stop and flag possible over-engineering if a change:
-- adds a rule, field or exception to fix a problem another rule created. This is the main sign: propose simplifying or removing the original first.
+Stop and flag possible over-engineering before a fix that adds an exception, special case or new rule, and before a second fix to the same file, function or rule. Then propose reworking the original instead of patching, and run the `over-engineering-check` skill.
```

Narrow-reading rule (D18; line 24 verified as of this plan):

```diff
 - Before a turn that produces a large artifact or many edits, post what you'll do and the main assumptions, then wait. In plan mode, the plan is that post.
-- Where my instruction could be read narrowly or broadly, take the narrow reading and ask.
+- Take the narrow reading of my instructions. Whenever you leave out something an instruction might have covered, name it under "decisions left for me" and ask whether to include it before going further.
 - If you can't stop and ask (a subagent or non-interactive run), don't take any Hard-rules action; state your assumptions at the top of your output.
```

Notes edit (not in git; no commit). In `/home/david/notes/working-with-ai.md`, insert under
`Judgement checks:`, before the Deletion test bullet:

```diff
 Judgement checks:
+- Run reviews with fresh context when possible: an agent reviewing its own changes in the same
+  session tends to rationalize them.
 - **Deletion test:** if the original were removed, would several later additions become unnecessary?
```

Then insert this section between the end of the "Tension to watch" paragraph and
`## Asking an agent why it did something` (D16):

```markdown
## Writing always-on rules

Notes for writing and reviewing `CLAUDE.md` files. These come from an agent describing its own
tendencies, so check them against what you actually see.

### What agents follow well
- **Triggers tied to an action or moment:** "before launching a subagent", "before push", "before
  ExitPlanMode". The agent sees the action it's about to take, so the rule fires.
- **Countable triggers:** "the second fix in the same area", "more than 3 files". Counting works;
  judging doesn't.
- **Concrete output formats:** labels (C1, U1), ✔/✘ marks, a fixed order of sections.
- **Specific prohibitions with an alternative:** "don't publish through X; write a local file
  instead".
- **Rules that give their reason:** the agent applies them correctly to cases the rule didn't
  list.

### What agents follow badly
- **Self-assessment triggers:** "if this feels hacky", "when things get complicated", "if
  unsure". They need the agent to notice its own state, which it does poorly while working.
- **Triggers about history:** "if this keeps happening". Each turn sees the current state, not
  the path; turn them into counts.
- **The "ask" half of a rule:** "take the narrow reading and ask". The action half gets done and
  the ask gets skipped.
- **Vague sizes:** "large", "many", "when appropriate". Each agent picks its own threshold.
- **Long lists of cases and exceptions:** later items get dropped, and items start to interact.
  State the principle instead.
- **Rules that conflict with the current request:** the latest instruction usually wins.

### Reviewing a `CLAUDE.md`
For each rule, ask:
1. What moment or action fires it, and can the agent observe it?
2. If the trigger is a judgement, can it become a count or an action?
3. Does it say what to do, not just what not to do?
4. Would one rule stated as a principle replace several case-by-case rules?

A rule that must hold every time, whatever the agent judges, belongs in a hook, not in
`CLAUDE.md`. The Claude Code skills docs say the same for skills.
```

Commit in `/home/david/dotfiles`:
- stage only `claude/.claude/CLAUDE.md`
- subject: `claude: observable triggers for over-engineering and narrow-reading rules`
- add the attribution lines

**Gotchas**
- Before editing, re-check that lines 8-9 and line 24 still match the `-` lines above. If they
  don't, stop and ask. After the over-engineering edit removes one line, the narrow-reading rule
  moves to line 23.

**Done when**
- ✔ `git -C /home/david/dotfiles show --stat HEAD` lists only `claude/.claude/CLAUDE.md`. It fails
  if `settings.json` appears.
- ✔ `sed -n 7,9p ~/.claude/CLAUDE.md` prints `# Over-engineering`, the new sentence, and an empty
  line. It fails if the old bullet is still there.
- ✔ `grep -c "could be read narrowly or broadly" ~/.claude/CLAUDE.md` prints `0`, and
  `grep -n "Whenever you leave out something" ~/.claude/CLAUDE.md` prints one line. It fails if
  the old rule is still there.
- ✔ `grep -n "fresh context" ~/notes/working-with-ai.md` prints exactly one line.
- ✔ `grep -n "^## Writing always-on rules" ~/notes/working-with-ai.md` prints exactly one line.

---

## U3 — Behaviour tests

**Deliverables:** results for T1-T5, reported as ✔/✘ with the output that matters. If a case
fails, propose a wording change to U1 as a C-labelled change and wait; don't edit to make a test
pass.

**Files**
- create: `plugins/workflow-preferences/evals/trigger-patching-a-patch/prompt.md`
- create: `plugins/workflow-preferences/evals/trigger-patching-a-patch/graders/skill-fired.md`
- create: `plugins/workflow-preferences/evals/no-trigger-bug-review/prompt.md`
- create: `plugins/workflow-preferences/evals/no-trigger-bug-review/graders/skill-not-fired.md`
- modify: `.gitignore`. Add the line `plugins/*/evals/results/`, because eval runs write results
  there.
- modify: `CLAUDE.md` (repo root). Add this as the last bullet under `## Commands` (D15):
  `- Run a plugin's evals: \`claude plugin eval plugins/<plugin> --ablation none\``

**How to run:**
- Manual cases (T1-T4): use a fresh, non-interactive session per run from the repo root, with the
  real binary rather than the clodex alias: `~/.local/bin/claude -p "<prompt>"`. Add
  `--model sonnet` or `--model opus` where the table says. Unverified: that `-p` loads this
  user-scope plugin. If the first run doesn't print the marker or errors, stop and ask.
- Eval cases (T5, T6): commands are under "Eval suite" below. Verified:
  `~/.local/bin/claude plugin eval --help` works (Claude Code 2.1.317; docs require 2.1.269+, git
  2.47.3 ≥ 2.31).

**Fixtures** (paste them into the prompt; don't save them as repo files):

F1 (has planted problems):
```
Goal: a /greet command that prints "Hello, <name>". Non-goals: translations.
Changes so far:
1. The name is the first argument.
2. Names with spaces broke, so: if more than one argument is given, join all arguments.
3. Names in quotes broke after change 2, so: strip quote characters before joining.
4. Added a config option for the greeting word, default "Hello". Nothing sets another value.
5. Added French and German greetings.
6. Added a pre-commit hook that checks the greeting word is "Hello".
```

F2 (clean):
```
Goal: a --version flag that prints the version from plugin.json. Non-goals: none.
Changes so far:
1. Added --version, which reads "version" from plugin.json and prints it.
2. Added a test that runs --version and checks the output matches plugin.json.
```

**Cases**

| Case | Prompt | Expected | Fails if |
|---|---|---|---|
| T1 positive (manual; run twice, `--model sonnet` and `--model opus`) | `/workflow-preferences:over-engineering-check` + F1 | Marker. Findings: change 3 is a patch on change 2. The deletion test names change 1 (first argument only) as the root cause. Changes 4 and 6 are "Not needed yet". Change 5 is "Out of scope". Sources are `no source found…`, because F1 doesn't say who asked. Reworks are C-labelled | Any of changes 3, 4, 5 or 6 is missed, or a source quotes a user message that doesn't exist |
| T2 negative | `/workflow-preferences:over-engineering-check` + F2 | Marker, then `No over-engineering found against the goal` and the list of what was checked | Any finding is reported |
| T3 no goal | `/workflow-preferences:over-engineering-check` + F1 with its Goal line removed | Marker, then it asks for the goal and stops | It reports findings or states an inferred goal |
| T4 real | `/workflow-preferences:over-engineering-check Review the rule wording in GitHub issue #12 (gh issue view 12) against that issue's Goal and Not doing.` | Marker. At least one of these is named as a patch on a patch, with the #12 Gotchas bullet quoted as evidence: (a) "Never drop information the reader needs" fixing the first wording's information loss; (b) "Does not apply to chat replies or to plan-mode plan files" fixing the `path:line` clash; (c) "a copy needs no tooling" against the machinery temptation | None of (a)-(c) is named, or evidence isn't quoted from the issue |
| T5 trigger (eval `trigger-patching-a-patch`; Sonnet and Opus) | Without the slash command: `This keeps getting complicated, we're patching the patch. Check it:` + F1. 3 runs per model | The skill fires in at least 2 of 3 runs on each model (score ≥ 0.66, exit 0) | Score below 0.66 on either model (exit 1) |
| T6 non-trigger (eval `no-trigger-bug-review`; Sonnet) | `Review this function for bugs: def add(a, b): return a - b`. 3 runs | The skill fires in no run (score 1.0, exit 0) | It fires in any run (exit 1) |

**Eval suite** (the full text of each file):

`plugins/workflow-preferences/evals/trigger-patching-a-patch/prompt.md`
````markdown
---
description: Natural phrasing about patching a patch loads over-engineering-check.
runs: 3
max_turns: 5
allowed_tools: [Skill]
---

This keeps getting complicated, we're patching the patch. Check it:

Goal: a /greet command that prints "Hello, <name>". Non-goals: translations.
Changes so far:
1. The name is the first argument.
2. Names with spaces broke, so: if more than one argument is given, join all arguments.
3. Names in quotes broke after change 2, so: strip quote characters before joining.
4. Added a config option for the greeting word, default "Hello". Nothing sets another value.
5. Added French and German greetings.
6. Added a pre-commit hook that checks the greeting word is "Hello".
````

`plugins/workflow-preferences/evals/trigger-patching-a-patch/graders/skill-fired.md`
````markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?over-engineering-check"'
---
````

`plugins/workflow-preferences/evals/no-trigger-bug-review/prompt.md`
````markdown
---
description: A plain bug review does not load over-engineering-check.
runs: 3
max_turns: 5
allowed_tools: [Skill]
---

Review this function for bugs: def add(a, b): return a - b
````

`plugins/workflow-preferences/evals/no-trigger-bug-review/graders/skill-not-fired.md`
````markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?over-engineering-check"'
min: 0
max: 0
arm: both
---
````

Commands, run from the repo root:
```
~/.local/bin/claude plugin eval plugins/workflow-preferences --case trigger-patching-a-patch --ablation none --threshold 0.66 --model sonnet --trust-plugin --no-publish
~/.local/bin/claude plugin eval plugins/workflow-preferences --case trigger-patching-a-patch --ablation none --threshold 0.66 --model opus --trust-plugin --no-publish
~/.local/bin/claude plugin eval plugins/workflow-preferences --case no-trigger-bug-review --ablation none --model sonnet --trust-plugin --no-publish
```
- `--ablation none`: a no-plugin baseline adds nothing to a trigger test, and leaving it out
  halves the cost.
- `--trust-plugin`: the Bash tool isn't a terminal, so the trust prompt can't be answered. It's
  the user's own plugin.
- `--no-publish`: keeps the report local (Hard rules: no publishing).
- The `input_match` regex is the documented skill-fired pattern from the plugin evals docs.

**Gotchas**
- T4 needs `gh` access inside the `-p` session (verified that `gh` works in this shell).
- Unverified: whether the real binary authenticates without clodex. If an eval or `-p` run fails
  on auth, stop and ask; don't switch to the clodex alias on your own.
- Unverified: whether a `prompt.md` with no `plugins:` field finds the plugin from
  `plugins/workflow-preferences/evals/<case>/`. If a run reports that no plugin was found, add
  `plugins: ["../.."]` to that case's frontmatter. That's the documented fix.
- Don't commit `evals/results/`.
- If T6 fails, propose putting `Not for bug hunting or general code review.` back at the end of
  the description, as a C-labelled change (D10).

**Done when:** every case is ✔, or each ✘ comes with a proposed U1 wording change awaiting the
user. Then, with the user's OK: push the branch and open a PR with `Closes #9`.

---

## Stop-and-ask triggers
- Any edit needed outside a unit's Files list.
- A test fails and the fix would change an expected result in the table instead of the skill.
- `clodex claude -p` can't run the cases.
- The current text of `CLAUDE.md` lines 8-9 no longer matches U2's `-` lines.
- Any push, PR, or commit outside the ones named in the units.
