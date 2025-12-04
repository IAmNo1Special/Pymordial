"""Element detection and interaction example with ready_element pattern.

This script demonstrates how to:
1. Define a ready_element for automatic READY state detection
2. Define UI elements (images, pixels, text)
3. Find elements on screen
4. Click elements
5. Check element visibility
"""

from logging import INFO, basicConfig, getLogger
from pathlib import Path

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.pymordial_app import PymordialApp

logger = getLogger(__name__)


def main():
    """Find and interact with UI elements on screen."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial Element Interaction Example ===\n")

    try:
        # Create controller
        logger.info("1. Creating PymordialController...")
        controller = PymordialController()

        if not controller.bluestacks.is_ready():
            logger.info("   Opening BlueStacks...")
            controller.bluestacks.open()
        logger.info("   ✓ BlueStacks ready\n")
    except Exception as e:
        logger.error(f"Failed to initialize controller: {e}")
        return

    # Example 1: Define an image element
    logger.info("2. Defining image element...")
    store_button: PymordialImage = PymordialImage(
        label="store_button",
        og_resolution=(1920, 1080),
        filepath=Path(r"F:\Pymordial\src\pymordial\assets\bluestacks_store_button.png"),
        confidence=0.6,
    )
    logger.info(f"   Created: {store_button}\n")

    # Example 2: Define a pixel element
    logger.info("3. Defining pixel element...")
    status_pixel = PymordialPixel(
        label="status_indicator",
        position=(100, 50),  # x, y coordinates
        pixel_color=(255, 255, 255),  # RGB white
        tolerance=10,
    )
    logger.info(f"   Created: {status_pixel}\n")

    # Example 3: Define a text element
    logger.info("4. Defining text element...")
    store_text = PymordialText(
        label="store_text",
        element_text="Store",
        position=(500, 100),  # Optional region to search
        size=(200, 2000),
    )
    logger.info(f"   Created: {store_text}\n")

    # Example 4: Define app with ready_element
    logger.info("5. Defining app with automatic READY detection...")
    # The app will auto-transition to READY when store_button is visible
    play_earn_text = PymordialText(label="play_earn_ready", element_text="Play & Earn")

    bluestacks_app = PymordialApp(
        app_name="BlueStacks",
        package_name="com.bluestacks.appmart",
        ready_element=play_earn_text,  # Auto-detects when app is ready!
    )
    controller.add_app(bluestacks_app)
    logger.info(f"   Created app with ready_element: {play_earn_text.label}\n")

    # Check visibility and click
    logger.info("6. Checking if store button is visible...")
    try:
        is_visible = controller.is_element_visible(store_button)
        if is_visible:
            logger.info("   ✓ Store button is visible!\n")

            # Try to click it
            logger.info("7. Clicking store button...")
            controller.click_element(store_button)
            logger.info("   ✓ Clicked!\n")
        else:
            logger.info("   ✗ Store button not visible\n")
    except Exception as e:
        logger.error(f"   Error: {e}\n")

    # Find element coordinates
    logger.info("8. Finding element coordinates...")
    try:
        coords = controller.find_element(store_button)
        if coords:
            logger.info(f"   Found at: {coords}\n")
        else:
            logger.info("   Not found\n")
    except Exception as e:
        logger.error(f"   Error: {e}\n")

    logger.info("✓ Example completed!\n")
    logger.info("Tips:")
    logger.info("  • Capture your own element images using Screenshot tools")
    logger.info("  • Adjust confidence (0.0-1.0) for matching sensitivity")
    logger.info("  • Use pixel elements for fast color-based detection")
    logger.info("  • Text elements require OCR (Tesseract or EasyOCR)")
    logger.info("  • Define ready_element for automatic LOADING→READY transition")


if __name__ == "__main__":
    main()
