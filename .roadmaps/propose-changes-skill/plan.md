# Plan: issue #8 — `propose-changes` skill for `workflow-preferences`

## Context
Issue #8 asks for a skill that loads the user's rules for presenting proposed changes. The issue body was drafted early by a less capable agent and pinned trigger phrases and exit criteria too soon. This plan replaces those details with what we agreed in discussion, plus fixes from a first subagent clarity test (run in planning while the rules were still in CLAUDE.md, so not clean). Long term, dotfiles#1 Part 2 trims the "Presenting proposed changes" section of `~/.claude/CLAUDE.md` to a pointer at this skill, so the copy in two places is temporary.

**Goal:** one skill file holding the user's proposal rules (updated as agreed), a description that fires whenever Claude presents changes for approval, a clean subagent clarity test, and a couple of live tests by the user.

**Not doing**
- No hook, no `bin/` script, no unittest (there is no script to test).
- No version bump in `plugin.json` (plugin unreleased, stays `0.1.0`).
- No permanent edit to `~/.claude/CLAUDE.md`; the section is moved out only for testing, then restored (U3, U4).
- No edits to other plugins or to `.claude-plugin/marketplace.json` (the plugin is already listed, verified at `.claude-plugin/marketplace.json:52-57`).
- No fixed trigger-count criterion (no "3 trials").

