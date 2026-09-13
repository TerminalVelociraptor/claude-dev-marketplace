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

The skill delegates the decision to a Sonnet subagent, which consults `reference/models-condensed.md` and returns a short recommendation.

## Development testing

```bash
claude --plugin-dir /home/david/agent-tools/plugin-marketplace/plugins/model-picker
```
