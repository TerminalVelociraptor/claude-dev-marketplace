export type Snapshot = {}

declare module 'claude-code' {
  interface PluginState {
    'telemetry-mod': { snap: Shaped<Snapshot> }
  }
}
