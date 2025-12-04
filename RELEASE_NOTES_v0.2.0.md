# Pymordial v0.2.0 - The "Streaming" Release 🎬

## 🎉 Major Update

**Pymordial v0.2.0** brings real-time streaming, a cleaner API, and modernized dataclass elements. This release includes breaking changes to improve consistency and usability.

## ⚠️ Breaking Changes

| Old API | New API |
|---------|---------|
| `bluestacks_resolution=(1920, 1080)` | `og_resolution=(1920, 1080)` |
| `asset_path="path/to/img.png"` | `filepath="path/to/img.png"` |
| `element.match(screenshot)` | `image_controller.where_element(element)` |
| `PymordialButton(...)` | `PymordialImage(...)` |
| `ImageTextChecker` | `TextController` |

## ✨ Key Highlights

### 🎬 Real-Time Streaming API
Access device frames with 16-33ms latency instead of 200ms+ screenshots:

```python
controller.start_streaming()
try:
    while True:
        frame = controller.get_frame()  # Instant!
        if controller.check_text("Victory", frame):
            break
finally:
    controller.stop_streaming()
```

### 🎮 Convenience Methods
New high-level methods on `PymordialController`:

```python
# Capture screen (falls back to screenshot if not streaming)
screen = controller.capture_screen()

# Click an element by image
controller.click_element(my_button)

# Check if element is visible
if controller.is_element_visible(my_button):
    ...

# Read text from screen
text = controller.read_text(screen)
```

### 📦 Modernized Dataclass Elements
All elements now use `@dataclass(kw_only=True)` with robust validation:

```python
from pymordial.core.elements import PymordialImage, PymordialPixel, PymordialText

# Image element with validation
button = PymordialImage(
    label="start_button",
    filepath="assets/start.png",  # Validated path
    confidence=0.8,               # Must be 0.0-1.0
)

# Pixel element
pixel = PymordialPixel(
    label="ready_indicator",
    position=(100, 200),
    pixel_color=(255, 0, 0),      # RGB tuple
    tolerance=10,                 # Color tolerance
)
```

### 📚 Project Intelligence Documentation
New `.protel/` directory with 3-tier documentation:
- **Stakeholders**: `explain_pymordial_like_im_a_potato.md`
- **Junior Devs**: `pymordial_survival_guide_for_eager_juniors.md`
- **Architects**: `pymordial_god_mode_architecture_review.md`

## 📦 Installation

```bash
pip install pymordial==0.2.0
# or
uv add pymordial==0.2.0
```

## 🔄 Migration Guide

### 1. Update Element Constructors

```python
# Before (v0.1.1)
img = PymordialImage(
    label="btn",
    bluestacks_resolution=(1920, 1080),
    asset_path="assets/btn.png",
    confidence=0.8,
)

# After (v0.2.0)
img = PymordialImage(
    label="btn",
    og_resolution=(1920, 1080),
    filepath="assets/btn.png",
    confidence=0.8,
)
```

### 2. Replace `.match()` Calls

```python
# Before (v0.1.1)
result = element.match(screenshot)

# After (v0.2.0)
result = controller.image.where_element(element, screenshot)
# Or use the convenience method:
if controller.is_element_visible(element):
    controller.click_element(element)
```

### 3. Replace `PymordialButton`

```python
# Before (v0.1.1)
btn = PymordialButton(label="click_me", ...)

# After (v0.2.0)
btn = PymordialImage(label="click_me", ...)
```

## 🧪 Test Suite

- **163 tests passing** (100% pass rate)
- Integration tests skip gracefully when BlueStacks unavailable
- Robust fixtures for CI/CD environments

## 📚 Documentation

- [GitHub Repository](https://github.com/IAmNo1Special/Pymordial)
- [API Reference](docs/API_REFERENCE.md)
- [Quickstart Guide](docs/QUICKSTART.md)

---
*Built with ❤️ by IAmNo1Special*
