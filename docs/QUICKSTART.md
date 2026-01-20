# Pymordial Quickstart Guide 🚀

Get up and running with Pymordial in 5 minutes.

## Prerequisites

1. **Python 3.11+** installed
2. **BlueStacks 5** installed and running
3. **ADB Enabled** in BlueStacks:
   - Settings → Advanced → Android Debug Bridge → **On**
   - Default port is 5555

## Installation

```bash
# Using pip
pip install pymordial

# Using uv (recommended)
uv add pymordial
```

## Your First Script

Create `my_first_bot.py`:

```python
from logging import INFO, basicConfig

from pymordial.controller.pymordial_controller import PymordialController

# Enable logging to see what's happening
basicConfig(level=INFO)

# Create controller - connects to BlueStacks automatically
controller = PymordialController()

# Ensure BlueStacks is running
if not controller.bluestacks.is_ready():
    print("Opening BlueStacks...")
    controller.bluestacks.open()

# Check ADB connection
if controller.adb.is_connected():
    print("✓ Connected to BlueStacks!")
    
    # Get Android version
    result = controller.adb.shell_command("getprop ro.build.version.release")
    print(f"Android version: {result.decode().strip()}")
    
    # Navigate to home screen
    controller.adb.go_home()
    print("✓ Navigated to home screen!")
else:
    print("✗ Connection failed")
```

Run it:
```bash
uv run python my_first_bot.py
```

## Working with Apps

```python
from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp

controller = PymordialController()

# Define your app
my_app = PymordialApp(
    app_name="Calculator",
    package_name="com.android.calculator2"
)

# Register with controller
controller.add_app(my_app)

# Open the app
my_app.open()

# Check if running
if controller.adb.is_app_running(my_app):
    print("App is running!")

# Close the app
my_app.close()
```

## Working with UI Elements

Pymordial supports three element types:

### Image Elements (Template Matching)
```python
from pathlib import Path
from pymordial.core.elements.pymordial_image import PymordialImage

button = PymordialImage(
    label="start_button",
    filepath=Path("assets/start_button.png"),
    confidence=0.8
)

# Check if visible
if controller.is_element_visible(button):
    controller.click_element(button)
```

### Pixel Elements (Color Detection)
```python
from pymordial.core.elements.pymordial_pixel import PymordialPixel

indicator = PymordialPixel(
    label="health_indicator",
    position=(100, 50),
    pixel_color=(255, 0, 0),  # Red
    tolerance=10
)

if controller.is_element_visible(indicator):
    print("Low health detected!")
```

### Text Elements (OCR)
```python
from pymordial.core.elements.pymordial_text import PymordialText

title = PymordialText(
    label="game_title",
    element_text="Start Game"
)

if controller.is_element_visible(title):
    print("Found start screen!")
```

## Using OCR

```python
# Capture screen
screenshot = controller.capture_screen()

# Extract all text
text_lines = controller.text.read_text(screenshot)
for line in text_lines:
    print(line)

# Search for specific text
if controller.text.check_text("Victory", screenshot):
    print("You won!")

# Find text coordinates
coords = controller.text.find_text("Start", screenshot)
if coords:
    print(f"Found 'Start' at {coords}")
```

## High-Performance Streaming

For real-time automation (e.g., game bots):

```python
import time

# Start H.264 streaming (low latency)
controller.start_streaming()

try:
    while True:
        # Get latest frame (numpy array)
        frame = controller.get_frame()
        
        if frame is not None:
            # Use OCR on frame
            if controller.text.check_text("Battle", frame):
                print("Battle screen detected!")
                controller.adb.tap(500, 800)
        
        time.sleep(0.1)  # 10 FPS check rate
        
except KeyboardInterrupt:
    pass
finally:
    controller.stop_streaming()
```

## Next Steps

- Explore [Examples](../examples/) for more patterns
- Read [API Reference](API_REFERENCE.md) for all methods
- Check [pymordial_knowledge.md](pymordial_knowledge.md) for architecture details

Happy automating! 🤖
