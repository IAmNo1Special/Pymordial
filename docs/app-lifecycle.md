# App Lifecycle

Pymordial builds reliability through state awareness.

## State Machine

Every `PymordialApp` has an internal `StateMachine`.

1. **Launch**: `open()` transitions state to `LOADING`.
2. **Wait**: The controller checks for a "Ready Element" (e.g. Main Menu).
3. **Ready**: When found, state transitions to `READY`.
4. **Close**: `close()` transitions state to `CLOSED`.

This prevents scripts from interacting with an app before it is ready.
