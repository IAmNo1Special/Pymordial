# Pymordial API Reference

This reference documents the public API of the Pymordial framework.

## PymordialController

The main entry point for automation. It acts as a facade, coordinating ADB, BlueStacks, and Image Recognition.

```python
from pymordial import PymordialController
controller = PymordialController(adb_host="127.0.0.1", adb_port=5555)
```

### Convenience Methods (Recommended)

These methods are the preferred way to interact with the emulator.

| Method | Description |
|--------|-------------|
| `tap(x, y)` | Tap at specific coordinates. |
| `swipe(x1, y1, x2, y2, duration_ms)` | Swipe from (x1, y1) to (x2, y2). |
| `go_home()` | Press the Home button. |
| `go_back()` | Press the Back button. |
| `press_enter()` | Press the Enter key. |
| `press_esc()` | Press the Escape key. |
| `send_text(text)` | Type text (ADB keyboard). |
| `capture_screen()` | Take a screenshot (returns bytes). |
| `read_text(image)` | Extract text from an image using OCR. |
| `check_text(text, image)` | Check if text exists in an image. |
| `start_streaming(resolution=1024, bitrate="5M")` | Start high-performance H.264 streaming. |
| `stop_streaming()` | Stop streaming. |
| `get_frame()` | Get the latest frame from the stream (numpy array). |
| `is_bluestacks_ready()` | Check if BlueStacks is in the `READY` state. |

### App Management

| Method | Description |
|--------|-------------|
| `add_app(app)` | Register a `PymordialApp` instance. |
| `list_apps()` | List registered apps. |
| `is_app_running(app)` | Check if an app's process is running. |

---

## PymordialApp

Represents an Android application.

```python
from pymordial import PymordialApp
app = PymordialApp("Revomon", "com.revomon.game")
```

| Method | Description |
|--------|-------------|
| `open()` | Launch the app (returns `bool`). |
| `close()` | Force-stop the app (returns `bool`). |
| `is_open()` | Check if the app is in `READY` state. |
| `is_loading()` | Check if the app is in `LOADING` state. |
| `is_closed()` | Check if the app is in `CLOSED` state. |

---

## PymordialElement

Represents a UI element (button, image, text) to interact with.

```python
from pymordial import PymordialElement

btn = PymordialElement(
    label="battle_btn",
    element_type="image",
    asset_path="assets/battle.png",
    confidence=0.8
)
```

| Property | Description |
|----------|-------------|
| `label` | Unique identifier. |
| `element_type` | "image", "text", "button", "pixel". |
| `asset_path` | Path to template image (for image matching). |
| `confidence` | Match confidence threshold (0.0 - 1.0). |
| `region` | Bounding box (x1, y1, x2, y2). |
| `center` | Center coordinates (x, y). |

---

## AdbController (Low-Level)

Direct access to ADB commands. Accessed via `controller.adb`.

| Method | Description |
|--------|-------------|
| `connect()` | Connect to ADB server. |
| `disconnect()` | Disconnect from ADB. |
| `shell_command(cmd)` | Run a raw shell command. |
| `get_current_app()` | Get the package name of the focused app. |

---

## BluestacksController (Low-Level)

Direct access to emulator control. Accessed via `controller.bluestacks`.

| Method | Description |
|--------|-------------|
| `open()` | Launch BlueStacks. |
| `kill_bluestacks()` | Force-kill the BlueStacks process. |
| `wait_for_load()` | Block until BlueStacks is `READY`. |

---

## ImageController (Low-Level)

Direct access to computer vision. Accessed via `controller.image`.

| Method | Description |
|--------|-------------|
| `where_element(element, image)` | Find coordinates of an element. |
| `check_pixel_color(coord, color, image)` | Verify pixel color at coordinates. |
