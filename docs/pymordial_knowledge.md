# Pymordial Knowledge Base

> **For AI Assistants & Developers**: This knowledge base covers the ENTIRE Pymordial project. Use this to understand, maintain, debug, or extend any part of the codebase.

---

## 1. Project Overview

Pymordial is a **Python automation framework** for controlling Android apps running in the BlueStacks emulator. It provides:

- **ADB Integration**: Low-level Android Debug Bridge commands (tap, swipe, shell, screen capture)
- **Screen Streaming**: Real-time H.264 video decoding using PyAV
- **Image Recognition**: Template matching using OpenCV/pyautogui
- **OCR (Optical Character Recognition)**: Text extraction with Tesseract (Bundled) or EasyOCR
- **State Management**: Lifecycle tracking for emulator + app states
- **Automation API**: High-level methods for clicking elements, reading text, managing apps

---

## 2. Architecture & Design Patterns

### 2.1 Facade Pattern (Primary Pattern)

**`PymordialController`** is the main facade that composes:
- `ADBController`: Low-level ADB operations
- `BluestacksController`: Emulator management
- `ImageController`: Image recognition + OCR

**Benefits**:
- **Single entry point** for users
- **Hides complexity** of subsystems
- **Dependency injection** via constructor

### 2.2 Strategy Pattern (OCR Preprocessing)

Different UI elements require different preprocessing.
- **`DefaultExtractStrategy`**: Generic preprocessing (Otsu thresholding, inversion)
- **`RevomonTextStrategy`**: Game-specific strategies (e.g., cropping specific regions, whitelisting characters)

### 2.3 State Machine Pattern

Prevents invalid operations (e.g., clicking buttons when app isn't loaded).
- **States**: `CLOSED`, `LOADING`, `READY`
- **Transitions**: Managed automatically by the controllers.

---

## 3. Core Systems Deep Dive

### 3.1 ADB Integration (`ADBController`)

Handles all communication with the Android instance.
- **Connection**: Manages TCP connection to ADB server.
- **Input**: `tap`, `swipe`, `text`, `keyevent`.
- **Streaming**: Decodes H.264 stream from `screenrecord` for low-latency (16-33ms) frame access.

### 3.2 BlueStacks Management (`BluestacksController`)

Manages the emulator process.
- **Lifecycle**: Opens/Closes `HD-Player.exe`.
- **Loading Detection**: Waits for the loading screen to disappear.

### 3.3 Image Recognition (`ImageController`)

- **Template Matching**: Finds UI elements using `pyautogui.locate`.
- **OCR**: Delegates to `TesseractOCR` (bundled) or `EasyOCR`.

---

## 4. Configuration

Pymordial uses `src/pymordial/configs.yaml` for defaults. Users can override these by creating a `config.yaml` in their project root.

**Key Configuration Options:**
- `adb.default_port`: ADB port (default 5555).
- `tesseract.tesseract_cmd`: Path to Tesseract binary (defaults to bundled version).
- `bluestacks.resolution`: Expected resolution (default 1920x1080).

---

## 5. Common Use Cases

### 5.1 Basic Automation
```python
controller = PymordialController()
controller.bluestacks.open()
controller.bluestacks.wait_for_load()
controller.revomon.open()
controller.tap(100, 200)
```

### 5.2 High-Performance Streaming
```python
controller.start_streaming()
while True:
    frame = controller.get_frame()
    # Process frame...
controller.stop_streaming()
```

### 5.3 OCR Reading
```python
text = controller.read_text(screenshot)
if "Victory" in text:
    print("Won!")
```

---

## 6. Troubleshooting

- **ADB Connection Failed**: Ensure BlueStacks ADB is enabled and port matches config.
- **OCR Empty**: Check image preprocessing strategies or Tesseract path.
- **App Not Opening**: Verify package name in `PymordialApp` definition.
