---
name: slice
description: Drafts a slice by interview, challenging each item, and returns it for you to put where you want.
argument-hint: "[what the user should be able to do]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh issue view *)
---

Document: `Slice`
Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Challenge menu: `${user_config.challenge_menu}`
From the developer: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/shared/generate.md` and follow it for this document.
