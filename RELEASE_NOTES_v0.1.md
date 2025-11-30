# Pymordial v0.1.0 - The "Genesis" Release 🦕

## 🎉 First Stable Release

**Pymordial** is a robust, open-source Python framework designed to automate Android applications on BlueStacks with ease. It abstracts away the complexities of ADB, image recognition, and OCR into a clean, high-level API.

## ✨ Key Highlights

### 🔓 Open Source (MIT License)
Free for everyone! Use it for personal projects, commercial tools, or anything in between.

### 📦 Zero-Config OCR
**Bundled Tesseract**: No need to manually install Tesseract or fiddle with PATH variables. Pymordial comes with a portable Tesseract binary ready to go out of the box.

### 🎮 The `PymordialController` Facade
A single, unified entry point for all automation needs.
- **Convenience Methods**: `controller.tap()`, `controller.swipe()`, `controller.go_home()`
- **App Management**: `controller.<app_name>.open()`, `controller.is_app_running()`
- **State Awareness**: Automatically handles emulator and app lifecycle states.

### 🚀 High-Performance Streaming
- **Real-Time**: Decodes H.264 video from ADB for ~16-33ms latency (vs. 200ms+ for screenshots).
- **Efficient**: Lock-free atomic operations for thread-safe frame access.

### 🔍 Robust Computer Vision
- **Template Matching**: OpenCV-based element detection with confidence thresholds.
- **OCR Strategies**: Pluggable strategies for game-specific text extraction (e.g., cropping, upscaling, whitelisting).
- **Pixel Color Checks**: Fast verification of UI states.

### 🧪 Battle-Tested Reliability
- **Comprehensive Test Suite**: 100% pass rate on both unit and integration tests.
- **Self-Healing**: Automatic retries and state recovery for flaky emulators.

## 📦 Installation

```bash
pip install pymordial
# or
uv add pymordial
```

## 🚀 Quick Start

```python
from pymordial import PymordialController

# Initialize (automatically connects to ADB)
controller = PymordialController()

# Wait for BlueStacks
if controller.is_bluestacks_ready():
    print("BlueStacks is ready!")

# Start high-speed streaming
controller.start_streaming()

try:
    while True:
        # Get latest frame (instant)
        frame = controller.get_frame()
        
        # Check for text on screen
        if controller.check_text("Victory", frame):
            print("We won!")
            break
            
        # Tap a button
        controller.tap(500, 300)
finally:
    controller.stop_streaming()
```

## 📚 Documentation
- [GitHub Repository](https://github.com/IAmNo1Special/Pymordial)
- [Full Documentation](docs/pymordial_knowledge.md)

---
*Built with ❤️ by IAmNo1Special*
