---
paths:
  - "plugins/spec-driven-development/**"
---

# spec-driven-development plugin

## Source of truth
- This plugin is the source of truth for the process it implements.
- `/home/david/plan-tooling/stages.md` is the temporary design skeleton the plugin is being built from. Read it for intent when adding a stage. Plugin files never read or cite it, and it will be retired.

## Which file owns which fact
Add a row when a new file becomes the owner of a fact. Everything else reads the owner or points to it.

| Fact | Owner |
|---|---|
| Overview headings, their order, and their comment prompts | `templates/01-overview.md` |
| Word limits, tiny marker, Priorities minimum items | `config.json` (`vision`) |
| Paths to docs in the target project | `config.json` (`project_paths`) |
| Paths to files inside this plugin, such as the template | `config.json` (`plugin_paths`) |

## Conventions
- Tunable numbers and paths live in `config.json`. Scripts, skills and agents read them instead of restating them.
- In `config.json`, keys starting with `_` are comments. Code ignores them.
- Adding an overview heading means editing only the template.
- Docs the plugin creates that stay in a project repo are prefixed with the number of the stage that creates them, e.g. `docs/01-overview.md`. Disposable files, such as drafts in `docs/drafts/`, are not numbered.
- A template is named after the file it creates.
