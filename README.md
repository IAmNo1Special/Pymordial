# Pymordial 🦕

**BlueStacks Automation Framework for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pymordial)](https://pypi.org/project/pymordial/)

Pymordial is a robust framework designed to automate Android applications. It leverages ADB for low-level device control and streaming, combined with advanced image processing (OpenCV) and OCR (Tesseract/EasyOCR) for reliable UI interaction.

---

## Features

*   **Robust Device Control**: Direct ADB integration for reliable tapping, swiping, and text input.
*   **High-Performance Streaming**: Real-time screen streaming via `screenrecord` for faster analysis than repeated screenshots.
*   **Smart Element Detection**: Locate UI elements using template matching (`PymordialImage`), pixel color (`PymordialPixel`), or text content (`PymordialText`).
*   **App Lifecycle Management**: Built-in state machine to handle app launching, loading, and ready states automatically.
*   **Flexible OCR**: Support for Tesseract (default) and EasyOCR, with customizable pre-processing strategies for difficult text.
*   **BlueStacks Integration**: automated window management and process handling.

---

## Installation

**Requirements**:
*   Python 3.13+
*   BlueStacks 5+ (Windows)

We strictly recommend using **[uv](https://docs.astral.sh/uv/)** for dependency management to ensure a reproducible environment.

```bash
# Add to your project
uv add pymordial
```

No system-wide ADB installation is required; Pymordial uses a pure-Python ADB implementation.

---

## Architecture

Pymordial is built on a modular controller-based architecture:

*   **`PymordialController`**: The central orchestrator that manages devices and applications.
*   **`PymordialApp`**: Represents an Android app with a defined lifecycle (CLOSED -> LOADING -> READY).
*   **`PymordialDevice`**:
    *   **`AdbDevice`**: Handles core Android interactions (shell commands, input, streaming).
    *   **`BluestacksDevice`**: Manages the emulator process and window.
*   **`ImageController`**: Handles visual search (template matching, pixel colors).
*   **`TextController`**: Manages OCR operations.

---

## Quick Start

### 1. Basic Connection

Connect to BlueStacks and verify the device state.

```python
from pymordial import PymordialController

# Auto-connects to ADB (default 127.0.0.1:5555)
controller = PymordialController()

# Ensure BlueStacks is running
if not controller.bluestacks.is_ready():
    print("Launching BlueStacks...")
    controller.bluestacks.open()

# Verify ADB connection
if controller.adb.is_connected():
    print(f"Connected to device: {controller.adb.device_id}")
```

### 2. Define UI Elements

Elements are the building blocks of your automation.

```python
from pymordial import PymordialImage, PymordialPixel, PymordialText

# 1. Image Element (Template Matching)
# Capture a small snippet of the UI you want to click.
start_btn = PymordialImage(
    label="start_button",
    filepath="assets/start_btn.png",
    confidence=0.8,
    og_resolution=(1920, 1080), # Resolution when the screenshot was captured
)

# 2. Pixel Element (Color Detection)
# Extremely fast checks for status indicators (e.g., health bars, red dots).
health_indicator = PymordialPixel(
    label="health_low",
    position=(100, 50),
    pixel_color=(255, 0, 0),    # RGB
    tolerance=10,
)

# 3. Text Element (OCR)
# Find elements by their text content.
login_text = PymordialText(
    label="login_label",
    element_text="Sign In",
)
```

### 3. Interact with Elements

```python
# Check visibility
if controller.is_element_visible(start_btn):
    controller.click_element(start_btn)

# Wait for an element to appear
try:
    coords = controller.find_element(login_text, max_tries=5)
    print(f"Login found at: {coords}")
except PymordialError:
    print("Element not found.")
```

### 4. App Lifecycle Automation

Use `PymordialApp` to handle app startup logic automatically.

```python
from pymordial import PymordialApp

# Define an element that proves the app is fully loaded
main_menu = PymordialImage(label="main_menu", filepath="assets/menu.png")

# Define the app
my_game = PymordialApp(
    app_name="My RPG",
    package_name="com.example.rpg",
    ready_element=main_menu,
)

# Register and open
controller.add_app(my_game)
controller.my_game.open()

# Wait for the app to be READY (automatically checks for ready_element)
if controller.my_game.is_open():
    print("App is ready for automation!")
```

---

## Configuration

Pymordial comes with sensible defaults, but it is highly configurable. To override defaults, create a `pymordial_config.yaml` file in your project root.

The configuration keys override the internal defaults found in `src/pymordial/configs.yaml`.

### Example `pymordial_config.yaml`

```yaml
adb:
  # Change if using a different emulator or remote device
  default_host: "127.0.0.1"
  default_port: 5555
  
  # Improve performance by adjusting stream settings
  stream:
    resolution: 1280  # Reduce resolution for speed
    bitrate: "2M"     # Lower bitrate for less bandwidth

bluestacks:
  # Target resolution for the emulator window
  default_resolution: [1920, 1080]
  
  # Path to BlueStacks executable if not standard
  hd_player_exe: "HD-Player.exe" 

extract_strategy:
  # Advanced OCR tuning for Tesseract
  default:
    upscale_factor: 3       # Resize image before OCR
    denoise_strength: 10    # Apply noise reduction
    threshold_binary_max: 255
```

### OCR Strategies

You can define custom strategies in `pymordial_config.yaml` to handle specific text extraction cases. For example, reading white text on a dark background vs. black text on light.

```python
# In code, use the strategy name defined in your config
text = controller.read_text(region=(0, 0, 100, 100), strategy="clean_white_text")
```

---

## Advanced Usage

### Screen Streaming

For high-speed automation, enable streaming. This sets up a background `screenrecord` process on the device and pipes the H264 data directly to Python.

```python
# Streaming is usually managed automatically by the controller
# To verify it's working:
if controller.adb.is_streaming():
    print("Streaming active - ultra low latency mode")
```

### Headless Mode

Pymordial is designed to work with minimal visual feedback if needed, but for BlueStacks, the window must be rendered. You can however run your Python script in headless environments as long as it can connect to the ADB port.

---

## Contributing

Contributions are welcome! Please ensure you use `uv` for development.

1.  Clone the repository.
2.  Run `uv sync` to install dependencies.
3.  Run `uv run pytest` to execute the test suite (requires an active BlueStacks instance for integration tests).

## License

MIT License. See [LICENSE](LICENSE) for details.
