---
name: system
description: Drafts or revises the System section by interview, challenging each item, and writes it where sdd.md says.
argument-hint: "[anything to start from]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh issue view *)
---

Document: `System`
Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Challenge menu: `${user_config.challenge_menu}`
From the developer: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/shared/generate.md` and follow it for this document.
