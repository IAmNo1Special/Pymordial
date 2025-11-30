# Pymordial Survival Guide for Eager Juniors 🐣

**Welcome to the team!** Please don't break anything.

This guide is designed to help you make your first contribution without taking down the entire automation grid.

---

## 1. Project Structure (Where things live)

```
f:\Pymordial/
├── src/pymordial/
│   ├── controller/                # THE BRAINS 🧠
│   │   ├── pymordial_controller.py         # The Boss (Facade). Start here.
│   │   ├── adb_controller.py              # Talks to Android. Scary low-level stuff.
│   │   └── bluestacks_controller.py       # Manages the emulator window.
│   │
│   ├── core/                      # THE DATA 📦
│   │   ├── pymordial_app.py                # Represents an App (e.g., Revomon).
│   │   └── pymordial_element.py            # Represents a Button/Image.
│   │
│   ├── ocr/                       # THE EYES 👀
│   │   ├── tesseract_ocr.py               # Reads text.
│   │   └── base.py                        # Abstract base class (don't touch).
│   │
│   └── constants/                 # THE CONFIG ⚙️
│       └── configs.yaml                   # Default settings.
│
├── tests/                         # THE SAFETY NET 🕸️
│   ├── integration/               # Real tests with BlueStacks (Slow).
│   └── controller/                # Unit tests (Fast).
```

## 2. The Happy Path (How it works when it works)

1.  **User** instantiates `PymordialController`.
2.  **Controller** connects to ADB (`adb connect 127.0.0.1:5555`).
3.  **User** calls `controller.tap(100, 200)`.
4.  **Controller** delegates to `AdbController.tap()`.
5.  **AdbController** sends shell command `input tap 100 200`.
6.  **Android** receives command and clicks the screen.
7.  **Profit**.

## 3. 🐉 HERE BE DRAGONS (Danger Zones)

### 3.1. `adb_controller.py` -> `start_streaming()`
This uses `subprocess` to pipe raw H.264 video bytes from ADB into `av` (PyAV) for decoding. It involves threading, queues, and binary data.
**Advice**: Do not touch this unless you understand `threading.Lock` and video codecs. If you break it, the bot goes blind.

### 3.2. `state_machine.py`
This manages the valid transitions (e.g., you can't go from `CLOSED` to `READY` without `LOADING`).
**Advice**: If you mess up the transitions, the bot will get stuck in an infinite loop waiting for a state that never comes.

## 4. Your First Safe Change 🛡️

Want to contribute? Add a new **Convenience Method** to `PymordialController`.

1.  Open `src/pymordial/controller/pymordial_controller.py`.
2.  Find the "Convenience Methods" section.
3.  Add a method like `long_press()`:
    ```python
    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Performs a long press."""
        self.adb.swipe(x, y, x, y, duration_ms)
    ```
4.  Add a test in `tests/controller/test_pymordial_controller.py`.
5.  Run tests: `uv run pytest`.

## 5. Common Mistakes (Don't do these)

-   **Hardcoding Paths**: Don't write `C:\Users\Dave\...`. Use `pathlib.Path` and relative paths.
-   **Ignoring Wait Times**: Android is slow. If you click a button, wait for the next screen to load. Use `wait_time` parameters.
-   **Committing `tessdata`**: We bundle Tesseract, but don't commit 500MB of training data. Check `.gitignore`.

## 6. Testing Checklist

Before you push code, run this:
- [ ] `uv run pytest -m "not integration"` (Unit tests, must pass)
- [ ] `uv run pytest tests/integration/` (Integration tests, requires BlueStacks)

---

## Outstanding Questions & Blockers

-   **How do we handle different screen resolutions?** Right now, we assume 1920x1080. If a user runs 720p, coordinates will be wrong. We need a scaling system.
-   **Where are the logs?** We print to stdout. We should probably use the `logging` module properly.
