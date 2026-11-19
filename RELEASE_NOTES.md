# Pymordial v0.5.0 Release Notes

## 🚀 App Lifecycle, Scaling, and Stricter States

This release gives `PymordialApp` its own lifecycle helpers, adds resolution-independent element coordinates, and makes invalid state transitions fail with a dedicated exception.

### Highlights

*   **App Lifecycle**: `PymordialApp` now has `open()`, `close()`, and `wait_until_ready()` methods that drive the app through a `PymordialController`. An app with a `ready_element` can reach `READY` without callers duplicating state transitions. A timed-out wait stays in `LOADING`, so it can be retried without relaunching.
*   **Element Scaling**: `PymordialElement` gained `scaled_position()`, `scaled_size()`, and `scaled_region()`, which map a layout recorded at `og_resolution` onto the current screen size.
*   **Plugin Cleanup**: `PluginRegistry.shutdown_all()` shuts down every registered plugin in order, logs failures instead of aborting, and makes repeat calls a no-op.
*   **Plugin Initialization**: Entry-point plugins are now initialized even when the registry has no configuration. An empty config means "use the plugin's defaults" rather than skipping setup.
*   **Handler Registration**: `StateMachine.register_handler()` merges enter/exit handlers for a state instead of replacing handlers registered earlier.

### ⚠️ Breaking Changes

*   **State Errors**: Invalid transitions now raise `PymordialStateError`. It subclasses both `PymordialError` and `ValueError`, so existing `except ValueError` handlers keep catching it.
*   **App State Transitions**: `AppState` is stricter. `CLOSED` may only transition to `LOADING`; `LOADING` may move to `CLOSED` or `READY`; `READY` may move to `CLOSED` or `LOADING`.

### 📦 Installation

```bash
uv add pymordial==0.5.0
```

---

### 🤝 Contributors

*   @IAmNo1Special
*   @Fsdiallo
