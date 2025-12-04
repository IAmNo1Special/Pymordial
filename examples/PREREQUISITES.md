# Prerequisites for Running Pymordial Examples

## System Requirements

### 1. BlueStacks Configuration
- **Version**: BlueStacks 5 or higher
- **ADB Enabled**: Settings → Advanced → Android Debug Bridge → **ON**
- **Port**: Default 5555 (configurable in `config.yaml`)
- **Instance**: Multi-instance manager works, examples use first instance

**Note**: Pymordial uses the `adb-shell` Python package for ADB connectivity. You do **NOT** need system ADB (`adb.exe`) installed!

### 2. Python Environment
- **Version**: Python 3.11+ (3.13+ recommended)
- **Package Manager**: `uv` (recommended) or `pip`

**Installation**:
```bash
# Using uv (recommended)
uv add pymordial

# Using pip
pip install pymordial
```

### 3. OCR Setup
- **Tesseract**: Bundled with Pymordial (no separate install needed!)
- **Custom Path** (optional): Override in `config.yaml`:
  ```yaml
  extract_strategy:
    tesseract:
      tesseract_cmd: "C:\\\\Path\\\\To\\\\tesseract.exe"
  ```

---

## Example-Specific Requirements

### All Examples
- **BlueStacks running**: Examples auto-launch if closed
- **Screen visible**: Some examples capture screenshots

### 03_element_clicking.py
- **Assets**: Uses bundled BlueStacks UI assets
- **Custom elements**: Replace paths with your own screenshots

### 04_ocr_reading.py
- **Clear text**: Works best with high-contrast UI
- **BlueStacks home screen**: Example reads from default screen

### 05_custom_app_screens.py  
- **Template code**: Replace `MyGame` with your actual app
- **Asset paths**: Update to your actual button/element images

---

## Common Issues

### "BlueStacks not detected"
- **Solution**: Verify `HD-Player.exe` is running
- **Multi-instance**: Rename desired instance's process if needed

### "App stays in LOADING state"
This is expected behavior! Apps remain in `LOADING` until:

1. **Automatic** (recommended): Define a `ready_element`:
   ```python
   app = PymordialApp(
       "MyGame", "com.example.game",
       ready_element=PymordialText(label="title", element_text="Play")
   )
   app.open()  # Auto-transitions to READY when "Play" visible
   ```

2. **Manual**: Detect loading and transition yourself:
   ```python
   app.open()
   # Your loading detection logic...
   if controller.is_element_visible(start_button):
       app.app_state.transition_to(AppLifecycleState.READY)
   ```

### "Element not found"
- **Confidence too high**: Lower `confidence` value (0.6-0.8)
- **Resolution mismatch**: Capture assets at current resolution
- **Timeout**: Increase `max_tries` parameter

### "OCR returns gibberish"
- **Poor contrast**: OCR needs clear, legible text
- **Wrong strategy**: Try `RevomonTextStrategy` or custom strategy
- **Crop region**: Focus on specific text area using `position`/`size`

---

## Running Examples

All examples use:
```bash
uv run examples/01_basic_connection.py
uv run examples/02_app_control.py
# ... etc
```

**Tip**: Run all at once:
```bash
uv run examples/01_basic_connection.py ; \
uv run examples/02_app_control.py ; \
uv run examples/03_element_clicking.py ; \
uv run examples/04_ocr_reading.py ; \
uv run examples/05_custom_app_screens.py
```

---

## Next Steps

After running examples:
- Read [QUICKSTART.md](../docs/QUICKSTART.md)
- Check [API_REFERENCE.md](../docs/API_REFERENCE.md)
- Review [pymordial_knowledge.md](../docs/pymordial_knowledge.md)

Happy automating! 🤖
