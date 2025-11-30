"""Custom app with screens example.

This script demonstrates how to:
1. Define a complete app with multiple screens
2. Add elements to screens
3. Organize your automation structure
4. Navigate between screens
"""

from pathlib import Path

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp
from pymordial.core.pymordial_screen import PymordialScreen
from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.core.elements.pymordial_text import PymordialText


def main():
    """Create a structured app with screens and elements."""
    print("=== Pymordial Custom App Structure Example ===\n")

    # Create controller
    print("1. Creating PymordialController...")
    controller = PymordialController()

    # Define your custom app
    print("2. Defining custom app...")
    my_game = PymordialApp(app_name="MyGame", package_name="com.example.mygame")

    # Define the main menu screen
    print("3. Creating Main Menu screen...")
    main_menu = PymordialScreen(name="main_menu")

    # Add elements to main menu
    play_button = PymordialButton(
        name="play_button",
        asset_path=Path("assets/play_button.png"),
        element_text="Play",
        is_static=True,
    )

    settings_button = PymordialButton(
        name="settings_button",
        asset_path=Path("assets/settings_button.png"),
        element_text="Settings",
        is_static=True,
    )

    title_text = PymordialText(
        name="game_title", element_text="My Game Title", is_static=True
    )

    main_menu.add_element(play_button)
    main_menu.add_element(settings_button)
    main_menu.add_element(title_text)

    # Define the gameplay screen
    print("4. Creating Gameplay screen...")
    gameplay = PymordialScreen(name="gameplay")

    pause_button = PymordialButton(
        name="pause_button",
        asset_path=Path("assets/pause_button.png"),
        element_text="Pause",
        is_static=True,
    )

    gameplay.add_element(pause_button)

    # Add screens to app
    print("5. Adding screens to app...")
    my_game.add_screen(main_menu)
    my_game.add_screen(gameplay)

    # Register app with controller
    print("6. Registering app with controller...")
    controller.add_app(my_game)

    # Display app structure
    print("\n=== App Structure ===")
    print(f"App: {my_game.app_name}")
    print(f"Package: {my_game.package_name}")
    print(f"Screens: {list(my_game.screens.keys())}")

    for screen_name, screen in my_game.screens.items():
        print(f"\n  Screen: {screen_name}")
        print(f"  Elements: {list(screen.elements.keys())}")

    print("\n=== Usage Pattern ===")
    print("# Open the app")
    print("controller.my_game.open()")
    print()
    print("# Click an element from main menu")
    print(
        "controller.click_element(my_game.screens['main_menu'].elements['play_button'])"
    )
    print()
    print("# Check if on gameplay screen")
    print(
        "pause_visible = controller.my_game.is_element_visible(my_game.screens['gameplay'].elements['pause_button'])"
    )

    print("\nTips:")
    print("  • Organize elements by screen for better structure")
    print("  • Use descriptive names for screens and elements")
    print("  • Store asset paths in a constants file")
    print("  • Consider creating helper functions for common actions\n")

    print("Example completed!")


if __name__ == "__main__":
    main()
