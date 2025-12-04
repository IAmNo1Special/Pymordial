# Pymordial 🦕

**BlueStacks Automation Framework for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pymordial)](https://pypi.org/project/pymordial/)

Pymordial automates Android apps running on BlueStacks using ADB, template matching, and OCR.

---

## Installation

**Requirements**: Python 3.13+, BlueStacks 5+ (Windows)

```bash
uv add pymordial
# or
pip install pymordial
```

No system ADB required - uses `adb-shell` Python package.

---

## Quick Start

### Basic Connection

```python
from pymordial import PymordialController

# Create controller (auto-connects to ADB at 127.0.0.1:5555)
controller = PymordialController()

# Check BlueStacks status
if controller.bluestacks.is_ready():
    print("BlueStacks is ready")
else:
    controller.bluestacks.open()

# Verify ADB connection
if controller.adb.is_connected():
    result = controller.adb.shell_command("getprop ro.build.version.release")
    print(f"Android: {result.decode().strip()}")
```

### Define UI Elements

```python
from pymordial import PymordialImage, PymordialPixel, PymordialText

# Image element (template matching)
button = PymordialImage(
    label="my_button",
    filepath="assets/button.png",
    confidence=0.8,
    og_resolution=(1920, 1080),  # Resolution when screenshot was taken
)

# Pixel element (color detection)
indicator = PymordialPixel(
    label="health_bar",
    position=(100, 50),
    pixel_color=(0, 255, 0),  # RGB
    tolerance=20,
)

# Text element (OCR)
title = PymordialText(
    label="game_title",
    element_text="Play Now",
)
```

### Find and Click Elements

```python
# Check if element is visible
if controller.is_element_visible(button):
    print("Button found!")

# Get element coordinates
coords = controller.find_element(button)
if coords:
    print(f"Found at: {coords}")

# Click element
controller.click_element(button)

# Click coordinates directly
controller.tap(500, 300)
```

### App Lifecycle with `ready_element`

The `ready_element` pattern auto-transitions from LOADING → READY:

```python
from pymordial import PymordialApp, PymordialText

# Define element that indicates app is loaded
ready_indicator = PymordialText(
    label="main_menu",
    element_text="Play & Earn"
)

# Create app with ready_element
my_game = PymordialApp(
    app_name="MyGame",
    package_name="com.example.game",
    ready_element=ready_indicator,
)

# Register with controller
controller.add_app(my_game)

# Open app - auto-detects when ready!
controller.my_game.open()

# Check app state
if controller.my_game.is_loading():
    print("Still loading...")
if controller.my_game.is_open():
    print("Ready to interact!")
```

---

## Architecture

```
PymordialController
├── adb        (AdbController)      - Shell commands, streaming, tap/swipe
├── bluestacks (BluestacksController) - Open/close emulator, window management
├── image      (ImageController)    - Template matching, pixel detection
└── text       (TextController)     - OCR via Tesseract
```

---

## Configuration

Create `config.yaml` in project root to override defaults:

```yaml
adb:
  default_port: 5555
  
bluestacks:
  resolution: [1920, 1080]

app:
  ready_check_max_tries: 3
```

---

## Documentation

- [Examples](examples/) - Working example scripts
- [API Reference](docs/API_REFERENCE.md) - Class documentation
- [Quick Start](docs/QUICKSTART.md) - Getting started guide

---

## License

MIT License - see [LICENSE](LICENSE)
