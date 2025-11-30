"""OCR text reading example.

This script demonstrates how to:
1. Capture screenshots
2. Extract text using OCR
3. Use extraction strategies for better results
4. Search for specific text on screen
"""

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.extract_strategy import RevomonTextStrategy


def main():
    """Read text from screen using OCR."""
    print("=== Pymordial OCR Reading Example ===\n")

    # Create and initialize controller
    print("1. Creating PymordialController...")
    controller = PymordialController()

    print("Opening Bluestacks...")
    controller.bluestacks.open()

    # Go to home screen (has visible text)
    print("2. Navigating to home screen...")
    controller.go_home()

    # Capture screenshot
    print("3. Capturing screenshot...")
    screenshot = controller.capture_screen()

    if screenshot:
        print("   ✓ Screenshot captured")
    else:
        print("   ✗ Failed to capture screenshot")
        return

    # Extract text using default OCR
    print("4. Extracting text with OCR...")
    text_lines = controller.read_text(screenshot)

    print(f"   Found {len(text_lines)} lines of text:")
    for i, line in enumerate(text_lines[:10], 1):  # Show first 10 lines
        print(f"     {i}. {line}")

    if len(text_lines) > 10:
        print(f"     ... and {len(text_lines) - 10} more lines")

    # Search for specific text
    print("\n5. Searching for specific text...")
    search_term = "store"
    found = controller.check_text(
        screenshot, text_to_find=search_term, case_sensitive=False
    )

    if found:
        print(f"   ✓ Found '{search_term}' on screen")
    else:
        print(f"   ✗ '{search_term}' not found")

    # Using a custom strategy (example with Revomon strategy)
    print("\n6. Using custom extraction strategy...")
    strategy = RevomonTextStrategy(mode="default")
    custom_text = controller.read_text(screenshot, strategy=strategy)

    print(f"   Extracted {len(custom_text)} lines with custom strategy")

    print("\nTips:")
    print("  • OCR works best on clear, high-contrast text")
    print("  • Use extraction strategies for game-specific formatting")
    print("  • Case-insensitive search is more reliable")
    print("  • Pre-process images (crop/enhance) for better results\n")

    print("Example completed!")


if __name__ == "__main__":
    main()
