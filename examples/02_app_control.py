"""App control example.

This script demonstrates how to:
1. Define a Pymordial app
2. Open and close apps
3. Check if an app is running
4. Use app lifecycle states
"""

import time
from logging import INFO, basicConfig, getLogger

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp

logger = getLogger(__name__)


def main():
    """Control an Android app lifecycle."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial App Control Example ===\n")

    # Create controller and ensure BlueStacks is running
    logger.info("1. Creating PymordialController...")
    controller = PymordialController()

    if not controller.bluestacks.is_ready():
        logger.info("   Opening BlueStacks...")
        controller.bluestacks.open()
    logger.info("   ✓ BlueStacks ready\n")

    # Define an app (using Android Settings as example)
    logger.info("2. Defining Android Settings app...")
    settings_app = PymordialApp(
        app_name="Settings", package_name="com.android.settings"
    )
    logger.info(f"   Created: {settings_app}")

    # Register the app with the controller
    logger.info("\n3. Registering app with controller...")
    controller.add_app(settings_app)
    logger.info("   ✓ App registered")

    # Open the app
    logger.info("\n4. Opening Settings app...")
    settings_app.open()
    logger.info(f"   App state: {settings_app.app_state.current_state.name}")

    # Wait for app to load
    time.sleep(2)

    # Check if app is running
    logger.info("\n5. Checking if app is running...")
    is_running = controller.adb.is_app_running(settings_app)
    if is_running:
        logger.info("   ✓ Settings app is running")
        logger.info(f"   State: {settings_app.app_state.current_state.name}")

    # Close the app
    logger.info("\n6. Closing Settings app...")
    settings_app.close()
    time.sleep(1)

    # Verify it's closed
    logger.info("\n7. Verifying app is closed...")
    is_running = controller.adb.is_app_running(settings_app)
    if not is_running:
        logger.info("   ✓ Settings app is not running")
        logger.info(f"   State: {settings_app.app_state.current_state.name}")

    logger.info("\n✓ Example completed successfully!\n")


if __name__ == "__main__":
    main()
