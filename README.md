# Pymordial 🦕

**Extensible Automation Framework for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pymordial)](https://pypi.org/project/pymordial/)

Pymordial is a platform-agnostic automation framework that provides a standardized interface for controlling applications on any device. It defines the core contracts (`Controller`, `App`, `Device`) that allow you to build robust, state-aware automation tools for Android, iOS, Windows, or Web.

> **Note:** This is the core framework. For Android/BlueStacks implementation, see [pymordialblue](https://github.com/IAmNo1Special/pymordialblue) (Coming Soon).

---

## 🏗️ Architecture

Pymordial provides the **Blueprints** for automation:

- **`PymordialController`**: The brain. Manages devices, apps, and user inputs (clicks, swipes, text).
- **`PymordialApp`**: The soul. A robust `StateMachine` (CLOSED → LOADING → READY) that tracks app lifecycle.
- **`PymordialElement`**: The eyes. Unified interface for finding UI components via:
    - **Images** (Template Matching)
    - **Text** (OCR)
    - **Pixels** (Color Arrays)
- **`PymordialDevice`**: The body. Abstract interfaces for emulators, bridges (ADB/Win32), and screen processing.

---

## 📦 Installation

```bash
uv add pymordial
```

Or using pip:

```bash
pip install pymordial
```

---

## 🚀 Quick Start: Building a Controller

Pymordial is designed to be extended. Here is how you implement a simple controller for a hypothetical platform.

### 1. Implement the Controller

```python
from pymordial.core.controller import PymordialController

class MyPlatformController(PymordialController):
    """A concrete implementation for MyPlatform."""
    
    def click_coord(self, coords, times=1):
        print(f"Clicking {coords} {times} times on target device...")
        # device_bridge.send_click(coords)
        return True

    def capture_screen(self):
        # return device_bridge.get_screenshot()
        pass
        
    # ... implement other abstract methods ...
```

### 2. Define an App

`PymordialApp` is a **pure data model**. It holds app metadata and screens:

```python
from pymordial.core.app import PymordialApp
from pymordial.core.screen import PymordialScreen
from pymordial.ui.image import PymordialImage

# Create an app with screens and elements
main_menu = PymordialScreen(name="main_menu")
main_menu.add_element(PymordialImage(label="play_button", source_path="assets/play.png"))

game = PymordialApp(app_name="SuperGame")
game.add_screen(main_menu)
```

### 3. Automate!

Once implemented, you get the full power of Pymordial's state machine and element system.

```python
# 1. Setup
controller = MyPlatformController()
controller.add_app(game)  # Register the app

# 2. Operate via Controller (which delegates to BridgeDevice)
controller.open_app("SuperGame", "com.game", timeout=60, wait_time=10)

# 3. Find and Click Elements
play_button = game.get_screen("main_menu").get_element("play_button")
if controller.is_element_visible(play_button):
    controller.click_element(play_button)
```

---

## ⚙️ Configuration

The core library uses a strictly typed, minimal configuration:

```yaml
# pymordial_config.yaml
app:
  action_timeout: 60
  action_wait_time: 10

element:
  default_confidence: 0.7

controller:
  default_click_times: 1
```

---

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes (please follow PEP 8).
4.  Submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
