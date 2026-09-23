---
paths:
  - "plugins/spec-driven-development/**"
---

# spec-driven-development plugin

## Source of truth
- This plugin is the source of truth for the process it implements.
- `/home/david/plan-tooling/documents.md` is the temporary design the plugin is being built from: what each project document holds and why. Read it for intent when adding tooling. Plugin files never read or cite it, and it will be retired.

## Which file owns which fact
Add a row when a new file becomes the owner of a fact. Everything else reads the owner or points to it.

| Fact | Owner |
|---|---|
| (none yet) | |

## Conventions
- Tunable numbers and paths live in `config.json`. Scripts, skills and agents read them instead of restating them.
- In `config.json`, keys starting with `_` are comments. Code ignores them.
- A template is named after the file it creates.
