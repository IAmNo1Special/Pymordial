"""OCR text reading example.

This script demonstrates how to:
1. Capture screenshots
2. Extract text using OCR (Tesseract)
3. Use extraction strategies for better results
4. Search for specific text on screen
5. Find text coordinates
"""

from logging import INFO, basicConfig, getLogger

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.ocr.extract_strategy import DefaultExtractStrategy, RevomonTextStrategy

logger = getLogger(__name__)


def main():
    """Read text from screen using OCR."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial OCR Reading Example ===\n")

    # Create controller
    logger.info("1. Creating PymordialController...")
    controller = PymordialController()

    if not controller.bluestacks.is_ready():
        controller.bluestacks.open()
    logger.info("   ✓ BlueStacks ready\n")

    # Capture screenshot
    logger.info("2. Capturing screenshot...")
    screenshot = controller.capture_screen()

    if screenshot:
        logger.info("   ✓ Screenshot captured\n")
    else:
        logger.error("   ✗ Failed to capture screenshot")
        return

    # Example 1: Extract all text using default OCR
    logger.info("3. Extracting all text (default OCR)...")
    text_lines = controller.text.read_text(screenshot)

    logger.info(f"   Found {len(text_lines)} lines of text:")
    for i, line in enumerate(text_lines[:5], 1):  # Show first 5 lines
        logger.info(f"     {i}. {line}")

    if len(text_lines) > 5:
        logger.info(f"     ... and {len(text_lines) - 5} more lines")

    # Example 2: Search for specific text
    logger.info("\n4. Searching for specific text...")
    search_term = "store"
    found = controller.text.check_text(
        text_to_find=search_term, image_path=screenshot, case_sensitive=False
    )

    if found:
        logger.info(f"   ✓ Found '{search_term}' on screen")
    else:
        logger.info(f"   ✗ '{search_term}' not found")

    # Example 3: Find text coordinates
    logger.info("\n5. Finding text coordinates...")
    coords = controller.text.find_text(text_to_find=search_term, image_path=screenshot)

    if coords:
        logger.info(f"   ✓ Found '{search_term}' at coordinates: {coords}")
    else:
        logger.info(f"   ✗ Coordinates not found for '{search_term}'")

    # Example 4: Using custom extraction strategy
    logger.info("\n6. Using default extraction strategy...")
    strategy = DefaultExtractStrategy()
    custom_text = controller.text.read_text(screenshot, strategy=strategy)

    logger.info(f"   Extracted {len(custom_text)} lines with strategy")

    # Example 5: Game-specific strategy (if using Revomon)
    logger.info("\n7. Using Revomon-specific strategy...")
    revomon_strategy = RevomonTextStrategy(mode="default")
    revomon_text = controller.text.read_text(screenshot, strategy=revomon_strategy)

    logger.info(f"   Extracted {len(revomon_text)} lines with Revomon strategy")

    logger.info("\n✓ Example completed!\n")
    logger.info("Tips:")
    logger.info("  • OCR works best on clear, high-contrast text")
    logger.info("  • Use extraction strategies for game-specific formatting")
    logger.info("  • Case-insensitive search is more reliable")
    logger.info("  • Crop to specific regions for better accuracy")
    logger.info("  • Create custom strategies for your game's UI")


if __name__ == "__main__":
    main()