## Decisions
**Agreed**
- D1 (U1): Every edit to existing code or text is shown as a ```diff block. Inline `~~removed~~ **added**` marks are dropped (user: they predate diff blocks being an option).
- D2 (U1): Description describes the situation (presenting changes, new formats/outputs/structures/processes, or review fixes for approval); phrases are examples. Direct requests to make a change ("fix the typo") are excluded.
- D3 (U1): Fixes suggested in a review use the same format; findings keep their defects-first order.
- D4 (U1): Two worked examples: a doc edit and a code fix, both as diff blocks.
- D5 (U1): Marker line "Say `propose-changes loaded`." as first body line; user removes it later once triggering is trusted.
- D6 (U1): Frontmatter is `name` + `description` only (skills are user-invocable by default → `/workflow-preferences:propose-changes`).
- D7 (U1): `What:` and `Why:` are each 1-3 sentences; default one, more only when a complex change needs detail or reasoning.
- D8 (U1): From the first clarity test: never invent a Why (`Why: unknown` + ask); title line `**C1 — <short title>**`; one label per independently approvable change (a multi-file rename is one); `(optional)` in the title of optional changes; implementation detail in the change or an `Assumptions:` line; no-code changes show the new steps or an example.
- D9 (U3, U4): Claude moves the section out of the dotfiles CLAUDE.md into a scratchpad backup, runs the clean subagent test, the user runs live tests, then Claude restores the section. Rules being absent machine-wide during testing is OK.
- D10 (U3): Subagent clarity test is a plan unit, run only after the section is removed so the test is clean.
- D11 (U2): Claude rewrites issue #8's body to match this plan.

**Assumed** (review these)
- A1 (U1): D1 covers prose too: a one-word doc change is a diff of the whole line, and a rewritten paragraph is a diff whose `-`/`+` lines act as before/after. So the separate before/after rule is dropped. No inline exception for long unwrapped lines: it would need a "how long" judgement (the kind of threshold the first test showed agents guess at), two formats for one job invite mixing, and inline marks are what broke inside backticks. Accepted cost: in a long line the changed word is harder to spot; `What:` already names the change.
- A2 (U1): Multi-file changes put one diff block per file, each preceded by the file path in backticks.
- A3 (U1): "I" in the source rules becomes "the user" (the skill is read by Claude). Body wrapped at ~100 columns like `plugins/roadmap/skills/roadmap/SKILL.md`.
- A4 (U5): Branch `8-add-propose-changes-skill`, commit subject `[#8] Add propose-changes skill` (pattern from remote branches `7-scaffold-workflow-preferences-plugin`, `4-create-telemetry-mod` and commit `66cac34`).

**Undecided:** none.

## Conventions
- Markdown skill file with YAML frontmatter, matching existing skills (`plugins/model-picker/skills/model-picker/SKILL.md:1-7` uses `name` + folded `description: >-`).
- `claude` is aliased to `clodex claude` on this machine (verified). Use `command claude …` to bypass the alias for CLI checks.
- Subagents need a posted pre-flight check and the user's OK before launch (user hard rule), even though this plan names one.

## Units
Dependencies: U1 → U3 → U4 → U5. U2 is independent. Stop for the user's review after each unit.

### U1 — Create the skill file
**Files:** create `plugins/workflow-preferences/skills/propose-changes/SKILL.md`. Must not touch anything else.

**Content** (exact text; between the outer four-backtick fences):

````markdown
---
name: propose-changes
description: >-
  Format for proposing changes for the user's review: each change labelled C1, C2…, with
  What:/Why: lines and the change shown as a diff block. Use whenever the user asks to
  "propose", "suggest" or "draft" changes, asks "what would you change", or wants to review an
  edit before it is made; whenever presenting changes to code, docs, config or prompts for
  approval before applying them; when proposing a new format, output, structure or process; and
  when suggesting fixes in a review. Not for direct requests to make a change ("fix the typo").
---

Say `propose-changes loaded`.

# Presenting proposed changes

- Head each change `**C1 — <short title>**` (C2, C3, …) so the user can approve by label. Use one
  label per change the user could approve or reject on its own; a rename across several files is
  one change. Mark optional changes `(optional)` in the title.
- Under the title, two labeled lines, then the change:
  - `What:` 1-3 sentences on what changes, in terms of behaviour, not code.
  - `Why:` 1-3 sentences on the problem it solves or what breaks without it.

  Default to one sentence each; use more only when a complex change needs detail or reasoning.
  Both must read without opening any file: no pointers such as "see plan U3" in their place, no
  restating the code. If the reason is not known, write `Why: unknown` and ask; never invent one.
- Show the change:
  - Edits to existing code or text: a `diff` block with a few unchanged lines for context. One
    block per file, each preceded by the file path in backticks.
  - New code or text: a fenced block in its language.
  - A new format or output: a short concrete example.
  - A process change with no code: the new steps.

  Single paths and commands may be inline. Implementation detail goes in the change, or in an
  `Assumptions:` line after it.
- When a review suggests fixes, present each fix in this format; the findings themselves keep
  their defects-first order.

## Examples

**C1 — README install step**

What: The install command names the marketplace the plugin comes from.
Why: Without the marketplace name, the install fails with "plugin not found".

`README.md`
```diff
 ## Install
-Run `claude plugin install workflow-preferences` to install.
+Run `claude plugin install workflow-preferences@dev-toolkits` to install.
```

**C2 — Fix the loop bound**

What: The loop stops at the last element instead of reading one past the end.
Why: Every call currently raises IndexError.

`utils.py`
```diff
 def last_items(xs, n):
     out = []
-    for i in range(len(xs) - n, len(xs) + 1):
+    for i in range(len(xs) - n, len(xs)):
         out.append(xs[i])
     return out
```
````

**Differences from the source** (`~/dotfiles/claude/.claude/CLAUDE.md:47-55`, current working copy): inline marks and "Doc edits are shown as before/after" replaced by diff blocks (D1, A1); What:/Why: 1-3 sentences (D7); title line, label granularity, `(optional)`, `Why: unknown`, `Assumptions:` line, no-code changes (D8); review-fix line (D3); "I" → "the user" (A3); two examples (D4); marker (D5). Kept: behaviour-not-code, readable without opening files, no restating code, concrete example for formats, inline single paths/commands.

**Gotchas**
- The source's What:/Why: wording is uncommitted in dotfiles (verified via `git diff`); the source to compare against is the working file, not `git show HEAD:`.
- The outer fence in this plan is four backticks because the file contains ```diff blocks; the file itself must use three.

**Done when**
- `command claude plugin validate plugins/workflow-preferences` reports the plugin as valid with no errors. It would fail on missing/invalid frontmatter.
- `grep -c '~~' plugins/workflow-preferences/skills/propose-changes/SKILL.md` → `0` (no inline marks left; fails if D1 wasn't applied).

### U2 — Rewrite issue #8's body
**Command:** write the body below to `/tmp/claude-1000/-home-david-agent-tools-plugin-marketplace/04260645-9a14-467f-ba8a-47a1f32ab095/scratchpad/issue-8-body.md`, then `gh issue edit 8 --body-file <that file>`.

**Content** (exact text):

```markdown
## Goal
Add skill `propose-changes` to the `workflow-preferences` plugin. It loads the user's rules for presenting proposed changes (C-labels, What:/Why: lines, diff blocks) whenever Claude presents changes for review.

## Not doing
- No hook, no script, no unittest.
- No permanent edit to `~/.claude/CLAUDE.md` (dotfiles#1 Part 2 trims it later). The section is moved out only temporarily for testing.

## Files
- create: `plugins/workflow-preferences/skills/propose-changes/SKILL.md`
- must not touch: other plugins

## Content
- The rules from the "Presenting proposed changes" section of `~/dotfiles/claude/.claude/CLAUDE.md`, updated: every edit is shown as a diff block (inline ~~/** marks dropped); `What:`/`Why:` 1-3 sentences; never invent a Why; title line per change; one label per independently approvable change; `(optional)` marker.
- Fixes suggested in a review use the same format.
- Two worked examples (doc edit, code fix).
- First body line: "Say `propose-changes loaded`." Remove once triggering is trusted.
- Description covers the situation (presenting changes, formats or review fixes for approval), not a fixed phrase list; excludes direct requests to make a change. User-invocable as `/workflow-preferences:propose-changes`.

## Done when
- `claude plugin validate plugins/workflow-preferences` passes.
- With the section removed from `~/.claude/CLAUDE.md`: a subagent clarity test reports no unresolved gaps or contradictions, and a few live sessions with `claude --plugin-dir plugins/workflow-preferences` show the skill fires and replies follow the format. Further tuning happens in use.
```

**Done when:** `gh issue view 8 --json body -q .body` prints the text above (starts with `## Goal`, contains "diff block", no "Blocked by #7", no "Repeat 3 times").

### U3 — Remove the CLAUDE.md section and run the clean subagent test
**Files:** modify `~/dotfiles/claude/.claude/CLAUDE.md` (resolved from `readlink -f ~/.claude/CLAUDE.md`, verified) temporarily; create backup `/tmp/claude-1000/-home-david-agent-tools-plugin-marketplace/04260645-9a14-467f-ba8a-47a1f32ab095/scratchpad/presenting-proposed-changes.md`. May modify `SKILL.md` only with user-approved changes (step 5).

**Steps**
1. Copy lines from `# Presenting proposed changes` through the blank line before `# After finishing work` (currently lines 47-56) into the backup file.
2. Remove exactly that block from CLAUDE.md with Edit. Confirm `grep -c "Presenting proposed changes" ~/dotfiles/claude/.claude/CLAUDE.md` → `0`.
3. Post the pre-flight check below and wait for the user's OK.
4. Launch the subagent. Read its output; check each proposal against the rules yourself (don't rely only on its checklist), and compare Part B with the expected answers.
5. Present findings as C-labelled proposals (defects first, optional separately). Apply only approved changes to `SKILL.md`, rerun U1's Done-when checks.

**Pre-flight**
| Field | Value |
|---|---|
| Agent type | `general-purpose` |
| Model | `sonnet` |
| Tools | `Read` on the SKILL.md path only (told in the prompt) |
| Read-only | Yes, writes no files |
| Expected output | 8 proposals, a rule checklist, a 10-row trigger table, a gap report |

**Prompt** (exact text):

````text
You are testing a Claude Code skill for clarity. Read
/home/david/agent-tools/plugin-marketplace/plugins/workflow-preferences/skills/propose-changes/SKILL.md
with the Read tool and apply ONLY its rules. Use no other tools and write no files. If any other
instructions you have conflict with the skill, follow the skill and report the conflict.

PART A. For each scenario, write the proposal exactly as you would present it to the user. Then
give a checklist: each rule in the skill → applied / not applicable / unclear (one-line reason).
If you need file contents, invent plausible ones and say so outside the proposal. If the scenario
gives no reason for a change, handle that as the skill says.
S1. Rename config key "timeout" to "timeout_seconds" in config.json (one occurrence).
S2. In README.md, the sentence "Run the installer once." should say "Run the installer twice."
S3. README.md has a 5-sentence "Installation" paragraph; 4 sentences need rewriting for a new
    install method.
S4. Propose a new single-line log format for a CLI tool's progress output.
S5. Review this function and propose fixes: it has an off-by-one in a loop bound, an unhandled
    None return, and a variable name that could be clearer (optional).
    def last_items(xs, n):
        out = []
        for i in range(len(xs) - n, len(xs) + 1):
            out.append(xs[i])
        return out.sort()
S6. Replace a hand-written retry loop (3 attempts, fixed 1s sleep) with the `tenacity` library;
    caveat: tenacity's default stop condition differs, so behaviour changes unless configured.
S7. Propose a process change: tag releases before merging to main. No code involved.
S8. Rename the function `load_cfg` to `load_config` everywhere: defined in config.py, called in
    cli.py and tests/test_config.py.

PART B. Based only on the description field, should the skill fire for each prompt? Answer
yes/no with a one-line reason.
1. "Propose a fix for the failing test."
2. "What would you change in this README?"
3. "Show me the git diff."
4. "Explain what this function does."
5. "Draft an edit to the onboarding doc for my review."
6. "Fix the typo in line 3."
7. "Review this PR and suggest fixes."
8. "What format should the report use?"
9. "Run the tests."
10. "Rename this variable."

PART C. Report, as bullets under each heading (write "none" if empty):
- Gaps: where you had to guess or invent; what you chose.
- Contradictions: between rules, or between the examples and the rules.
- Blocked: scenarios where no rule told you what to do or you could not proceed.
- Ambiguous terms: the term, your interpretation, and an alternative reading.
- Redundant or ignored rules.
- Conflicts with other instructions you have.
- Anything else that would make the skill clearer or more consistent.
````

**Expected Part B:** 1 yes, 2 yes, 3 no, 4 no, 5 yes, 6 no, 7 yes, 8 yes, 9 no, 10 no.

**What to check yourself in Part A** (from the first test): no invented Why (S2, S7, S8 → `Why: unknown`); every edit as a diff block, none with `~~`; S5 findings listed defects-first and C3 marked `(optional)`; S8 is one C with three per-file diff blocks; S7 shows steps, not a code block of invented code.

**Gotchas**
- dotfiles has uncommitted changes in `CLAUDE.md` and `settings.json` (verified). Never use `git restore`/`git checkout` on them; restore only from the backup (U4).
- While the section is out, every Claude session on this machine runs without these rules (accepted, D9).

**Done when:** Part B matches the expected answers 10/10 (or the user accepts each mismatch), and every Part C defect is either fixed by an approved change or explicitly waived by the user.

### U4 — User live tests, then restore the section
**Steps**
1. Hand over to the user: from the repo root run `claude --plugin-dir plugins/workflow-preferences` (if the alias doesn't pass the flag through, `command claude --plugin-dir …`). Recommend one test per format, each in a fresh session so earlier replies don't prime later ones. Tell the user not to approve any change, so the tests edit nothing:

| # | Prompt | Checks | Expected reply |
|---|---|---|---|
| T1 | "Propose a change to CLAUDE.md for my review: add a command that runs every plugin's tests in one go." | Diff block for prose | Marker; `**C1 — …**`; What:/Why:; `CLAUDE.md` then a `diff` block with the `## Commands` lines as context and one `+` line |
| T2 | "Propose changing the workflow-preferences description to 'Personal rules for how Claude plans, proposes and checks work.' everywhere it appears." | Multi-file change; no reason given | One C; two `diff` blocks headed `plugins/workflow-preferences/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; `Why: unknown` plus a question |
| T3 | "Review plugins/learning/bin/learn-session and suggest fixes." | Review fixes; code diff | Findings listed defects-first; each fix a C with a `diff` block; optional fixes titled `(optional)` |
| T4 | "Propose a new standalone unittest file for plugins/sdd/bin/sdd-check." | New code | One C; a `python` fenced block, not a diff |
| T5 | "Propose a format for a one-line summary that /roadmap could print after each unit." | New format | One C; a short concrete example of the line |
| T6 | "Propose a change to how we name branches in this repo." | Process change, no code | One C; the new steps as a list; no invented code |
| T7 | "Show me the git diff." | Should not fire | No marker; plain git diff output |

A test fails if the marker is missing (T1-T6) or present (T7), or if the reply uses `~~`/`**` inline marks, lacks a C title, or puts the change somewhere other than the expected block.
2. If the user wants wording changes, propose them as C-labels, apply approved ones to `SKILL.md`, rerun U1's Done-when checks.
3. Paste the backup block back in its original place (before `# After finishing work`) with Edit.

**Done when:** user reports the live-test result; `grep -c "Presenting proposed changes" ~/dotfiles/claude/.claude/CLAUDE.md` → `1`; `cd ~/dotfiles && git diff claude/.claude/CLAUDE.md` shows only the user's pre-existing What:/Why: change (fails if the restore dropped or duplicated lines).

### U5 — Commit
On branch `8-add-propose-changes-skill` (create from `main`), commit `SKILL.md` with subject `[#8] Add propose-changes skill` and the attribution trailer. Ask before `git push` / opening a PR (hard rule).

**Done when:** `git log -1 --stat` shows only `plugins/workflow-preferences/skills/propose-changes/SKILL.md`.

## Stop-and-ask triggers
- `plugin validate` fails for a reason not fixable inside `SKILL.md`.
- Any need to touch a file outside a unit's Files list.
- The CLAUDE.md block at U3 step 1 doesn't match lines 47-56 as described (the file changed since planning).
- A subagent finding that would add a rule to fix a problem another rule created (flag as over-engineering; propose simplifying first).
- Restore diff in U4 shows anything other than the pre-existing change.

## Verification (end to end)
- `command claude plugin validate plugins/workflow-preferences` → valid.
- `grep -c '~~' plugins/workflow-preferences/skills/propose-changes/SKILL.md` → `0`.
- Subagent test: Part B 10/10 vs expected; Part C defects resolved.
- User live sessions T1-T7 (U4) with `--plugin-dir`: each matches its expected reply.
- `grep -c "Presenting proposed changes" ~/dotfiles/claude/.claude/CLAUDE.md` → `1` after restore.

## Unverified
- `clodex claude` passes `--plugin-dir` through (help shows `[claude-flags]`).
- Exact output text of `claude plugin validate` on success.
- Whether subagents load the global CLAUDE.md (assumed yes; that's why U3 removes the section first).
