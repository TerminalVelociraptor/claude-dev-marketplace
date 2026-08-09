# spec-tools marketplace

A personal Claude Code marketplace. Currently ships one plugin:

- **spec-toolkit** — author, evaluate, and maintain project design/architecture specs against
  a rubric derived from ISO/IEC/IEEE 42010, arc42, Architecture Decision Records, and
  ISO/IEC 25010. Four skills:
  - `spec-writer` — draft a spec that satisfies the rubric ("write a design doc for X").
  - `spec-evaluator` — full review: runs consistency, completeness, technical fact-check
    (web search), and moderate concision, then a retention check ("review my design doc").
  - `spec-consistency` — fast internal-coherence check only, no web search, for when you've
    edited sections and want to confirm the spec still holds together.
  - `spec-factcheck` — validate the spec's technical claims against the current world via
    web search, flagging wrong/outdated/unsupported ones (abstains on non-checkable claims).

  Shared definitions live in `plugins/spec-toolkit/shared/` — `rubric.md`,
  `consistency-checks.md`, `factcheck-procedure.md`. The standalone skills and the full
  evaluator read the *same* shared files, so editing a check in one place changes both the
  focused skill and the full evaluation. This is the single control surface for the toolkit.

## Try it without installing (fastest for testing)

Load the plugin directly from this folder for one session:

```bash
claude --plugin-dir /path/to/spec-tools/plugins/spec-toolkit
```

Then in the session, ask something like: "Evaluate this design doc" and attach a spec.

## Install locally at user (global) scope

This adds the marketplace from your local path and installs the plugin so it is available
across all your projects.

```bash
# 1. Add this local folder as a marketplace
claude plugin marketplace add /path/to/spec-tools

# 2. Install the plugin at user scope (the default)
claude plugin install spec-toolkit@spec-tools --scope user

# 3. Restart Claude Code to apply
```

Verify:

```bash
claude plugin list
```

## Updating after you edit the plugin

```bash
claude plugin marketplace update spec-tools   # refresh the catalog
claude plugin update spec-toolkit@spec-tools  # update the installed plugin
# then restart Claude Code
```

If an update reports "already at latest" but you know it changed, reinstall:

```bash
claude plugin uninstall spec-toolkit@spec-tools
claude plugin install spec-toolkit@spec-tools --scope user
```

## Later: publish to a private GitHub repo

Push this whole folder to a private repo, then on any machine:

```bash
claude plugin marketplace add your-username/spec-tools
claude plugin install spec-toolkit@spec-tools --scope user
```
