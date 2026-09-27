---
name: update
description: Checks the project's documents against sdd.md and against each other, and reports what's inconsistent. Runs on docs/ plus any slices or tasks you name (files or GitHub issue numbers). Reports only; you approve every edit.
argument-hint: "[slice or task files, or issue numbers]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(${CLAUDE_PLUGIN_ROOT}/bin/sdd-check *), Bash(gh issue view *)
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Named by the developer: $ARGUMENTS

# Update

## 1. Deterministic checks
From the project root, run:

    ${CLAUDE_PLUGIN_ROOT}/bin/sdd-check --doc <entry> <file> ...

Add one `--doc` per slice or task file the developer named. `<entry>` is the `sdd.md` entry the file is; ask if you can't tell. If nothing was named, run it with no `--doc` and don't ask for a target: it still checks every document at a location `sdd.md` gives. For a GitHub issue, pipe it in, one issue per run:

    gh issue view <n> --json title,body --jq '"# " + .title + "\n\n" + .body' | ${CLAUDE_PLUGIN_ROOT}/bin/sdd-check --doc <entry> -

Exit 2 means the script itself failed: show its message and stop.

## 2. Judgment checks
Read `${CLAUDE_PLUGIN_ROOT}/sdd.md` and every document checked in step 1; for an issue, run `gh issue view <n>`. Report, with `path:line`:
- **Outside Contains:** content that isn't one of its entry's Contains items. Say which document it belongs in, if any.
- **Contradictions:** two documents that say incompatible things, e.g. an Open decisions question with no answer link while an ADR or document already settles it. Quote both sides.

Don't repeat what the script reported. Don't comment on style, or on how or when the developer works.

## 3. Report
Group findings by document, each as `path:line — finding — (script)` or `(judgment)`. Then list proposed edits as E1, E2, …: each with its file, the change as before/after, and the finding it fixes. For a finding only the developer can settle, propose nothing and say so.

## 4. Edits
Make no edit until the developer approves it by label. Apply only the approved edits, then run `sdd-check` again and show its last line.
