# Pymordial Examples

Practical examples demonstrating Pymordial for Android automation on BlueStacks.

## Prerequisites

- BlueStacks 5+ installed and running
- Pymordial installed (`uv pip install pymordial`)
- ADB connection working

## Examples Overview

### [01_basic_connection.py](01_basic_connection.py)
**Basics**: Connecting to BlueStacks via ADB

Learn how to:
- Create a `PymordialController`
- Check connection status
- Execute shell commands
- Verify Android version

```bash
uv run examples/01_basic_connection.py
```

---

### [02_app_control.py](02_app_control.py)
**App Lifecycle**: Opening, closing, and managing apps

Learn how to:
- Define `PymordialApp` instances
- Register apps with controller
- Open/close apps
- Check app running status
- Use app lifecycle states

```bash
uv run examples/02_app_control.py
```

---

### [03_element_clicking.py](03_element_clicking.py)
**Element Interaction**: Finding and clicking UI elements

Learn how to:
- Define `PymordialImage` elements (buttons, icons)
- Define `PymordialPixel` elements (color-based)
- Define `PymordialText` elements (OCR-based)
- Check element visibility
- Find element coordinates
- Click elements

```bash
uv run examples/03_element_clicking.py
```

**Note**: Requires actual image assets for full functionality.

---

### [04_ocr_reading.py](04_ocr_reading.py)
**OCR**: Text extraction and search

Learn how to:
- Capture screenshots
- Extract all text from screen
- Search for specific text
- Find text coordinates
- Use extraction strategies (`DefaultExtractStrategy`, `RevomonTextStrategy`)

```bash
uv run examples/04_ocr_reading.py
```

**Requires**: Tesseract OCR installed (see `TESSERACT_INSTALL.md`)

---

### [05_custom_app_screens.py](05_custom_app_screens.py)
**App Structure**: Organizing complex automations

Learn how to:
- Create apps with multiple screens
- Add elements to screens
- Access elements via screens
- Structure automation code properly

```bash
uv run examples/05_custom_app_screens.py
```

---

## Element Types

Pymordial supports three element types:

### `PymordialImage`
Image-based detection using template matching.

```python
button = PymordialImage(
    label="play_button",
    filepath=Path("assets/play.png"),
    confidence=0.8  # 0.0-1.0
)
```

### `PymordialPixel`
Fast color-based detection at specific coordinates.

```python
indicator = PymordialPixel(
    label="status",
    position=(100, 50),
    pixel_color=(255, 255, 255),  # RGB
    tolerance=10  # 0-255
)
```

### `PymordialText`
OCR-based text detection and search.

```python
title = PymordialText(
    label="game_title",
    element_text="My Game",
    position=(0, 0),  # Optional region
    size=(800, 100)
)
```

---

## Tips

1. **Start Simple**: Begin with `01_basic_connection.py` to verify setup
2. **Capture Assets**: Screenshot and crop UI elements as PNGs
3. **Use Streaming**: Enable video streaming for faster frame capture
4. **Adjust Confidence**: Lower for fuzzy matching, higher for precision
5. **Enable Logging**: Set level to DEBUG to see what's happening

## Creating Element Images

To use `PymordialImage` elements:

1. Take a screenshot of BlueStacks
2. Crop the button/element you want to detect
3. Save as PNG
4. Reference in your code:

```python
my_button = PymordialImage(
    label="my_button",
    filepath=Path("assets/my_button.png"),
    confidence=0.8
)
```

## Common Issues

**"ADB not connected"**
- Ensure BlueStacks is running
- Check ADB enabled in BlueStacks settings
- Try restarting BlueStacks

**"Element not found"**
- Element must be visible on screen
- Image resolution must match
- Try lowering confidence threshold

**"OCR not detecting text"**
- Ensure Tesseract is installed
- Text needs good contrast
- Try different extraction strategies
- Crop to text region

## Next Steps

- Review [Quickstart Guide](../README.md#quickstart)
- Build your own automation!

Happy automating! 🎮🤖
