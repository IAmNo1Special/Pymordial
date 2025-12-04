"""Custom app with screens and elements example.

This script demonstrates how to:
1. Define a complete app with multiple screens
2. Add elements to screens
3. Organize your automation structure
4. Access app elements properly
"""

from logging import INFO, basicConfig, getLogger
from pathlib import Path

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.pymordial_app import PymordialApp
from pymordial.core.pymordial_screen import PymordialScreen

logger = getLogger(__name__)


def main():
    """Create a structured app with screens and elements."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial Custom App Structure Example ===\n")

    # Create controller
    logger.info("1. Creating PymordialController...")
    controller = PymordialController()
    logger.info("   ✓ Controller created\n")

    # Define your custom app
    # TODO: Replace with your app name and package name
    logger.info("2. Defining custom app...")
    my_game = PymordialApp(app_name="MyGame", package_name="com.example.mygame")
    logger.info(f"   Created app: {my_game}\n")

    # Create main menu screen
    logger.info("3. Creating Main Menu screen...")
    main_menu_screen = PymordialScreen(name="main_menu")

    # Add elements to main menu
    store_button: PymordialImage = PymordialImage(
        label="store_button",
        og_resolution=(1920, 1080),
        filepath=Path(r"F:\Pymordial\src\pymordial\assets\bluestacks_store_button.png"),
        confidence=0.6,
    )

    playstore_search_input: PymordialImage = PymordialImage(
        label="playstore_search_input",
        og_resolution=(1920, 1080),
        filepath=Path(r"F:\Pymordial\src\pymordial\assets\bluestacks_playstore_search_input.png"),
        confidence=0.5,
        image_text="Search for games & apps",
    )

    play_earn_text = PymordialText(label="play_earn_text", element_text="Play & Earn")

    main_menu_screen.add_element(store_button)
    main_menu_screen.add_element(playstore_search_input)
    main_menu_screen.add_element(play_earn_text)
    logger.info(f"   Added {len(main_menu_screen.elements)} elements to main menu\n")

    # Add screens to app
    logger.info("5. Adding screens to app...")
    my_game.add_screen(main_menu_screen)
    logger.info(f"   App now has {len(my_game.screens)} screens\n")

    # Register app with controller
    logger.info("6. Registering app with controller...")
    controller.add_app(my_game)
    logger.info("   ✓ App registered\n")

    # Display app structure
    logger.info("=" * 50)
    logger.info("APP STRUCTURE")
    logger.info("=" * 50)
    logger.info(f"\nApp: {my_game.app_name}")
    logger.info(f"Package: {my_game.package_name}")
    logger.info(f"State: {my_game.app_state.current_state.name}")
    logger.info(f"\nScreens: {list(my_game.screens.keys())}")

    for screen_name, screen in my_game.screens.items():
        logger.info(f"\n  Screen: {screen_name}")
        logger.info(f"  Elements ({len(screen.elements)}):")
        for elem_name, element in screen.elements.items():
            logger.info(f"    - {elem_name}: {type(element).__name__}")

    # Show usage patterns
    logger.info("\n" + "=" * 50)
    logger.info("USAGE PATTERNS")
    logger.info("=" * 50 + "\n")

    logger.info("# Open the app:")
    logger.info("my_game.open()\n")

    logger.info("# Get an element from a screen:")
    logger.info("play_btn = my_game.screens['main_menu'].get_element('play_button')\n")

    logger.info("# Click the element:")
    logger.info("controller.click_element(play_btn)\n")

    logger.info("# Check if element is visible:")
    logger.info("is_visible = controller.is_element_visible(play_btn)\n")

    logger.info("# Find element coordinates:")
    logger.info("coords = controller.find_element(play_btn)\n")

    logger.info("\n✓ Example completed!\n")
    logger.info("Tips:")
    logger.info("  • Organize elements by screen for better structure")
    logger.info("  • Use descriptive names for everything")
    logger.info("  • Store asset paths in constants")
    logger.info("  • Create helper methods for common actions")
    logger.info("  • Use app states to track where you are")


if __name__ == "__main__":
    main()
