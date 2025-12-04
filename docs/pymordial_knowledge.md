# Pymordial Knowledge Base

> **For AI Assistants & Developers**: Complete technical reference for understanding, maintaining, and extending Pymordial.

---

## 1. Project Overview

Pymordial is a Python automation framework for Android apps running in BlueStacks.

### Core Capabilities

- **ADB Integration**: Low-level Android Debug Bridge (tap, swipe, shell, streaming)
- **Screen Capture**: Real-time H.264 video streaming (16-33ms latency)
- **Image Recognition**: Template matching with OpenCV
- **OCR**: Text extraction via Tesseract (bundled) or EasyOCR
- **State Management**: Lifecycle tracking for emulator + apps
- **High-Level API**: Unified interface for element interaction

---

## 2. Architecture

### 2.1 Facade Pattern

**`PymordialController`** is the main facade coordinating:
- `AdbController`: Android Debug Bridge operations
- `BluestacksController`: Emulator lifecycle management
- `ImageController`: Computer vision (template matching, pixel detection)
- `TextController`: OCR text extraction and search

**Benefits:**
- Single entry point for users
- Hides complexity of subsystems
- Clean dependency injection

### 2.2 Element Type Hierarchy

```
PymordialElement (base class)
├── PymordialImage (template matching)
├── PymordialPixel (color detection)
└── PymordialText (OCR-based)
```

Each element has:
- `label`: Unique identifier
- `position`: (x, y) coordinates
- `size`: (width, height) dimensions
- `id`: UUID for hashing/equality
- `region`, `center`: Computed properties

### 2.3 Strategy Pattern (OCR Preprocessing)

Different UIs need different preprocessing:

- **`DefaultExtractStrategy`**: Generic (thresholding, denoising)
- **`RevomonTextStrategy`**: Game-specific (cropping, whitelisting)

Users can create custom strategies by inheriting from `PymordialExtractStrategy`.

### 2.4 State Machine Pattern

Prevents invalid operations (e.g., clicking before app loads).

**States**: `CLOSED`, `LOADING`, `READY`

**Transitions**:
- `CLOSED → LOADING` (app launching)
- `LOADING → READY` (app loaded)
- `READY → CLOSED` (app closed)
- `READY → LOADING` (app reloading)

---

## 3. Core Systems

### 3.1 ADB Integration

**Connection Management**:
- TCP socket to ADB server (default 127.0.0.1:5555)
- Uses `adb-shell` library for pure Python implementation
- Automatic reconnection on connection loss

**Input Simulation**:
```python
controller.adb.tap(x, y)                    # Single tap
controller.adb.swipe(x1, y1, x2, y2, ms)   # Swipe gesture
controller.adb.send_text("Hello")           # Text input
controller.adb.go_home()                    # Home button
```

**H.264 Streaming**:
- Uses `screenrecord` command piped over ADB
- PyAV decodes H.264 to RGB numpy arrays
- Runs in background thread
- Typical latency: 16-33ms

### 3.2 BlueStacks Management

**Process Control**:
- Detects `HD-Player.exe` via psutil
- Launches via subprocess if not running
- Waits for ADB connectivity (polling-based)

**State Tracking**:
- Uses `StateMachine` class
- `CLOSED → LOADING → READY` lifecycle
- Transition handlers can trigger actions

### 3.3 Image Recognition

**Template Matching** (`PymordialImage`):
- Uses `pyautogui.locate()` (wrapper for OpenCV)
- Confidence threshold (0.0-1.0)
- Returns center coordinates of match

**Pixel Detection** (`PymordialPixel`):
- Fast RGB color check at specific (x, y)
- Tolerance for minor color variations (0-255)
- Ideal for health bars, status indicators

### 3.4 OCR

**Tesseract** (Default):
- Bundled with package (no separate install needed)
- Configured via `tesseract_cmd` in config
- Supports custom page segmentation modes (PSM)

**EasyOCR** (Optional):
- GPU-accelerated
- Better for non-Latin scripts
- Slower but more accurate

**Extraction Strategies**:
- Preprocess images (resize, denoise, threshold)
- Crop to specific regions
- Whitelist/blacklist characters

---

## 4. Configuration System

**Default Config**: `src/pymordial/configs.yaml` (tracked in git)

**User Overrides**: `config.yaml` at project root (gitignored)

**Loading**:
1. Load defaults
2. Deep merge user overrides
3. Validate required keys

**Key Sections**:
- `adb`: Connection settings, stream config
- `bluestacks`: Resolution, paths
- `element`: Default confidence
- `tesseract`: OCR settings
- `easyocr`: Language support

**TypedDict Definitions**:
All config sections have strongly-typed `TypedDict` classes in `utils/config.py`.

---

## 5. Common Patterns

### 5.1 Basic Automation

```python
from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp

controller = PymordialController()

# Ensure emulator ready
if not controller.bluestacks.is_ready():
    controller.bluestacks.open()

# Define app
app = PymordialApp("MyGame", "com.example.game")
controller.add_app(app)

# Open app
app.open()

# Interact
controller.adb.tap(500, 800)
```

