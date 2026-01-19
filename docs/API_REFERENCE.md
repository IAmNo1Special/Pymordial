# Pymordial API Reference

Complete reference for the Pymordial automation framework.

## PymordialController

Main entry point - coordinates all subsystems.

### Initialization

```python
from pymordial.controller.pymordial_controller import PymordialController

# Default connection (127.0.0.1:5555)
controller = PymordialController()

# Custom ADB connection
controller = PymordialController(adb_host="192.168.1.100", adb_port=5037)
```

### App Management

| Method | Description | Returns |
|--------|-------------|---------|
| `add_app(app: PymordialApp)` | Register an app | `None` |
| `is_element_visible(element: PymordialElement)` | Check if element is on screen | `bool` |
| `click_element(element: PymordialElement)` | Click an element | `bool` |
| `find_element(element: PymordialElement)` | Get element coordinates | `tuple[int, int] \| None` |

### Screen Capture

| Method | Description | Returns |
|--------|-------------|---------|
| `capture_screen()` | Take screenshot | `bytes \| None` |
| `start_streaming()` | Start H.264 video stream | `bool` |
| `get_frame()` | Get latest stream frame | `np.ndarray \| None` |
| `stop_streaming()` | Stop video stream | `bool` |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `adb` | `AdbController` | ADB subsystem |
| `bluestacks` | `BluestacksController` | Emulator subsystem |
| `image` | `ImageController` | Image recognition |
| `text` | `TextController` | OCR |
| `apps` | `dict` | Registered apps |

---

## PymordialApp

Represents an Android application with lifecycle management.

### Initialization

```python
from pymordial.core.pymordial_app import PymordialApp

app = PymordialApp(
    app_name="MyGame",
    package_name="com.example.mygame"
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `open()` | Launch the app | `bool` |
| `close()` | Force-stop the app | `bool` |
| `is_open()` | Check if state is `READY` | `bool` |
| `is_loading()` | Check if state is `LOADING` | `bool` |
| `is_closed()` | Check if state is `CLOSED` | `bool` |
| `add_screen(screen: PymordialScreen)` | Add a screen | `None` |
| `get_screen(name: str)` | Get a screen by name | `PymordialScreen` |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `app_name` | `str` | Human-readable name |
| `package_name` | `str` | Android package ID |
| `app_state` | `StateMachine` | Lifecycle state |
| `screens` | `dict` | App screens |

---

## PymordialElement Subclasses

Base class for all UI elements.

### PymordialImage

Image-based template matching.

```python
from pathlib import Path
from pymordial.core.elements.pymordial_image import PymordialImage

element = PymordialImage(
    label="unique_id",
    filepath=Path("assets/button.png"),
    confidence=0.8,  # 0.0 - 1.0
    position=(100, 100),  # Optional
    size=(200, 50)  # Optional
)
```

### PymordialPixel

Color-based detection at specific coordinates.

```python
from pymordial.core.elements.pymordial_pixel import PymordialPixel

pixel = PymordialPixel(
    label="unique_id",
    position=(100, 50),  # Required
    pixel_color=(255, 255, 255),  # RGB tuple
    tolerance=10  # 0-255
)
```

### PymordialText

OCR-based text detection.

```python
from pymordial.core.elements.pymordial_text import PymordialText

text = PymordialText(
    label="unique_id",
    element_text="Button Text",
    position=(0, 0),  # Optional search region
    size=(800, 100),  # Optional search region
    extract_strategy=None  # Optional preprocessing
)
```

---

## AdbController

Low-level ADB commands. Access via `controller.adb`.

### Connection

| Method | Description | Returns |
|--------|-------------|---------|
| `connect()` | Connect to ADB | `bool` |
| `disconnect()` | Disconnect from ADB | `None` |
| `is_connected()` | Check connection status | `bool` |

### Input

| Method | Description | Returns |
|--------|-------------|---------|
| `tap(x: int, y: int)` | Tap coordinates | `bool` |
| `swipe(x1, y1, x2, y2, duration_ms)` | Swipe gesture | `bool` |
| `send_text(text: str)` | Type text | `bool` |
| `go_home()` | Press home button | `None` |
| `go_back()` | Press back button | `None` |
| `press_enter()` | Press enter | `None` |
| `press_esc()` | Press escape | `None` |

### App Control

| Method | Description | Returns |
|--------|-------------|---------|
| `open_app(app: PymordialApp)` | Launch app | `bool` |
| `close_app(app: PymordialApp)` | Force-stop app | `bool` |
| `is_app_running(app: PymordialApp)` | Check if running | `bool` |
| `get_current_app()` | Get focused package name | `str \| None` |

### Shell

| Method | Description | Returns |
|--------|-------------|---------|
| `shell_command(cmd: str)` | Execute shell command | `bytes \| None` |

### Streaming

| Method | Description | Returns |
|--------|-------------|---------|
| `start_stream()` | Start H.264 stream | `bool` |
| `get_stream_frame()` | Get latest frame | `np.ndarray \| None` |
| `stop_stream()` | Stop stream | `bool` |

---

## BluestacksController

Emulator management. Access via `controller.bluestacks`.

| Method | Description | Returns |
|--------|-------------|---------|
| `open()` | Launch BlueStacks | `bool` |
| `kill_bluestacks()` | Force-kill process | `None` |
| `wait_for_load()` | Wait until READY | `None` |
| `is_ready()` | Check if state is READY | `bool` |

---

## ImageController

Computer vision. Access via `controller.image`.

| Method | Description | Returns |
|--------|-------------|---------|
| `where_element(element, screenshot, max_tries, set_position, set_size)` | Find element | `tuple[int, int] \| None` |
| `check_pixel_color(coords, color, screenshot, tolerance)` | Verify pixel color | `bool` |

---

## TextController

OCR operations. Access via `controller.text`.

| Method | Description | Returns |
|--------|-------------|---------|
| `read_text(image, strategy)` | Extract all text | `list[str]` |
| `check_text(text_to_find, image, case_sensitive, strategy)` | Search for text | `bool` |
| `find_text(text_to_find, image, strategy)` | Get text coordinates | `tuple[int, int] \| None` |

### OCR Strategies

```python
from pymordial.ocr.extract_strategy import DefaultExtractStrategy, RevomonTextStrategy

# Default preprocessing
strategy = DefaultExtractStrategy()
text = controller.text.read_text(screenshot, strategy=strategy)

# Game-specific preprocessing
revomon = RevomonTextStrategy(mode="default")
text = controller.text.read_text(screenshot, strategy=revomon)
```

---

## Configuration

Customize via `config.yaml` in project root:

```yaml
adb:
  default_ip: "127.0.0.1"
  default_port: 5555

bluestacks:
  resolution: [1920, 1080]
  
element:
  default_confidence: 0.8

tesseract:
  tesseract_cmd: "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

See `src/pymordial/configs.yaml` for all options.

---

## Error Handling

```python
from pymordial.exceptions import (
    PymordialError,  # Base exception
    PymordialConnectionError,
    PymordialTimeoutError,
    ElementNotFoundError
)

try:
    controller.click_element(button)
except ElementNotFoundError:
    print("Button not found!")
except PymordialTimeoutError:
    print("Operation timed out!")
```
