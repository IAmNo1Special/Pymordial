"""Element clicking example.

This script demonstrates how to:
1. Define UI elements (buttons/images)
2. Find elements on screen
3. Click elements with retry logic (using config values)
4. Handle element not found scenarios
"""

from pathlib import Path

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.utils.config import get_config

config = get_config()
ELEMENT_RESOLUTION = config["bluestacks"]["resolution"]
ACTION_TIMEOUT = config["app"]["action_timeout"]


def main():
    """Find and click UI elements on screen."""
    print("=== Pymordial Element Clicking Example ===\n")

    # Create and initialize controller
    print("1. Creating Blue PyllController...")
    controller = PymordialController()
    controller.open()

    # Ensure we're on home screen
    print("2. Navigating to home screen...")
    controller.go_home()

    # Define a button element
    # NOTE: You need to capture and save button images first!
    print("3. Defining button element...")

    # Example: BlueStacks store button
    store_button = PymordialButton(
        label="store_button",
        asset_path=Path("src/pymordial/assets/bluestacks_store_button.png"),
        bluestacks_resolution=ELEMENT_RESOLUTION,
        element_text="Store",
        is_static=True,
    )

    # Try to find and click the element
    print(f"4. Attempting to find and click store button (timeout={ACTION_TIMEOUT}s)...")
    result = controller.click_element(store_button, timeout=ACTION_TIMEOUT)

    if result:
        print("   ✓ Successfully clicked store button!")
        print("   Store app should be opening...")
    else:
        print("   ✗ Could not find store button")
        print("   Possible reasons:")
        print("     - Element not visible on current screen")
        print("     - Image asset needs updating")
        print("     - Screen resolution changed")

    print("\nTips:")
    print("  • Capture element images at your BlueStacks resolution")
    print("  • Use PNG format for best matching")
    print("  • Adjust timeout in config.yaml for slow-loading screens")
    print("  • Check element is actually visible before clicking\n")

    print("Example completed!")


if __name__ == "__main__":
    main()
