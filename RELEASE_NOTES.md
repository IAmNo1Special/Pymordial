# Pymordial v0.4.0 Release Notes

## 🚀 Platform-Agnostic Core

This release marks a major architectural shift, decoupling the core framework from Android-specific implementations. `pymordial` is now a truly platform-agnostic automation interface.

### Highlights

*   **Abstract Core**: `PymordialApp` is now an Abstract Base Class (ABC). It defines the contract for applications (`open`, `close`, `state`) but contains no platform logic.
*   **Android Decoupling**: Moved all Android package management, ADB commands, and BlueStacks logic out of the core library. These will live in platform-specific extensions (e.g., `pymordialblue`).
*   **Clean Configuration**: The `configs.yaml` and `TypedDict` structures have been stripped of all ADB/BlueStacks settings. The core config now only manages generic `app`, `element`, and `controller` settings.
*   **Enhanced Testing**: Added rigorous verification for abstract interfaces and state machine logic using concrete test implementations.

### ⚠️ Breaking Changes

*   **PymordialApp Instantiation**: You can no longer instantiate `PymordialApp` directly. You must use a concrete implementation (e.g., `PymordialAndroidApp` from a platform extension).
*   **Configuration Keys**: Removed `adb`, `bluestacks`, `image_controller`, `extract_strategy`, and `setup` sections from the configuration.

### 📦 Installation

```bash
uv add pymordial==0.4.0
```

---

### 🤝 Contributors

*   @IAmNo1Special