### 5.2 Element-Based Interaction

```python
from pathlib import Path
from pymordial.core.elements.pymordial_image import PymordialImage

button = PymordialImage(
    label="start_btn",
    filepath=Path("assets/start.png"),
    confidence=0.8
)

if controller.is_element_visible(button):
    controller.click_element(button)
```

### 5.3 Streaming-Based Bot

```python
controller.start_streaming()

while True:
    frame = controller.get_frame()
    
    if frame is not None:
        # OCR on frame
        if controller.text.check_text("Victory", frame):
            print("Won!")
            break
    
    time.sleep(0.1)

controller.stop_streaming()
```

### 5.4 Multi-Screen App Structure

```python
from pymordial.core.pymordial_screen import PymordialScreen

main_menu = PymordialScreen(name="main_menu")
main_menu.add_element(play_button)
main_menu.add_element(settings_button)

gameplay = PymordialScreen(name="gameplay")
gameplay.add_element(pause_button)

app.add_screen(main_menu)
app.add_screen(gameplay)

# Access elements
play_btn = app.screens['main_menu'].get_element('play_button')
controller.click_element(play_btn)
```

---

## 6. Debugging

### 6.1 Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 6.2 Common Issues

**"ADB not connected"**:
- Check BlueStacks ADB enabled
- Verify port matches config (default 5555)
- Try `adb kill-server && adb start-server`

**"Element not found"**:
- Ensure element visible on screen
- Lower confidence threshold
- Increase `max_tries` parameter
- Check image resolution matches

**"OCR returns empty"**:
- Verify Tesseract installed (or using bundled version)
- Try different extraction strategy
- Check image has good contrast
- Crop to text region only

**"Streaming not working"**:
- Ensure ADB connection stable
- Check `screenrecord` available on device
- Try lower resolution/bitrate

### 6.3 Useful Debug Commands

```python
# Check current app
pkg = controller.adb.get_current_app()
print(f"Current app: {pkg}")

# Check connection
print(f"Connected: {controller.adb.is_connected()}")

# Check BlueStacks state
print(f"State: {controller.bluestacks.bluestacks_state.current_state.name}")

# Manual element search
coords = controller.image.where_element(button, screenshot)
print(f"Found at: {coords}")
```

---

## 7. Extension Points

### 7.1 Custom OCR Strategy

```python
from pymordial.ocr.extract_strategy import PymordialExtractStrategy
import cv2

class MyGameStrategy(PymordialExtractStrategy):
    def preprocess(self, image):
        # Custom preprocessing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # ... more processing
        return gray
    
    def get_tesseract_config(self):
        return "--psm 7 -c tessedit_char_whitelist=0123456789"
```

### 7.2 Custom Element Type

```python
from pymordial.core.pymordial_element import PymordialElement

@dataclass(kw_only=True)
class PymordialButton(PymordialElement):
    """Custom button element with click animations."""
    
    click_animation: str = "scale"
    
    def __post_init__(self):
        super().__post_init__()
        # Custom validation
```

---

## 8. Performance Tips

1. **Use streaming for real-time bots** (16-33ms vs 200-500ms screenshots)
2. **Cache element locations** when elements are static
3. **Use pixel detection** when possible (faster than image matching)
4. **Crop screenshot regions** before OCR (faster + more accurate)
5. **Lower stream resolution** if FPS more important than clarity
6. **Reuse controller instance** (connection overhead is expensive)

---

## 9. Testing

See [TESTING.md](TESTING.md) for complete testing guide.

**Quick Reference**:
```bash
# Unit tests only
uv run pytest -m "not integration"

# All tests
uv run pytest

# With coverage
uv run pytest --cov=pymordial
```

---

## 10. Dependencies

**Core**:
- `adb-shell`: Pure Python ADB implementation
- `pyautogui`: Template matching wrapper
- `opencv-python`: Image processing
- `pytesseract`: Tesseract OCR binding
- `PyAV`: H.264 video decoding
- `psutil`: Process management
- `Pillow`: Image handling
- `PyYAML`: Configuration

**Optional**:
- `easyocr`: Alternative OCR engine

---

## 11. Project Structure

```
src/pymordial/
├── controller/          # Main controllers
│   ├── adb_controller.py
│   ├── bluestacks_controller.py
│   ├── image_controller.py
│   ├── text_controller.py
│   └── pymordial_controller.py
├── core/               # Core data models
│   ├── elements/       # Element types
│   ├── pymordial_app.py
│   ├── pymordial_element.py
│   └── pymordial_screen.py
├── ocr/                # OCR engines & strategies
│   ├── base.py
│   ├── tesseract_ocr.py
│   ├── easyocr_ocr.py
│   └── extract_strategy.py
├── utils/              # Utilities
│   └── config.py
├── exceptions.py       # Custom exceptions
├── state_machine.py    # State management
└── configs.yaml        # Default configuration
```

---

This knowledge base is version-controlled. Update it when making architectural changes!
