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
