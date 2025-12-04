# Pymordial Survival Guide for Eager Juniors 🛡️

*Don't break prod. Please. We're begging you.*

---

## Welcome, Brave Junior Developer!

You've been handed the keys to Pymordial. This guide will help you:
1. Understand what's where
2. Make your first safe change
3. Avoid the landmines that will ruin your day

---

## Project Structure (The Map)

```
f:\Pymordial\
├── src/pymordial/           # 🏠 The actual code (don't break this)
│   ├── controller/          # 🎮 The brains - ADB, BlueStacks, Image, Text
│   │   ├── adb_controller.py       # Talks to Android (dangerous territory)
│   │   ├── bluestacks_controller.py # Manages BlueStacks window
│   │   ├── image_controller.py     # Template matching, pixel detection
│   │   ├── pymordial_controller.py # THE FACADE - your main entry point
│   │   └── text_controller.py      # OCR text operations
│   ├── core/                # 📦 Data models & elements
│   │   ├── elements/        # UI element types (Image, Pixel, Text)
│   │   ├── pymordial_app.py        # App lifecycle management
│   │   ├── pymordial_element.py    # Base element class
│   │   └── pymordial_screen.py     # Screen state abstraction
│   ├── ocr/                 # 👁️ Optical Character Recognition
│   │   ├── base.py          # Abstract OCR interface
│   │   ├── tesseract_ocr.py # Default OCR engine
│   │   └── easyocr_ocr.py   # Alternative (ML-based) OCR
│   ├── utils/               # 🔧 Helper stuff
│   │   └── config.py        # Configuration loader
│   ├── assets/              # 🖼️ Image files for UI detection
│   └── configs.yaml         # ⚙️ THE config file (be careful!)
├── tests/                   # 🧪 Test suite (163+ tests)
│   ├── controller/          # Controller tests
│   ├── core/                # Core model tests
│   ├── integration/         # Live BlueStacks tests
│   └── unit/                # Unit tests
├── docs/                    # 📚 Documentation
└── examples/                # 💡 Usage examples
```

---

## Happy Path: How It All Works

Here's the data flow when Pymordial automates a game:

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR AUTOMATION SCRIPT                   │
│                  (e.g., example_main.py)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ Uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              PymordialController (FACADE)                   │
│  - start_streaming(), get_frame(), capture_screen()         │
│  - click_element(), is_element_visible()                    │
│  - read_text(), check_text()                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ Delegates to
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ AdbController│ │ImageController│ │TextController│
    │  - tap()     │ │ - where_image│ │ - read_text  │
    │  - shell()   │ │ - check_pixel│ │ - check_text │
    │  - stream()  │ │ - where_elem │ │ - find_text  │
    └──────┬───────┘ └──────────────┘ └──────────────┘
           │
           ▼
    ┌──────────────┐
    │  BlueStacks  │ ◄── The Android Emulator
    │   Emulator   │
    └──────────────┘
```

### Step-by-Step: Clicking a Button

1. **You call**: `controller.click_element(my_button)`
2. **PymordialController** captures a screenshot via `AdbController`
3. **ImageController** searches for `my_button.filepath` image
4. **If found**: Position is calculated, `AdbController.tap(x, y)` is called
5. **BlueStacks receives the tap** and your game responds

---

## ⚠️ HERE BE DRAGONS ⚠️

These areas will hurt you. Avoid touching unless absolutely necessary.

### 🐉 Dragon #1: `adb_controller.py` - Streaming Code (lines 172-286)

The `start_stream()` method uses:
- Threading with daemon threads
- Queue-based byte buffers
- PyAV H264 decoding
- Lock-free frame access

**Why it's scary**: Race conditions, memory leaks, hanging threads. If you break this, streaming dies and you'll spend HOURS debugging threading issues.

**Safe alternative**: Use the `PymordialController` wrapper methods instead.

### 🐉 Dragon #2: `bluestacks_controller.py` - Window Detection

The `_autoset_filepath()` method does registry magic to find BlueStacks. If you touch this and break it, BlueStacks won't open.

### 🐉 Dragon #3: `configs.yaml` - The Sacred Config

Every controller reads from this file. One typo = the entire framework crashes on import.

**Golden rule**: If you add a config key, add it with a default. Always.

---

## Your First Safe Change ✅

Let's add a new element type detection. This is the **safest, most common** task.

### Step 1: Create a new image asset

Save your game UI element screenshot to:
```
src/pymordial/assets/my_new_button.png
```

### Step 2: Define the element

```python
from pymordial.core.elements.pymordial_image import PymordialImage

my_button = PymordialImage(
    label="my_new_button",
    filepath="src/pymordial/assets/my_new_button.png",
    confidence=0.8,  # How strict the match should be (0.0-1.0)
)
```

### Step 3: Use it in your script

```python
from pymordial.controller.pymordial_controller import PymordialController

controller = PymordialController()
controller.bluestacks.open()

# Click the button when visible
if controller.is_element_visible(my_button):
    controller.click_element(my_button)
```

### Step 4: Run tests

```bash
uv run --dev pytest tests/ -q
```

If all 163 tests pass, you didn't break anything. Congrats! 🎉

---

## Testing Checklist

Before pushing ANY code:

- [ ] `uv run --dev pytest tests/` passes (163+ tests)
- [ ] You didn't modify `configs.yaml` without defaults
- [ ] You didn't touch streaming code (if you did, pray)
- [ ] New code has type hints
- [ ] New public methods have docstrings

---

## Common Pitfalls

| Mistake | Why It Hurts | Fix |
|---------|--------------|-----|
| Using `asset_path` | It's `filepath` now | Check API docs |
| Using `bluestacks_resolution` | It's `og_resolution` now | Check element constructors |
| Calling `.match()` on elements | Method was removed | Use `ImageController.where_element()` |
| Not calling `super().__post_init__()` | Validation breaks | Always call parent post_init |
| Hardcoding paths | Cross-platform hell | Use `Path` objects and config |

---

## Getting Help

1. **Read the tests** - They're the best documentation
2. **Check `docs/`** - API reference, quickstart, testing guide
3. **Search codebase** - `grep_search` is your friend
4. **Ask before touching Dragons** - Seriously, just ask

---

## Outstanding Questions & Blockers

- Are there specific areas of the codebase juniors should focus on first?
- Should there be a "training exercise" repo with guided tasks?
- What's the expected Git workflow (branching, PRs, reviews)?
- Are there code style guides beyond Google Python Style?

> **If you have answers to these questions, run this workflow again (ideally in a new session) with the answers for a more detailed, accurate analysis.**
