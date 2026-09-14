# Model Picker

Recommends a Claude or GPT model and effort level for an upcoming task using a bundled comparison reference.

## Install / uninstall

This plugin is part of the `dev-toolkits` marketplace at
`/home/david/agent-tools/plugin-marketplace`.

- **Install:** `/plugin install model-picker@dev-toolkits`
- **Uninstall:** `/plugin uninstall model-picker@dev-toolkits`

## Usage

Ask for a recommendation before beginning work, for example:

- "What model should I use for this?"
- "Should I switch models for a multi-file refactor?"
- "Recommend a model and effort level for a security review."

The skill launches the plugin's `model-picker:picker` agent (**Opus 5**, defined in
[`agents/picker.md`](agents/picker.md)) for the lookup. Claude Code only spawns subagents on an
explicit request or a named agent type, so the skill names the agent directly. If the agent is
unavailable, the skill reads the same instructions and works inline, and says so. Opus is a workflow choice, not a measured
claim about model-selection accuracy or cost. The skill returns a short, evidence-qualified
recommendation and does not switch models or execute the proposed task.

## Reference and evidence

- [`models-condensed.md`](skills/model-picker/reference/models-condensed.md): shared task
  categories, model overlap, pricing/cache/context constraints, supported effort settings,
  comparative results, and clodex integration limits.
- [`evidence.md`](skills/model-picker/reference/evidence.md): source links, dates, configurations,
  metric definitions, provenance, and comparison limits for the **2026-09-13** audit snapshot.

The reference separates provider documentation, provider-run evaluations, third-party evaluations,
and **CodeRabbit supporting evidence**. CodeRabbit figures from different review pipelines and
snapshots are not treated as one model leaderboard. Where quality is unranked, recommendations
say so rather than inventing a winner. API token rates are not subscription costs or measured
cost per successful task.

Update source conditions alongside numbers when refreshing the snapshot. The recorded clodex
2.11.6 check verified offline mapping and serialization only, not live backend/OAuth behavior.

## Development testing

```bash
claude --plugin-dir /home/david/agent-tools/plugin-marketplace/plugins/model-picker
```
