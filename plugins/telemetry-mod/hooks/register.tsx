// Entry point of the telemetry-mod plugin. Claude Code loads this file
// (hooks/hooks.json names it) and calls `register` once, handing it `on`,
// which adds hooks. This stub adds none yet; U5 fills it in.
import type { Register } from 'claude-code'

export const register: Register = () => {}
