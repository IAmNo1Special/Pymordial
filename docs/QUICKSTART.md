# Pymordial Quickstart Guide 🚀

Get up and running with Pymordial in 5 minutes.

## Prerequisites

1. **Python 3.13+** installed.
2. **BlueStacks 5** installed and running.
3. **ADB Enabled** in BlueStacks:
   - Settings → Advanced → Android Debug Bridge → **On**.
   - Note the port (usually 5555).

## Step 1: Installation

We recommend using `uv` for fast package management, but `pip` works too.

```bash
# Using uv (Recommended)
uv add pymordial

# Using pip
pip install pymordial
```

## Step 2: Your First Bot

Create a file named `my_bot.py`:

```python
import time
from pymordial import PymordialController

# 1. Initialize the controller
# Pymordial automatically connects to ADB at 127.0.0.1:5555
controller = PymordialController()

print("Connecting to BlueStacks...")

# 2. Ensure BlueStacks is ready
if not controller.is_bluestacks_ready():
    print("Opening BlueStacks...")
    controller.bluestacks.open()
    controller.bluestacks.wait_for_load()

print("BlueStacks is Ready!")

# 3. Start high-performance streaming
# This lets us see the screen in real-time (16-33ms latency)
# Defaults to 1024x576 @ 5Mbps for optimal performance
controller.start_streaming()

try:
    while True:
        # Get the latest frame
        frame = controller.get_frame()
        
        if frame is None:
            continue

        # Example: Check for a "Start" button text
        if controller.check_text("Start Game", frame):
            print("Found Start Game button!")
            # Tap coordinates (replace with actual coordinates)
            controller.tap(500, 800)
            time.sleep(1)
        
        # Example: Go home if stuck
        # controller.go_home()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping bot...")

finally:
    # Always clean up!
    controller.stop_streaming()
    controller.disconnect()
```

## Step 3: Run It

```bash
uv run my_bot.py
# or
python my_bot.py
```

## Next Steps

- Check out the [API Reference](API_REFERENCE.md) for all available commands.
- Learn about [Configuration](pymordial_knowledge.md#configuration) to customize ADB ports and OCR settings.
- Explore `examples/` in the repository for more complex bots.
