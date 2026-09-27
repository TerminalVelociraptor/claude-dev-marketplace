---
name: task
description: Drafts a task by interview, challenging each item, and returns it for you to put where you want.
argument-hint: "[the slice file or issue, or the change]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh issue view *)
---

Document: `Task`
Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Challenge menu: `${user_config.challenge_menu}`
From the developer: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/shared/generate.md` and follow it for this document.
