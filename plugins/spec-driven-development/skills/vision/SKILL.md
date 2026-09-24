---
name: vision
description: Drafts or revises the project's Vision by interview, challenging each item, and writes it where sdd.md says.
argument-hint: "[your idea, in a line or two]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh issue view *)
---

Document: `Vision`
Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Challenge menu: `${user_config.challenge_menu}`
From the developer: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/shared/generate.md` and follow it for this document.
