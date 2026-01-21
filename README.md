# Pymordial 🦕

**Extensible Automation Framework for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pymordial)](https://pypi.org/project/pymordial/)

Pymordial is an extensible automation framework designed to support any platform (Android, iOS, Windows, etc.). Currently, it features complete **end-to-end support for BlueStacks 5**, utilizing ADB (Android Debug Bridge) for device control and a unified vision system for UI interaction.

---

## Key Features

- **Platform Agnostic Design**: Built to support custom device implementations.
- **BlueStacks Integration**: Native support for **BlueStacks 5** (launch, kill, window management) included out-of-the-box.
- **Pure Python ADB**: Uses `adb-shell` for direct communication without requiring a system ADB installation.
- **High-Performance Streaming**: Implements H.264 screen capture streaming for low-latency visual feedback.
- **Unified Vision System**: Seamlessly find and interact with:
    - **Images**: Template matching with confidence thresholds.
    - **Text**: OCR powered by Tesseract.
    - **Pixels**: Precise color verification with tolerance.
- **BlueStacks Integration**: Native control over the BlueStacks emulator (launch, kill, window management).
- **App Lifecycle Management**: Robust `StateMachine` (CLOSED → LOADING → READY) for app stability.
- **Type-Safe Configuration**: Strictly typed configuration system via `TypedDict`.

---

## Prerequisites

- **BlueStacks 5**: Installed on Windows (Hyper-V, Nougat, Pie, or Android 11 instances supported).
- **Enable ADB**: Enable "Android Debug Bridge" in BlueStacks Settings > Advanced.
- **Python 3.13+**: Ensure you have a modern Python version installed.

---

## Installation

We recommend using [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv add pymordial
```

Alternatively, you can use pip:

```bash
pip install pymordial
```

### Setup BlueStacks

If you don't have BlueStacks installed, you can use the included setup script:

```bash
uv run src/pymordial/scripts/setup_bluestacks.py
```

---

## Configuration

Pymordial uses a sensible default configuration suitable for most use cases. To override these settings, create a `pymordial_config.yaml` file in your project root.

**Example `pymordial_config.yaml`:**

```yaml
adb:
  default_host: "127.0.0.1"
  default_port: 5555
  stream:
    resolution: 1024  # Stream width

bluestacks:
  resolution: [1920, 1080]  # Target resolution for scaling

app:
  action_timeout: 45
```

---

## Quick Start

### 1. Connect and Verify

Create a `PymordialController` to manage the connection.

```python
from pymordial import PymordialController

# Initialize controller (auto-connects to default ADB host/port)
controller = PymordialController()

# Check Device Status
if controller.bluestacks.is_ready():
    print("✅ BlueStacks is ready")
else:
    print("⏳ Launching BlueStacks...")
    controller.bluestacks.open()

if controller.adb.is_connected():
    print("✅ ADB Connected")
```

### 2. Define UI Elements

Define the elements you want to interact with using `PymordialImage`, `PymordialText`, or `PymordialPixel`.

```python
from pymordial import PymordialImage, PymordialPixel, PymordialText

# Image Element (Template Matching)
start_button = PymordialImage(
    label="start_button",
    filepath="assets/start_btn.png",
    confidence=0.8,
    og_resolution=(1920, 1080),  # Resolution where asset was captured
)

# Text Element (OCR)
level_text = PymordialText(
    label="level_indicator",
    element_text="Level 1",
)

# Pixel Element (Color Check)
health_bar = PymordialPixel(
    label="full_health",
    position=(100, 50),
    pixel_color=(0, 255, 0),
    tolerance=10,
)
```

### 3. Interacting with Elements

Use the controller to find, click, or read elements.

```python
# Check visibility
if controller.is_element_visible(start_button):
    print("Start button found!")
    
    # Click element
    controller.click_element(start_button)

# Find coordinates directly
coords = controller.find_element(health_bar)
if coords:
    print(f"Health bar at: {coords}")

# Read text from screen
text_lines = controller.read_text(controller.capture_screen())
print("Screen text:", text_lines)
```

### 4. Managing App Lifecycle

Use `PymordialApp` to robustly manage application state.

```python
from pymordial import PymordialApp

# Define an app with a "ready marker"
my_game = PymordialApp(
    app_name="MyGame",
    package_name="com.example.mygame",
    ready_element=start_button,  # App is 'READY' when this is visible
)

# Register app with controller
controller.add_app(my_game)

# Open app and wait for it to be ready
controller.my_game.open()

if controller.my_game.is_open():
    print("App represents: READY state")
```

---

## Architecture Overview

The system is organized into a clean implementation hierarchy:

```
PymordialController
├── adb (PymordialAdbDevice)
│   ├── AdbShell (Bridge)
│   ├── Streaming (H.264 -> PyAV)
│   └── Input (Tap, Swipe, Text)
│
├── bluestacks (PymordialBluestacksDevice)
│   ├── Process Management
│   └── Window Control
│
└── ui (PymordialUiDevice)
    ├── Vision Strategy (OpenCV)
    ├── OCR Engine (Tesseract)
    └── Matching Logic (Image/Pixel/Text)
```

---

## Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes (please follow PEP 8).
4.  Submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
