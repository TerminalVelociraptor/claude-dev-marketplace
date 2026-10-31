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
