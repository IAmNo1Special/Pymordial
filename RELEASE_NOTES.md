# Pymordial v0.4.0 Release Notes

## 🚀 Platform-Agnostic Core

This release marks a major architectural shift, decoupling the core framework from Android-specific implementations. `pymordial` is now a truly platform-agnostic automation interface.

### Highlights

*   **Dataclass Architecture**: `PymordialApp`, `PymordialScreen`, and `PymordialElement` are now pure dataclasses with auto-generated IDs and built-in validation.
*   **Android Decoupling**: Moved all Android package management, ADB commands, and BlueStacks logic out of the core library. These will live in platform-specific extensions (e.g., `pymordialblue`).
*   **Clean Configuration**: The `configs.yaml` and `TypedDict` structures have been stripped of all ADB/BlueStacks settings. The core config now only manages generic `app`, `element`, and `controller` settings.
*   **Blueprint Cleanup**: Removed improper `basicConfig` calls from device blueprints and aligned state machines to be instance attributes.
*   **Enhanced Testing**: Added rigorous verification for dataclass validation and state machine logic using concrete test implementations.

### ⚠️ Breaking Changes

*   **PymordialApp Changes**: `PymordialApp` is now a dataclass, not an ABC. You can instantiate it directly or extend it with additional fields.
*   **Configuration Keys**: Removed `adb`, `bluestacks`, `image_controller`, `extract_strategy`, and `setup` sections from the configuration.
*   **Element Location**: `PymordialElement` moved from `pymordial.core.blueprints.element` to `pymordial.ui.element`.

### 📦 Installation

```bash
uv add pymordial==0.4.0
```

---

### 🤝 Contributors

*   @IAmNo1Special
