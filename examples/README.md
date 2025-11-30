# Pymordial Examples

This directory contains practical examples demonstrating how to use Pymordial for Android automation on BlueStacks.

## Prerequisites

- BlueStacks 5+ installed and running
- Pymordial installed (`uv pip install .` from project root)
- ADB connection working

## Examples Overview

### [01_basic_connection.py](01_basic_connection.py)
**What it teaches**: Automatic connection setup

Learn how to:
- Create a `PymordialController` (connection is automatic!)
- Verify ADB connection status
- Execute shell commands
- Disconnect cleanly

**Key Insight**: ADB connection happens automatically via the state machine. You don't need to manually call `connect()`!

**Run it**:
```bash
uv run python examples/01_basic_connection.py
```

---

### [02_app_control.py](02_app_control.py)
**What it teaches**: App lifecycle management

Learn how to:
- Define a `PymordialApp`
- Register apps with the controller
- Open and close apps
- Check if an app is running
- Use config values for timeouts (best practice!)

**Run it**:
```bash
uv run python examples/02_app_control.py
```

---

### [03_element_clicking.py](03_element_clicking.py)
**What it teaches**: Finding and clicking UI elements

Learn how to:
- Define buttons as elements
- Use `controller.go_home()` for navigation (clean API!)
- Use `click_element()` to interact with UI
- Handle element not found scenarios
- Use config-based timeout values

**Run it**:
```bash
uv run python examples/03_element_clicking.py
```

**Note**: Uses the BlueStacks store button (asset already included).

---

### [04_ocr_reading.py](04_ocr_reading.py)
**What it teaches**: Text extraction with OCR

Learn how to:
- Use `controller.capture_screen()` convenience method
- Extract text using OCR
- Search for specific text on screen
- Use extraction strategies for better results

**Run it**:
```bash
uv run python examples/04_ocr_reading.py
```

---

### [05_custom_app_screens.py](05_custom_app_screens.py)
**What it teaches**: Organizing complex apps

Learn how to:
- Define apps with multiple screens
- Add elements to specific screens
- Structure your automation code
- Access elements through screens

**Run it**:
```bash
uv run python examples/05_custom_app_screens.py
```

**Note**: Demonstration only - replace asset paths with your own button images.

## 🎯 Convenience Methods

All examples now use the clean API:

```python
# ✅ Clean and intuitive
controller.go_home()
controller.capture_screen()
controller.tap(x, y)
controller.swipe(x1, y1, x2, y2)
controller.go_back()

#  ❌ Old verbose syntax (still works but not recommended)
controller.adb.go_home()
controller.bluestacks.capture_screen()
```

## Tips for Working with Examples

1. **Start Simple**: Begin with `01_basic_connection.py` to verify your setup
2. **Capture Elements**: Use screenshots to capture UI elements for clicking
3. **Use Config**: Store timeout values in `config.yaml` instead of hardcoding
4. **Check Logs**: Set logging level to DEBUG to see what's happening
5. **Handle Errors**: All examples include basic error handling patterns

## Creating Your Own Element Images

To click UI elements, you need PNG images of those elements:

1. Take a screenshot of BlueStacks
2. Crop the button/element you want to click
3. Save as PNG in `assets/` or your own folder
4. Reference the path in your `PymordialButton` or `PymordialImage`

## Common Issues

**"No ADB device connected"**
- Ensure BlueStacks is running
- Check ADB is enabled in BlueStacks settings
- Restart BlueStacks

**"Element not found"**
- Verify the element is visible on screen
- Check your asset image matches the current screen resolution
- Increase the timeout parameter
- Verify you're using config values for consistency

**"OCR not detecting text"**
- Text must have good contrast
- Try different extraction strategies
- Crop the image to focus on the text area

## Next Steps

After working through these examples:
- Read the [Quickstart Guide](../docs/QUICKSTART.md)
- Check the [API Reference](../docs/API_REFERENCE.md)
- Review the [State Management](../docs/STATE_MANAGEMENT.md) guide
- Start building your own automation!

Happy automating! 🎮💊
