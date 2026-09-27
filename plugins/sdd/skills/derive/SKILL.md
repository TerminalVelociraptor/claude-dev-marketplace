---
name: derive
description: Proposes the derived files sdd.md defines, from the current documents, and writes only what you approve.
argument-hint: "[one derived file to regenerate; default all]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Asked for: $ARGUMENTS

# Derive files

1. Read `${CLAUDE_PLUGIN_ROOT}/sdd.md` in full. Its derived-files entries define each derived file: where it lives, what it is **Derived from**, and what it **Holds**, each with a *Why*. Work on the one the developer asked for, or all of them.
2. For each derived file:
   - Read everything its **Derived from** names. Build exactly what **Holds** lists and nothing else: copy only where Holds says to copy, and link otherwise.
   - If its location limits when it exists, or a source it needs doesn't exist yet, skip it and say why.
   - If its location is a block between markers in a file the developer owns, change only the lines between the markers. If the markers aren't there, propose adding the block, markers included, at the end of the file. Never edit outside them.
   - If **Derived from** names something taken from the repo rather than a document (such as code paths), take it from the existing derived file if there is one, and check with Glob that it still matches files. If it matches nothing, or there is no existing file, propose it from the repo layout, check with Glob that it matches files, and confirm it with the developer.
   - A file under `.claude/rules/` starts with YAML frontmatter holding a `paths` list of globs, so it loads only for those files.
   - A Mermaid diagram goes in a fenced `mermaid` block.
3. Show the difference from what is there now, or the whole content for a new file.
4. Write only the changes the developer approves. Propose; never overwrite unasked.
5. End with one line per derived file: written, proposed and declined, skipped (with the reason), or unchanged.
