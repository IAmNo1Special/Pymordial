# Pymordial 🦕

**The Primal Automation Framework for BlueStacks**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Google](https://img.shields.io/badge/code%20style-google-blueviolet.svg)](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)

Pymordial is a robust, high-performance Python framework designed to automate Android applications running on BlueStacks. It abstracts away the complexities of ADB, image recognition, and OCR into a clean, unified API, allowing you to build reliable bots and automation tools in minutes.

---

## ✨ Key Features

- **🚀 High-Performance Streaming**: Real-time H.264 video decoding via ADB (16-33ms latency) for instant frame access.
- **📦 Zero-Config OCR**: Bundled portable Tesseract binary means no manual installation required.
- **🎮 Unified Controller**: A single `PymordialController` facade manages ADB, BlueStacks, and Image Recognition.
- **🧠 Smart State Management**: Automatically tracks app and emulator states (`LOADING`, `READY`, `CLOSED`) to prevent crashes.
- **👁️ Computer Vision**: Built-in template matching, pixel color verification, and text extraction.
- **⚡ Atomic & Thread-Safe**: Designed for concurrency with lock-free frame access.

## 📦 Installation

Pymordial requires **Python 3.13+** and **BlueStacks 5+**.

### Using uv (Recommended)
```bash
uv add pymordial
```

### Using pip
```bash
pip install pymordial
```

## 🚀 Quick Start

Here's a complete example of a bot that waits for an app to load, checks for a "Victory" screen, and taps a button.

```python
import time
from pymordial import PymordialController

# 1. Initialize Controller (Auto-connects to ADB)
controller = PymordialController()

# 2. Open BlueStacks & App
print("Launching BlueStacks...")
controller.bluestacks.open()
controller.bluestacks.wait_for_load()

print("Launching Game...")
# Assuming 'com.example.game' is configured
controller.adb.open_app("com.example.game")

# 3. Start High-Speed Streaming
controller.start_streaming()

try:
    while True:
        # Get the latest frame (instant)
        frame = controller.get_frame()
        
        if frame is None:
            continue

        # Check for text on screen
        if controller.check_text("Victory", frame):
            print("🏆 Victory detected!")
            break
            
        # Tap 'Battle' button if visible
        # (Assuming you have a 'battle_btn' element defined)
        # if controller.click_element(battle_btn):
        #     print("Battle started!")
        
        time.sleep(0.1)

finally:
    # Always clean up
    controller.stop_streaming()
    controller.disconnect()
```

## 🛠️ Configuration

Pymordial uses a YAML-based configuration system. To customize settings (e.g., ADB port, OCR strategies), copy `config.example.yaml` to `config.yaml` in your project root.

**Example `config.yaml`:**
```yaml
adb:
  default_port: 5555
  stream:
    resolution: 1024
    bitrate: "5M"

bluestacks:
  resolution: [1920, 1080]
```

## 📚 Documentation

- **[API Reference](docs/API_REFERENCE.md)**: Detailed guide to all classes and methods.
- **[Knowledge Base](docs/pymordial_knowledge.md)**: Deep dive into architecture and patterns.
- **[Release Notes](RELEASE_NOTES_v0.1.md)**: What's new in v0.1.0.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) (coming soon) and ensure your code follows the **Google Python Style Guide**.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ by IAmNo1Special*
